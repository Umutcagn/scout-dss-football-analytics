import io
from typing import List, Dict, Optional, Tuple, Union
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Global Dark Theme Styling
DARK_BG = "#0e1117"
CARD_BG = "#161b22"
ACCENT_CYAN = "#00f2fe"
ACCENT_MAGENTA = "#ff007f"
ACCENT_GREEN = "#00ff87"
ACCENT_GOLD = "#ffd700"
ACCENT_RED = "#ff4b4b"
TEXT_COLOR = "#f0f6fc"
TEXT_MUTED = "#8b949e"
GRID_COLOR = "#30363d"

METRIC_LABELS = {
    "xG_per90": "xG /90",
    "xA_per90": "xA /90",
    "Key_Passes_per90": "Kilit Pas /90",
    "Dribbles_per90": "Çalım /90 (simüle)",
    "Defensive_Duels_per90": "Def. İkili Müc. /90 (simüle)",
    "Pressures_per90": "Baskı /90 (simüle)",
    "Progressive_Passes_per90": "Prog. Pas /90 (simüle)",
    "Interceptions_per90": "Pas Arası /90 (simüle)",
    "Tackles_per90": "Top Çalma /90 (simüle)",
    "Pass_Accuracy_Pct": "Pas İsabeti % (simüle)",
    "Shot_Accuracy_Pct": "Şut İsabeti % (simüle)",
    # Advanced Industry Metrics
    "xT_per90": "xT (Tehlike Tehdidi) /90 (simüle)",
    "Pack_Rate": "Pack Rate (Ekarte Adam) (simüle)",
    "PADJ_Tackles_per90": "PADJ Top Çalma /90 (simüle)",
    "High_Turnovers_per90": "Ön Alan Top Kazanımı /90 (simüle)",
    "PPDA_Contribution": "PPDA Baskı Katkısı (simüle)",
    "PSxG_Net": "PSxG Net (+/-) (simüle)",
    "xG_per_Shot": "Şut Başı xG (Kalite)",
    "xG_Buildup_per90": "xG Oyun Kurulumu /90",
    # Fixed per-position defaults (no live Sofascore data)
    "Sofascore_Attacking": "Hücum Puanı (mevki sabiti)",
    "Sofascore_Creativity": "Yaratıcılık (mevki sabiti)",
    "Sofascore_Technical": "Teknik Puanı (mevki sabiti)",
    "Sofascore_Defending": "Defans Puanı (mevki sabiti)",
    "Sofascore_Tactical": "Taktik Puanı (mevki sabiti)"
}

CLUSTER_COLORS = {
    "Attacking": ACCENT_RED,
    "Creation": ACCENT_CYAN,
    "Dribbling": ACCENT_GOLD,
    "Defending": ACCENT_GREEN,
    "Goalkeeping": ACCENT_GREEN,
    "Sofascore": ACCENT_CYAN
}


