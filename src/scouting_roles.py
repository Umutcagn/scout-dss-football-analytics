"""
Professional Scouting Roles & Metric Weights (Inspired by SciSports, Wyscout, Smarterscout).
Defines tactical roles per position and their metric weight distributions.
"""

from typing import Dict, List

# Metric categories for Wyscout / StatsBomb style pizza charts
METRIC_CLUSTERS = {
    "Attacking": ["xG_per90", "Shot_Accuracy_Pct"],
    "Creation": ["xA_per90", "Key_Passes_per90", "Progressive_Passes_per90", "Pass_Accuracy_Pct"],
    "Dribbling": ["Dribbles_per90", "Pressures_per90"],
    "Defending": ["Defensive_Duels_per90", "Interceptions_per90", "Tackles_per90"]
}

# Tactical Roles per main position
TACTICAL_ROLES: Dict[str, Dict[str, Dict[str, float]]] = {
    "Kaleci": {
        "Oyun Kurucu Kaleci (Sweeper-Keeper)": {
            "Pass_Accuracy_Pct": 0.40, "Progressive_Passes_per90": 0.30,
            "Interceptions_per90": 0.20, "Key_Passes_per90": 0.10
        },
        "Klasik Çizgi Kalecisi (Shot-Stopper)": {
            "Pass_Accuracy_Pct": 0.50, "Interceptions_per90": 0.30,
            "Progressive_Passes_per90": 0.20
        }
    },
    "Santrafor": {
        "Komple Santrafor (Complete Forward)": {
            "xG_per90": 0.35, "Shot_Accuracy_Pct": 0.20, "xA_per90": 0.15,
            "Dribbles_per90": 0.15, "Pressures_per90": 0.15
        },
        "Fırsatçı Golcü (Poacher)": {
            "xG_per90": 0.55, "Shot_Accuracy_Pct": 0.30, "xA_per90": 0.05,
            "Dribbles_per90": 0.05, "Pressures_per90": 0.05
        },
        "Sahte 9 / Yaratıcı Golcü (False 9)": {
            "xA_per90": 0.30, "Key_Passes_per90": 0.25, "xG_per90": 0.25,
            "Progressive_Passes_per90": 0.10, "Dribbles_per90": 0.10
        },
        "Presçi Santrafor (Pressing Forward)": {
            "Pressures_per90": 0.35, "xG_per90": 0.25, "Defensive_Duels_per90": 0.20,
            "Tackles_per90": 0.10, "Shot_Accuracy_Pct": 0.10
        }
    },
    "Kanat": {
        "Ters Ayaklı Kanat (Inverted Winger)": {
            "Dribbles_per90": 0.30, "xG_per90": 0.25, "Key_Passes_per90": 0.20,
            "Shot_Accuracy_Pct": 0.15, "Progressive_Passes_per90": 0.10
        },
        "Klasik Çizgi Kanatı (Traditional Winger)": {
            "Key_Passes_per90": 0.35, "xA_per90": 0.25, "Dribbles_per90": 0.25,
            "Progressive_Passes_per90": 0.10, "Pressures_per90": 0.05
        },
        "Kanat Oyun Kurucu (Wide Playmaker)": {
            "Key_Passes_per90": 0.30, "Progressive_Passes_per90": 0.25, "xA_per90": 0.25,
            "Pass_Accuracy_Pct": 0.15, "xG_per90": 0.05
        }
    },
    "Merkez Orta Saha": {
        "Orkestra Şefi (Deep-Lying Playmaker)": {
            "Progressive_Passes_per90": 0.35, "Pass_Accuracy_Pct": 0.30,
            "Key_Passes_per90": 0.20, "Interceptions_per90": 0.10, "xA_per90": 0.05
        },
        "İki Yönlü Orta Saha (Box-to-Box)": {
            "Pressures_per90": 0.25, "Progressive_Passes_per90": 0.25,
            "Defensive_Duels_per90": 0.20, "Key_Passes_per90": 0.15, "xG_per90": 0.15
        },
        "Savaşçı / Çapa (Ball-Winning Midfielder)": {
            "Defensive_Duels_per90": 0.35, "Tackles_per90": 0.25,
            "Interceptions_per90": 0.20, "Pressures_per90": 0.15, "Pass_Accuracy_Pct": 0.05
        },
        "10 Numara / Yaratıcı Orta Saha (Advanced Playmaker)": {
            "Key_Passes_per90": 0.35, "xA_per90": 0.30, "Dribbles_per90": 0.15,
            "xG_per90": 0.10, "Pass_Accuracy_Pct": 0.10
        }
    },
    "Stoper": {
        "Pasör Stoper (Ball-Playing Defender)": {
            "Pass_Accuracy_Pct": 0.35, "Progressive_Passes_per90": 0.25,
            "Interceptions_per90": 0.20, "Defensive_Duels_per90": 0.15, "Tackles_per90": 0.05
        },
        "Kesici Stoper (Stopper / Marker)": {
            "Defensive_Duels_per90": 0.40, "Interceptions_per90": 0.30,
            "Tackles_per90": 0.20, "Pressures_per90": 0.05, "Pass_Accuracy_Pct": 0.05
        }
    },
    "Bek": {
        "Hücumcu Bek (Attacking Wing-Back)": {
            "Key_Passes_per90": 0.30, "xA_per90": 0.25, "Dribbles_per90": 0.20,
            "Progressive_Passes_per90": 0.15, "Defensive_Duels_per90": 0.10
        },
        "İç Bek (Inverted Full-Back)": {
            "Progressive_Passes_per90": 0.35, "Pass_Accuracy_Pct": 0.25,
            "Interceptions_per90": 0.20, "Defensive_Duels_per90": 0.15, "Tackles_per90": 0.05
        },
        "Savunmacı Bek (Defensive Full-Back)": {
            "Defensive_Duels_per90": 0.35, "Tackles_per90": 0.25,
            "Interceptions_per90": 0.25, "Pressures_per90": 0.10, "Pass_Accuracy_Pct": 0.05
        }
    }
}


def get_role_weights(position: str, role_name: str) -> Dict[str, float]:
    """Returns metric weights for a given tactical role."""
    roles = TACTICAL_ROLES.get(position, {})
    if role_name in roles:
        return roles[role_name]
    if roles:
        return next(iter(roles.values()))
    return {"xG_per90": 0.2, "xA_per90": 0.2, "Key_Passes_per90": 0.2, "Defensive_Duels_per90": 0.2, "Pass_Accuracy_Pct": 0.2}
