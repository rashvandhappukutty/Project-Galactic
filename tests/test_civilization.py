"""
Unit tests for Phase 4: Civilization Evolution Engine (Analytics & Visualization).
Verifies ranking metrics, superlatives calculations, and output plotting.
"""

import os
import tempfile
import unittest
import pandas as pd
from simulation.analytics.civilization_analytics import CivilizationAnalytics
from simulation.visualization.civilization_visualizer import CivilizationVisualizer


class TestCivilizationAnalyticsAndVisualizer(unittest.TestCase):
    def setUp(self):
        # Create temporary directory for tests
        self.test_dir_obj = tempfile.TemporaryDirectory()
        self.test_dir = self.test_dir_obj.name

        self.civs_csv = os.path.join(self.test_dir, "civilizations.csv")
        self.tech_csv = os.path.join(self.test_dir, "tech_progress.csv")
        self.events_csv = os.path.join(self.test_dir, "events.csv")

        # Mock civilization data
        # Civ 1: Fastest growing
        # Civ 2: Largest, most advanced, highest Kardashev
        # Civ 3: Most stable government
        # Plus 17 more to test Top 20 ranking
        civs_data = []
        for i in range(1, 23):
            pop = 1e9 * i
            initial_pop = 1e6 if i == 1 else (pop * 0.5)
            gov = "Democracy" if i % 2 == 0 else "Technocracy"
            if i == 3:
                gov = "Federation"
                stability = 99.0
            else:
                stability = 50.0 + i

            civs_data.append({
                "civilization_id": f"civ_{i}",
                "name": f"Empire of {i}",
                "government_type": gov,
                "population": pop,
                "initial_population": initial_pop,
                "tech_level": 40.0 + i * 2,
                "kardashev_rating": 0.5 + (i * 0.05),
                "stability_score": stability,
            })
        
        pd.DataFrame(civs_data).to_csv(self.civs_csv, index=False)

        # Mock timeseries data
        tech_data = []
        for i in range(1, 23):
            for year in [1000, 5000, 10000]:
                pop = (1e9 * i) * (year / 10000.0)
                tech_data.append({
                    "civilization_id": f"civ_{i}",
                    "year": year,
                    "tech_level": (40.0 + i * 2) * (year / 10000.0),
                    "population": pop,
                    "kardashev_rating": (0.5 + (i * 0.05)) * (year / 10000.0),
                    "stability_score": 75.0,
                })
        pd.DataFrame(tech_data).to_csv(self.tech_csv, index=False)

        # Mock event data
        events_data = [
            {"civilization_id": "civ_22", "year": 1000, "event_type": "First Contact", "description": "Met another species"},
            {"civilization_id": "civ_22", "year": 5000, "event_type": "War", "description": "Galactic conflict started"},
            {"civilization_id": "civ_21", "year": 1200, "event_type": "Golden Age", "description": "Age of enlightenment"},
            {"civilization_id": "civ_20", "year": 9000, "event_type": "Collapse", "description": "System failure occurred"},
        ]
        pd.DataFrame(events_data).to_csv(self.events_csv, index=False)

    def tearDown(self):
        # Clean up temporary directory
        self.test_dir_obj.cleanup()

    def test_analytics_metrics(self):
        """Test calculation of superlatives and Top 20 ranking."""
        analytics = CivilizationAnalytics(self.civs_csv, self.tech_csv, self.events_csv)
        metrics = analytics.calculate_metrics()

        # Fastest growing: initial pop 1e6, final 1e9 (growth ratio 999.0)
        self.assertEqual(metrics["fastest_growing"]["civilization_id"], "civ_1")
        self.assertAlmostEqual(metrics["fastest_growing"]["growth_ratio"], 999.0)

        # Largest: civ_22 with population 22 billion
        self.assertEqual(metrics["largest"]["civilization_id"], "civ_22")
        self.assertEqual(metrics["largest"]["population"], 22e9)

        # Most advanced: civ_22 with tech_level 84.0
        self.assertEqual(metrics["most_advanced"]["civilization_id"], "civ_22")
        self.assertEqual(metrics["most_advanced"]["tech_level"], 84.0)

        # Most stable: civ_3 with stability 99.0
        self.assertEqual(metrics["most_stable_government"]["civilization_id"], "civ_3")
        self.assertEqual(metrics["most_stable_government"]["stability_score"], 99.0)

        # Highest Kardashev: civ_22 with rating 1.6
        self.assertEqual(metrics["highest_kardashev"]["civilization_id"], "civ_22")
        self.assertEqual(metrics["highest_kardashev"]["kardashev_rating"], 1.6)

        # Top 20 Powers: should rank and return exactly 20 items
        self.assertEqual(len(metrics["top_20_powers"]), 20)
        # Power index ranking check (civ_22 should be first or near the top)
        self.assertEqual(metrics["top_20_powers"][0]["civilization_id"], "civ_22")

    def test_analytics_print_summary(self):
        """Test print_summary works without exceptions."""
        analytics = CivilizationAnalytics(self.civs_csv, self.tech_csv, self.events_csv)
        try:
            analytics.print_summary()
        except Exception as e:
            self.fail(f"print_summary raised exception: {e}")

    def test_visualizer_plots(self):
        """Test visualizer output file generation."""
        visualizer = CivilizationVisualizer(self.civs_csv, self.tech_csv, self.events_csv)

        # Generate plots
        visualizer.plot_civilization_growth(self.test_dir)
        visualizer.plot_technology_progress(self.test_dir)
        visualizer.plot_government_distribution(self.test_dir)
        visualizer.plot_kardashev_scale_distribution(self.test_dir)
        visualizer.plot_civilization_timeline(self.test_dir)

        # Check files exist
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "civilization_growth.png")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "technology_progress.png")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "government_distribution.png")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "kardashev_scale_distribution.png")))
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "civilization_timeline.html")))


if __name__ == "__main__":
    unittest.main()
