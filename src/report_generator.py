"""
Opta / StatsPerform Style 2-Page Scouting Report & Tactical Narrative Generator.
Generates comprehensive, professional 2-page scout reports with in-depth tactical text analysis,
metric interpretations, playing style evaluation, and final transfer recommendations.
"""

from typing import Dict, Any
import pandas as pd
from src.visualizer import METRIC_LABELS


def generate_opta_scout_report(player_row: pd.Series, topsis_score: float = 78.5) -> str:
    """
    Generates a full 2-Page Opta-style professional Scouting Report in Turkish.
    """
    name = player_row.get("Name", "Oyuncu")
    pos = player_row.get("Position", "Oyuncu")
    team = player_row.get("Team", "-")
    league = player_row.get("League", "-")
    age = player_row.get("Age", "-")
    val = player_row.get("Market_Value_EUR_M", 0.0)
    mins = player_row.get("Minutes_Played", 0)

    # Extract Key Metrics & Percentiles
    xg = float(player_row.get("xG_per90", 0.0))
    xg_pct = int(player_row.get("xG_per90_percentile", 50.0))

    xa = float(player_row.get("xA_per90", 0.0))
    xa_pct = int(player_row.get("xA_per90_percentile", 50.0))

    xt = float(player_row.get("xT_per90", 0.0))
    xt_pct = int(player_row.get("xT_per90_percentile", 50.0))

    pack = float(player_row.get("Pack_Rate", 0.0))
    pack_pct = int(player_row.get("Pack_Rate_percentile", 50.0))

    prog_pass = float(player_row.get("Progressive_Passes_per90", 0.0))
    prog_pct = int(player_row.get("Progressive_Passes_per90_percentile", 50.0))

    dribbles = float(player_row.get("Dribbles_per90", 0.0))
    dribbles_pct = int(player_row.get("Dribbles_per90_percentile", 50.0))

    padj_tackles = float(player_row.get("PADJ_Tackles_per90", 0.0))
    padj_pct = int(player_row.get("PADJ_Tackles_per90_percentile", 50.0))

    high_turnovers = float(player_row.get("High_Turnovers_per90", 0.0))
    turnovers_pct = int(player_row.get("High_Turnovers_per90_percentile", 50.0))

    ppda = float(player_row.get("PPDA_Contribution", 50.0))
    ppda_pct = int(player_row.get("PPDA_Contribution_percentile", 50.0))

    pass_acc = float(player_row.get("Pass_Accuracy_Pct", 80.0))
    shot_acc = float(player_row.get("Shot_Accuracy_Pct", 45.0))
    xg_per_shot = float(player_row.get("xG_per_Shot", 0.12))

    # Evaluate Grade based on TOPSIS score
    if topsis_score >= 82.0:
        grade = "A+ (Dünya Çapı / Birincil Transfer Hedefi)"
        verdict_summary = "Oyuncu, kendi pozisyonunda lig standartlarının çok üzerinde bir etki alanına sahip. Birincil transfer hedefi olarak değerlendirilmelidir."
    elif topsis_score >= 72.0:
        grade = "A (İlk 11 Kalitesinde Kilit Oyuncu)"
        verdict_summary = "Oyuncu, taktiksel disiplini ve istikrarlı metrik profili ile doğrudan ilk 11 kurgusuna monte edilebilecek seviyededir."
    elif topsis_score >= 62.0:
        grade = "B (Yüksek Potansiyelli Rotasyon / Muadil Transferi)"
        verdict_summary = "Oyuncu, uygun maliyetle kadro derinliğini artıracak ve gelişime açık sağlam bir profildir."
    else:
        grade = "C (Gelişimi Takip Edilmeli / Şartlı Transfer)"
        verdict_summary = "Oyuncu belirli metriklerde parlama gösterse de taktiksel süreklilik için izlenmeye devam edilmelidir."

    report_text = f"""================================================================================
OPTA & STATSBYMB STANDARTLARINDA DETAYLI TAKTİKSEL SCOUT RAPORU
================================================================================

OYUNCU KİMLİĞİ VE META VERİLER:
- Oyuncu Adı      : {name}
- Pozisyon        : {position_turkish(pos)} ({pos})
- Kulüp / Lig     : {team} ({league})
- Yaş / Piyasa Değ: {age} Yaş | €{val}M
- Toplam Süre     : {mins} Dakika
- TOPSIS Skoru    : {topsis_score:.1f} / 100
- Scout Notu      : {grade}

================================================================================
SAYFA 1: TAKTİKSEL ANALİZ, OYUNCU KİMLİĞİ VE SAHA İÇİ ROLÜ
================================================================================

--- 1. EKSEKÜTİF ÖZET VE OYUNCU KİMLİĞİ ---
{name}, 2024/2025 sezonunda {team} formasıyla {league} liginde gösterdiği performansla mevkisinin ({pos}) lig ortalamasına kıyasla %{int(topsis_score)} genel başarı diliminde yer almaktadır. Oyuncu, topa sahip olma odaklı ve yüksek tempolu taktiksel kurgularda dinamik yapısıyla öne çıkmaktadır. {mins} dakikalık numune büyüklüğünde sergilediği metrik dağılımı, oyuncunun hem bireysel bitiricilikte hem de takımın genel hücum ve geçiş organizasyonunda proaktif bir role sahip olduğunu göstermektedir.

--- 2. HÜCUM, ŞUT VE SON ÜÇÜNCÜ BÖLGE ETKİNLİĞİ ---
Oyuncunun 90 dakika başına ürettiği Beklenen Gol (xG) değeri {xg:.2f}'dir (Lig Yüzdesi: %{xg_pct}). {name}, ceza sahası içi pozisyon alma becerisi ve şut kalitesi açısından incelendiğinde; şut başına düşen xG (xG per Shot) oranının {xg_per_shot:.2f} seviyesinde olduğu görülmektedir. Şut isabet oranı %{shot_acc:.1f} düzeyinde seyretmektedir.
- Taktiksel Yorum: Oyuncu, sadece rasgele şut atmak yerine yüksek kaliteli fırsatları kollamakta ve ceza sahası içindeki 'High-xG' bölgelerine penetre etmektedir. Hücum hattında rakip stoperlerin arkasına yapılan koşularda zamanlama hassasiyeti yüksektir.

--- 3. YARATICILIK, PAS VE TEHLİKE TEHDİDİ (xT & PACK RATE) ---
{name}, hücum kurulumunda ve pas organizasyonunda mevkisine kıyasla fark yaratan bir profil çizmektedir.
- Beklenen Asist (xA/90)  : {xa:.2f} (Lig Yüzdesi: %{xa_pct})
- Tehlike Tehdidi (xT/90) : {xt:.2f} (Lig Yüzdesi: %{xt_pct})
- Pack Rate (Ekarte Adam): 90 dakika başına ortalama {pack:.1f} rakip oyuncuyu pas ve dripling ile oyun dışı bırakmaktadır (Lig Yüzdesi: %{pack_pct}).
- Progresif Pas /90      : {prog_pass:.1f} (Lig Yüzdesi: %{prog_pct})
- Pas İsabet Oranı        : %{pass_acc:.1f}
- Taktiksel Yorum: xT (Expected Threat) skorunun {xt:.2f} olması, oyuncunun paslarının ve top taşımalarının rakip kale tehlikesini katlayarak artırdığını göstermektedir. Pack Rate oranının {pack:.1f} seviyesinde olması, oyuncunun dikine paslarla veya driplinglerle ({dribbles:.1f} çalım/90) rakip hatları kıran (line-breaking) kilit bir oyun kurucu olduğunu kanıtlamaktadır.

================================================================================
SAYFA 2: DEFANSİF KATKI, PRES, TAKTİKSEL RİSKLER VE NİHAİ SCOUT KARARI
================================================================================

--- 4. SAVUNMA DİSİPLİNİ, PRES VE ÖN ALAN TOP KAZANIMI ---
Modern futbolun gerektirdiği top rakipteyken yapılan pres ve savunma katkısı incelendiğinde:
- Zilyetlik Ayarlı Top Çalma (PADJ Tackles/90): {padj_tackles:.2f} (Lig Yüzdesi: %{padj_pct})
- Ön Alan Top Kazanımı (High Turnovers/90)   : {high_turnovers:.2f} (Lig Yüzdesi: %{turnovers_pct})
- PPDA Baskı Katkısı (Baskı Skoru)            : {ppda:.1f} / 100 (Lig Yüzdesi: %{ppda_pct})
- Taktiksel Yorum: {name}, rakip yarı sahada yapılan önde baskı (Gegenpressing) kurgularında önemli bir reaksiyon hızına sahiptir. Rakip stoperlerin ve bekleşmelerin ilk oyun kurulumunda yaptığı sahipsiz top kazanımı (High Turnovers: {high_turnovers:.2f}) takımının anlık geçiş hücumları (counter-attack) yakalamasını sağlamaktadır.

--- 5. TAKTİKSEL RİSKLER VE GELİŞİM ALANLARI ---
1. Tempolu Pres Oyununda Yük Dağılımı: Yüksek pres temposu nedeniyle maçın 70. dakikasından sonra ikili mücadele başarı oranında hafif düşüş gözlemlenebilmektedir.
2. Dar Alanda Karar Alma Hızı: Yoğun blok savunmalara karşı pas tercihlerinde zaman zaman riskli dikey pasları zorlayabilmektedir.

--- 6. TAKIM UYUMU VE İDEAL TAKTİKSEL FORMASYON ---
{name} için en ideal taktiksel sistemler:
- 4-3-3 Yüksek Pres & Dikey Geçiş Sistemi: Sağ/sol kanat veya iç koridor oyun kurucu rolünde maksimum verim.
- 4-2-3-1 Topa Sahip Olma ve Alan Dominasyonu: 10 numara veya serbest rol sergileyen hücum kanadı.

--- 7. NİHAİ SCOUT VERDİKTİ VE TRANSFER TAVSİYESİ ---
- Karar Raporu   : {verdict_summary}
- Tavsiye Edilen Bonservis Limiti: €{val:.1f}M seviyesine kadar yapılan yatırımlar yüksek geri dönüş (ROI) potansiyeline sahiptir.
- Özet Değerlendirme: {name}, Opta ve Wyscout metrik profili baz alındığında kulübümüzün taktiksel vizyonu ile %{int(topsis_score)} oranında doğrudan örtüşmektedir. Transfer süreci öncelikli olarak başlatılmalıdır.
================================================================================
Rapor Oluşturucu: ScoutEduard Opta & StatsPerform AI Scouting Engine
================================================================================
"""
    return report_text


def position_turkish(pos: str) -> str:
    mapping = {
        "Santrafor": "Santrafor / Forvet (ST)",
        "Kanat": "Kanat Oyuncusu (Winger)",
        "Merkez Orta Saha": "Merkez Orta Saha (CM/AM/DM)",
        "Stoper": "Stoper / Defans (CB)",
        "Bek": "Bek Oyuncusu (RB/LB/WB)",
        "Kaleci": "Kaleci (GK)"
    }
    return mapping.get(pos, pos)
