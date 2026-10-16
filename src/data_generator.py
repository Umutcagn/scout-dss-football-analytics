import os
import random
from typing import Dict, List, Tuple
import numpy as np
import pandas as pd

# Seed for reproducibility
np.random.seed(42)
random.seed(42)

FIRST_NAMES = [
    "Arda", "Kerem", "Ferdi", "Orkun", "Hakan", "Semih", "Barış", "Yunus", "Kenan", "Cenk",
    "Gabriel", "Lucas", "Mateo", "Julian", "Alexander", "Victor", "Enzo", "Federico", "Florian", "Sandro",
    "Dominik", "Warmond", "Bruno", "Bernardo", "Gonçalo", "Kylian", "Eduardo", "Aurélien", "Dayot", "William",
    "Rasmus", "Marcus", "Bukayo", "Declan", "Cole", "Jude", "Phil", "Kobbie", "Harvey", "Oliver"
]

LAST_NAMES = [
    "Güler", "Aktürkoğlu", "Kadıoğlu", "Kökçü", "Çalhanoğlu", "Kılıçsoy", "Alper Yılmaz", "Akgün", "Yıldız", "Tosun",
    "Silva", "Torreira", "Kovačić", "Alvarez", "Isak", "Gyökeres", "Fernandez", "Valverde", "Wirtz", "Tonali",
    "Szoboszlai", "Muani", "Guimaraes", "Silva", "Ramos", "Mbappé", "Camavinga", "Tchouaméni", "Upamecano", "Saliba",
    "Højlund", "Rashford", "Saka", "Rice", "Palmer", "Bellingham", "Foden", "Mainoo", "Elliott", "Watkins"
]

TEAMS_BY_LEAGUE = {
    "Süper Lig": ["Galatasaray", "Fenerbahçe", "Beşiktaş", "Trabzonspor", "Başakşehir"],
    "Premier League": ["Arsenal", "Manchester City", "Liverpool", "Aston Villa", "Tottenham Hotspur"],
    "La Liga": ["Real Madrid", "Barcelona", "Atletico Madrid", "Real Sociedad", "Girona"],
    "Serie A": ["Inter", "AC Milan", "Juventus", "Atalanta", "Napoli"],
    "Bundesliga": ["Bayer Leverkusen", "Bayern Munich", "RB Leipzig", "Borussia Dortmund", "VfB Stuttgart"],
}

POSITIONS = ["Santrafor", "Kanat", "Merkez Orta Saha", "Stoper", "Bek"]

