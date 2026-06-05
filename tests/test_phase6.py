"""
test_phase6.py — Unit tests and validation suite for Phase 6 Colonization Engine.
"""

import unittest
from typing import Dict, Any, List

from simulation.ai.strategic_planner import CivilizationAgent
from simulation.colonization.colony_generator import Colony, ColonyGenerator
from simulation.colonization.territory_manager import Territory, TerritoryManager
from simulation.colonization.expansion_planner import ExpansionPlanner
from simulation.colonization.colonization_engine import ColonizationEngine


class TestPhase6Colonization(unittest.TestCase):
    """Verifies target selection scoring, borders resolution, colony growth, and routes."""

    def setUp(self) -> None:
        self.agent_a = CivilizationAgent(
            civilization_id="civ_a",
            name="Vesperan Directorate",
            technology_level=6.0,
            population=1.2e8,
            resources=1000.0,
            government="Technocracy",
            energy_system="Fusion",
            kardashev_rating=0.85,
            aggression=30.0,
            curiosity=80.0,
            cooperation=75.0,
            risk_tolerance=60.0,
            home_planet_id="p_a",
            home_star_id="s_a",
            coordinates=(0.0, 0.0, 0.0),
        )

        self.agent_b = CivilizationAgent(
            civilization_id="civ_b",
            name="Krog Star Empire",
            technology_level=4.5,
            population=5e7,
            resources=800.0,
            government="Autocracy",
            energy_system="Fission",
            kardashev_rating=0.6,
            aggression=90.0,
            curiosity=20.0,
            cooperation=20.0,
            risk_tolerance=80.0,
            home_planet_id="p_b",
            home_star_id="s_b",
            coordinates=(40.0, 30.0, 0.0),  # Distance 50 LY
        )

        self.agents_registry = {
            "civ_a": self.agent_a,
            "civ_b": self.agent_b,
        }

        self.stars_dict = {
            "s_a": {"id": "s_a", "name": "Vesper", "x": 0.0, "y": 0.0, "z": 0.0, "region": "Core"},
            "s_b": {"id": "s_b", "name": "Krog", "x": 40.0, "y": 30.0, "z": 0.0, "region": "Core"},
            "s_target": {"id": "s_target", "name": "Eden", "x": 20.0, "y": 15.0, "z": 0.0, "region": "Core"},  # Closest to A
            "s_far": {"id": "s_far", "name": "Far Star", "x": 300.0, "y": 300.0, "z": 0.0, "region": "Rim"},   # Exceeds 250 LY
        }

        self.planets_list = [
            {"planet_id": "p_a", "star_id": "s_a", "habitability_score": 85.0, "resource_score": 70.0, "planet_name": "Vesper I"},
            {"planet_id": "p_b", "star_id": "s_b", "habitability_score": 75.0, "resource_score": 80.0, "planet_name": "Krog I"},
            {"planet_id": "p_target", "star_id": "s_target", "habitability_score": 90.0, "resource_score": 60.0, "planet_name": "Eden Prime"},
            {"planet_id": "p_far", "star_id": "s_far", "habitability_score": 95.0, "resource_score": 90.0, "planet_name": "Far Outpost"},
        ]

        self.planet_star_coords = {
            "p_a": (0.0, 0.0, 0.0),
            "p_b": (40.0, 30.0, 0.0),
            "p_target": (20.0, 15.0, 0.0),
            "p_far": (300.0, 300.0, 0.0),
        }

        self.colony_gen = ColonyGenerator(seed=42)
        self.territory_mgr = TerritoryManager(proximity_threshold=150.0)
        self.planner = ExpansionPlanner(max_range_ly=250.0)

    def test_colony_generation_attributes(self) -> None:
        """Verify colony attributes are generated correctly based on target planet characteristics."""
        planet_target = self.planets_list[2]  # Eden Prime: hab 90, res 60
        self.agent_a.personality = "Scientific"
        
        colony = self.colony_gen.create_colony(
            civ_id="civ_a",
            civ_name="Vesperan Directorate",
            civ_personality=self.agent_a.personality,
            planet=planet_target,
        )

        self.assertEqual(colony.parent_civilization_id, "civ_a")
        self.assertEqual(colony.home_star_id, "s_target")
        self.assertEqual(colony.target_planet_id, "p_target")
        self.assertTrue(colony.population > 0.0)
        self.assertEqual(colony.colony_type, "Capital Colony")  # Hab > 75.0 triggers Capital Colony

    def test_sphere_of_influence_radius(self) -> None:
        """Verify Sphere of Influence radius scales logarithmically with population and tech level."""
        # A: tech 6.0, pop 1.2e8 (log10 ~ 8.08)
        # R = 25 + 10 * 6.0 + 5 * 8.08 = 25 + 60 + 40.4 = 125.4
        r_a = self.territory_mgr.calculate_influence_radius(self.agent_a.technology_level, self.agent_a.population)
        self.assertAlmostEqual(r_a, 25.0 + 60.0 + 5.0 * 8.07918, places=1)

    def test_target_scoring_planner(self) -> None:
        """Verify target selection AI filters out-of-range planets and scores viable targets correctly."""
        unoccupied = [self.planets_list[2], self.planets_list[3]]  # p_target ( Eden ), p_far
        
        scored = self.planner.score_targets(
            self.agent_a,
            unoccupied,
            self.stars_dict,
            self.agents_registry,
            self.planet_star_coords,
        )

        # p_far should be filtered out because distance is > 250 LY (approx 424 LY)
        # Only p_target should remain in scored list
        self.assertEqual(len(scored), 1)
        self.assertEqual(scored[0][0]["planet_id"], "p_target")
        self.assertTrue(scored[0][1] > 0.0)

    def test_territory_conflict_resolution(self) -> None:
        """Verify contested star claims are awarded to the agent with the highest Power Index."""
        # Place both agents so s_target lies within their SOIs
        # A coordinates = (0,0,0) -> distance to s_target (20,15,0) is 25 LY
        # B coordinates = (40,30,0) -> distance to s_target is 25 LY
        # SOIs are both > 25 LY.
        # A tech = 6.0, pop = 1.2e8 -> higher power than B (tech=4.5, pop=5e7)
        # Winner must be A.
        self.agent_a.colonies = []
        self.agent_b.colonies = []
        
        territories = self.territory_mgr.update_territories(
            self.agents_registry, self.stars_dict, self.planets_list
        )

        terr_a = territories["civ_a"]
        terr_b = territories["civ_b"]

        self.assertIn("s_target", terr_a.controlled_systems)
        self.assertNotIn("s_target", terr_b.controlled_systems)

    def test_networkx_routes_generation(self) -> None:
        """Verify that trade and migration routes are mapped correctly in the engine."""
        engine = ColonizationEngine(seed=42)
        engine.agents = self.agents_registry
        engine.stars = self.stars_dict
        engine.planets = self.planets_list
        engine.planets_dict = {p["planet_id"]: p for p in self.planets_list}
        
        # Manually establish a colony for agent A
        colony_planet_id = "p_target"
        col = self.colony_gen.create_colony(
            "civ_a", "Vesperan Directorate", "Scientific", engine.planets_dict[colony_planet_id]
        )
        engine.colonies_db[colony_planet_id] = col
        self.agent_a.colonies.append(colony_planet_id)

        # Establish trade partnership between A and B
        self.agent_a.trading_partners.append("civ_b")
        self.agent_b.trading_partners.append("civ_a")

        engine._generate_interstellar_routes()

        routes = engine.routes_db
        # We expect 2 routes: 1 migration route (A capital -> Eden colony) and 1 trade route (A capital -> B capital)
        self.assertEqual(len(routes), 2)
        
        r_types = [r["route_type"] for r in routes]
        self.assertIn("Migration Route", r_types)
        self.assertIn("Trade Route", r_types)


if __name__ == "__main__":
    unittest.main()
