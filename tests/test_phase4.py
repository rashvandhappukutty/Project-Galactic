"""
test_phase4.py — Unit tests for Phase 4: Civilization Evolution Engine.
Verifies tech progress math, governance profiles, energy transitions, carrying capacity scaling, and events.
"""

import os
import shutil
import unittest
import numpy as np
import pandas as pd

from simulation.evolution.technology_engine import TechnologyEngine
from simulation.evolution.government_engine import GovernmentEngine
from simulation.evolution.energy_engine import EnergyEngine
from simulation.evolution.civilization_evolution import CivilizationEvolutionSimulator
from simulation.analytics.civilization_analytics import CivilizationAnalytics
from simulation.visualization.civilization_visualizer import CivilizationVisualizer


class TestPhase4Evolution(unittest.TestCase):
    """
    Test suite verifying correctness of the Phase 4 Civilization Evolution package.
    """

    def setUp(self) -> None:
        self.seed = 42
        self.tech_engine = TechnologyEngine(seed=self.seed)
        self.gov_engine = GovernmentEngine(seed=self.seed)
        self.energy_engine = EnergyEngine(seed=self.seed)
        self.simulator = CivilizationEvolutionSimulator(seed=self.seed)

        # Temporary directory for visualizer/analytics test data
        self.test_dir = os.path.abspath("test_temp_phase4_datasets")
        os.makedirs(self.test_dir, exist_ok=True)
        
        self.civs_csv = os.path.join(self.test_dir, "civilization_evolution.csv")
        self.tech_csv = os.path.join(self.test_dir, "technology_progress.csv")
        self.events_csv = os.path.join(self.test_dir, "civilization_events.csv")

    def tearDown(self) -> None:
        if os.path.exists(self.test_dir):
            try:
                shutil.rmtree(self.test_dir)
            except Exception:
                pass

    def test_technology_engine_math(self) -> None:
        """
        Verify TechnologyEngine calculations for research output and tier progression.
        """
        # Test research output calculation
        # Pop: 10 Billion (10e9), Intelligence: 100, Innovation: 50
        # Expected research = 10 * 100 * (1.0 + 0.5) = 1500
        research = self.tech_engine.calculate_research_output(10e9, 100.0, 50.0)
        self.assertEqual(research, 1500.0)

        # Test digital age transition (1000 research points)
        # Digital Age req: 1000. Next (Space Age) req: 5000.
        # L = 2 + (1200 - 1000) / (5000 - 1000) = 2.05
        tech_level, new_res, tier, name = self.tech_engine.update_technology(1.0, 0.0, 1200.0)
        self.assertEqual(tier, 2)
        self.assertEqual(name, "Digital Age")
        self.assertEqual(new_res, 1200.0)
        self.assertAlmostEqual(tech_level, 2.05, places=4)

        # Test transcendent age (312,500,000 research points)
        # Transcendent Age req: 312.5M.
        # L = 10.0 + (625M - 312.5M) / 312.5M = 11.0
        tech_level_trans, new_res_trans, tier_trans, name_trans = self.tech_engine.update_technology(
            10.0, 312500000.0, 312500000.0
        )
        self.assertEqual(tier_trans, 10)
        self.assertEqual(name_trans, "Transcendent Civilization")
        self.assertAlmostEqual(tech_level_trans, 11.0, places=4)

    def test_government_engine_updates(self) -> None:
        """
        Verify GovernmentEngine updates for stability, corruption, innovation, and reforms.
        """
        # Update Stability
        stability = self.gov_engine.update_stability(
            gov_type="Democracy",
            current_stability=80.0,
            pop_carrying_ratio=0.5,  # No pop pressure (under 0.8)
            corruption=10.0
        )
        # Base change is between -3 and 3, profile.stability_mod for Democracy = 1.0. No pop pressure. Corruption penalty = 1.5.
        # Expected stability should be between 80 - 3 - 1.5 = 75.5 and 80 + 3 - 1.5 = 81.5.
        self.assertTrue(75.0 <= stability <= 82.0)

        # Update Corruption
        corruption = self.gov_engine.update_corruption(
            gov_type="AI Governance",
            current_corruption=10.0,
            population=1e9,
            stability=80.0
        )
        # AI Governance corruption modifier is 0.1, pop factor = 9 * 0.5 = 4.5. Stability benefit = 30 * 0.1 = 3.0.
        # Base change = U(0.5, 2.0) * 0.1.
        self.assertTrue(10.0 <= corruption <= 14.0)

        # Government reform trigger from low stability
        # A low stability (e.g. 10.0) has 40% chance of collapse (force reform)
        reformed, new_gov = self.gov_engine.roll_government_reform("Monarchy", 5.0, 50.0, 50.0, 50.0)
        # Under seed=42, check if reform triggers
        self.assertTrue(isinstance(reformed, bool))
        self.assertTrue(new_gov in self.gov_engine.profiles.keys())

    def test_energy_engine_kardashev(self) -> None:
        """
        Verify EnergyEngine updates and Kardashev rating calculations.
        """
        # Test tech thresholds for energy source
        self.assertEqual(self.energy_engine.update_energy_source(1.5), "Fossil")
        self.assertEqual(self.energy_engine.update_energy_source(3.5), "Nuclear")
        self.assertEqual(self.energy_engine.update_energy_source(5.5), "Fusion")
        self.assertEqual(self.energy_engine.update_energy_source(7.0), "Antimatter")
        self.assertEqual(self.energy_engine.update_energy_source(8.0), "Dyson Swarm")
        self.assertEqual(self.energy_engine.update_energy_source(9.0), "Dyson Sphere")
        self.assertEqual(self.energy_engine.update_energy_source(10.0), "Galactic Energy Grid")

        # Test Kardashev rating calculation
        # Fusion base = 1e18 W. Tech level = 5.0. Output = 1e18 * (1.0 + 2.5) = 3.5e18.
        # Kardashev = (log10(3.5e18) - 6) / 10 = (18.544 - 6) / 10 = 1.2544
        output, rating = self.energy_engine.calculate_kardashev("Fusion", 5.0)
        self.assertEqual(output, 3.5e18)
        self.assertAlmostEqual(rating, 1.2544, places=4)

    def test_carrying_capacity(self) -> None:
        """
        Verify simulator carrying capacity formula matches design specs.
        """
        # Rocky base capacity: 6 Billion (6e9). Hab score: 80. Tech level: 5.0.
        # CC = 6e9 * 0.80 * (1.0 + 5.0 * 0.20) = 4.8e9 * 2.0 = 9.6 Billion (9.6e9)
        cc = self.simulator.calculate_carrying_capacity("Rocky", 1.0, 80.0, 5.0)
        self.assertEqual(cc, 9.6e9)

        # Super Earth base capacity: 12 Billion (12e9). Hab score: 100. Tech level: 10.0.
        # CC = 12e9 * 1.0 * (1.0 + 10 * 0.20) = 12e9 * 3.0 = 3.6e10
        cc_se = self.simulator.calculate_carrying_capacity("SUPER_EARTH", 2.0, 100.0, 10.0)
        self.assertEqual(cc_se, 3.6e10)

    def test_demographics_logistic_growth_extinction(self) -> None:
        """
        Verify logistic growth step bounds and extinction triggers.
        """
        civ = {
            "civilization_id": "test-ext",
            "name": "Testing Powers",
            "population": 5e4,  # Under 100,000 threshold
            "tech_level": 2.0,
            "research_points": 1000.0,
            "government_type": "Democracy",
            "stability_score": 80.0,
            "corruption_score": 10.0,
            "innovation_score": 50.0
        }
        planet = {"planet_type": "ROCKY", "radius": 1.0, "habitability_score": 80.0, "resource_score": 50.0}
        species = {"intelligence": 100.0, "cooperation": 50.0, "aggression": 30.0}

        # Simulating should trigger immediate extinction
        updated_civ, events = self.simulator.simulate_civilization_step(civ, planet, species, 100, 100)
        self.assertEqual(updated_civ["population"], 0.0)
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["event_type"], "Extinction")

    def test_analytics_and_visualizations_run(self) -> None:
        """
        Smoke test for analytics summaries and visual plots.
        """
        # Create dummy catalogs
        civs_data = {
            "civilization_id": ["c1", "c2"],
            "name": ["Consolidated Valan Council", "Zylarian Directorate"],
            "species_id": ["s1", "s2"],
            "species_name": ["Valan", "Zylarian"],
            "planet_id": ["p1", "p2"],
            "population": [5.5e9, 1.2e9],
            "tech_level": [6.2, 8.5],
            "research_points": [500000.0, 12500000.0],
            "tech_tier": [6, 8],
            "tech_stage_name": ["Fusion Civilization", "Dyson Swarm Civilization"],
            "energy_source": ["Fusion", "Dyson Swarm"],
            "energy_output_watts": [3.5e18, 5.25e26],
            "kardashev_rating": [1.2544, 2.0720],
            "government_type": ["Technocracy", "Scientific Council"],
            "stability_score": [85.0, 75.0],
            "corruption_score": [12.0, 18.0],
            "innovation_score": [75.0, 80.0],
            "civilization_age": [10000.0, 25000.0]
        }
        pd.DataFrame(civs_data).to_csv(self.civs_csv, index=False)

        tech_data = {
            "civilization_id": ["c1", "c1", "c2", "c2"],
            "name": ["Consolidated Valan Council", "Consolidated Valan Council", "Zylarian Directorate", "Zylarian Directorate"],
            "year": [0, 100, 0, 100],
            "population": [5.0e9, 5.5e9, 1.0e9, 1.2e9],
            "tech_level": [6.0, 6.2, 8.0, 8.5],
            "energy_source": ["Fusion", "Fusion", "Dyson Swarm", "Dyson Swarm"],
            "kardashev_rating": [1.2, 1.2544, 2.0, 2.0720],
            "stability_score": [80.0, 85.0, 70.0, 75.0],
            "corruption_score": [10.0, 12.0, 15.0, 18.0],
            "innovation_score": [70.0, 75.0, 75.0, 80.0],
            "government_type": ["Technocracy", "Technocracy", "Scientific Council", "Scientific Council"]
        }
        pd.DataFrame(tech_data).to_csv(self.tech_csv, index=False)

        events_data = {
            "event_id": ["EVT-00001", "EVT-00002"],
            "civilization_id": ["c1", "c2"],
            "civilization_name": ["Consolidated Valan Council", "Zylarian Directorate"],
            "year": [50, 80],
            "event_type": ["Scientific Breakthrough", "Golden Age"],
            "description": ["Breakthrough description", "Golden Age description"],
            "stability_impact": [0.0, 20.0],
            "population_impact": [0.0, 0.0]
        }
        pd.DataFrame(events_data).to_csv(self.events_csv, index=False)

        # Run analytics
        analytics = CivilizationAnalytics(self.civs_csv, self.tech_csv, self.events_csv)
        metrics = analytics.calculate_metrics()
        self.assertEqual(metrics["total_active_civilizations"], 2)
        self.assertEqual(metrics["extinct_civilizations"], 0)
        self.assertEqual(metrics["largest"]["name"], "Consolidated Valan Council")
        self.assertEqual(metrics["most_advanced"]["name"], "Zylarian Directorate")

        # Run visualizer plots
        visualizer = CivilizationVisualizer(self.civs_csv, self.tech_csv, self.events_csv)
        
        # Test matplotlib plots
        visualizer.plot_civilization_growth(self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "civilization_growth.png")))

        visualizer.plot_technology_progress(self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "technology_progress.png")))

        visualizer.plot_government_distribution(self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "government_distribution.png")))

        visualizer.plot_kardashev_scale_distribution(self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "kardashev_scale_distribution.png")))

        # Test plotly interactive plot
        visualizer.plot_civilization_timeline(self.test_dir)
        self.assertTrue(os.path.exists(os.path.join(self.test_dir, "civilization_timeline.html")))


if __name__ == "__main__":
    unittest.main()
