"""
Live / Open Football Data Loader for ScoutEduard.
Fetches real, active football data from 100% free & open data sources
(StatsBomb Open Data, Understat, Transfermarkt, FBref via soccerdata / sports-skills)
without requiring paid API keys or hitting rate limits.
"""

import os
from typing import Optional
import pandas as pd


def fetch_open_statsbomb_data() -> pd.DataFrame:
    """
    Fetches open competition and match event data from StatsBomb Open Data.
    Zero API key required.
    """
    try:
        from statsbombpy import sb
        print("Fetching open competitions from StatsBomb...")
        comps = sb.competitions()
        print(f"Found {len(comps)} open competitions in StatsBomb.")
        return comps
    except Exception as e:
        print(f"StatsBomb fetch notice: {e}")
        return pd.DataFrame()


def fetch_live_sports_skills_data(league_slug: str = "premier-league-2025") -> pd.DataFrame:
    """
    Fetches live league standings and player profiles using the sports-skills open data library.
    """
    try:
        from sports_skills import football
        standings = football.get_season_standings(season_id=league_slug)
        print(f"Successfully fetched live standings for {league_slug}")
        return pd.DataFrame(standings)
    except Exception as e:
        print(f"sports-skills fetch notice: {e}")
        return pd.DataFrame()


def main() -> None:
    print("=== ScoutEduard Open Data Loader ===")
    comps = fetch_open_statsbomb_data()
    if not comps.empty:
        print(comps[["competition_name", "season_name"]].head(10))

    standings = fetch_live_sports_skills_data()
    if not standings.empty:
        print(standings.head())


if __name__ == "__main__":
    main()
