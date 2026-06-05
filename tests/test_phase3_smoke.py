"""
test_phase3_smoke.py - Smoke tests for Phase 3 analytics and visualization.
"""

from __future__ import annotations

import os
import shutil
import unittest
import pandas as pd
import numpy as np

from simulation.analytics.life_analytics import LifeAnalytics
from simulation.visualization.life_visualizer import LifeVisualizer


class TestPhase3Smoke(unittest.TestCase):
    """
    Test suite to verify functionality of LifeAnalytics and LifeVisualizer.
    """

    @classmethod
    def setUpClass(cls) -> None:
        # Define temporary directory and file paths
        cls.test_dir = os.path.abspath("test_temp_datasets")
        os.makedirs(cls.test_dir, exist_ok=True)

        cls.life_csv = os.path.join(cls.test_dir, "life_catalog.csv")
        cls.species_csv = os.path.join(cls.test_dir, "species_catalog.csv")
        cls.civs_csv = os.path.join(cls.test_dir, "civilizations.csv")
        cls.planets_csv = os.path.join(cls.test_dir, "planets.csv")
        cls.systems_csv = os.path.join(cls.test_dir, "star_systems.csv")

        # 1. Create dummy star systems
        systems_data = {
            "star_id": ["s1", "s2", "s3"],
            "star_name": ["Alpha Centauri", "Sol", "Sirius"],
            "x": [0.0, 10.0, -25.0],
            "y": [0.0, -5.0, 30.0],
            "z": [0.0, 2.0, -10.0],
        }
        pd.DataFrame(systems_data).to_csv(cls.systems_csv, index=False)

        # 2. Create dummy planets
        planets_data = {
            "planet_id": ["p1", "p2", "p3", "p4", "p5"],
            "planet_name": ["Centauri-b", "Earth", "Mars", "Sirius-Prime", "Sirius-c"],
            "star_id": ["s1", "s2", "s2", "s3", "s3"],
            "planet_type": ["Ocean", "Super Earth", "Desert", "Rocky", "Gas Giant"],
            "habitability_score": [85.0, 98.0, 45.0, 65.0, 5.0],
            "temperature": [290.0, 287.0, 210.0, 320.0, 120.0],
            "water_percentage": [100.0, 71.0, 0.1, 15.0, 0.0],
        }
        pd.DataFrame(planets_data).to_csv(cls.planets_csv, index=False)

        # 3. Create dummy life catalog
        life_data = {
            "planet_id": ["p1", "p2", "p3", "p4", "p5"],
            "life_stage": [3, 5, 1, 4, 0],
            "life_probability": [85.0, 99.0, 15.0, 60.0, 0.0],
            "habitability_score": [85.0, 98.0, 45.0, 65.0, 5.0],
            "planet_type": ["Ocean", "Super Earth", "Desert", "Rocky", "Gas Giant"],
            "temperature": [290.0, 287.0, 210.0, 320.0, 120.0],
            "water_percentage": [100.0, 71.0, 0.1, 15.0, 0.0],
        }
        pd.DataFrame(life_data).to_csv(cls.life_csv, index=False)

        # 4. Create dummy species catalog
        species_data = {
            "species_id": ["sp1", "sp2"],
            "name": ["Zoltan", "Human"],
            "planet_id": ["p4", "p2"],
            "intelligence": [85.0, 75.0],
            "cooperation": [90.0, 60.0],
            "aggression": [20.0, 80.0],
            "adaptability": [70.0, 95.0],
            "lifespan": [200.0, 80.0],
            "population": [5.0e9, 8.0e9],
        }
        pd.DataFrame(species_data).to_csv(cls.species_csv, index=False)

        # 5. Create dummy civilizations
        civs_data = {
            "civilization_id": ["c1", "c2"],
            "name": ["Zoltan Collective", "United Nations of Earth"],
            "planet_id": ["p4", "p2"],
            "tech_level": [90.0, 45.0],
            "energy_source": ["Fusion", "Nuclear"],
            "government_type": ["Technocracy", "Democracy"],
            "civilization_age": [10000.0, 2500.0],
            "population": [5.0e9, 8.0e9],
        }
        pd.DataFrame(civs_data).to_csv(cls.civs_csv, index=False)

    @classmethod
    def tearDownClass(cls) -> None:
        # Clean up temporary test files
        if os.path.exists(cls.test_dir):
            try:
                shutil.rmtree(cls.test_dir)
            except PermissionError:
                # Fallback: ignore locked files on Windows
                pass

    def test_analytics_metrics(self) -> None:
        """Verify that analytics calculate metrics correctly."""
        analytics = LifeAnalytics(self.life_csv, self.species_csv, self.civs_csv)
        metrics = analytics.calculate_metrics()

        # Check stage count totals
        self.assertEqual(metrics["total_life_bearing_planets"], 4)  # p1, p2, p3, p4 (stages >= 1)
        self.assertEqual(metrics["microbial_worlds"], 1)            # p3 (stage == 1)
        self.assertEqual(metrics["simple_multicellular"], 0)        # none (stage == 2)
        self.assertEqual(metrics["complex_ecosystems"], 1)          # p1 (stage == 3)
        self.assertEqual(metrics["intelligent_worlds"], 1)          # p4 (stage == 4)
        self.assertEqual(metrics["civilizations_generated"], 2)     # rows in civilizations.csv (c1, c2)

        # Check top habitable planet sorting
        top_hab = metrics["most_habitable_worlds_with_life"]
        self.assertEqual(len(top_hab), 4)  # 4 planets have life
        self.assertEqual(top_hab[0]["planet_name"], "Earth")  # highest habitability score (98)

        # Check top advanced civilization sorting
        top_civ = metrics["most_advanced_civilizations"]
        self.assertEqual(len(top_civ), 2)
        self.assertEqual(top_civ[0]["name"], "Zoltan Collective")  # highest tech_level (90)

    def test_analytics_print_summary(self) -> None:
        """Ensure the summary prints without raising exceptions."""
        analytics = LifeAnalytics(self.life_csv, self.species_csv, self.civs_csv)
        try:
            analytics.print_summary()
        except Exception as e:
            self.fail(f"print_summary() raised an exception: {e}")

    def test_visualization_generation(self) -> None:
        """Verify that visualizer generates the expected files."""
        # Note: We pass the systems_csv coordinate file explicitly in the test setup
        # because the visualizer will search for star_systems.csv in the same folder as civilizations.csv
        visualizer = LifeVisualizer(self.life_csv, self.species_csv, self.civs_csv)

        # Plot distributions
        try:
            visualizer.plot_life_distribution(self.test_dir)
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, "life_distribution.png")))

            visualizer.plot_life_probability_dashboard(self.test_dir)
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, "life_probability_dashboard.png")))

            visualizer.plot_civilization_map(self.test_dir)
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, "civilization_map.png")))
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, "civilization_map.html")))

            visualizer.plot_civilization_statistics(self.test_dir)
            self.assertTrue(os.path.exists(os.path.join(self.test_dir, "civilization_statistics.png")))
        except Exception as e:
            self.fail(f"Visualization generation failed with error: {e}")


if __name__ == "__main__":
    unittest.main()
