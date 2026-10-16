import os
import io
from typing import Dict, Any, List
import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
import plotly.express as px

from src.real_data_pipeline import main as generate_real_data
from src.normalizer import MetricNormalizer
from src.dss_engine import DSSEngine, ALL_METRICS
from src.visualizer import ScoutVisualizer, METRIC_LABELS
from src.scouting_roles import TACTICAL_ROLES, get_role_weights, METRIC_CLUSTERS
from src.report_generator import generate_opta_scout_report
from src.data_verifier_agent import RealDataVerifierAgent

# Streamlit Page Configuration
st.set_page_config(
    page_title="ScoutEduard Pro - Endüstri Standardı Scouting Altyapısı",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End Dark Theme Styling
st.markdown("""
<style>
    .main {
        background-color: #0e1117;
    }
    .stMetric {
        background-color: #161b22;
        padding: 14px;
        border-radius: 10px;
        border: 1px solid #30363d;
    }
    .stButton>button {
        background-color: #00f2fe;
        color: #000000;
        font-weight: bold;
        border-radius: 8px;
        border: none;
        padding: 8px 16px;
    }
    .stButton>button:hover {
        background-color: #00c6ff;
        color: #000000;
    }
    .player-card-box {
        background-color: #161b22;
        padding: 18px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 12px;
    }
    .badge-pos {
        background-color: #21262d;
        color: #00ff87;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
    }
    .badge-league {
        background-color: #21262d;
        color: #00f2fe;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
    }
    .badge-role {
        background-color: #30363d;
        color: #ffd700;
        padding: 4px 10px;
        border-radius: 6px;
        font-weight: bold;
        font-size: 13px;
    }
    .opta-report-container {
        background-color: #161b22;
        padding: 24px;
        border-radius: 12px;
        border: 1px solid #30363d;
        font-family: 'Courier New', Courier, monospace;
        color: #f0f6fc;
        line-height: 1.6;
        white-space: pre-wrap;
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load_real_scout_dataset() -> pd.DataFrame:
    """Loads processed real player dataset or triggers pipeline if missing."""
    raw_path = "data/raw/players.csv"
    processed_path = "data/processed/players_normalized.csv"

    if not os.path.exists(processed_path) or not os.path.exists(raw_path):
        with st.spinner("Gerçek oyuncu veri seti hazırlanıyor..."):
            generate_real_data()
            normalizer = MetricNormalizer()
            df = normalizer.process_and_save(raw_path, processed_path)
    else:
        df = pd.read_csv(processed_path)

    return df


def add_custom_player_to_dataset(new_player_data: Dict[str, Any]) -> None:
    """
    Appends custom player to raw CSV, re-runs normalizer, and clears Streamlit cache.
    """
    raw_path = "data/raw/players.csv"
    processed_path = "data/processed/players_normalized.csv"

    if os.path.exists(raw_path):
        df_raw = pd.read_csv(raw_path)
        new_id = int(df_raw["Player_ID"].max()) + 1 if not df_raw.empty else 1
        new_player_data["Player_ID"] = new_id

        df_updated = pd.concat([df_raw, pd.DataFrame([new_player_data])], ignore_index=True)
        df_updated.to_csv(raw_path, index=False, encoding="utf-8")

        normalizer = MetricNormalizer()
        normalizer.process_and_save(raw_path, processed_path)

        st.cache_data.clear()
        st.success(f"✅ {new_player_data['Name']} başarıyla sisteme eklendi ve yeniden normalize edildi!")


def render_player_profile_dossier(player_row: pd.Series, df: pd.DataFrame, engine: DSSEngine, visualizer: ScoutVisualizer) -> None:
    """
    Renders a comprehensive 360° Player Profile Dossier page with 2-Page Opta Scouting Narrative.
    """
    name = player_row["Name"]
    position = player_row["Position"]
    team = player_row["Team"]
    league = player_row["League"]
    age = player_row["Age"]
    val = player_row["Market_Value_EUR_M"]
    mins = player_row["Minutes_Played"]

    # Header Card
    st.markdown(f"""
    <div class="player-card-box" style="border-left: 6px solid #00f2fe; padding: 22px;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <h1 style="margin:0; color:#f0f6fc; font-size:32px;">👤 {name}</h1>
                <p style="margin-top:8px; font-size:16px;">
                    <span class="badge-pos">{position}</span> &nbsp;
                    <span class="badge-league">{league}</span> &nbsp;
                    <b>Takım:</b> {team} | <b>Yaş:</b> {age} | <b>Piyasa Değeri:</b> €{val}M | <b>Süre:</b> {mins} dk
                </p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Calculate overall position TOPSIS score
    scored_pos_df = engine.calculate_topsis_score(position_filter=position)
    p_scored = scored_pos_df[scored_pos_df["Player_ID"] == player_row["Player_ID"]]
    topsis_score = float(p_scored["TOPSIS_Score"].iloc[0]) if not p_scored.empty else 75.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("TOPSIS Uygunluk Skoru", f"{topsis_score:.1f} / 100")
    c2.metric("Mevki Havuz Sıralaması", f"#{int(p_scored.index.get_loc(p_scored.index[0]) + 1)} / {len(scored_pos_df)}")
    c3.metric("xT (Tehlike Tehdidi) /90", f"{player_row.get('xT_per90', 0.0):.2f}")
    c4.metric("Pack Rate (Ekarte Adam)", f"{player_row.get('Pack_Rate', 0.0):.1f}")

    st.divider()

    # Section A: Wyscout Pizza & Radar Charts
    st.subheader("📊 360° Wyscout Pizza & Radar Profili")
    col_piz, col_rad = st.columns(2)

    with col_piz:
        fig_piz = visualizer.create_pizza_chart(player_row, role_name=f"{position} Profil")
        st.pyplot(fig_piz)

    with col_rad:
        fig_rad = visualizer.create_radar_chart(player_row, title_suffix=f"- {name}")
        st.pyplot(fig_rad)

    st.divider()

    # Section B: Tactical Role Fit Analysis (SciSports Style)
    st.subheader("🎭 Taktiksel Rol Uyumluluk Analizi (SciSports)")
    avail_roles = TACTICAL_ROLES.get(position, {})

    if avail_roles:
        role_cols = st.columns(len(avail_roles))
        for idx, (r_name, r_weights) in enumerate(avail_roles.items()):
            r_scored = engine.calculate_topsis_score(position_filter=position, custom_weights=r_weights)
            r_player_score = r_scored[r_scored["Player_ID"] == player_row["Player_ID"]]
            r_val = float(r_player_score["TOPSIS_Score"].iloc[0]) if not r_player_score.empty else 70.0

            with role_cols[idx]:
                st.markdown(f"**{r_name}**")
                st.progress(min(1.0, max(0.0, r_val / 100.0)))
                st.caption(f"Uyumluluk Skoru: **%{r_val:.1f}**")

    st.divider()

    # Section C: Advanced Metric Breakdown Table
    st.subheader("📑 Kapsamlı İstatistik ve Yüzdelik (Percentile) Dökümü")
    cat_cols = st.columns(2)

    with cat_cols[0]:
        st.markdown("#### ⚽ Hücum & Yaratıcılık Metrikleri")
        att_metrics = ["xG_per90", "xG_per_Shot", "xA_per90", "Key_Passes_per90", "xT_per90", "Progressive_Passes_per90", "Pack_Rate", "Pass_Accuracy_Pct"]
        att_rows = []
        for m in att_metrics:
            if m in player_row:
                raw_v = player_row[m]
                pct_v = player_row.get(f"{m}_percentile", 50.0)
                att_rows.append({
                    "Metrik": METRIC_LABELS.get(m, m),
                    "Değer": f"{raw_v:.2f}" if not m.endswith("_Pct") else f"%{raw_v:.1f}",
                    "Percentile (Yüzdelik)": f"%{int(pct_v)}"
                })
        st.dataframe(pd.DataFrame(att_rows), use_container_width=True)

    with cat_cols[1]:
        st.markdown("#### 🛡️ Defans, Baskı & Fiziksel Metrikler")
        def_metrics = ["PADJ_Tackles_per90", "Defensive_Duels_per90", "Interceptions_per90", "Pressures_per90", "High_Turnovers_per90", "PPDA_Contribution", "PSxG_Net"]
        def_rows = []
        for m in def_metrics:
            if m in player_row:
                raw_v = player_row[m]
                pct_v = player_row.get(f"{m}_percentile", 50.0)
                def_rows.append({
                    "Metrik": METRIC_LABELS.get(m, m),
                    "Değer": f"{raw_v:.2f}" if not m.endswith("_Pct") else f"%{raw_v:.1f}",
                    "Percentile (Yüzdelik)": f"%{int(pct_v)}"
                })
        st.dataframe(pd.DataFrame(def_rows), use_container_width=True)

    st.divider()

    # Section D: OPTA STYLE 2-PAGE SCOUTING NARRATIVE
    st.subheader("📄 2 Sayfalık Opta & StatsPerform Stil Taktiksel Scout Raporu")
    opta_report_text = generate_opta_scout_report(player_row, topsis_score=topsis_score)

    with st.expander(f"📑 {name} - 2 Sayfalık Taktiksel Scout Raporunu İncele", expanded=True):
        st.markdown(f'<div class="opta-report-container">{opta_report_text}</div>', unsafe_allow_html=True)

    st.download_button(
        label="📥 2 Sayfalık Opta Scout Raporunu İndir (TXT)",
        data=opta_report_text.encode("utf-8"),
        file_name=f"{name.replace(' ', '_')}_opta_scout_report.txt",
        mime="text/plain"
    )

    st.divider()

    # Section E: Similar Replacements
    st.subheader("🎯 Bu Oyuncuya En Benzer 3 Muadil Oyuncu")
    _, sims_df = engine.find_similar_players(
        target_player_id=int(player_row["Player_ID"]),
        same_position_only=True,
        top_n=3
    )

    if not sims_df.empty:
        sim_cols = st.columns(3)
        for idx, (_, s_row) in enumerate(sims_df.iterrows()):
            with sim_cols[idx]:
                st.markdown(f"""
                <div class="player-card-box">
                    <h4>#{idx+1} {s_row['Name']}</h4>
                    <p><span class="badge-pos">{s_row['Position']}</span> <span class="badge-league">{s_row['League']}</span></p>
                    <p><b>Takım:</b> {s_row['Team']}</p>
                    <p><b>Yaş:</b> {s_row['Age']} | <b>Değer:</b> €{s_row['Market_Value_EUR_M']}M</p>
                </div>
                """, unsafe_allow_html=True)
                st.metric("Vektör Benzerlik", f"%{s_row['Similarity_Pct']}")

    st.divider()

    # Download Buttons
    st.subheader("📥 Scout Rapor Kartı İndir")
    fig_card = visualizer.create_player_card(player_row, dss_score=topsis_score)
    bytes_card = visualizer.fig_to_bytes(fig_card)
    st.download_button(
        label="📥 360° Oyuncu İstatistik Kartını İndir (PNG)",
        data=bytes_card,
        file_name=f"{name.replace(' ', '_')}_dossier_card.png",
        mime="image/png"
    )


def main() -> None:
    # Header Banner
    st.title("⚽ ScoutEduard Pro - Endüstri Standardı Karar Destek Platformu")
    st.markdown(
        "**SciSports, Wyscout, Opta & StatsBomb Standartlarında Scouting Altyapısı:** "
        "2.000+ Gerçek Futbolcu, **Taktiksel Rol Profilleri**, **Wyscout Yüzdelik Pizza Grafikleri**, "
        "**TOPSIS Skorlama**, **Birebir Kıyaslama** ve **Google Data Verifier Ajanı**."
    )
    st.divider()

    # Load Real Dataset
    df = load_real_scout_dataset()
    visualizer = ScoutVisualizer()
    engine = DSSEngine(df)

    # Sidebar Controls & Filters
    st.sidebar.header("🔍 Scout Filtre & Kontrol Paneli")

    # Data Verifier Agent Trigger Button in Sidebar
    st.sidebar.subheader("🤖 Otomatik Veri Doğrulama Ajanı")
    if st.sidebar.button("🔍 Verileri Google & Transfermarkt İle Teyit Et"):
        with st.spinner("Google & Transfermarkt Doğrulama Ajanı çalışıyor..."):
            verifier_agent = RealDataVerifierAgent()
            audit_summary = verifier_agent.run_full_audit()
            st.cache_data.clear()
            st.sidebar.success(
                f"✅ Teyit Tamamlandı!\n"
                f"• Denetlenen: {audit_summary['Total_Players_Audited']} Oyuncu\n"
                f"• Düzeltilen Değişiklik: {audit_summary['Total_Corrections_Made']}"
            )

    st.sidebar.divider()

    search_query = st.sidebar.text_input("🔎 Oyuncu Ara (İsim):", placeholder="Örn: Ghedjemis, Saka, Osimhen, Güler...")

    positions = ["Tümü"] + sorted(list(df["Position"].unique()))
    selected_position = st.sidebar.selectbox("Mevki Seçiniz", positions, index=0)

    leagues = ["Tümü"] + sorted(list(df["League"].unique()))
    selected_league = st.sidebar.selectbox("Lig Seçiniz", leagues, index=0)

    st.sidebar.subheader("💰 Bütçe & Yaş Filtresi")
    min_val, max_val = float(df["Market_Value_EUR_M"].min()), float(df["Market_Value_EUR_M"].max())
    budget_range = st.sidebar.slider("Piyasa Değeri (€M)", min_val, max_val, (min_val, max_val))

    min_age, max_age = int(df["Age"].min()), int(df["Age"].max())
    age_range = st.sidebar.slider("Yaş Aralığı", min_age, max_age, (min_age, max_age))

    # Add Custom Player Widget in Sidebar Expander
    with st.sidebar.expander("➕ Veri Tabanına Özel Oyuncu Ekle"):
        c_name = st.text_input("Oyuncu Adı Soyadı", placeholder="Örn: Farès Ghedjemis")
        c_pos = st.selectbox("Mevkisi", ["Kanat", "Santrafor", "Merkez Orta Saha", "Stoper", "Bek", "Kaleci"])
        c_team = st.text_input("Takımı", placeholder="Örn: Frosinone")
        c_league = st.text_input("Ligi", placeholder="Örn: Serie B İtalya")
        c_age = st.number_input("Yaş", min_value=15, max_value=45, value=22)
        c_val = st.number_input("Piyasa Değeri (€M)", min_value=0.1, max_value=150.0, value=2.5)
        c_mins = st.number_input("Dakika", min_value=100, max_value=4000, value=1500)

        c_xg = st.number_input("xG /90", min_value=0.0, max_value=2.0, value=0.35)
        c_xa = st.number_input("xA /90", min_value=0.0, max_value=2.0, value=0.28)
        c_xt = st.number_input("xT /90", min_value=0.0, max_value=2.0, value=0.32)
        c_pack = st.number_input("Pack Rate", min_value=0.0, max_value=60.0, value=28.0)

        if st.button("💾 Oyuncuyu Veri Tabanına Kaydet"):
            if c_name.strip():
                new_p = {
                    "Name": c_name.strip(), "Position": c_pos, "Team": c_team.strip() or "Serbest",
                    "League": c_league.strip() or "Diğer", "Age": int(c_age), "Market_Value_EUR_M": float(c_val),
                    "Minutes_Played": int(c_mins), "xG_per90": float(c_xg), "xA_per90": float(c_xa),
                    "Key_Passes_per90": round(float(c_xa) * 8.0, 1), "Dribbles_per90": 2.5,
                    "Defensive_Duels_per90": 2.0, "Pressures_per90": 14.0, "Progressive_Passes_per90": 4.5,
                    "Interceptions_per90": 0.8, "Tackles_per90": 1.2, "Pass_Accuracy_Pct": 80.0,
                    "Shot_Accuracy_Pct": 45.0, "xT_per90": float(c_xt), "Pack_Rate": float(c_pack),
                    "PADJ_Tackles_per90": 1.5, "High_Turnovers_per90": 1.2, "PPDA_Contribution": 65.0,
                    "PSxG_Net": 0.04, "xG_per_Shot": 0.12, "xG_Buildup_per90": 0.45
                }
                add_custom_player_to_dataset(new_p)

    df_filtered = df.copy()
    if search_query.strip():
        df_filtered = df_filtered[df_filtered["Name"].str.contains(search_query, case=False, na=False)]

    if selected_position != "Tümü":
        df_filtered = df_filtered[df_filtered["Position"] == selected_position]

    if selected_league != "Tümü":
        df_filtered = df_filtered[df_filtered["League"] == selected_league]

    df_filtered = df_filtered[
        (df_filtered["Market_Value_EUR_M"] >= budget_range[0]) &
        (df_filtered["Market_Value_EUR_M"] <= budget_range[1]) &
        (df_filtered["Age"] >= age_range[0]) &
        (df_filtered["Age"] <= age_range[1])
    ]

    tab0, tab1, tab2, tab3, tab4 = st.tabs([
        "👤 360° Oyuncu Profil Dosyası & 2 Sayfa Rapor",
        "🏆 Rol Bazlı Scouting (SciSports)",
        "🎯 Muadil Bulucu (Smarterscout)",
        "⚔️ Birebir Kıyaslama (Transfermarkt)",
        "📊 Metrik Analitiği & İnteraktif Dağılım"
    ])

    # ========================================================
    # TAB 0: DEDICATED 360° PLAYER PROFILE DOSSIER & 2-PAGE REPORT
    # ========================================================
    with tab0:
        st.subheader("👤 Oyuncu Profil Dosyası & 2 Sayfalık Opta Scout Raporu")
        st.caption("Veri tabanındaki tüm gerçek oyuncuların detaylı istatistik, taktiksel rol uyumu, radar, pizza grafikleri ve 2 sayfalık metinsel analiz raporlarını inceleyin.")

        all_player_names_sorted = sorted(df["Name"].tolist())
        selected_dossier_name = st.selectbox(
            "🔍 İncelemek İstediğiniz Oyuncuyu Seçiniz:",
            all_player_names_sorted,
            index=0
        )

        dossier_row = df[df["Name"] == selected_dossier_name].iloc[0]
        render_player_profile_dossier(dossier_row, df, engine, visualizer)

    # ========================================================
    # TAB 1: TACTICAL ROLE-BASED SCOUTING & TOPSIS (SciSports)
    # ========================================================
    with tab1:
        st.subheader("⚽ Taktiksel Rol Bazlı Scouting & TOPSIS Sıralaması")
        st.caption("Oyuncular, seçilen taktiksel role (Örn: *Fırsatçı Golcü*, *Ters Ayaklı Kanat*, *Orkestra Şefi*) göre ağırlıklandırılmış TOPSIS modeli ile puanlanır.")

        col_pos_sel, col_role_sel = st.columns(2)

        with col_pos_sel:
            target_pos = st.selectbox("Aranan Mevki:", ["Santrafor", "Kanat", "Merkez Orta Saha", "Stoper", "Bek", "Kaleci"], index=0)

        avail_roles = list(TACTICAL_ROLES.get(target_pos, {}).keys())
        with col_role_sel:
            selected_role = st.selectbox("Taktiksel Oyuncu Rolü:", avail_roles, index=0)

        role_weights = get_role_weights(target_pos, selected_role)

        st.info(f"📌 **Seçilen Rol:** `{selected_role}` — Metrik Ağırlıkları: " +
                ", ".join([f"{METRIC_LABELS.get(k, k)}: %{int(v*100)}" for k, v in role_weights.items()]))

        df_role_scored = engine.calculate_topsis_score(
            position_filter=target_pos,
            custom_weights=role_weights
        )

        df_role_scored_filtered = df_role_scored[df_role_scored["Player_ID"].isin(df_filtered["Player_ID"])].copy()

        if df_role_scored_filtered.empty:
            st.warning("Seçilen taktiksel rol ve filtrelere uygun oyuncu bulunamadı. Lütfen sol taraftaki sidebar filtrelerini genişletin.")
        else:
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Uygun Oyuncu", f"{len(df_role_scored_filtered)}")
            c2.metric("Lider TOPSIS Skoru", f"{df_role_scored_filtered['TOPSIS_Score'].max():.1f}")
            c3.metric("Ortalama Değer", f"€{df_role_scored_filtered['Market_Value_EUR_M'].mean():.1f}M")
            c4.metric("Ortalama Yaş", f"{df_role_scored_filtered['Age'].mean():.1f}")

            st.divider()

            show_cols = [
                "Name", "Position", "TOPSIS_Score", "Age", "Market_Value_EUR_M",
                "Team", "League", "xG_per90", "xA_per90", "Key_Passes_per90", "Dribbles_per90"
            ]
            st.dataframe(
                df_role_scored_filtered[show_cols].rename(columns={
                    "Name": "Oyuncu Adı",
                    "Position": "Mevki",
                    "TOPSIS_Score": "TOPSIS Skoru",
                    "Age": "Yaş",
                    "Market_Value_EUR_M": "Piyasa Değeri (€M)",
                    "Team": "Takım",
                    "League": "Lig",
                    "xG_per90": "xG /90",
                    "xA_per90": "xA /90",
                    "Key_Passes_per90": "Kilit Pas /90",
                    "Dribbles_per90": "Çalım /90"
                }),
                use_container_width=True,
                height=350
            )

            st.divider()
            st.subheader("🖼️ Wyscout Stil Pizza Chart & Oyuncu Kartı")

            p_list = df_role_scored_filtered["Name"].tolist()
            sel_player = st.selectbox("İncelenecek Oyuncuyu Seçiniz:", p_list, index=0)

            p_row = df_role_scored_filtered[df_role_scored_filtered["Name"] == sel_player].iloc[0]
            p_topsis = float(p_row["TOPSIS_Score"])

            col_piz, col_card = st.columns(2)

            with col_piz:
                fig_pizza = visualizer.create_pizza_chart(p_row, role_name=selected_role)
                st.pyplot(fig_pizza)
                bytes_pizza = visualizer.fig_to_bytes(fig_pizza)
                st.download_button(
                    label="📥 Wyscout Pizza Grafiğini İndir (PNG)",
                    data=bytes_pizza,
                    file_name=f"{p_row['Name'].replace(' ', '_')}_pizza.png",
                    mime="image/png"
                )

            with col_card:
                fig_card = visualizer.create_player_card(p_row, dss_score=p_topsis)
                st.pyplot(fig_card)
                bytes_card = visualizer.fig_to_bytes(fig_card)
                st.download_button(
                    label="📥 Oyuncu İstatistik Kartını İndir (PNG)",
                    data=bytes_card,
                    file_name=f"{p_row['Name'].replace(' ', '_')}_card.png",
                    mime="image/png"
                )

    # ========================================================
    # TAB 2: SMARTERSCOUT REPLACEMENT FINDER
    # ========================================================
    with tab2:
        st.subheader("🎯 Smarterscout Stil Muadil & Benzerlik Motoru (Cosine Similarity)")
        st.caption("Seçeceğiniz referans oyuncuyu baz alarak belirtilen bütçe ve yaş limitlerinde en benzer 5 muadili çıkarır.")

        col_sim1, col_sim2, col_sim3 = st.columns(3)

        with col_sim1:
            all_names = sorted(df["Name"].tolist())
            target_name = st.selectbox("Referans (Hedef) Oyuncu Seçiniz:", all_names, index=0)

        target_row_full = df[df["Name"] == target_name].iloc[0]
        target_val = float(target_row_full["Market_Value_EUR_M"])
        target_age = int(target_row_full["Age"])

        with col_sim2:
            max_b_sim = st.slider(
                "Maksimum Bütçe Limiti (€M):",
                min_value=1.0,
                max_value=120.0,
                value=float(min(120.0, max(5.0, target_val * 1.1))),
                step=1.0
            )

        with col_sim3:
            max_a_sim = st.slider(
                "Maksimum Yaş Limiti:",
                min_value=18,
                max_value=38,
                value=int(min(38, target_age + 2))
            )

        if st.button("🚀 En Benzer 5 Muadil Oyuncuyu Ara"):
            t_row, s_df = engine.find_similar_players(
                target_player_id=int(target_row_full["Player_ID"]),
                max_market_value=max_b_sim,
                max_age=max_a_sim,
                same_position_only=True,
                top_n=5
            )
            st.session_state["sim_target_row"] = t_row
            st.session_state["sim_results_df"] = s_df

        if "sim_results_df" in st.session_state and "sim_target_row" in st.session_state:
            target_row = st.session_state["sim_target_row"]
            sims_df = st.session_state["sim_results_df"]

            st.divider()
            st.markdown(
                f"### 📌 Referans Oyuncu: **{target_row['Name']}** "
                f"({target_row['Position']} | **{target_row['Team']}** | €{target_row['Market_Value_EUR_M']}M | Yaş: {target_row['Age']})"
            )

            if sims_df.empty:
                st.error("Belirtilen bütçe ve yaş kısıtlarına uygun muadil oyuncu bulunamadı. Lütfen bütçe/yaş sınırını esnetin.")
            else:
                st.subheader("✨ En Benzer 5 Muadil Oyuncu:")

                for idx, (_, sim_row) in sims_df.iterrows():
                    val_diff = float(sim_row["Market_Value_EUR_M"]) - target_val
                    val_diff_str = f"+€{val_diff:.1f}M" if val_diff >= 0 else f"-€{abs(val_diff):.1f}M"

                    st.markdown(f"""
                    <div class="player-card-box">
                        <div style="display:flex; justify-content:space-between; align-items:center;">
                            <h4 style="margin:0;">#{idx+1} {sim_row['Name']}</h4>
                            <span style="font-size:18px; font-weight:bold; color:#00f2fe;">Benzerlik: %{sim_row['Similarity_Pct']}</span>
                        </div>
                        <p style="margin-top:6px;">
                            <span class="badge-pos">{sim_row['Position']}</span> 
                            <span class="badge-league">{sim_row['League']}</span> 
                            <b>Takım:</b> {sim_row['Team']} | <b>Yaş:</b> {sim_row['Age']} | 
                            <b>Piyasa Değeri:</b> €{sim_row['Market_Value_EUR_M']}M <i>({val_diff_str})</i>
                        </p>
                    </div>
                    """, unsafe_allow_html=True)

                st.divider()
                st.subheader("⚔️ Kıyaslamalı Wyscout Radar & Pizza Önizleme")

                comp_name = st.selectbox("Radarda Kıyaslanacak Muadili Seçiniz:", sims_df["Name"].tolist(), index=0)
                comp_row = sims_df[sims_df["Name"] == comp_name].iloc[0]

                fig_comp = visualizer.create_radar_chart(
                    player_data=target_row,
                    compare_player_data=comp_row,
                    title_suffix="- KARŞILAŞTIRMA"
                )
                st.pyplot(fig_comp)

                bytes_comp = visualizer.fig_to_bytes(fig_comp)
                st.download_button(
                    label="📥 Karşılaştırmalı Radar Grafiğini İndir (PNG)",
                    data=bytes_comp,
                    file_name=f"karsilastirma_{target_row['Name']}_vs_{comp_row['Name']}.png",
                    mime="image/png"
                )

    # ========================================================
    # TAB 3: TRANSFERMARKT STYLE HEAD-TO-HEAD COMPARISON
    # ========================================================
    with tab3:
        st.subheader("⚔️ Transfermarkt Stil Birebir (Head-to-Head) Karşılaştırma")
        st.caption("Herhangi 2 oyuncuyu seçerek metriklerini ve performans farklarını yan yana kıyaslayın.")

        col_h1, col_h2 = st.columns(2)
        with col_h1:
            p1_select = st.selectbox("1. Oyuncuyu Seçiniz:", sorted(df["Name"].tolist()), index=0)
        with col_h2:
            p2_select = st.selectbox("2. Oyuncuyu Seçiniz:", sorted(df["Name"].tolist()), index=min(1, len(df)-1))

        row1 = df[df["Name"] == p1_select].iloc[0]
        row2 = df[df["Name"] == p2_select].iloc[0]

        st.divider()

        c_h1, c_h2 = st.columns(2)
        with c_h1:
            st.markdown(f"""
            <div class="player-card-box" style="border-left: 4px solid #00f2fe;">
                <h3 style="color:#00f2fe; margin:0;">{row1['Name']}</h3>
                <p><b>{row1['Position']}</b> • {row1['Team']} ({row1['League']})</p>
                <p><b>Yaş:</b> {row1['Age']} | <b>Değer:</b> €{row1['Market_Value_EUR_M']}M</p>
            </div>
            """, unsafe_allow_html=True)
        with c_h2:
            st.markdown(f"""
            <div class="player-card-box" style="border-left: 4px solid #ff007f;">
                <h3 style="color:#ff007f; margin:0;">{row2['Name']}</h3>
                <p><b>{row2['Position']}</b> • {row2['Team']} ({row2['League']})</p>
                <p><b>Yaş:</b> {row2['Age']} | <b>Değer:</b> €{row2['Market_Value_EUR_M']}M</p>
            </div>
            """, unsafe_allow_html=True)

        comp_metrics_data = []
        for m in ALL_METRICS:
            lbl = METRIC_LABELS.get(m, m)
            val1 = float(row1.get(m, 0.0))
            val2 = float(row2.get(m, 0.0))
            pct1 = float(row1.get(f"{m}_percentile", val1))
            pct2 = float(row2.get(f"{m}_percentile", val2))
            diff = val1 - val2

            comp_metrics_data.append({
                "Metrik": lbl,
                f"{row1['Name']} (Değer)": f"{val1:.2f}",
                f"{row1['Name']} (Percentile)": f"%{int(pct1)}",
                f"{row2['Name']} (Değer)": f"{val2:.2f}",
                f"{row2['Name']} (Percentile)": f"%{int(pct2)}",
                "Fark": f"{diff:+.2f}"
            })

        df_h2h = pd.DataFrame(comp_metrics_data)
        st.dataframe(df_h2h, use_container_width=True, height=400)

        st.divider()
        fig_h2h_radar = visualizer.create_radar_chart(row1, row2, title_suffix="- H2H BİREBİR KIYAS")
        st.pyplot(fig_h2h_radar)

    # ========================================================
    # TAB 4: INTERACTIVE PLOTLY SCATTER ANALYTICS
    # ========================================================
    with tab4:
        st.subheader("📊 Opta / Wyscout Stil İnteraktif Metrik Dağılımı")
        st.info("💡 **İnteraktif Özellik:** Fareyi (mouse) grafikteki herhangi bir noktanın üzerine getirdiğinizde oyuncunun detay bilgileri açılır.")

        col_sc1, col_sc2 = st.columns(2)
        with col_sc1:
            x_metric = st.selectbox("X Ekseni Metriği:", ALL_METRICS, index=0)
        with col_sc2:
            y_metric = st.selectbox("Y Ekseni Metriği:", ALL_METRICS, index=1)

        if not df_filtered.empty:
            x_lbl = METRIC_LABELS.get(x_metric, x_metric)
            y_lbl = METRIC_LABELS.get(y_metric, y_metric)

            fig_sc = px.scatter(
                df_filtered,
                x=x_metric,
                y=y_metric,
                color="Position",
                hover_name="Name",
                hover_data={
                    "Team": True,
                    "League": True,
                    "Position": True,
                    "Age": True,
                    "Market_Value_EUR_M": ":.1f",
                    x_metric: ":.2f",
                    y_metric: ":.2f"
                },
                labels={
                    x_metric: x_lbl,
                    y_metric: y_lbl,
                    "Position": "Mevki",
                    "Team": "Takım",
                    "League": "Lig",
                    "Age": "Yaş",
                    "Market_Value_EUR_M": "Piyasa Değeri (€M)"
                },
                title=f"<b>{x_lbl} vs {y_lbl} Dağılım Grafiği</b>",
                template="plotly_dark"
            )

            fig_sc.update_traces(
                marker=dict(size=11, opacity=0.85, line=dict(width=1, color="#30363d")),
                hovertemplate="<b>%{hovertext}</b><br><br>" +
                              "<b>Takım:</b> %{customdata[0]} (%{customdata[1]})<br>" +
                              "<b>Mevki:</b> %{customdata[2]} | <b>Yaş:</b> %{customdata[3]}<br>" +
                              "<b>Piyasa Değeri:</b> €%{customdata[4]:.1f}M<br><br>" +
                              f"<b>{x_lbl}:</b> %{{x:.2f}}<br>" +
                              f"<b>{y_lbl}:</b> %{{y:.2f}}<extra></extra>"
            )

            fig_sc.update_layout(
                paper_bgcolor="#0e1117",
                plot_bgcolor="#161b22",
                font=dict(color="#f0f6fc", size=12),
                height=650,
                legend=dict(
                    bgcolor="#161b22",
                    bordercolor="#30363d",
                    borderwidth=1,
                    font=dict(size=11)
                ),
                xaxis=dict(gridcolor="#30363d", zerolinecolor="#30363d"),
                yaxis=dict(gridcolor="#30363d", zerolinecolor="#30363d")
            )

            st.plotly_chart(fig_sc, use_container_width=True)


if __name__ == "__main__":
    main()
