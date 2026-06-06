"""
warfare_analytics.py — Compiles conflict superlatives, espionage ranks, alliance stats, and the Top 20 Galactic Superpowers.
"""

import os
from typing import Dict, List, Any
import pandas as pd
import numpy as np


class WarfareAnalytics:
    """Processes Phase 9 CSV databases to compile geopolitical superlatives and superpower power indexes."""

    def __init__(self, datasets_dir: str = "datasets") -> None:
        self.datasets_dir = datasets_dir

    def print_summary(self) -> None:
        """Calculate and display the geopolitical transit, military, and espionage reports."""
        print("\n" + "=" * 80)
        print("          THE GALACTIC DREAM ENGINE - PHASE 9 GEOPOLITICAL REPORT")
        print("=" * 80)

        # Load tables
        relations_df = self._load_csv("diplomatic_relations.csv")
        alliances_df = self._load_csv("alliances.csv")
        espionage_df = self._load_csv("espionage_operations.csv")
        fleets_df = self._load_csv("fleets.csv")
        wars_df = self._load_csv("wars.csv")
        battles_df = self._load_csv("battles.csv")
        conquests_df = self._load_csv("conquests.csv")
        peace_df = self._load_csv("peace_treaties.csv")
        empires_df = self._load_csv("empires.csv")

        # Counts
        active_fleets = fleets_df[fleets_df["status"] != "Destroyed"] if not fleets_df.empty else pd.DataFrame()
        num_fleets = len(active_fleets)
        num_alliances = len(alliances_df) if not alliances_df.empty else 0
        num_wars = len(wars_df) if not wars_df.empty else 0
        num_battles = len(battles_df) if not battles_df.empty else 0
        num_conquests = len(conquests_df) if not conquests_df.empty else 0

        print(f"Bilateral Relations : {len(relations_df) if not relations_df.empty else 0} | Active Alliances: {num_alliances}")
        print(f"Space Fleets Active : {num_fleets} | Simulated Battles: {num_battles}")
        print(f"Conflicts Triggered : {num_wars} | Conquest Operations: {num_conquests}")
        print("-" * 80)

        # 1. Superlatives
        # Most Powerful Military
        mil_pow = "None"
        if not active_fleets.empty:
            mil_grp = active_fleets.groupby("owner_empire_id")["fleet_power"].sum()
            if not mil_grp.empty:
                strongest_id = mil_grp.idxmax()
                mil_pow = self._resolve_name(strongest_id, empires_df)

        # Strongest Alliance
        strongest_alliance = "None"
        if not alliances_df.empty:
            idx = alliances_df["combined_fleet_power"].astype(float).idxmax()
            strongest_alliance = f"{alliances_df.at[idx, 'alliance_name']} (power: {alliances_df.at[idx, 'combined_fleet_power']})"

        # Best spy network
        best_spy = "None"
        if not espionage_df.empty:
            succ = espionage_df[espionage_df["success"] == True]
            if not succ.empty:
                spy_grp = succ.groupby("attacker_id")["operation_id"].count()
                if not spy_grp.empty:
                    best_spy_id = spy_grp.idxmax()
                    best_spy = f"{self._resolve_name(best_spy_id, empires_df)} ({spy_grp.max()} operations)"

        # Largest fleet
        largest_fleet = "None"
        if not active_fleets.empty:
            idx = active_fleets["fleet_power"].astype(float).idxmax()
            largest_fleet = f"{active_fleets.at[idx, 'fleet_name']} (power: {active_fleets.at[idx, 'fleet_power']:.1f})"

        # Longest war
        longest_war = "None"
        if not wars_df.empty:
            concluded = wars_df[wars_df["status"] == "Concluded"]
            if not concluded.empty:
                durations = concluded["end_year"].astype(float) - concluded["start_year"].astype(float)
                if not durations.empty:
                    longest_idx = durations.idxmax()
                    longest_war = f"{concluded.at[longest_idx, 'cause']} ({durations.max():.1f} years)"

        # Most conquered empire
        most_conquered = "None"
        if not conquests_df.empty:
            loss_grp = conquests_df.groupby("defender_id")["conquest_id"].count()
            if not loss_grp.empty:
                most_conquered_id = loss_grp.idxmax()
                most_conquered = f"{self._resolve_name(most_conquered_id, empires_df)} ({loss_grp.max()} systems/colonies lost)"

        # Most influential diplomatic power
        influential = "None"
        if not relations_df.empty:
            avg_rel = relations_df.groupby("empire_a")["relation_score"].mean()
            if not avg_rel.empty:
                inf_id = avg_rel.idxmax()
                influential = f"{self._resolve_name(inf_id, empires_df)} (Avg relation: +{avg_rel.max():.1f})"

        print("GEOPOLITICAL SUPERLATIVES:")
        print(f"  - Most Powerful Military      : {mil_pow}")
        print(f"  - Strongest Alliance Coalition: {strongest_alliance}")
        print(f"  - Most Effective Spy Network  : {best_spy}")
        print(f"  - Largest Space Fleet Force   : {largest_fleet}")
        print(f"  - Longest Interstellar War    : {longest_war}")
        print(f"  - Most Target-Conquered Empire: {most_conquered}")
        print(f"  - Most Friendly Diplomat State: {influential}")
        print("-" * 80)

        # 2. Superpowers Ranking
        print("TOP 20 GALACTIC SUPERPOWERS POWER RANKING (BY POWER INDEX):")
        print("  Rank | Empire/Civilization Name         | Capital Star        | Fleets | Power Index")
        print("  ---------------------------------------------------------------------------")

        if not empires_df.empty:
            # Build stats
            empire_fleet_pow = {}
            empire_fleet_count = {}
            if not active_fleets.empty:
                empire_fleet_pow = active_fleets.groupby("owner_empire_id")["fleet_power"].sum().to_dict()
                empire_fleet_count = active_fleets.groupby("owner_empire_id")["fleet_id"].count().to_dict()

            superpower_records = []
            for _, row in empires_df.iterrows():
                cid = str(row["founding_civilization_id"])
                
                # Fetch economics
                gdp = float(row.get("gdp", 1000.0))
                pop = float(row.get("population", 1e9))
                
                fleet_pow = empire_fleet_pow.get(cid, 0.0)
                num_flt = empire_fleet_count.get(cid, 0)

                # Power Index Formula: GDP * 0.4 + Population * 0.2 + Fleet Power * 0.4
                # We normalize population log-wise to avoid skewing
                pop_log = np.log10(max(1.0, pop))
                gdp_log = np.log10(max(1.0, gdp))
                power_index = (gdp_log * 40.0) + (pop_log * 20.0) + (np.log10(max(1.0, fleet_pow)) * 40.0)

                # Resolve capital star name
                cap_world = str(row.get("capital_world", "Core Star"))

                superpower_records.append({
                    "cid": cid,
                    "name": str(row["empire_name"]),
                    "capital": cap_world,
                    "fleets": num_flt,
                    "power_index": power_index
                })

            superpower_records.sort(key=lambda x: x["power_index"], reverse=True)

            for idx, r in enumerate(superpower_records[:20], 1):
                print(f"    {idx:2d} | {r['name']:32.32s} | {r['capital']:20.20s} | {r['fleets']:6d} | {r['power_index']:11.2f}")
        
        print("=" * 80)

    def _load_csv(self, filename: str) -> pd.DataFrame:
        path = os.path.join(self.datasets_dir, filename)
        if os.path.exists(path):
            return pd.read_csv(path)
        return pd.DataFrame()

    def _resolve_name(self, empire_id: str, empires_df: pd.DataFrame) -> str:
        if not empires_df.empty:
            match = empires_df[empires_df["founding_civilization_id"] == empire_id]
            if not match.empty:
                return str(match.iloc[0]["empire_name"])
        return empire_id
