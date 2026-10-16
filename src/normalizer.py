import os
from typing import List, Optional
import numpy as np
import pandas as pd
from scipy.stats import percentileofscore

METRIC_COLUMNS = [
    "xG_per90",
    "xA_per90",
    "Key_Passes_per90",
    "Dribbles_per90",
    "Defensive_Duels_per90",
    "Pressures_per90",
    "Progressive_Passes_per90",
    "Interceptions_per90",
    "Tackles_per90",
    "Pass_Accuracy_Pct",
    "Shot_Accuracy_Pct",
    # Advanced Metrics
    "xT_per90",
    "Pack_Rate",
    "PADJ_Tackles_per90",
    "High_Turnovers_per90",
    "PPDA_Contribution",
    "PSxG_Net",
    "xG_per_Shot",
    "xG_Buildup_per90",
    # Sofascore Live Ratings
    "Sofascore_Attacking",
    "Sofascore_Creativity",
    "Sofascore_Technical",
    "Sofascore_Defending",
    "Sofascore_Tactical"
]

METADATA_COLUMNS = [
    "Player_ID", "Name", "Age", "Position", "Team", "League",
    "Market_Value_EUR_M", "Minutes_Played", "Season"
]


class MetricNormalizer:
    """
    Normalizes football player metrics within position pools using
    Percentile Ranking (0-100) or Z-Score.
    """

    def __init__(self, metric_cols: Optional[List[str]] = None) -> None:
        self.metric_cols = metric_cols or METRIC_COLUMNS

    def normalize_percentile(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforms raw metrics into 0-100 percentile scores within each position pool.
        """
        df_norm = df.copy()

        for position in df_norm["Position"].unique():
            pos_mask = df_norm["Position"] == position
            pos_df = df_norm[pos_mask]

            for metric in self.metric_cols:
                if metric in df_norm.columns:
                    col_vals = pos_df[metric].values
                    percentiles = [
                        round(float(percentileofscore(col_vals, val, kind="weak")), 1)
                        for val in col_vals
                    ]
                    df_norm.loc[pos_mask, f"{metric}_percentile"] = percentiles

        return df_norm

    def normalize_zscore(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Computes Z-scores (mean=0, std=1) per metric within each position pool.
        """
        df_norm = df.copy()

        for position in df_norm["Position"].unique():
            pos_mask = df_norm["Position"] == position
            pos_df = df_norm[pos_mask]

            for metric in self.metric_cols:
                if metric in df_norm.columns:
                    mean = pos_df[metric].mean()
                    std = pos_df[metric].std()
                    if std == 0 or np.isnan(std):
                        std = 1.0
                    z_scores = (pos_df[metric] - mean) / std
                    df_norm.loc[pos_mask, f"{metric}_zscore"] = z_scores.round(2)

        return df_norm

    def process_and_save(
        self,
        raw_csv_path: str = "data/raw/players.csv",
        output_csv_path: str = "data/processed/players_normalized.csv"
    ) -> pd.DataFrame:
        """
        Reads raw dataset, performs percentile normalization, and writes output CSV.
        """
        if not os.path.exists(raw_csv_path):
            raise FileNotFoundError(f"Raw dataset not found at {raw_csv_path}")

        df_raw = pd.read_csv(raw_csv_path)
        df_norm = self.normalize_percentile(df_raw)
        df_norm = self.normalize_zscore(df_norm)

        os.makedirs(os.path.dirname(output_csv_path), exist_ok=True)
        df_norm.to_csv(output_csv_path, index=False, encoding="utf-8")
        print(f"Normalized dataset successfully saved to: {output_csv_path}")
        return df_norm


def main() -> None:
    normalizer = MetricNormalizer()
    normalizer.process_and_save()


if __name__ == "__main__":
    main()
