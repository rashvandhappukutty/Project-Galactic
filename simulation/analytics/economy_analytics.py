"""
economy_analytics.py — Economic reports, rankings, and superlative compiler.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, Any


class EconomyAnalytics:
    """Compiles macroeconomic rankings and prints the imperial summary reports."""

    def __init__(self, datasets_dir: str = "datasets") -> None:
        self.datasets_dir = datasets_dir
        self.economy_csv = os.path.join(datasets_dir, "economy.csv")
        self.market_csv = os.path.join(datasets_dir, "market_prices.csv")
        self.agreements_csv = os.path.join(datasets_dir, "trade_agreements.csv")
        self.events_csv = os.path.join(datasets_dir, "economic_events.csv")
        self.blocs_csv = os.path.join(datasets_dir, "economic_blocs.csv")
        self.gdp_rankings_csv = os.path.join(datasets_dir, "gdp_rankings.csv")

    def compile_superlatives(self) -> Dict[str, Any]:
        """Compile macroeconomic superlative metrics across empires.

        Returns
        -------
        Dict[str, Any]
            Superlative metrics dictionary.
        """
        econ_df = pd.read_csv(self.economy_csv)
        mkt_df = pd.read_csv(self.market_csv)
        rank_df = pd.read_csv(self.gdp_rankings_csv)
        civ_df = pd.read_csv(os.path.join(self.datasets_dir, "civilization_evolution.csv"))
        
        # Merge names
        name_map = civ_df.set_index("civilization_id")["name"].to_dict()

        # 1. Richest Empire (Treasury)
        final_tick = econ_df["tick"].max()
        final_econ = econ_df[econ_df["tick"] == final_tick]
        richest_row = final_econ.loc[final_econ["treasury"].idxmax()]
        richest_name = name_map.get(richest_row["civilization_id"], richest_row["civilization_id"])
        
        # 2. Largest GDP & Growth
        largest_gdp_row = rank_df.iloc[0]
        
        fastest_growth_row = final_econ.loc[final_econ["gdp_growth"].idxmax()]
        fastest_growth_name = name_map.get(fastest_growth_row["civilization_id"], fastest_growth_row["civilization_id"])

        # 3. Largest Trade Network
        trade_vol_row = final_econ.loc[final_econ["trade_volume"].idxmax()]
        trade_vol_name = name_map.get(trade_vol_row["civilization_id"], trade_vol_row["civilization_id"])

        # 4. Most Valuable Resource (Highest average price in final tick)
        final_mkt = mkt_df[mkt_df["tick"] == final_tick]
        avg_prices = final_mkt.groupby("commodity")["price"].mean()
        most_valuable_commodity = avg_prices.idxmax()
        most_valuable_price = avg_prices.max()

        # 5. Strongest Economic Bloc
        blocs_df = pd.read_csv(self.blocs_csv)
        if not blocs_df.empty:
            final_blocs = blocs_df[blocs_df["tick"] == final_tick]
            strongest_bloc = final_blocs.loc[final_blocs["combined_gdp"].idxmax()]
            strongest_bloc_name = strongest_bloc["bloc_name"]
            strongest_bloc_gdp = strongest_bloc["combined_gdp"]
        else:
            strongest_bloc_name = "None"
            strongest_bloc_gdp = 0.0

        # 6. Most Resource-Rich Empire (based on planet resource_score of homeworld)
        civ_planets = civ_df.merge(pd.read_csv(os.path.join(self.datasets_dir, "planets.csv")), on="planet_id")
        richest_res_row = civ_planets.loc[civ_planets["resource_score"].idxmax()]
        richest_res_name = richest_res_row["name"]
        richest_res_score = richest_res_row["resource_score"]

        return {
            "richest_name": richest_name,
            "richest_treasury": richest_row["treasury"],
            "largest_gdp_name": largest_gdp_row["name"],
            "largest_gdp_value": largest_gdp_row["gdp"],
            "fastest_growth_name": fastest_growth_name,
            "fastest_growth_val": fastest_growth_row["gdp_growth"] * 100.0,
            "trade_vol_name": trade_vol_name,
            "trade_vol_val": trade_vol_row["trade_volume"],
            "commodity_name": most_valuable_commodity,
            "commodity_price": most_valuable_price,
            "bloc_name": strongest_bloc_name,
            "bloc_gdp": strongest_bloc_gdp,
            "res_rich_name": richest_res_name,
            "res_rich_val": richest_res_score
        }

    def print_summary(self) -> None:
        """Format and print the summary report of Phase 7 to console."""
        rank_df = pd.read_csv(self.gdp_rankings_csv)
        econ_df = pd.read_csv(self.economy_csv)
        events_df = pd.read_csv(self.events_csv)
        
        sup = self.compile_superlatives()

        print("\n" + "=" * 80)
        print("          THE GALACTIC DREAM ENGINE - PHASE 7 ECONOMY REPORT")
        print("=" * 80)
        print(f"Total Empires Simulated: {len(rank_df)} | Ticks: {econ_df['tick'].max()}")
        print(f"Economic Events Logged : {len(events_df)}")
        print("-" * 80)
        print("MACROECONOMIC SUPERLATIVES:")
        print(f"  - Largest GDP Empire          : {sup['largest_gdp_name']} ({sup['largest_gdp_value']:.2f} credits)")
        print(f"  - Richest Empire (Treasury)   : {sup['richest_name']} ({sup['richest_treasury']:.2f} credits)")
        print(f"  - Fastest Growing Economy     : {sup['fastest_growth_name']} (+{sup['fastest_growth_val']:.2f}% GDP growth)")
        print(f"  - Largest Interstellar Trader : {sup['trade_vol_name']} (Volume: {sup['trade_vol_val']:.2f} credits)")
        print(f"  - Most Valuable Commodity     : {sup['commodity_name']} (Avg Price: {sup['commodity_price']:.2f} Credits)")
        print(f"  - Strongest Economic Alliance : {sup['bloc_name']} (GDP: {sup['bloc_gdp']:.2f} credits)")
        print(f"  - Most Resource-Rich Capital  : {sup['res_rich_name']} (Homeworld Resource Score: {sup['res_rich_val']:.1f})")
        print("-" * 80)
        print("TOP 20 ECONOMIC POWERS RANKING (BY GDP):")
        print("  Rank | Empire/Civilization Name         | GDP (credits) | Treasury (GC) | Inflation")
        print("  ---------------------------------------------------------------------------")
        
        top_20 = rank_df.head(20)
        for idx, row in top_20.iterrows():
            print(f"  {row['gdp_rank']:4d} | {row['name']:32s} | {row['gdp']:13.2f} | {row['treasury']:13.2f} | {row['inflation_rate']*100:8.2f}%")
        print("=" * 80)
