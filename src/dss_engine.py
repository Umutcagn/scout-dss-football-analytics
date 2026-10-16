from typing import Dict, List, Optional, Tuple, Union
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# Default weight profiles per position for DSS Scoring
DEFAULT_POSITION_WEIGHTS: Dict[str, Dict[str, float]] = {
    "Kanat": {
        "xT_per90": 0.20,
        "Dribbles_per90": 0.15,
        "Pack_Rate": 0.15,
        "xG_per90": 0.15,
        "Sofascore_Attacking": 0.15,
        "Sofascore_Creativity": 0.10,
        "High_Turnovers_per90": 0.10,
    },
    "Santrafor": {
        "xG_per90": 0.25,
        "xG_per_Shot": 0.15,
        "Sofascore_Attacking": 0.20,
        "Shot_Accuracy_Pct": 0.15,
        "xA_per90": 0.15,
        "Pack_Rate": 0.10,
    },
    "Merkez Orta Saha": {
        "xT_per90": 0.20,
        "Progressive_Passes_per90": 0.20,
        "Sofascore_Creativity": 0.15,
        "Sofascore_Technical": 0.15,
        "Pack_Rate": 0.15,
        "PADJ_Tackles_per90": 0.15,
    },
    "Stoper": {
        "PADJ_Tackles_per90": 0.20,
        "Defensive_Duels_per90": 0.20,
        "Sofascore_Defending": 0.20,
        "Sofascore_Tactical": 0.15,
        "Interceptions_per90": 0.15,
        "Progressive_Passes_per90": 0.10,
    },
    "Bek": {
        "Progressive_Passes_per90": 0.15,
        "xT_per90": 0.15,
        "Sofascore_Defending": 0.20,
        "Sofascore_Technical": 0.15,
        "Pack_Rate": 0.15,
        "PADJ_Tackles_per90": 0.20,
    },
    "Kaleci": {
        "PSxG_Net": 0.35,
        "Sofascore_Defending": 0.25,
        "Pass_Accuracy_Pct": 0.20,
        "Progressive_Passes_per90": 0.20,
    }
}

ALL_METRICS = [
    "xG_per90", "xA_per90", "Key_Passes_per90", "Dribbles_per90",
    "Defensive_Duels_per90", "Pressures_per90", "Progressive_Passes_per90",
    "Interceptions_per90", "Tackles_per90", "Pass_Accuracy_Pct", "Shot_Accuracy_Pct",
    "xT_per90", "Pack_Rate", "PADJ_Tackles_per90", "High_Turnovers_per90",
    "PPDA_Contribution", "PSxG_Net", "xG_per_Shot", "xG_Buildup_per90",
    # Sofascore Live Ratings
    "Sofascore_Attacking", "Sofascore_Creativity", "Sofascore_Technical",
    "Sofascore_Defending", "Sofascore_Tactical"
]


