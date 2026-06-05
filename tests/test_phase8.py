"""
test_phase8.py — Unit tests and validation suite for Phase 8 Transportation Layer.
"""

import unittest
from typing import Dict, Any, List
import networkx as nx

from simulation.ftl.wormhole_generator import Wormhole, WormholeGenerator
from simulation.ftl.hyperlane_network import Hyperlane, HyperlaneNetwork
from simulation.ftl.jump_gate_engine import JumpGate, JumpGateEngine
from simulation.ftl.route_calculator import RouteCalculator
from simulation.ftl.transit_optimizer import TransitOptimizer


class TestPhase8Transit(unittest.TestCase):
    """Verifies wormhole generation, hyperlane mesh mapping, gateway connectivity, and network calculations."""

    def setUp(self) -> None:
        self.stars = {
            "s_a": {"id": "s_a", "name": "Vesper", "x": 0.0, "y": 0.0, "z": 0.0, "region": "Core"},
            "s_b": {"id": "s_b", "name": "Krog", "x": 40.0, "y": 0.0, "z": 0.0, "region": "Core"},
            "s_c": {"id": "s_c", "name": "Eden", "x": 80.0, "y": 0.0, "z": 0.0, "region": "Core"},
            "s_far": {"id": "s_far", "name": "Far Star", "x": 300.0, "y": 0.0, "z": 0.0, "region": "Rim"},
        }
        
        self.empires = [
            {"founding_civilization_id": "civ_a", "empire_name": "Vesperan Directorate", "capital_world": "Vesper Prime"},
            {"founding_civilization_id": "civ_b", "empire_name": "Krog Empire", "capital_world": "Krog Homeworld"}
        ]
        
        self.colonies = [
            {"target_planet_id": "p_colony", "parent_civilization_id": "civ_a", "home_star_id": "s_c", "colony_name": "New Eden", "colony_type": "Mining Colony"}
        ]

        self.w_gen = WormholeGenerator(seed=42)
        self.l_gen = HyperlaneNetwork(seed=42)
        self.g_eng = JumpGateEngine(seed=42)
        self.router = RouteCalculator()

    def test_wormhole_generation_rules(self) -> None:
        """Verify natural wormholes only connect distant systems."""
        wormholes = self.w_gen.generate_natural_wormholes(self.stars, num_wormholes=1)
        self.assertEqual(len(wormholes), 1)
        w = wormholes[0]
        # Must connect s_a/s_b/s_c to s_far (since only those are separated by > 200 LY)
        self.assertIn("s_far", [w.entry_system, w.exit_system])
        self.assertTrue(w.distance_reduction > 100.0)

    def test_hyperlane_knn_grid(self) -> None:
        """Verify hyperlanes are constructed correctly using K-Nearest Neighbors."""
        lanes = self.l_gen.generate_hyperlanes(self.stars, self.empires, self.colonies, k_neighbors=2, max_distance=100.0)
        # s_far is 300 LY away, so it should not have any hyperlane connections within max_distance of 100 LY.
        # Only s_a, s_b, s_c should connect.
        self.assertTrue(len(lanes) > 0)
        for l in lanes:
            self.assertNotEqual(l.source_star_id, "s_far")
            self.assertNotEqual(l.target_star_id, "s_far")

    def test_jump_gate_relay_links(self) -> None:
        """Verify jump gates are constructed and connect correctly based on type and distance."""
        # 1. Attempt construction with L6+ tech (Quantum Relay)
        success, cost, gate_a = self.g_eng.attempt_construction(
            gate_counter=1,
            star_id="s_a",
            tech_level=9.0,
            treasury=10000.0,
            empire_id="civ_a",
            colony_type="Capital Colony"
        )
        self.assertTrue(success)
        self.assertEqual(gate_a.gate_type, "Quantum Relay Gate")

        # 2. Attempt construction for another empire capital with L4 tech (Empire Gate)
        success2, cost2, gate_b = self.g_eng.attempt_construction(
            gate_counter=2,
            star_id="s_b",
            tech_level=6.0,
            treasury=4000.0,
            empire_id="civ_b",
            colony_type="Capital Colony"
        )
        self.assertTrue(success2)
        self.assertEqual(gate_b.gate_type, "Empire Gate")

        # 3. Connect gateways
        self.stars["s_b"]["x"] = 120.0
        self.g_eng.connect_gateways(self.stars)
        
        # Empire gates only connect to same owner gates.
        # Quantum gates link globally to other high-tech gates, but not to standard empire gates of a different owner.
        self.assertNotIn("s_b", gate_a.connected_systems)

    def test_routing_pathfinder(self) -> None:
        """Verify that FTL travel routing selects the fastest path combining FTL lanes and warp flight."""
        # Setup hyperlanes and wormhole shortcut
        # A connects to B via hyperlane (40 LY). Travel time at 5 LY/year = 8 years.
        # Wormhole connects A to C instantly (travel time = 0.05 years).
        # B connects to C via hyperlane (40 LY). Travel time = 8 years.
        # Shortest path A -> B should route via C (0.05 + 8 = 8.05 years) instead of direct warp (40 years) or direct lane (8.00 years).
        # Actually direct lane (8.00 years) is faster than via C (8.05 years).
        # Let's adjust weights so wormhole goes A -> B directly.
        w = Wormhole(
            wormhole_id="WRM-001",
            wormhole_type="Natural",
            stability_type="Stable",
            entry_system="s_a",
            exit_system="s_b",
            distance_reduction=35.0,
            stability=1.0,
            capacity=1000.0
        )
        self.router.build_network_graph(self.stars, [], [w], {}, global_avg_tech=2.0)
        
        path, time = self.router.calculate_transit("s_a", "s_b")
        self.assertEqual(path, ["s_a", "s_b"])
        # Wormhole transit time is 0.05 years
        self.assertAlmostEqual(time, 0.05, places=2)

    def test_chokepoints_centrality(self) -> None:
        """Verify betweenness centrality identifies transit hub chokepoints correctly."""
        # Simple line graph: A -- B -- C
        # B is the clear chokepoint between A and C.
        lane_1 = Hyperlane("LAN-01", "Hyperlane Route", "s_a", "s_b", 40.0, 100.0, 100.0, 0.8)
        lane_2 = Hyperlane("LAN-02", "Hyperlane Route", "s_b", "s_c", 40.0, 100.0, 100.0, 0.8)
        
        self.router.build_network_graph(self.stars, [lane_1, lane_2], [], {}, global_avg_tech=5.0)
        chokepoints = TransitOptimizer.identify_chokepoints(self.router.graph, self.stars)
        
        # B (s_b) must have the highest strategic value score
        self.assertEqual(chokepoints[0]["star_id"], "s_b")
        self.assertEqual(chokepoints[0]["strategic_value_score"], 100.0)


if __name__ == "__main__":
    unittest.main()