POSITION_METRIC_PROFILES: Dict[str, Dict[str, Tuple[float, float]]] = {
    "Santrafor": {
        "xG_per90": (0.35, 0.85),
        "xA_per90": (0.08, 0.30),
        "Key_Passes_per90": (0.6, 2.0),
        "Dribbles_per90": (0.8, 2.8),
        "Defensive_Duels_per90": (0.8, 2.5),
        "Pressures_per90": (9.0, 22.0),
        "Progressive_Passes_per90": (1.0, 3.2),
        "Interceptions_per90": (0.2, 1.2),
        "Tackles_per90": (0.3, 1.2),
        "Pass_Accuracy_Pct": (68.0, 84.0),
        "Shot_Accuracy_Pct": (42.0, 65.0),
    },
    "Kanat": {
        "xG_per90": (0.20, 0.55),
        "xA_per90": (0.22, 0.52),
        "Key_Passes_per90": (1.5, 3.8),
        "Dribbles_per90": (2.2, 5.8),
        "Defensive_Duels_per90": (1.2, 3.8),
        "Pressures_per90": (10.0, 24.0),
        "Progressive_Passes_per90": (2.2, 5.5),
        "Interceptions_per90": (0.4, 1.8),
        "Tackles_per90": (0.5, 2.0),
        "Pass_Accuracy_Pct": (72.0, 86.0),
        "Shot_Accuracy_Pct": (34.0, 54.0),
    },
    "Merkez Orta Saha": {
        "xG_per90": (0.05, 0.28),
        "xA_per90": (0.12, 0.42),
        "Key_Passes_per90": (1.2, 3.4),
        "Dribbles_per90": (1.0, 3.2),
        "Defensive_Duels_per90": (2.8, 6.8),
        "Pressures_per90": (12.0, 26.0),
        "Progressive_Passes_per90": (4.5, 9.8),
        "Interceptions_per90": (1.2, 4.2),
        "Tackles_per90": (1.2, 3.8),
        "Pass_Accuracy_Pct": (82.0, 93.0),
        "Shot_Accuracy_Pct": (25.0, 45.0),
    },
    "Stoper": {
        "xG_per90": (0.01, 0.12),
        "xA_per90": (0.01, 0.08),
        "Key_Passes_per90": (0.1, 0.8),
        "Dribbles_per90": (0.1, 0.8),
        "Defensive_Duels_per90": (4.5, 9.2),
        "Pressures_per90": (5.0, 14.0),
        "Progressive_Passes_per90": (2.5, 6.8),
        "Interceptions_per90": (3.2, 7.5),
        "Tackles_per90": (1.6, 4.2),
        "Pass_Accuracy_Pct": (85.0, 95.0),
        "Shot_Accuracy_Pct": (15.0, 35.0),
    },
    "Bek": {
        "xG_per90": (0.02, 0.18),
        "xA_per90": (0.10, 0.35),
        "Key_Passes_per90": (0.8, 2.6),
        "Dribbles_per90": (1.0, 3.2),
        "Defensive_Duels_per90": (3.2, 7.5),
        "Pressures_per90": (8.0, 20.0),
        "Progressive_Passes_per90": (3.2, 7.8),
        "Interceptions_per90": (2.0, 5.5),
        "Tackles_per90": (1.5, 4.0),
        "Pass_Accuracy_Pct": (76.0, 89.0),
        "Shot_Accuracy_Pct": (20.0, 40.0),
    },
}


def generate_player_dataset(n_players: int = 180) -> pd.DataFrame:
    """
    Generates a realistic synthetic player dataset containing per-90 metrics
    across 5 main football positions.
    """
    players_data = []

    for i in range(1, n_players + 1):
        first_name = random.choice(FIRST_NAMES)
        last_name = random.choice(LAST_NAMES)
        full_name = f"{first_name} {last_name}"

        # To avoid duplicated names, append small variation if needed
        if any(p["Name"] == full_name for p in players_data):
            full_name = f"{first_name} {last_name} ({i})"

        position = random.choice(POSITIONS)
        league = random.choice(list(TEAMS_BY_LEAGUE.keys()))
        team = random.choice(TEAMS_BY_LEAGUE[league])
        age = int(np.random.randint(18, 35))

        # Realistic market value generation (skewed)
        base_value = float(np.random.lognormal(mean=2.2, sigma=0.9))
        market_value = round(max(0.8, min(120.0, base_value)), 2)

        minutes_played = int(np.random.randint(900, 3200))

        # Sample metrics according to position profile
        profile = POSITION_METRIC_PROFILES[position]
        metric_values = {}
        for metric, (low, high) in profile.items():
            # Uniform distribution with slight Gaussian noise
            val = np.random.uniform(low, high)
            if "%" in metric or "Pct" in metric:
                metric_values[metric] = round(float(np.clip(val, 50.0, 98.0)), 1)
            else:
                metric_values[metric] = round(float(max(0.01, val)), 2)

        player_row = {
            "Player_ID": i,
            "Name": full_name,
            "Age": age,
            "Position": position,
            "Team": team,
            "League": league,
            "Market_Value_EUR_M": market_value,
            "Minutes_Played": minutes_played,
            **metric_values
        }
        players_data.append(player_row)

    df = pd.DataFrame(players_data)
    return df


def main(output_path: str = "data/raw/players.csv") -> None:
    """
    Generates synthetic dataset and saves it to specified output_path.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df = generate_player_dataset(n_players=180)
    df.to_csv(output_path, index=False, encoding="utf-8")
    print(f"Successfully generated {len(df)} players dataset at: {output_path}")


if __name__ == "__main__":
    main()
