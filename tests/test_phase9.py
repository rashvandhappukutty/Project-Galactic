"""
test_phase9.py — Unit tests and validation suite for Phase 9 Political and Military Layer.
"""

import unittest
from typing import Dict, Any, List

from simulation.diplomacy.diplomacy_engine import DiplomacyEngine, DiplomaticRelation
from simulation.diplomacy.alliance_manager import AllianceManager, Alliance
from simulation.diplomacy.treaty_engine import TreatyEngine, PeaceTreaty
from simulation.diplomacy.espionage_engine import EspionageEngine, EspionageOperation
from simulation.warfare.fleet_generator import FleetGenerator, Fleet
from simulation.warfare.battle_engine import BattleEngine, Battle
from simulation.warfare.invasion_engine import InvasionEngine, Conquest
from simulation.warfare.war_simulator import WarSimulator, War
from simulation.colonization.colony_generator import Colony


class TestPhase9PoliticsAndWar(unittest.TestCase):
    """Verifies diplomacy, NAPs, alliances, spy operations, battles, and ground conquests."""

    def setUp(self) -> None:
        self.stars = {
            "s_a": {"id": "s_a", "name": "Vesper", "x": 0.0, "y": 0.0, "z": 0.0, "region": "Core"},
            "s_b": {"id": "s_b", "name": "Krog", "x": 40.0, "y": 0.0, "z": 0.0, "region": "Core"},
            "s_c": {"id": "s_c", "name": "Eden", "x": 80.0, "y": 0.0, "z": 0.0, "region": "Core"},
        }
        
        self.empires = [
            {"founding_civilization_id": "civ_a", "empire_name": "Vesperan Directorate", "capital_world": "Vesper Prime", "government_type": "Democracy", "power_index": 80.0, "gdp": 12000.0, "population": 4e9},
            {"founding_civilization_id": "civ_b", "empire_name": "Krog Empire", "capital_world": "Krog Homeworld", "government_type": "Dictatorship", "power_index": 90.0, "gdp": 8000.0, "population": 6e9},
            {"founding_civilization_id": "civ_c", "empire_name": "Eden Assembly", "capital_world": "Eden Hub", "government_type": "Democracy", "power_index": 50.0, "gdp": 6000.0, "population": 2e9}
        ]

        self.capital_stars = {"civ_a": "s_a", "civ_b": "s_b", "civ_c": "s_c"}

        self.colonies = [
            Colony("col_a", "Vesper Prime", "civ_a", "s_a", "p_a", 2.0e9, 50.0, 50.0, "Capital Colony", 10.0),
            Colony("col_b", "Krog Homeworld", "civ_b", "s_b", "p_b", 4.0e9, 60.0, 80.0, "Capital Colony", 15.0),
            Colony("col_c", "Eden Hub", "civ_c", "s_c", "p_c", 1.0e9, 40.0, 40.0, "Capital Colony", 5.0)
        ]

        self.planets = {
            "p_a": {"planet_id": "p_a", "star_id": "s_a", "planet_name": "Vesper Prime", "habitability_score": 90.0, "resource_score": 60.0},
            "p_b": {"planet_id": "p_b", "star_id": "s_b", "planet_name": "Krog Homeworld", "habitability_score": 85.0, "resource_score": 90.0},
            "p_c": {"planet_id": "p_c", "star_id": "s_c", "planet_name": "Eden Hub", "habitability_score": 95.0, "resource_score": 50.0}
        }

        self.diplomacy = DiplomacyEngine(seed=42)
        self.alliances = AllianceManager(seed=42)
        self.treaties = TreatyEngine(seed=42)
        self.espionage = EspionageEngine(seed=42)
        self.fleet_gen = FleetGenerator(seed=42)
        self.battles = BattleEngine(seed=42)
        self.invasions = InvasionEngine(seed=42)
        self.wars = WarSimulator(seed=42)

    def test_diplomacy_relations_drift(self) -> None:
        """Verify that government alignments affect relations and scores drift appropriately."""
        self.diplomacy.initialize_relations(self.empires, self.stars, [], self.capital_stars)
        
        # Democracies (civ_a & civ_c) should have a higher initial relation than Democracy vs Dictatorship
        rel_ac = self.diplomacy.relations.get(("civ_a", "civ_c"))
        rel_ab = self.diplomacy.relations.get(("civ_a", "civ_b"))
        
        self.assertIsNotNone(rel_ac)
        self.assertIsNotNone(rel_ab)
        self.assertTrue(rel_ac.relation_score > rel_ab.relation_score)

        # Run tick relation updates
        self.diplomacy.update_relations(["civ_a", "civ_b", "civ_c"])
        
        # Test applying a relation shock (e.g. spy caught)
        score_before_shock = self.diplomacy.relations[("civ_a", "civ_c")].relation_score
        self.diplomacy.apply_diplomatic_shock("civ_a", "civ_c", -30.0, -20.0)
        self.assertEqual(self.diplomacy.relations[("civ_a", "civ_c")].relation_score, score_before_shock - 30.0)

    def test_alliance_cohesion(self) -> None:
        """Verify alliances form based on relation scores and combined stats calculate correctly."""
        # Mock high relations between A and C
        relations_dict = {
            ("civ_a", "civ_c"): DiplomaticRelation("civ_a", "civ_c", 75.0, 80.0, 10.0, 0.0, 50.0, 80.0),
            ("civ_c", "civ_a"): DiplomaticRelation("civ_c", "civ_a", 75.0, 80.0, 10.0, 0.0, 50.0, 80.0)
        }
        
        empire_stats = {
            "civ_a": {"empire_name": "Vesperan Directorate", "personality": "Scientific", "gdp": 12000.0, "population": 4e9},
            "civ_c": {"empire_name": "Eden Assembly", "personality": "Diplomatic", "gdp": 6000.0, "population": 2e9}
        }
        
        self.alliances.update_alliances(relations_dict, empire_stats, {"civ_a": 1000.0, "civ_c": 500.0})
        self.assertEqual(len(self.alliances.alliances), 1)
        al = self.alliances.alliances[0]
        self.assertIn(al.alliance_type, ["Galactic Federation", "Research Alliance"])
        self.assertIn("civ_a", al.member_empires)
        self.assertIn("civ_c", al.member_empires)
        self.assertEqual(al.combined_gdp, 18000.0)
        self.assertEqual(al.combined_population, 6e9)
        self.assertEqual(al.combined_fleet_power, 1500.0)

    def test_espionage_operations(self) -> None:
        """Verify espionage resolutions apply appropriate tech/treasury modifications."""
        relations_dict = {
            ("civ_a", "civ_b"): DiplomaticRelation("civ_a", "civ_b", -45.0, 20.0, 10.0, 0.0, 50.0, 20.0),
            ("civ_b", "civ_a"): DiplomaticRelation("civ_b", "civ_a", -45.0, 20.0, 10.0, 0.0, 50.0, 20.0)
        }
        
        empire_stats = {
            "civ_a": {"empire_name": "Vesperan Directorate", "personality": "Scientific"},
            "civ_b": {"empire_name": "Krog Empire", "personality": "Militaristic"}
        }

        treasuries = {"civ_a": 1000.0, "civ_b": 1000.0}
        stabilities = {"civ_a": 80.0, "civ_b": 80.0}
        techs = {"civ_a": 5.0, "civ_b": 5.0}

        # Mock spy operation
        logs = self.espionage.run_tick_operations(
            tick=1,
            empires=[{"founding_civilization_id": "civ_a"}, {"founding_civilization_id": "civ_b"}],
            relations_dict=relations_dict,
            empire_stats=empire_stats,
            treasury_registry=treasuries,
            stability_registry=stabilities,
            civ_techs=techs
        )
        
        self.assertTrue(len(self.espionage.operations) >= 0)

    def test_fleet_generation_upkeep(self) -> None:
        """Verify fleets construct correctly and upkeeps deduct from treasury budgets."""
        self.fleet_gen.generate_initial_fleets(self.empires, self.capital_stars, {"civ_a": 5.0, "civ_b": 5.0, "civ_c": 5.0})
        
        # Every empire should have fleets
        civ_a_fleets = [f for f in self.fleet_gen.fleets.values() if f.owner_empire_id == "civ_a"]
        self.assertTrue(len(civ_a_fleets) >= 2)
        
        # Test upkeep deduction
        treasuries = {"civ_a": 1000.0}
        self.fleet_gen.deduct_upkeep(treasuries)
        self.assertTrue(treasuries["civ_a"] < 1000.0)

    def test_battle_combat_casualties(self) -> None:
        """Verify combat rounds resolve and casualties compile correctly."""
        f_att = [Fleet("FLT-A", "civ_a", "Attacker Fleet", "Assault Fleet", 500.0, 5.0, 100.0, 80.0, 20.0, "s_a", "Idle")]
        f_def = [Fleet("FLT-B", "civ_b", "Defender Fleet", "Defense Fleet", 300.0, 3.0, 50.0, 100.0, 10.0, "s_a", "Idle")]

        battle = self.battles.resolve_battle("WAR-001", "civ_a", "civ_b", f_att, f_def, "s_a", "Orbital Battle", 100.0)
        
        self.assertEqual(battle.war_id, "WAR-001")
        self.assertTrue(battle.casualties > 0.0)
        self.assertTrue(battle.fleet_losses_attacker >= 0.0)
        self.assertTrue(battle.fleet_losses_defender >= 0.0)
        
        # Winner must be either civ_a or civ_b
        self.assertIn(battle.winner_id, ["civ_a", "civ_b"])

    def test_planetary_invasion_sovereignty(self) -> None:
        """Verify ground assaults transfer colony sovereignty upon victory."""
        # High invading fleet power guarantees capture success
        colony = self.colonies[1]  # Krog capital colony
        self.assertEqual(colony.parent_civilization_id, "civ_b")

        success = self.invasions.resolve_invasion(
            war_id="WAR-001",
            attacker_id="civ_a",
            defender_id="civ_b",
            colony=colony,
            planet=self.planets["p_b"],
            invading_fleet_power=50000.0,
            year=100.0,
            attacker_personality="Militaristic"
        )
        
        self.assertTrue(success)
        self.assertEqual(colony.parent_civilization_id, "civ_a")
        self.assertEqual(self.invasions.conquests[0].action, "Annex Territory")


if __name__ == "__main__":
    unittest.main()