class ScoutVisualizer:
    """
    Industry-Standard Visualization Engine for ScoutEduard.
    Renders Radar Charts, Wyscout-style Pizza Charts, and Player Stats Cards.
    """

    def __init__(self) -> None:
        plt.style.use("dark_background")

    def create_radar_chart(
        self,
        player_data: pd.Series,
        compare_player_data: Optional[pd.Series] = None,
        metrics: Optional[List[str]] = None,
        title_suffix: str = ""
    ) -> plt.Figure:
        pos = player_data.get("Position", "")

        if metrics is None:
            if pos == "Kaleci":
                metrics = [
                    "PSxG_Net", "Pass_Accuracy_Pct", "Progressive_Passes_per90",
                    "Interceptions_per90", "Pack_Rate", "Sofascore_Defending"
                ]
            else:
                metrics = [
                    "xG_per90", "xA_per90", "xT_per90", "Pack_Rate",
                    "Sofascore_Attacking", "Sofascore_Creativity",
                    "Progressive_Passes_per90", "PADJ_Tackles_per90"
                ]

        labels = [METRIC_LABELS.get(m, m) for m in metrics]
        num_vars = len(metrics)

        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
        angles += angles[:1]

        values1 = []
        for m in metrics:
            pct_col = f"{m}_percentile" if f"{m}_percentile" in player_data else m
            values1.append(player_data.get(pct_col, 50.0))
        values1 += values1[:1]

        fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True), facecolor=DARK_BG)
        ax.set_facecolor(DARK_BG)

        plt.xticks(angles[:-1], labels, color=TEXT_COLOR, size=10, fontweight="bold")
        ax.tick_params(axis="x", pad=15)

        ax.set_rlabel_position(0)
        plt.yticks([25, 50, 75, 100], ["25", "50", "75", "100"], color=TEXT_MUTED, size=9)
        plt.ylim(0, 100)

        ax.spines["polar"].set_color(GRID_COLOR)
        ax.grid(color=GRID_COLOR, linestyle="--", linewidth=1)

        p1_name = player_data.get("Name", "Oyuncu 1")
        p1_team = player_data.get("Team", "")
        ax.plot(angles, values1, color=ACCENT_CYAN, linewidth=2.5, linestyle="solid", label=f"{p1_name} ({p1_team})")
        ax.fill(angles, values1, color=ACCENT_CYAN, alpha=0.3)

        if compare_player_data is not None:
            values2 = []
            for m in metrics:
                pct_col = f"{m}_percentile" if f"{m}_percentile" in compare_player_data else m
                values2.append(compare_player_data.get(pct_col, 50.0))
            values2 += values2[:1]

            p2_name = compare_player_data.get("Name", "Oyuncu 2")
            p2_team = compare_player_data.get("Team", "")
            ax.plot(angles, values2, color=ACCENT_MAGENTA, linewidth=2.5, linestyle="solid", label=f"{p2_name} ({p2_team})")
            ax.fill(angles, values2, color=ACCENT_MAGENTA, alpha=0.25)

        title = f"SCOUT EDUARD - ADVANCED METRİK RADARI {title_suffix}"
        ax.set_title(title, size=13, color=TEXT_COLOR, weight="bold", pad=25)

        legend = ax.legend(loc="upper right", bbox_to_anchor=(1.25, 1.1), facecolor=CARD_BG, edgecolor=GRID_COLOR)
        for text in legend.get_texts():
            text.set_color(TEXT_COLOR)

        plt.tight_layout()
        return fig

    def create_pizza_chart(
        self,
        player_data: pd.Series,
        role_name: str = "Komple Profil"
    ) -> plt.Figure:
        pos = player_data.get("Position", "")

        if pos == "Kaleci":
            metrics = [
                ("PSxG_Net", "Goalkeeping"), ("Pass_Accuracy_Pct", "Creation"),
                ("Progressive_Passes_per90", "Creation"), ("Pack_Rate", "Creation"),
                ("Sofascore_Defending", "Defending"), ("PPDA_Contribution", "Defending")
            ]
        else:
            metrics = [
                ("xG_per90", "Attacking"), ("Sofascore_Attacking", "Attacking"),
                ("xA_per90", "Creation"), ("xT_per90", "Creation"),
                ("Sofascore_Creativity", "Creation"), ("Pack_Rate", "Creation"),
                ("Dribbles_per90", "Dribbling"), ("Sofascore_Technical", "Dribbling"),
                ("PADJ_Tackles_per90", "Defending"), ("Sofascore_Defending", "Defending"),
                ("Interceptions_per90", "Defending")
            ]

        num_vars = len(metrics)
        angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False)
        width = 2 * np.pi / num_vars

        fig, ax = plt.subplots(figsize=(9, 9), subplot_kw=dict(polar=True), facecolor=DARK_BG)
        ax.set_facecolor(DARK_BG)

        for i, (m, cluster) in enumerate(metrics):
            pct_col = f"{m}_percentile" if f"{m}_percentile" in player_data else m
            val = float(player_data.get(pct_col, 50.0))
            color = CLUSTER_COLORS.get(cluster, ACCENT_CYAN)

            ax.bar(angles[i], val, width=width, color=color, alpha=0.7, edgecolor=DARK_BG, linewidth=1.5)
            angle_rad = angles[i]
            r_pos = min(95.0, max(15.0, val + 6.0))
            ax.text(angle_rad, r_pos, f"{int(val)}", color=TEXT_COLOR, fontsize=9, fontweight="bold", ha="center", va="center")

        labels = [METRIC_LABELS.get(m[0], m[0]) for m in metrics]
        plt.xticks(angles, labels, color=TEXT_COLOR, size=9, fontweight="bold")
        ax.tick_params(axis="x", pad=18)

        ax.set_rlabel_position(0)
        plt.yticks([25, 50, 75, 100], ["", "", "", ""], color=TEXT_MUTED)
        plt.ylim(0, 105)

        name = player_data.get("Name", "Oyuncu")
        team = player_data.get("Team", "")

        title = f"{name} ({team} - {pos})\n[Wyscout Stil Yüzdelik Pizza Chart • {role_name}]"
        ax.set_title(title, size=13, color=TEXT_COLOR, weight="bold", pad=30)

        plt.tight_layout()
        return fig

    def create_player_card(
        self,
        player_data: pd.Series,
        dss_score: Optional[float] = None,
        metrics: Optional[List[str]] = None
    ) -> plt.Figure:
        pos = player_data.get("Position", "")

        if metrics is None:
            if pos == "Kaleci":
                metrics = [
                    "PSxG_Net", "Pass_Accuracy_Pct", "Progressive_Passes_per90",
                    "Interceptions_per90", "Sofascore_Defending", "Sofascore_Tactical"
                ]
            else:
                metrics = [
                    "xG_per90", "xA_per90", "xT_per90", "Pack_Rate",
                    "Sofascore_Attacking", "Sofascore_Creativity",
                    "Sofascore_Technical", "PADJ_Tackles_per90"
                ]

        fig, ax = plt.subplots(figsize=(8, 10), facecolor=DARK_BG)
        ax.set_facecolor(CARD_BG)
        ax.axis("off")

        name = player_data.get("Name", "Bilinmeyen Oyuncu")
        position = player_data.get("Position", "-")
        team = player_data.get("Team", "-")
        league = player_data.get("League", "-")
        age = player_data.get("Age", "-")
        val = player_data.get("Market_Value_EUR_M", "-")

        ax.text(0.05, 0.92, name, color=TEXT_COLOR, fontsize=20, fontweight="bold", transform=ax.transAxes)
        subtitle = f"{position}  •  {team} ({league})  •  Yaş: {age}  •  Değer: €{val}M"
        ax.text(0.05, 0.88, subtitle, color=TEXT_MUTED, fontsize=11, transform=ax.transAxes)

        if dss_score is not None:
            score_box = dict(boxstyle="round,pad=0.5", facecolor=ACCENT_CYAN, alpha=0.9)
            ax.text(0.85, 0.90, f"{dss_score:.1f}", color="#000000", fontsize=18, fontweight="bold",
                    ha="center", bbox=score_box, transform=ax.transAxes)
            ax.text(0.85, 0.85, "DSS SKORU", color=TEXT_MUTED, fontsize=8, fontweight="bold",
                    ha="center", transform=ax.transAxes)

        ax.axhline(0.83, color=GRID_COLOR, linewidth=1.5, xmin=0.05, xmax=0.95)

        start_y = 0.75
        step_y = 0.075

        ax.text(0.05, start_y + 0.03, "ADVANCED & SOFASCORE METRİKLERİ (PERCENTILE YÜZDELİK)",
                color=ACCENT_GREEN, fontsize=10, fontweight="bold", transform=ax.transAxes)

        for i, m in enumerate(metrics):
            y_pos = start_y - (i * step_y)
            label = METRIC_LABELS.get(m, m)
            pct_col = f"{m}_percentile" if f"{m}_percentile" in player_data else m
            val_pct = float(player_data.get(pct_col, 50.0))
            raw_val = float(player_data.get(m, 0.0))

            ax.text(0.05, y_pos, label, color=TEXT_COLOR, fontsize=9.5, transform=ax.transAxes, va="center")

            bar_bg = plt.Rectangle((0.45, y_pos - 0.015), 0.35, 0.025, facecolor="#21262d", transform=ax.transAxes)
            ax.add_patch(bar_bg)

            fill_width = (val_pct / 100.0) * 0.35
            bar_fill = plt.Rectangle((0.45, y_pos - 0.015), fill_width, 0.025, facecolor=ACCENT_CYAN, transform=ax.transAxes)
            ax.add_patch(bar_fill)

            val_str = f"{raw_val:.2f}" if not (m.endswith("_Pct") or m.startswith("Sofascore_")) else f"{int(raw_val)}"
            ax.text(0.82, y_pos, f"{val_str} ({int(val_pct)}%)", color=TEXT_COLOR, fontsize=9,
                    fontweight="bold", transform=ax.transAxes, va="center")

        ax.axhline(0.08, color=GRID_COLOR, linewidth=1.5, xmin=0.05, xmax=0.95)
        ax.text(0.5, 0.04, "SCOUT EDUARD ADVANCED & SOFASCORE METRICS ENGINE",
                color=TEXT_MUTED, fontsize=8, ha="center", transform=ax.transAxes)

        plt.tight_layout()
        return fig

    @staticmethod
    def fig_to_bytes(fig: plt.Figure, format_ext: str = "png") -> bytes:
        buf = io.BytesIO()
        fig.savefig(buf, format=format_ext, bbox_inches="tight", dpi=300, facecolor=fig.get_facecolor())
        buf.seek(0)
        return buf.getvalue()
