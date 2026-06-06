# simulation/analytics/diplomacy_analytics.py
"""Analytics for diplomatic relations and alliances.
Provides functions to compute top powers, alliance strength, and diplomatic heatmaps.
"""

from __future__ import annotations

import pandas as pd
from typing import List

from ..models import Empire, Relation, Alliance
from ..utils import logger


def load_relations_df() -> pd.DataFrame:
    return pd.read_csv("datasets/diplomatic_relations.csv")


def load_alliances_df() -> pd.DataFrame:
    return pd.read_csv("datasets/alliances.csv")


def compute_power_index(empires: List[Empire]) -> pd.DataFrame:
    """Combine GDP, fleet power, and diplomatic influence into a single index.
    This is a simplified placeholder implementation.
    """
    rows = []
    for e in empires:
        rows.append({"empire_id": e.empire_id, "gdp": e.gdp, "tech_level": e.tech_level})
    df = pd.DataFrame(rows)
    df["power_index"] = df["gdp"] * 0.6 + df["tech_level"] * 1000
    return df.sort_values(by="power_index", ascending=False)


def top_diplomatic_influencers(relations_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """Rank empires by aggregate influence across all relations."""
    influence_a = relations_df.groupby("empire_a")["influence"].sum().reset_index().rename(columns={"empire_a": "empire_id", "influence": "influence_sum"})
    influence_b = relations_df.groupby("empire_b")["influence"].sum().reset_index().rename(columns={"empire_b": "empire_id", "influence": "influence_sum"})
    total = pd.concat([influence_a, influence_b]).groupby("empire_id")["influence_sum"].sum().reset_index()
    return total.sort_values(by="influence_sum", ascending=False).head(top_n)

# Simple heatmap generation stub (no actual image output in this placeholder)
def generate_diplomatic_heatmap(relations_df: pd.DataFrame) -> None:
    logger.info("Generating diplomatic heatmap – placeholder implementation.")
    # In a full implementation we would use seaborn/matplotlib to plot.
    pass
