"""
ftl_analytics.py — FTL rankings, chokepoint statistics, and transit superlatives.
"""

import os
import pandas as pd
from typing import Dict, Any, List


class FtlAnalytics:
    """Compiles transportation superlatives and prints the summary reports."""

    def __init__(self, datasets_dir: str = "datasets") -> None:
        self.datasets_dir = datasets_dir
        self.wormholes_csv = os.path.join(datasets_dir, "wormholes.csv")
        self.hyperlanes_csv = os.path.join(datasets_dir, "hyperlane_network.csv")
        self.gates_csv = os.path.join(datasets_dir, "jump_gates.csv")
        self.routes_csv = os.path.join(datasets_dir, "ftl_routes.csv")
        self.strategic_csv = os.path.join(datasets_dir, "strategic_systems.csv")
        self.events_csv = os.path.join(datasets_dir, "transport_events.csv")

    def compile_superlatives(self) -> Dict[str, Any]:
        """Compile transportation metrics across empires and networks.

        Returns
        -------
        Dict[str, Any]
            Superlative metrics dictionary.
        """
        w_df = pd.read_csv(self.wormholes_csv)
        l_df = pd.read_csv(self.hyperlanes_csv)
        g_df = pd.read_csv(self.gates_csv)
        r_df = pd.read_csv(self.routes_csv)
        s_df = pd.read_csv(self.strategic_csv)
        
        civ_df = pd.read_csv(os.path.join(self.datasets_dir, "civilization_evolution.csv"))
        name_map = civ_df.set_index("civilization_id")["name"].to_dict()

        # 1. Most Connected Empire
        # We look at the empire with the lowest average FTL travel time
        fastest_path = r_df.groupby("empire_id")["travel_time_years"].mean()
        most_connected_cid = fastest_path.idxmin() if not fastest_path.empty else "None"
        most_connected_name = name_map.get(most_connected_cid, most_connected_cid)
        avg_travel_time = fastest_path.min() if not fastest_path.empty else 0.0

        # 2. Most Strategic System
        most_strat_row = s_df.iloc[0] if not s_df.empty else {"star_name": "None", "strategic_value_score": 0.0}

        # 3. Largest Transit Hub (Star with highest neighbors_count)
        most_neighbors_row = s_df.loc[s_df["neighbors_count"].idxmax()] if not s_df.empty else {"star_name": "None", "neighbors_count": 0}

        # 4. Fastest Trade Route (lowest travel_time_years where source != target)
        inter_routes = r_df[r_df["route_type"] == "Trade Route"]
        fastest_route_row = inter_routes.loc[inter_routes["travel_time_years"].idxmin()] if not inter_routes.empty else {"source_star_name": "None", "target_star_name": "None", "travel_time_years": 0.0}

        # 5. Most Valuable Wormhole (highest distance_reduction)
        most_val_w = w_df.loc[w_df["distance_reduction"].idxmax()] if not w_df.empty else {"wormhole_id": "None", "distance_reduction": 0.0}

        # 6. Largest Gate Network (Owner with the most jump gates)
        gate_counts = g_df.groupby("owner_empire")["gate_id"].count()
        largest_gate_cid = gate_counts.idxmax() if not gate_counts.empty else "None"
        largest_gate_name = name_map.get(largest_gate_cid, largest_gate_cid)
        num_gates = gate_counts.max() if not gate_counts.empty else 0

        # 7. Largest Wormhole Owner (Empire owning most artificial wormholes)
        w_counts = w_df[w_df["owner_empire"] != "None"].groupby("owner_empire")["wormhole_id"].count()
        largest_w_cid = w_counts.idxmax() if not w_counts.empty else "None"
        largest_w_name = name_map.get(largest_w_cid, largest_w_cid)
        num_w = w_counts.max() if not w_counts.empty else 0

        return {
            "most_connected_name": most_connected_name,
            "avg_travel_time": avg_travel_time,
            "most_strat_name": most_strat_row["star_name"],
            "most_strat_score": most_strat_row["strategic_value_score"],
            "hub_name": most_neighbors_row["star_name"],
            "hub_neighbors": most_neighbors_row["neighbors_count"],
            "fastest_trade_src": fastest_route_row.get("source_star_name", "None"),
            "fastest_trade_tgt": fastest_route_row.get("target_star_name", "None"),
            "fastest_trade_time": fastest_route_row["travel_time_years"],
            "w_id": most_val_w["wormhole_id"],
            "w_saved": most_val_w["distance_reduction"],
            "gate_owner_name": largest_gate_name,
            "gate_count": num_gates,
            "w_owner_name": largest_w_name,
            "w_owner_count": num_w
        }

    def print_summary(self) -> None:
        """Format and print the summary report of Phase 8 to console."""
        w_df = pd.read_csv(self.wormholes_csv)
        l_df = pd.read_csv(self.hyperlanes_csv)
        g_df = pd.read_csv(self.gates_csv)
        s_df = pd.read_csv(self.strategic_csv)
        r_df = pd.read_csv(self.routes_csv)
        events_df = pd.read_csv(self.events_csv)
        
        sup = self.compile_superlatives()

        print("\n" + "=" * 80)
        print("          THE GALACTIC DREAM ENGINE - PHASE 8 TRANSIT REPORT")
        print("=" * 80)
        print(f"Hyperlanes in Network: {len(l_df)} | Active Gateways: {len(g_df)}")
        print(f"Stable Wormholes     : {len(w_df)} | FTL Transit Events: {len(events_df)}")
        print("-" * 80)
        print("TRANSPORTATION SUPERLATIVES:")
        print(f"  - Fastest Travel Network      : {sup['most_connected_name']} (Avg Travel: {sup['avg_travel_time']:.2f} years)")
        print(f"  - Most Strategic Chokepoint   : {sup['most_strat_name']} (Strategic Score: {sup['most_strat_score']:.1f}/100)")
        print(f"  - Largest Transit Hub System  : {sup['hub_name']} ({sup['hub_neighbors']} connected systems)")
        print(f"  - Fastest Interstellar Trade  : {sup['fastest_trade_src']} ↔ {sup['fastest_trade_tgt']} ({sup['fastest_trade_time']:.2f} years)")
        print(f"  - Most Valuable Wormhole      : {sup['w_id']} (distance reduction: {sup['w_saved']:.1f} light-years)")
        print(f"  - Largest Gateway Network     : {sup['gate_owner_name']} ({sup['gate_count']} jump gates built)")
        print(f"  - Artificial Wormhole Owner   : {sup['w_owner_name']} ({sup['w_owner_count']} portals constructed)")
        print("-" * 80)
        print("TOP 20 TRANSPORTATION POWERS RANKING (BY CONNECTIVITY INDEX):")
        print("  Rank | Empire/Civilization Name         | Capital Star        | Gates | Travel Index")
        print("  ---------------------------------------------------------------------------")
        
        # Sort and display top 20 empires based on their travel times (lowest is best)
        civ_df = pd.read_csv(os.path.join(self.datasets_dir, "civilization_evolution.csv"))
        name_map = civ_df.set_index("civilization_id")["name"].to_dict()
        
        final_routes = r_df.groupby(["empire_id", "source_star_name"])["travel_time_years"].mean().reset_index()
        final_routes = final_routes.sort_values(by="travel_time_years").reset_index(drop=True)
        final_routes.index += 1
        
        # Build gateway count per owner
        gate_counts = g_df.groupby("owner_empire")["gate_id"].count().to_dict()

        top_20 = final_routes.head(20)
        for idx, row in top_20.iterrows():
            cid = str(row["empire_id"])
            emp_name = name_map.get(cid, cid)
            gates_built = gate_counts.get(cid, 0)
            
            # Connectivity index proxy
            conn_idx = 100.0 / (row["travel_time_years"] + 1.0)
            print(f"  {idx:4d} | {emp_name:32s} | {row['source_star_name']:18s} | {gates_built:5d} | {conn_idx:11.2f}")
        print("=" * 80)
