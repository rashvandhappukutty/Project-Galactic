# simulation/analytics/narrative_analytics.py
"""Narrative and Geopolitical Legacy Analytics Engine.
Calculates most documented empires, legendary figures, and logs summary metrics.
"""

from __future__ import annotations
import os
import pandas as pd
from typing import List, Dict, Any
from ..utils import write_csv, logger

class NarrativeAnalytics:
    """Computes narrative stats, top characters, and flags legendary lore indicators."""

    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = datasets_dir

    def run_narrative_analytics(self) -> Dict[str, Any]:
        """Loads Phase 11 story databases and runs legacy queries."""
        logger.info("Running Phase 11 narrative analytics...")
        
        figures_path = os.path.join(self.datasets_dir, "historical_figures.csv")
        news_path = os.path.join(self.datasets_dir, "galactic_news.csv")
        war_reports_path = os.path.join(self.datasets_dir, "war_reports.csv")
        chronicles_path = os.path.join(self.datasets_dir, "empire_chronicles.csv")

        results = {}

        # 1. Most Legendary Figure (max legacy_score)
        if os.path.exists(figures_path):
            df_fig = pd.read_csv(figures_path)
            if not df_fig.empty:
                top_fig = df_fig.loc[df_fig["legacy_score"].idxmax()]
                results["most_legendary_figure"] = {
                    "name": top_fig["name"],
                    "civilization": top_fig["civilization"],
                    "role": top_fig["role"],
                    "legacy_score": int(top_fig["legacy_score"]),
                    "achievements": top_fig["achievements"]
                }
                
                # Output Top 100 historical figures to rankings/datasets
                top_100 = df_fig.sort_values(by="legacy_score", ascending=False).head(100)
                top_100.to_csv(os.path.join(self.datasets_dir, "top_100_figures.csv"), index=False)
            else:
                results["most_legendary_figure"] = {"name": "None", "legacy_score": 0}
        else:
            results["most_legendary_figure"] = {"name": "None", "legacy_score": 0}

        # 2. Most Documented Empire (news frequency)
        if os.path.exists(news_path):
            df_news = pd.read_csv(news_path)
            if not df_news.empty:
                # Group by mention or count strings
                # News articles body contains civilization names, let's count occurrences
                counts = {}
                if os.path.exists(chronicles_path):
                    df_chron = pd.read_csv(chronicles_path)
                    for _, row in df_chron.iterrows():
                        name = row["empire_name"]
                        # count mentions in news body
                        mentions = df_news["body"].str.contains(name, case=False, na=False).sum()
                        counts[name] = mentions
                
                if counts:
                    most_doc = max(counts, key=counts.get)
                    results["most_documented_empire"] = {
                        "name": most_doc,
                        "mentions_count": int(counts[most_doc])
                    }
                else:
                    results["most_documented_empire"] = {"name": "None", "mentions_count": 0}
            else:
                results["most_documented_empire"] = {"name": "None", "mentions_count": 0}
        else:
            results["most_documented_empire"] = {"name": "None", "mentions_count": 0}

        # 3. Most Important War (highest casualties)
        if os.path.exists(war_reports_path):
            df_war = pd.read_csv(war_reports_path)
            if not df_war.empty:
                # Parse casualties column to integer
                df_war = df_war.copy()
                df_war["cas_int"] = df_war["casualties"].str.replace(",", "").str.extract(r"(\d+)").astype(float).fillna(0)
                if not df_war[df_war["cas_int"] > 0].empty:
                    top_war = df_war.loc[df_war["cas_int"].idxmax()]
                    results["most_important_war"] = {
                        "participants": top_war["participants"],
                        "cause": top_war["cause"],
                        "casualties": top_war["casualties"],
                        "outcome": top_war["outcome"]
                    }
                else:
                    results["most_important_war"] = {"participants": "Minor conflicts", "casualties": "0"}
            else:
                results["most_important_war"] = {"participants": "Minor conflicts", "casualties": "0"}
        else:
            results["most_important_war"] = {"participants": "Minor conflicts", "casualties": "0"}

        results["largest_historical_legacy"] = sum(df_fig["legacy_score"]) if os.path.exists(figures_path) and not df_fig.empty else 0

        return results

    def print_summary(self, results: Dict[str, Any]) -> None:
        """Outputs story analytics summary to the console."""
        print("=" * 80)
        print("                 GALACTIC LORE & NARRATIVE ANALYTICS")
        print("=" * 80)
        if not results:
            print("No narrative analytics compiled.")
            return

        print(f"Most Legendary Figure : {results['most_legendary_figure']['name']} ({results['most_legendary_figure']['role']})")
        print(f"                         Civilization: {results['most_legendary_figure']['civilization']}")
        print(f"                         Legacy Score: {results['most_legendary_figure']['legacy_score']}")
        print(f"                         Achievements: {results['most_legendary_figure']['achievements']}")
        print(f"Most Documented Empire: {results['most_documented_empire']['name']} ({results['most_documented_empire']['mentions_count']} News Mentions)")
        print(f"Most Important War    : {results['most_important_war']['participants']}")
        print(f"                         Cause: {results['most_important_war']['cause']}")
        print(f"                         Casualties: {results['most_important_war']['casualties']}")
        print(f"                         Outcome: {results['most_important_war']['outcome']}")
        print(f"Largest Historical Legacy: {results['largest_historical_legacy']:,} cumulative legacy points.")
        print("=" * 80)
