import numpy as np
import pandas as pd
import pytest

from src.dss_engine import (
    ALL_METRICS, FIXED_DEFAULT_METRICS, REAL_METRICS, SIMULATED_METRICS, DSSEngine,
)
from src.normalizer import MetricNormalizer


def _players(rows):
    base = {"Age": 25, "Position": "Santrafor", "Market_Value_EUR_M": 10.0}
    return pd.DataFrame([{**base, **r} for r in rows])


def test_topsis_matches_hand_calculation():
    # Two criteria, equal weights. Hand-computed closeness: A=1.0, B=0.5, C=0.0
    df = _players([
        {"Player_ID": 1, "Name": "A", "xG_per90": 3.0, "xA_per90": 4.0},
        {"Player_ID": 2, "Name": "B", "xG_per90": 2.0, "xA_per90": 2.5},
        {"Player_ID": 3, "Name": "C", "xG_per90": 1.0, "xA_per90": 1.0},
    ])
    res = DSSEngine(df).calculate_topsis_score("Santrafor", {"xG_per90": 0.5, "xA_per90": 0.5})
    scores = dict(zip(res["Name"], res["TOPSIS_Score"]))
    assert scores["A"] == pytest.approx(100.0)
    assert scores["C"] == pytest.approx(0.0)

    # Independent reference implementation for the middle alternative
    X = np.array([[3.0, 4.0], [2.0, 2.5], [1.0, 1.0]])
    V = X / np.sqrt((X ** 2).sum(axis=0)) * 0.5
    s_plus = np.linalg.norm(V[1] - V.max(axis=0))
    s_minus = np.linalg.norm(V[1] - V.min(axis=0))
    assert scores["B"] == pytest.approx(round(s_minus / (s_plus + s_minus) * 100, 2))


def test_topsis_ranking_responds_to_weights():
    df = _players([
        {"Player_ID": 1, "Name": "Scorer", "xG_per90": 0.9, "xA_per90": 0.1},
        {"Player_ID": 2, "Name": "Creator", "xG_per90": 0.1, "xA_per90": 0.9},
    ])
    engine = DSSEngine(df)
    assert engine.calculate_topsis_score("Santrafor", {"xG_per90": 0.9, "xA_per90": 0.1}).iloc[0]["Name"] == "Scorer"
    assert engine.calculate_topsis_score("Santrafor", {"xG_per90": 0.1, "xA_per90": 0.9}).iloc[0]["Name"] == "Creator"


def test_weighted_score_is_weighted_mean_of_percentiles():
    df = _players([{"Player_ID": 1, "Name": "A", "xG_per90_percentile": 80.0, "xA_per90_percentile": 40.0}])
    res = DSSEngine(df).calculate_weighted_score("Santrafor", {"xG_per90": 3.0, "xA_per90": 1.0})
    assert res.iloc[0]["DSS_Score"] == pytest.approx(70.0)


def _similarity_pool():
    rng = np.random.default_rng(0)
    rows = []
    for i in range(1, 9):
        row = {"Player_ID": i, "Name": f"P{i}", "Age": 20 + i, "Market_Value_EUR_M": 5.0 * i,
               "Position": "Kanat" if i < 8 else "Stoper"}
        row.update({f"{m}_percentile": float(rng.uniform(0, 100)) for m in ALL_METRICS})
        rows.append(row)
    df = pd.DataFrame(rows)
    # P2 mirrors P1's profile; it must be the best match
    df.loc[df["Player_ID"] == 2, [f"{m}_percentile" for m in ALL_METRICS]] = \
        df.loc[df["Player_ID"] == 1, [f"{m}_percentile" for m in ALL_METRICS]].values
    return df


def test_similar_players_respects_filters_and_excludes_target():
    target, similar = DSSEngine(_similarity_pool()).find_similar_players(
        1, max_market_value=30.0, max_age=26, same_position_only=True, top_n=10)
    assert target["Player_ID"] == 1
    assert 1 not in similar["Player_ID"].values
    assert (similar["Position"] == "Kanat").all()
    assert (similar["Market_Value_EUR_M"] <= 30.0).all()
    assert (similar["Age"] <= 26).all()


def test_identical_profile_is_top_match_with_full_similarity():
    _, similar = DSSEngine(_similarity_pool()).find_similar_players(1, top_n=3)
    assert similar.iloc[0]["Player_ID"] == 2
    assert similar.iloc[0]["Similarity_Pct"] == pytest.approx(100.0)


def test_unknown_player_raises():
    with pytest.raises(ValueError):
        DSSEngine(_similarity_pool()).find_similar_players(999)


def test_percentiles_are_computed_within_position():
    df = pd.DataFrame({
        "Position": ["Kanat", "Kanat", "Stoper", "Stoper"],
        "xG_per90": [0.1, 0.5, 5.0, 9.0],
    })
    out = MetricNormalizer(metric_cols=["xG_per90"]).normalize_percentile(df)
    # Each position's best player is at the 100th percentile of its own pool
    assert out["xG_per90_percentile"].tolist() == [50.0, 100.0, 50.0, 100.0]


def test_metric_provenance_partitions_all_metrics():
    groups = [set(REAL_METRICS), set(SIMULATED_METRICS), set(FIXED_DEFAULT_METRICS)]
    assert set().union(*groups) == set(ALL_METRICS)
    assert sum(len(g) for g in groups) == len(ALL_METRICS)
