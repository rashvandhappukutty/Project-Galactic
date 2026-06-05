"""
civilization_analytics.py — CivilizationAnalytics class for the Galactic Dream Engine.

Phase 4: Civilization Evolution Engine.
Processes final catalogs to evaluate the fastest growing, largest, and most advanced galactic powers.
"""

from __future__ import annotations

import os
import math
from typing import Any, Dict, List
import numpy as np
import pandas as pd


class CivilizationAnalytics:
    """
    Analytics engine to summarize and grade evolved civilization records.

    Parameters
    ----------
    civs_csv : str
        Path to civilization_evolution.csv.
    tech_csv : str
        Path to technology_progress.csv.
    events_csv : str
        Path to civilization_events.csv.
    """

    def __init__(self, civs_csv: str, tech_csv: str, events_csv: str) -> None:
        self.civs_csv = civs_csv
        self.tech_csv = tech_csv
        self.events_csv = events_csv

    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Read final catalogs and compute galactic power summaries.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing key metrics and top lists.
        """
        metrics: Dict[str, Any] = {
            "total_active_civilizations": 0,
            "extinct_civilizations": 0,
            "fastest_growing": {},
            "largest": {},
            "most_advanced": {},
            "most_stable": {},
            "highest_kardashev": {},
            "top_galactic_powers": []
        }

        if not os.path.exists(self.civs_csv):
            return metrics

        civs_df = pd.read_csv(self.civs_csv)
        if civs_df.empty:
            return metrics

        # Parse tech progress to find initial population at year 0
        initial_pop_map = {}
        if os.path.exists(self.tech_csv):
            tech_df = pd.read_csv(self.tech_csv)
            if not tech_df.empty:
                init_df = tech_df[tech_df["year"] == 0]
                for _, row in init_df.iterrows():
                    initial_pop_map[row["civilization_id"]] = float(row["population"])

        # Basic Stats
        active_df = civs_df[civs_df["population"] > 0]
        extinct_df = civs_df[civs_df["population"] <= 0]
        
        metrics["total_active_civilizations"] = len(active_df)
        metrics["extinct_civilizations"] = len(extinct_df)

        if civs_df.empty:
            return metrics

        # Largest Civilization
        largest_row = civs_df.loc[civs_df["population"].idxmax()]
        metrics["largest"] = {
            "civilization_id": largest_row.get("civilization_id", "unknown"),
            "name": largest_row.get("name", "unknown"),
            "population": float(largest_row["population"]),
            "tech_level": float(largest_row["tech_level"]),
            "government": largest_row.get("government_type", "unknown")
        }

        # Most Advanced
        advanced_row = civs_df.loc[civs_df["tech_level"].idxmax()]
        metrics["most_advanced"] = {
            "civilization_id": advanced_row.get("civilization_id", "unknown"),
            "name": advanced_row.get("name", "unknown"),
            "population": float(advanced_row["population"]),
            "tech_level": float(advanced_row["tech_level"]),
            "stage": advanced_row.get("tech_stage_name", "unknown")
        }

        # Most Stable
        stable_row = civs_df.loc[civs_df["stability_score"].idxmax()]
        metrics["most_stable"] = {
            "civilization_id": stable_row.get("civilization_id", "unknown"),
            "name": stable_row.get("name", "unknown"),
            "stability_score": float(stable_row["stability_score"]),
            "government": stable_row.get("government_type", "unknown")
        }
        metrics["most_stable_government"] = metrics["most_stable"]

        # Highest Kardashev
        kardashev_row = civs_df.loc[civs_df["kardashev_rating"].idxmax()]
        metrics["highest_kardashev"] = {
            "civilization_id": kardashev_row.get("civilization_id", "unknown"),
            "name": kardashev_row.get("name", "unknown"),
            "rating": float(kardashev_row["kardashev_rating"]),
            "kardashev_rating": float(kardashev_row["kardashev_rating"]),
            "energy_source": kardashev_row.get("energy_source", "unknown")
        }

        # Fastest Growing (highest ratio: final population / initial population)
        fastest_growth_ratio = -1.0
        fastest_civ = {}
        for _, row in civs_df.iterrows():
            cid = row["civilization_id"]
            if "initial_population" in row:
                init_pop = float(row["initial_population"])
            else:
                init_pop = initial_pop_map.get(cid, 1e9)
            final_pop = float(row["population"])
            if init_pop > 0:
                ratio = (final_pop - init_pop) / init_pop
                if ratio > fastest_growth_ratio:
                    fastest_growth_ratio = ratio
                    fastest_civ = {
                        "civilization_id": cid,
                        "name": row.get("name", cid),
                        "growth_ratio": ratio,
                        "final_population": final_pop,
                        "initial_population": init_pop
                    }
        metrics["fastest_growing"] = fastest_civ

        # Top 20 Galactic Powers
        # Power Index = tech_level * 0.4 + log10(population) * 0.3 + kardashev_rating * 0.3
        power_records = []
        for _, row in civs_df.iterrows():
            pop = float(row["population"])
            tech = float(row["tech_level"])
            kardashev = float(row["kardashev_rating"])
            
            log_pop = math.log10(pop) if pop > 0 else 0.0
            power_index = tech * 0.4 + log_pop * 0.3 + kardashev * 0.3
            
            power_records.append({
                "civilization_id": row["civilization_id"],
                "name": row.get("name", row["civilization_id"]),
                "population": pop,
                "tech_level": tech,
                "kardashev_rating": kardashev,
                "government_type": row.get("government_type", "unknown"),
                "power_index": power_index
            })

        power_df = pd.DataFrame(power_records)
        if not power_df.empty:
            top_20 = power_df.sort_values(by="power_index", ascending=False).head(20)
            metrics["top_galactic_powers"] = top_20.to_dict(orient="records")
            metrics["top_20_powers"] = metrics["top_galactic_powers"]

        return metrics

    def print_summary(self) -> None:
        """
        Format and print the metrics cleanly to the console.
        """
        metrics = self.calculate_metrics()
        
        print("\n" + "=" * 60)
        print("           CIVILIZATION EVOLUTION SUMMARY REPORT")
        print("=" * 60)
        print(f"Total Active Civilizations : {metrics['total_active_civilizations']}")
        print(f"Extinct Civilizations      : {metrics['extinct_civilizations']}")
        print("-" * 60)

        # Fastest Growing
        fg = metrics["fastest_growing"]
        if fg:
            print("FASTEST GROWING CIVILIZATION:")
            print(f"  Name: {fg['name']}")
            print(f"  Growth Factor: {fg['growth_ratio']:.2f}x")
            print(f"  Initial Pop: {fg['initial_population']:,.0f} -> Final Pop: {fg['final_population']:,.0f}")
            print("-" * 60)

        # Largest
        lg = metrics["largest"]
        if lg:
            print("LARGEST GALACTIC EMPIRE:")
            print(f"  Name: {lg['name']}")
            print(f"  Population: {lg['population']:,.0f}")
            print(f"  Government: {lg['government']} | Tech Level: {lg['tech_level']:.2f}")
            print("-" * 60)

        # Most Advanced
        ma = metrics["most_advanced"]
        if ma:
            print("MOST ADVANCED CIVILIZATION:")
            print(f"  Name: {ma['name']}")
            print(f"  Tech Level: {ma['tech_level']:.2f} ({ma['stage']})")
            print(f"  Population: {ma['population']:,.0f}")
            print("-" * 60)

        # Highest Energy regime
        hk = metrics["highest_kardashev"]
        if hk:
            print("HIGHEST ENERGY REGIME (KARDASHEV SCALE):")
            print(f"  Name: {hk['name']}")
            print(f"  Rating: Type {hk['rating']:.3f}")
            print(f"  Regime: {hk['energy_source']}")
            print("-" * 60)

        # Top 20 Galactic Powers Table
        top_powers = metrics["top_galactic_powers"]
        if top_powers:
            print("TOP 20 GALACTIC POWERS RANKING (BY POWER INDEX):")
            print(f"  {'Rank':<4} | {'Civilization Name':<22} | {'Gov Type':<13} | {'Tech':<5} | {'Kardashev':<9} | {'Power Index':<11}")
            print("  " + "-" * 73)
            for idx, civ in enumerate(top_powers, 1):
                name = civ["name"]
                gov = civ["government_type"]
                tech = civ["tech_level"]
                kard = civ["kardashev_rating"]
                index = civ["power_index"]
                # truncate name if too long
                if len(name) > 22:
                    name = name[:19] + "..."
                print(f"  {idx:<4d} | {name:<22} | {gov:<13} | {tech:<5.2f} | {kard:<9.3f} | {index:<11.3f}")
        else:
            print("  No galactic power rankings available.")
            
        print("=" * 60 + "\n")
