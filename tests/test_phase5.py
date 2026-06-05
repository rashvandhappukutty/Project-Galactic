"""
test_phase5.py — Unit tests and validation suite for Phase 5 AI Decision Engine.
"""

import unittest
import numpy as np
from typing import Dict, Any, List

from simulation.ai.strategic_planner import CivilizationAgent, StrategicPlanner
from simulation.ai.threat_assessment import ThreatAssessmentEngine
from simulation.ai.opportunity_analyzer import OpportunityAnalyzer
from simulation.ai.diplomacy_engine import DiplomacyEngine


class TestPhase5DecisionEngine(unittest.TestCase):
    """Verifies that strategic reasoning, threat/opportunity calculations, and megastructure progression function correctly."""

    def setUp(self) -> None:
        # Create a set of test agents
        self.agent_a = CivilizationAgent(
            civilization_id="civ_a",
            name="Zoltan Collective",
            technology_level=6.0,
            population=5e9,
            resources=1000.0,
            government="Technocracy",
            energy_system="Fusion",
            kardashev_rating=0.8,
            aggression=20.0,
            curiosity=90.0,
            cooperation=80.0,
            risk_tolerance=40.0,
            home_planet_id="p_a",
            home_star_id="s_a",
            coordinates=(0.0, 0.0, 0.0),
        )

        self.agent_b = CivilizationAgent(
            civilization_id="civ_b",
            name="Krog Imperium",
            technology_level=4.0,
            population=8e9,
            resources=500.0,
            government="Military Monarchy",
            energy_system="Nuclear",
            kardashev_rating=0.6,
            aggression=95.0,
            curiosity=20.0,
            cooperation=15.0,
            risk_tolerance=85.0,
            home_planet_id="p_b",
            home_star_id="s_b",
            # Neighbor within proximity threshold (e.g. 50 LY)
            coordinates=(30.0, 40.0, 0.0),
        )

        self.agent_c = CivilizationAgent(
            civilization_id="civ_c",
            name="Orion Republic",
            technology_level=5.5,
            population=6e9,
            resources=1200.0,
            government="Representative Democracy",
            energy_system="Fusion",
            kardashev_rating=0.75,
            aggression=40.0,
            curiosity=60.0,
            cooperation=75.0,
            risk_tolerance=50.0,
            home_planet_id="p_c",
            home_star_id="s_c",
            # Neighbor far away (e.g. 300 LY)
            coordinates=(200.0, 200.0, 100.0),
        )

        self.agents_registry = {
            "civ_a": self.agent_a,
            "civ_b": self.agent_b,
            "civ_c": self.agent_c,
        }

        self.planner = StrategicPlanner()
        self.threat_engine = ThreatAssessmentEngine(proximity_threshold=150.0)
        self.opportunity_engine = OpportunityAnalyzer(proximity_threshold=150.0)
        self.diplomacy = DiplomacyEngine(seed=42)

    def test_personality_assignment(self) -> None:
        """Verify that personalities are assigned correctly based on highest traits."""
        # Zoltan Collective: high curiosity (90), high cooperation (80), low aggression (20)
        # StrategicPlanner classifies best personality
        p_a = self.planner.assign_personality(self.agent_a)
        self.assertEqual(p_a, "Scientific")

        # Krog Imperium: high aggression (95), low cooperation (15), high risk (85)
        p_b = self.planner.assign_personality(self.agent_b)
        self.assertEqual(p_b, "Militaristic")

    def test_threat_assessment_proximity(self) -> None:
        """Verify that nearby hostile neighbors correctly raise the threat score."""
        # Evaluate threat on Zoltan Collective
        res = self.threat_engine.evaluate_threat(self.agent_a, self.agents_registry, planet_resource_score=60.0)
        threat_score = res["threat_score"]

        # Threat score must be positive because Krog Imperium is close (50 LY) and aggressive (95)
        self.assertTrue(threat_score > 0.0)
        self.assertTrue(threat_score <= 100.0)
        self.assertTrue(res["rival_factor"] > 0.0)

        # Far neighbor check: B moving to 300 LY away should reduce threat to 0 (excluding resource scarcity)
        self.agent_b.coordinates = (200.0, 200.0, 200.0)
        res_far = self.threat_engine.evaluate_threat(self.agent_a, self.agents_registry, planet_resource_score=100.0)
        # With high resources (100) and no nearby rivals, threat score should decay to 0 (or close to 0)
        self.agent_a.stability = 100.0
        self.agent_a.resources = 1000.0
        res_decay = self.threat_engine.evaluate_threat(self.agent_a, self.agents_registry, planet_resource_score=100.0)
        self.assertEqual(res_decay["rival_factor"], 0.0)

    def test_opportunity_analyzer(self) -> None:
        """Verify opportunity scoring evaluates expansion and trade potential correctly."""
        # Setup mock planets list
        mock_planets = [
            {
                "planet_id": "p_hab",
                "planet_name": "New Genesis",
                "star_id": "s_hab",
                "habitability_score": 90.0,
            }
        ]
        mock_stars = {
            "s_hab": {"x": 20.0, "y": 0.0, "z": 0.0}  # Very close to agent A
        }

        res = self.opportunity_engine.evaluate_opportunity(
            self.agent_a, self.agents_registry, mock_planets, mock_stars
        )
        self.assertTrue(res["opportunity_score"] > 0.0)
        self.assertTrue(res["expansion_factor"] > 0.0)

    def test_action_probability_modifications(self) -> None:
        """Verify that action weights adjust dynamically according to agent profiles."""
        self.planner.assign_personality(self.agent_a)  # Scientific
        self.planner.assign_personality(self.agent_b)  # Militaristic

        # Scientific agent should favor research
        probs_a = self.planner.evaluate_action_probabilities(
            self.agent_a, threat_score=10.0, opportunity_score=50.0, nearby_habitable=1
        )
        self.assertTrue(probs_a["RESEARCH"] > probs_a["ATTACK"])

        # Militaristic agent should favor attack
        probs_b = self.planner.evaluate_action_probabilities(
            self.agent_b, threat_score=10.0, opportunity_score=50.0, nearby_habitable=1
        )
        self.assertTrue(probs_b["ATTACK"] > probs_b["RESEARCH"])

    def test_megastructure_construction_progression(self) -> None:
        """Verify starting, advancing, and completing megastructures behaves correctly."""
        from simulation.ai.ai_decision_engine import AIDecisionEngine
        engine = AIDecisionEngine(seed=42)
        engine.agents = self.agents_registry
        engine.planets_dict = {
            "p_a": {"planet_id": "p_a", "resource_score": 80.0}
        }

        # 1. Start megastructure (requires tech >= 7.0 for Dyson Swarm)
        self.agent_a.technology_level = 7.0
        self.agent_a.resources = 1000.0
        reason, result = engine._execute_action(
            self.agent_a, "BUILD_MEGASTRUCTURE", {"threat_score": 10}, {"opportunity_score": 50, "tech_factor": 15}, 1, 100, set()
        )
        self.assertEqual(self.agent_a.megastructure_type, "Dyson Swarm")
        self.assertEqual(self.agent_a.megastructure_progress, 10.0)
        self.assertEqual(self.agent_a.resources, 200.0)  # 1000 - 800

        # 2. Advance megastructure
        self.agent_a.resources = 500.0
        reason, result = engine._execute_action(
            self.agent_a, "BUILD_MEGASTRUCTURE", {"threat_score": 10}, {"opportunity_score": 50, "tech_factor": 15}, 2, 200, set()
        )
        # progress should increase
        self.assertTrue(self.agent_a.megastructure_progress > 10.0)
        self.assertEqual(self.agent_a.resources, 300.0)  # 500 - 200

        # 3. Force complete megastructure
        self.agent_a.megastructure_progress = 95.0
        self.agent_a.resources = 300.0
        reason, result = engine._execute_action(
            self.agent_a, "BUILD_MEGASTRUCTURE", {"threat_score": 10}, {"opportunity_score": 50, "tech_factor": 15}, 3, 300, set()
        )
        self.assertEqual(self.agent_a.megastructure_progress, 100.0)
        self.assertTrue(self.agent_a.megastructure_energy > 0.0)
        self.assertEqual(self.agent_a.energy_system, "Completed Dyson Swarm")
        # Dyson Swarm = 1e16 Watts -> log10(1e16) = 16 -> (16 - 6)/10 = 1.0 Kardashev rating
        self.assertEqual(self.agent_a.kardashev_rating, 1.0)


if __name__ == "__main__":
    unittest.main()