class DSSEngine:
    """
    Decision Support System Engine supporting Weighted Scoring, TOPSIS ranking,
    and Cosine Similarity player replacement finding.
    """

    def __init__(self, data: pd.DataFrame) -> None:
        self.df = data.copy()

    @staticmethod
    def get_default_weights(position: str) -> Dict[str, float]:
        """Returns default metric weights for a given position."""
        return DEFAULT_POSITION_WEIGHTS.get(
            position,
            {m: round(1.0 / len(ALL_METRICS), 4) for m in ALL_METRICS}
        )

    def calculate_weighted_score(
        self,
        position_filter: Optional[str] = None,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Calculates position suitability score (0-100) using weighted percentile metrics.
        """
        df_sub = self.df.copy()
        if position_filter:
            df_sub = df_sub[df_sub["Position"] == position_filter].copy()

        if df_sub.empty:
            return df_sub

        scores = []
        for idx, row in df_sub.iterrows():
            pos = row["Position"]
            weights = custom_weights if custom_weights else self.get_default_weights(pos)

            weight_sum = sum(weights.values())
            if weight_sum > 0:
                normalized_weights = {k: v / weight_sum for k, v in weights.items()}
            else:
                normalized_weights = weights

            player_score = 0.0
            for metric, w in normalized_weights.items():
                pct_col = f"{metric}_percentile" if f"{metric}_percentile" in row else metric
                val = row.get(pct_col, 50.0)
                player_score += val * w

            scores.append(round(player_score, 2))

        df_sub["DSS_Score"] = scores
        return df_sub.sort_values(by="DSS_Score", ascending=False)

    def calculate_topsis_score(
        self,
        position_filter: Optional[str] = None,
        custom_weights: Optional[Dict[str, float]] = None
    ) -> pd.DataFrame:
        """
        Calculates TOPSIS score with zero-sum division safety and key guards.
        """
        df_sub = self.df.copy()
        if position_filter:
            df_sub = df_sub[df_sub["Position"] == position_filter].copy()

        if df_sub.empty:
            return df_sub

        pos = position_filter or df_sub["Position"].iloc[0]
        weights = custom_weights if custom_weights else self.get_default_weights(pos)

        metric_keys = [k for k in weights.keys() if k in ALL_METRICS or f"{k}_percentile" in df_sub.columns]
        if not metric_keys:
            metric_keys = list(self.get_default_weights(pos).keys())

        w_vals = np.array([weights.get(k, 0.1) for k in metric_keys], dtype=float)
        w_sum = np.sum(w_vals)
        if w_sum <= 0:
            w_vals = np.ones_like(w_vals) / len(w_vals)
        else:
            w_vals = w_vals / w_sum

        matrix = []
        for m in metric_keys:
            col = f"{m}_percentile" if f"{m}_percentile" in df_sub.columns else m
            if col in df_sub.columns:
                matrix.append(df_sub[col].values)
            else:
                matrix.append(np.full(len(df_sub), 50.0))

        X = np.column_stack(matrix)

        norm_factor = np.sqrt(np.sum(X**2, axis=0))
        norm_factor[norm_factor == 0] = 1.0
        X_norm = X / norm_factor

        V = X_norm * w_vals

        A_plus = np.max(V, axis=0)
        A_minus = np.min(V, axis=0)

        S_plus = np.sqrt(np.sum((V - A_plus)**2, axis=1))
        S_minus = np.sqrt(np.sum((V - A_minus)**2, axis=1))

        denom = S_plus + S_minus
        denom[denom == 0] = 1.0
        closeness = (S_minus / denom) * 100.0

        df_sub["TOPSIS_Score"] = np.round(closeness, 2)
        return df_sub.sort_values(by="TOPSIS_Score", ascending=False)

    def find_similar_players(
        self,
        target_player_id: int,
        max_market_value: Optional[float] = None,
        max_age: Optional[int] = None,
        same_position_only: bool = True,
        top_n: int = 5
    ) -> Tuple[pd.Series, pd.DataFrame]:
        """
        Finds top N most similar budget/age-compliant alternative players using Cosine Similarity.
        """
        if target_player_id not in self.df["Player_ID"].values:
            raise ValueError(f"Player ID {target_player_id} not found in dataset.")

        target_row = self.df[self.df["Player_ID"] == target_player_id].iloc[0]
        candidates = self.df[self.df["Player_ID"] != target_player_id].copy()

        if same_position_only:
            candidates = candidates[candidates["Position"] == target_row["Position"]]

        if max_market_value is not None:
            candidates = candidates[candidates["Market_Value_EUR_M"] <= max_market_value]

        if max_age is not None:
            candidates = candidates[candidates["Age"] <= max_age]

        if candidates.empty:
            return target_row, pd.DataFrame()

        vector_cols = [f"{m}_percentile" for m in ALL_METRICS if f"{m}_percentile" in self.df.columns]
        if not vector_cols:
            vector_cols = ALL_METRICS

        target_vector = target_row[vector_cols].values.reshape(1, -1).astype(float)
        candidate_vectors = candidates[vector_cols].values.astype(float)

        similarities = cosine_similarity(target_vector, candidate_vectors)[0]
        similarity_pct = np.round(similarities * 100.0, 1)

        candidates["Similarity_Pct"] = similarity_pct
        similar_df = candidates.sort_values(by="Similarity_Pct", ascending=False).head(top_n)

        return target_row, similar_df
