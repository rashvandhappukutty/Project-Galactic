"""
colonization_analytics.py — Computes post-simulation rankings for Phase 6.
"""

import pandas as pd
from typing import Dict, Any, List


class ColonizationAnalytics:
    """Calculates and prints out strategic analytics for galactic colonization and empires."""

    def __init__(
        self,
        colonies_csv: str,
        empires_csv: str,
        territories_csv: str,
        routes_csv: str,
        events_csv: str,
    ) -> None:
        self.colonies_df = pd.read_csv(colonies_csv)
        self.empires_df = pd.read_csv(empires_csv)
        self.territories_df = pd.read_csv(territories_csv)
        self.routes_df = pd.read_csv(routes_csv)
        self.events_df = pd.read_csv(events_csv)

    def calculate_metrics(self) -> Dict[str, Any]:
        """Compute top ranking empires and routes."""
        metrics = {}

        # 1. Largest Empire (By Population)
        if not self.empires_df.empty:
            largest_pop_row = self.empires_df.loc[self.empires_df["population"].idxmax()]
            metrics["largest_empire_pop"] = (largest_pop_row["empire_name"], float(largest_pop_row["population"]))
            
            # By Territory Size
            largest_terr_row = self.empires_df.loc[self.empires_df["territory_size_ly3"].idxmax()]
            metrics["largest_empire_terr"] = (largest_terr_row["empire_name"], float(largest_terr_row["territory_size_ly3"]))
        else:
            metrics["largest_empire_pop"] = ("None", 0.0)
            metrics["largest_empire_terr"] = ("None", 0.0)

        # 2. Most Colonized Civilization (Highest colony count)
        if not self.empires_df.empty:
            most_col_row = self.empires_df.loc[self.empires_df["colonies_count"].idxmax()]
            metrics["most_colonized"] = (most_col_row["founding_civilization"], int(most_col_row["colonies_count"]))
        else:
            metrics["most_colonized"] = ("None", 0)

        # 3. Most Valuable Trade Route
        if not self.routes_df.empty:
            trade_routes = self.routes_df[self.routes_df["route_type"] == "Trade Route"]
            if not trade_routes.empty:
                max_val_row = trade_routes.loc[trade_routes["economic_value"].idxmax()]
                route_desc = f"{max_val_row['source_star_name']} ↔ {max_val_row['target_star_name']}"
                metrics["most_valuable_route"] = (route_desc, float(max_val_row["economic_value"]))
            else:
                metrics["most_valuable_route"] = ("None", 0.0)
        else:
            metrics["most_valuable_route"] = ("None", 0.0)

        # 4. Fastest Expansion Rate
        # Estimated as maximum colony count in 1000 years (since simulation age is 10 ticks = 1000 years)
        if not self.empires_df.empty:
            fastest_row = self.empires_df.loc[self.empires_df["colonies_count"].idxmax()]
            rate = fastest_row["colonies_count"] / 10.0  # colonies per century
            metrics["fastest_expansion"] = (fastest_row["empire_name"], rate)
        else:
            metrics["fastest_expansion"] = ("None", 0.0)

        # 5. Top 20 Galactic Empires sorted by Power Index
        if not self.empires_df.empty:
            top_20 = self.empires_df.sort_values(by="power_index", ascending=False).head(20).to_dict(orient="records")
        else:
            top_20 = []
        metrics["top_20_empires"] = top_20

        return metrics

    def print_summary(self) -> None:
        """Print formatted imperial analytics summary."""
        metrics = self.calculate_metrics()

        print("\n" + "=" * 80)
        print("          THE GALACTIC DREAM ENGINE - PHASE 6 COLONIZATION REPORT")
        print("=" * 80)

        total_colonies = len(self.colonies_df)
        total_empires = len(self.empires_df)
        total_routes = len(self.routes_df)
        total_events = len(self.events_df)

        print(f"Total Colonies: {total_colonies:4d} | Active Empires: {total_empires:3d} | Interstellar Routes: {total_routes:4d} | Events: {total_events:4d}")
        print("-" * 80)

        print("IMPERIAL SUPERLATIVES:")
        lep_name, lep_val = metrics["largest_empire_pop"]
        print(f"  - Largest Empire (Population) : {lep_name} ({lep_val:,.0f} citizens)")

        let_name, let_val = metrics["largest_empire_terr"]
        print(f"  - Largest Empire (Territory)  : {let_name} ({let_val:,.1f} cubic light-years)")

        mc_name, mc_val = metrics["most_colonized"]
        print(f"  - Most Colonized Civilization : {mc_name} ({mc_val} outposts established)")

        mvr_name, mvr_val = metrics["most_valuable_route"]
        print(f"  - Most Valuable Trade Route   : {mvr_name} (economic value: {mvr_val:.1f} credits)")

        fe_name, fe_val = metrics["fastest_expansion"]
        print(f"  - Fastest Expansionist Power   : {fe_name} ({fe_val:.2f} colonies established per century)")

        print("-" * 80)
        print("TOP 20 GALACTIC EMPIRES RANKING (BY POWER INDEX):")
        print(f"  {'Rank':4s} | {'Empire Designation':32s} | {'Capital':18s} | {'Colonies':8s} | {'Power Index':12s}")
        print("  " + "-" * 76)

        for rank, emp in enumerate(metrics["top_20_empires"], 1):
            name_truncated = emp["empire_name"][:32]
            print(f"  {rank:<4d} | {name_truncated:32s} | {emp['capital_world'][:18]:18s} | {emp['colonies_count']:<8d} | {emp['power_index']:<12.2f}")

        print("=" * 80 + "\n")
