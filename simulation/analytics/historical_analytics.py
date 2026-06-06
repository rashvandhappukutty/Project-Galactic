# simulation/analytics/historical_analytics.py
"""Historical Analytics Engine.
Calculates rankings, filters legendary achievements, and generates timeline summaries.
"""

from __future__ import annotations
import os
import pandas as pd
from typing import List, Dict, Any
from ..utils import write_csv, logger

class HistoricalAnalytics:
    """Computes advanced historical stats, rankings, summaries, and legendary achievements."""

    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = datasets_dir

    def run_analytics(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Runs the entire historical analytics suite."""
        logger.info("Running Phase 10 historical analytics...")
        df = pd.DataFrame(events)

        if df.empty:
            logger.warning("Empty timeline. Cannot compute analytics.")
            return {}

        results = {}

        # 1. Most Significant Event
        top_event = df.loc[df["impact_score"].idxmax()]
        results["most_significant_event"] = {
            "event_id": top_event["event_id"],
            "year": int(top_event["year"]),
            "event_type": top_event["event_type"],
            "empire": top_event["empire"],
            "impact_score": float(top_event["impact_score"]),
            "description": top_event["description"]
        }

        # 2. Most Influential Empire (sum of impact_score of events they participated in)
        empire_influence = {}
        for _, row in df.iterrows():
            emp = row["empire"]
            score = row["impact_score"]
            if pd.notna(emp) and str(emp).strip() and str(emp).lower() not in ["nan", "unknown", "galaxy", "none"]:
                empire_influence[emp] = empire_influence.get(emp, 0.0) + score
            part = row["participants"]
            if pd.notna(part) and str(part).strip() and str(part).lower() not in ["nan", "unknown", "galaxy", "none", ""]:
                for p in str(part).split("|"):
                    p_clean = p.strip()
                    if p_clean and p_clean.lower() not in ["nan", "unknown", "galaxy", "none"]:
                        empire_influence[p_clean] = empire_influence.get(p_clean, 0.0) + score

        most_influential = max(empire_influence, key=empire_influence.get) if empire_influence else "Unknown"
        results["most_influential_empire"] = {
            "name": most_influential,
            "total_influence_score": round(empire_influence.get(most_influential, 0.0), 2)
        }

        # 3. Era Stats (Prosperous vs Violent)
        eras_path = os.path.join(self.datasets_dir, "era_history.csv")
        most_prosperous_era = "Unknown"
        most_violent_era = "Unknown"

        if os.path.exists(eras_path):
            eras_df = pd.read_csv(eras_path)
            prosperous_scores = {}
            violent_scores = {}
            for _, era in eras_df.iterrows():
                era_events = df[(df["year"] >= era["start_year"]) & (df["year"] <= era["end_year"])]
                duration = max(1, era["end_year"] - era["start_year"])
                
                # Prosperous: high science, economy, trade, colonization
                pos_events = era_events[era_events["event_category"].isin(["Science", "Economy", "Colonization", "Diplomacy"])]
                prosperous_scores[era["era_name"]] = len(pos_events) / duration
                
                # Violent: military and battles
                neg_events = era_events[era_events["event_category"] == "Military"]
                violent_scores[era["era_name"]] = len(neg_events) / duration

            most_prosperous_era = max(prosperous_scores, key=prosperous_scores.get) if prosperous_scores else "Unknown"
            most_violent_era = max(violent_scores, key=violent_scores.get) if violent_scores else "Unknown"

        results["most_prosperous_era"] = most_prosperous_era
        results["most_violent_era"] = most_violent_era

        # 4. Longest Lasting Empire (from lifecycles)
        lifecycle_path = os.path.join(self.datasets_dir, "empire_lifecycles.csv")
        longest_lasting = "Unknown"
        max_lifespan = 0
        if os.path.exists(lifecycle_path):
            lc_df = pd.read_csv(lifecycle_path)
            lifespans = {}
            for emp, group in lc_df.groupby("empire_name"):
                lifespan = group["year"].max() - group["year"].min()
                lifespans[emp] = lifespan
            if lifespans:
                longest_lasting = max(lifespans, key=lifespans.get)
                max_lifespan = lifespans[longest_lasting]

        results["longest_lasting_empire"] = {
            "name": longest_lasting,
            "lifespan_years": max_lifespan
        }

        # 5. Save rankings to datasets/historical_rankings.csv
        rankings = []
        sorted_empires = sorted(empire_influence.items(), key=lambda x: x[1], reverse=True)
        for rank, (emp, score) in enumerate(sorted_empires, 1):
            rankings.append({
                "rank": rank,
                "empire_name": emp,
                "influence_score": round(score, 2),
                "lifespan_rank": rank,  # proxy for ranking
                "historical_rank": rank
            })
        rankings_path = os.path.join(self.datasets_dir, "historical_rankings.csv")
        write_csv(rankings_path, rankings, ["rank", "empire_name", "influence_score", "lifespan_rank", "historical_rank"])

        # 6. Flags and logs "Legendary Events"
        self._generate_legendary_events(df, results)

        # 7. Generate compressed timeline summaries (timeline_summaries.csv)
        self._generate_timeline_summaries(df)

        return results

    def _generate_legendary_events(self, df: pd.DataFrame, results: Dict[str, Any]):
        """Detects and saves legendary events to datasets/legendary_events.csv."""
        legendary = []

        # A. Largest War
        wars = df[df["event_type"] == "War Declaration"]
        if not wars.empty:
            largest_war = wars.loc[wars["impact_score"].idxmax()]
            legendary.append({
                "legendary_type": "Largest War",
                "year": int(largest_war["year"]),
                "empire_involved": largest_war["empire"],
                "description": largest_war["description"],
                "impact_score": float(largest_war["impact_score"])
            })

        # B. Longest War
        wars_end = df[df["event_type"] == "War End"]
        if not wars_end.empty:
            # Parse duration from description
            import re
            longest_duration = 0
            longest_war_row = None
            for _, row in wars_end.iterrows():
                dur_match = re.search(r"after (\d+) years", row["description"])
                if dur_match:
                    dur = int(dur_match.group(1))
                    if dur > longest_duration:
                        longest_duration = dur
                        longest_war_row = row
            if longest_war_row is not None:
                legendary.append({
                    "legendary_type": "Longest War",
                    "year": int(longest_war_row["year"]),
                    "empire_involved": longest_war_row["empire"],
                    "description": f"{longest_war_row['description']} (Duration: {longest_duration} years)",
                    "impact_score": float(longest_war_row["impact_score"])
                })

        # C. First Galactic Empire
        first_emp_evt = df[df["description"].str.contains("emerges|found", case=False, na=False)].head(1)
        if not first_emp_evt.empty:
            legendary.append({
                "legendary_type": "First Galactic Empire",
                "year": int(first_emp_evt.iloc[0]["year"]),
                "empire_involved": first_emp_evt.iloc[0]["empire"],
                "description": first_emp_evt.iloc[0]["description"],
                "impact_score": float(first_emp_evt.iloc[0]["impact_score"])
            })

        # D. First Federation
        fed_evt = df[df["event_type"].isin(["Alliance Formation", "Galactic Federation"])].head(1)
        if not fed_evt.empty:
            legendary.append({
                "legendary_type": "First Federation",
                "year": int(fed_evt.iloc[0]["year"]),
                "empire_involved": fed_evt.iloc[0]["empire"],
                "description": fed_evt.iloc[0]["description"],
                "impact_score": float(fed_evt.iloc[0]["impact_score"])
            })

        # E. First Type III Civilization
        type3_evt = df[df["description"].str.contains("Type III|Kardashev III", case=False, na=False)].head(1)
        if not type3_evt.empty:
            legendary.append({
                "legendary_type": "First Type III Civilization",
                "year": int(type3_evt.iloc[0]["year"]),
                "empire_involved": type3_evt.iloc[0]["empire"],
                "description": type3_evt.iloc[0]["description"],
                "impact_score": float(type3_evt.iloc[0]["impact_score"])
            })

        # F. Most Destructive War
        destructive_evt = df[df["description"].str.contains("casualties", case=False, na=False)]
        if not destructive_evt.empty:
            most_destructive = destructive_evt.loc[destructive_evt["impact_score"].idxmax()]
            legendary.append({
                "legendary_type": "Most Destructive War",
                "year": int(most_destructive["year"]),
                "empire_involved": most_destructive["empire"],
                "description": most_destructive["description"],
                "impact_score": float(most_destructive["impact_score"])
            })

        # G. Great Galactic Crisis
        crisis_evt = df[df["event_category"] == "Crisis"].head(1)
        if not crisis_evt.empty:
            legendary.append({
                "legendary_type": "Great Galactic Crisis",
                "year": int(crisis_evt.iloc[0]["year"]),
                "empire_involved": crisis_evt.iloc[0]["empire"],
                "description": crisis_evt.iloc[0]["description"],
                "impact_score": float(crisis_evt.iloc[0]["impact_score"])
            })

        # H. Galactic Unification Attempt
        unif_evt = df[df["description"].str.contains("unification|hegemony|unified", case=False, na=False)].head(1)
        if not unif_evt.empty:
            legendary.append({
                "legendary_type": "Galactic Unification Attempt",
                "year": int(unif_evt.iloc[0]["year"]),
                "empire_involved": unif_evt.iloc[0]["empire"],
                "description": unif_evt.iloc[0]["description"],
                "impact_score": float(unif_evt.iloc[0]["impact_score"])
            })

        # If empty, write fallback
        if not legendary:
            legendary.append({
                "legendary_type": "None",
                "year": 0,
                "empire_involved": "None",
                "description": "No legendary event occurred during this simulation cycle.",
                "impact_score": 0.0
            })

        out_path = os.path.join(self.datasets_dir, "legendary_events.csv")
        header = ["legendary_type", "year", "empire_involved", "description", "impact_score"]
        write_csv(out_path, legendary, header)
        logger.info(f"Saved legendary events to {out_path}")

    def _generate_timeline_summaries(self, df: pd.DataFrame):
        """Generates summaries at different compression levels: 100, 1000, 10000, 100000, 1000000 years."""
        summaries = []
        max_year = df["year"].max()

        compression_levels = [100, 1000, 10000, 100000, 1000000]
        for scale in compression_levels:
            if max_year < scale / 10:
                continue # Skip scales too large for short simulations

            # Split timeline into chunks of 'scale' size
            start = 0
            while start <= max_year:
                end = start + scale
                chunk = df[(df["year"] >= start) & (df["year"] < end)]
                if not chunk.empty:
                    # Get top 2 events by impact score
                    top_evts = chunk.sort_values(by="impact_score", ascending=False).head(2)
                    evt_summaries = []
                    for _, row in top_evts.iterrows():
                        evt_summaries.append(f"{row['event_type']} (Yr {row['year']}): {row['description'][:60]}...")
                    summary_text = " | ".join(evt_summaries)
                    
                    summaries.append({
                        "compression_scale": f"{scale} Years",
                        "start_year": start,
                        "end_year": end,
                        "summary": summary_text
                    })
                start = end

        # If empty, add default
        if not summaries:
            summaries.append({
                "compression_scale": "100 Years",
                "start_year": 0,
                "end_year": 100,
                "summary": "The dawn of a new galactic era begins."
            })

        out_path = os.path.join(self.datasets_dir, "timeline_summaries.csv")
        header = ["compression_scale", "start_year", "end_year", "summary"]
        write_csv(out_path, summaries, header)
        logger.info(f"Saved timeline summaries to {out_path}")

    def print_summary(self, results: Dict[str, Any]) -> None:
        """Prints the compiled report to the console."""
        print("=" * 80)
        print("                 GALACTIC HISTORICAL ANALYTICS REPORT")
        print("=" * 80)
        
        if not results:
            print("No analytics data compiled.")
            return

        print(f"Most Significant Event : {results['most_significant_event']['event_type']} (Year {results['most_significant_event']['year']})")
        print(f"                         Score: {results['most_significant_event']['impact_score']:.1f}")
        print(f"                         Description: {results['most_significant_event']['description']}")
        print(f"Most Influential Empire: {results['most_influential_empire']['name']} (Influence: {results['most_influential_empire']['total_influence_score']:.1f})")
        print(f"Longest Lasting Empire : {results['longest_lasting_empire']['name']} (Lifespan: {results['longest_lasting_empire']['lifespan_years']} Years)")
        print(f"Most Prosperous Era    : {results['most_prosperous_era']}")
        print(f"Most Violent Era       : {results['most_violent_era']}")
        print("=" * 80)
