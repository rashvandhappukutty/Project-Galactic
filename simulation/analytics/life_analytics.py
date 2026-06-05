"""
life_analytics.py - Analytics engine for Phase 3: Life Emergence Engine.

Computes overall metrics, classifies life-bearing worlds, and extracts top entries
for habitability and technology levels.
"""

from __future__ import annotations

import os
from typing import Any, Dict, List
import pandas as pd


class LifeAnalytics:
    """
    Analytics engine to evaluate and summarize life, species, and civilization catalogs.

    Parameters
    ----------
    life_catalog_csv : str
        Path to the CSV catalog of planetary life states.
    species_catalog_csv : str
        Path to the CSV catalog of emerged sentient species.
    civilizations_csv : str
        Path to the CSV catalog of generated civilizations.
    """

    def __init__(
        self,
        life_catalog_csv: str,
        species_catalog_csv: str,
        civilizations_csv: str,
    ) -> None:
        self.life_catalog_csv = life_catalog_csv
        self.species_catalog_csv = species_catalog_csv
        self.civilizations_csv = civilizations_csv

    def calculate_metrics(self) -> Dict[str, Any]:
        """
        Read the catalogs and compute summary statistics.

        Returns
        -------
        Dict[str, Any]
            A dictionary containing key metrics:
            - "total_life_bearing_planets" : int
            - "microbial_worlds" : int
            - "simple_multicellular" : int
            - "complex_ecosystems" : int
            - "intelligent_worlds" : int
            - "civilizations_generated" : int
            - "most_habitable_worlds_with_life" : List[Dict[str, Any]]
            - "most_advanced_civilizations" : List[Dict[str, Any]]

        Raises
        ------
        FileNotFoundError
            If any of the critical CSV files cannot be found and no fallback is possible.
        KeyError
            If critical columns are missing from the files.
        """
        # Load Life Catalog
        if not os.path.exists(self.life_catalog_csv):
            raise FileNotFoundError(f"Life catalog not found at {self.life_catalog_csv}")
        life_df = pd.read_csv(self.life_catalog_csv)

        # Check if basic columns are present
        if "life_stage" not in life_df.columns:
            raise KeyError("Critical column 'life_stage' not found in life catalog.")

        # Ensure we have habitability_score and planet_name in life_df
        # If they are not in the life catalog, try to find planets.csv to merge
        required_cols = {"habitability_score", "planet_name"}
        missing_cols = required_cols - set(life_df.columns)
        if missing_cols:
            planets_csv_path = None
            dir_name = os.path.dirname(self.life_catalog_csv)
            candidate_1 = os.path.join(dir_name, "planets.csv")
            if os.path.exists(candidate_1):
                planets_csv_path = candidate_1
            else:
                candidate_2 = os.path.join("datasets", "planets.csv")
                if os.path.exists(candidate_2):
                    planets_csv_path = candidate_2

            if planets_csv_path:
                planets_df = pd.read_csv(planets_csv_path)
                cols_to_merge = ["planet_id"] + [col for col in missing_cols if col in planets_df.columns]
                if len(cols_to_merge) > 1 and "planet_id" in life_df.columns:
                    life_df = life_df.merge(planets_df[cols_to_merge], on="planet_id", how="left")

        # Re-check columns after potential merge
        if "habitability_score" not in life_df.columns:
            # If still missing, we will default habitability_score to 0 or raise error if needed
            life_df["habitability_score"] = 0.0
        if "planet_name" not in life_df.columns:
            life_df["planet_name"] = life_df["planet_id"].astype(str)

        # Compute Life Stage metrics
        total_life_bearing = int((life_df["life_stage"] >= 1).sum())
        microbial = int((life_df["life_stage"] == 1).sum())
        simple = int((life_df["life_stage"] == 2).sum())
        complex_eco = int((life_df["life_stage"] == 3).sum())
        intelligent = int((life_df["life_stage"] == 4).sum())

        # Compute Civilizations count
        civilizations_generated = 0
        if os.path.exists(self.civilizations_csv) and os.path.getsize(self.civilizations_csv) > 0:
            try:
                civs_df = pd.read_csv(self.civilizations_csv)
                civilizations_generated = len(civs_df)
            except Exception:
                civilizations_generated = int((life_df["life_stage"] == 5).sum())
        else:
            civilizations_generated = int((life_df["life_stage"] == 5).sum())

        # Top 10 most habitable worlds with life (Stage >= 1)
        life_bearing_df = life_df[life_df["life_stage"] >= 1]
        top_habitable = (
            life_bearing_df.sort_values(by="habitability_score", ascending=False)
            .head(10)
        )
        # Convert NaN values safely for JSON/Dict compatibility
        top_habitable = top_habitable.fillna({
            "habitability_score": 0.0,
            "life_probability": 0.0,
            "planet_type": "Unknown"
        })
        most_habitable_list = top_habitable.to_dict(orient="records")

        # Top 10 most advanced civilizations
        most_advanced_list: List[Dict[str, Any]] = []
        if os.path.exists(self.civilizations_csv) and os.path.getsize(self.civilizations_csv) > 0:
            try:
                civs_df = pd.read_csv(self.civilizations_csv)
                if not civs_df.empty:
                    # Find tech column name
                    tech_col = None
                    if "technology_level" in civs_df.columns:
                        tech_col = "technology_level"
                    elif "tech_level" in civs_df.columns:
                        tech_col = "tech_level"

                    if tech_col:
                        # Ensure both technology_level and tech_level are in the returned dictionaries
                        top_civs = civs_df.sort_values(by=tech_col, ascending=False).head(10)
                        top_civs = top_civs.fillna({
                            tech_col: 0.0,
                            "civilization_age": 0.0,
                            "government_type": "Unknown",
                            "energy_source": "Unknown"
                        })
                        for _, row in top_civs.iterrows():
                            row_dict = row.to_dict()
                            # Standardize tech keys
                            val = row_dict[tech_col]
                            row_dict["technology_level"] = val
                            row_dict["tech_level"] = val
                            most_advanced_list.append(row_dict)
            except Exception:
                pass

        return {
            "total_life_bearing_planets": total_life_bearing,
            "microbial_worlds": microbial,
            "simple_multicellular": simple,
            "complex_ecosystems": complex_eco,
            "intelligent_worlds": intelligent,
            "civilizations_generated": civilizations_generated,
            "most_habitable_worlds_with_life": most_habitable_list,
            "most_advanced_civilizations": most_advanced_list,
        }

    def print_summary(self) -> None:
        """
        Format and print the metrics cleanly to the console.
        """
        try:
            metrics = self.calculate_metrics()
        except Exception as e:
            print(f"Error calculating analytics metrics: {e}")
            return

        print("\n" + "=" * 60)
        print("          THE GALACTIC DREAM ENGINE - LIFE SUMMARY")
        print("=" * 60)
        print(f"Total Life-Bearing Planets : {metrics['total_life_bearing_planets']}")
        print(f"  - Microbial Worlds       : {metrics['microbial_worlds']}")
        print(f"  - Simple Multicellular   : {metrics['simple_multicellular']}")
        print(f"  - Complex Ecosystems     : {metrics['complex_ecosystems']}")
        print(f"  - Intelligent Worlds     : {metrics['intelligent_worlds']}")
        print(f"Civilizations Generated    : {metrics['civilizations_generated']}")
        print("-" * 60)

        # Top Habitable Worlds with Life
        print("\nTOP 10 MOST HABITABLE WORLDS WITH LIFE:")
        top_hab = metrics["most_habitable_worlds_with_life"]
        if top_hab:
            print(f"  {'Planet Name':<20} | {'Type':<12} | {'Hab. Score':<10} | {'Stage':<6} | {'Life Prob.':<10}")
            print("  " + "-" * 67)
            for idx, p in enumerate(top_hab, 1):
                name = p.get("planet_name", p.get("planet_id", "Unknown"))
                ptype = p.get("planet_type", "Unknown")
                score = p.get("habitability_score", 0.0)
                stage = p.get("life_stage", 0)
                prob = p.get("life_probability", 0.0)
                print(f"  {name:<20} | {ptype:<12} | {score:<10.1f} | {stage:<6d} | {prob:9.1f}%")
        else:
            print("  No life-bearing worlds detected in the catalog.")

        # Top Advanced Civilizations
        print("\nTOP 10 MOST ADVANCED CIVILIZATIONS:")
        top_civ = metrics["most_advanced_civilizations"]
        if top_civ:
            print(f"  {'Civilization Name':<20} | {'Gov Type':<12} | {'Energy Source':<15} | {'Tech Level':<10}")
            print("  " + "-" * 67)
            for idx, c in enumerate(top_civ, 1):
                name = c.get("name", c.get("civilization_id", "Unknown"))
                gov = c.get("government_type", "Unknown")
                energy = c.get("energy_source", "Unknown")
                tech = c.get("technology_level", 0.0)
                print(f"  {name:<20} | {gov:<12} | {energy:<15} | {tech:<10.1f}")
        else:
            print("  No active civilizations detected in the catalog.")
        print("=" * 60 + "\n")
