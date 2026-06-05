"""
route_calculator.py — Shortest path FTL routing solvers and path registers.
"""

from typing import Dict, List, Any, Tuple
import math
import networkx as nx

from simulation.ftl.wormhole_generator import Wormhole
from simulation.ftl.hyperlane_network import Hyperlane
from simulation.ftl.jump_gate_engine import JumpGate


class RouteCalculator:
    """Calculates shortest path FTL travel times combining warp, lanes, wormholes, and relays."""

    def __init__(self) -> None:
        self.graph = nx.Graph()

    def build_network_graph(
        self,
        stars: Dict[str, Dict[str, Any]],
        hyperlanes: List[Hyperlane],
        wormholes: List[Wormhole],
        gates: Dict[str, JumpGate],
        global_avg_tech: float
    ) -> None:
        """Construct a weighted NetworkX graph where edge weights represent travel time in years.

        Parameters
        ----------
        stars : Dict[str, Dict[str, Any]]
        hyperlanes : List[Hyperlane]
        wormholes : List[Wormhole]
        gates : Dict[str, JumpGate]
        global_avg_tech : float
            Used to determine base FTL speeds.
        """
        self.graph.clear()

        # Add all star systems as nodes
        for star_id in stars:
            self.graph.add_node(star_id)

        # 1. Base Warp flight travel
        # Speed = 1.0 LY/year (basic) or 2.0 LY/year (L2 warp tech)
        warp_speed = 2.0 if global_avg_tech >= 3.0 else 1.0
        
        # Connect each star to its 3 nearest neighbors via warp flight (to ensure base connectivity)
        star_ids = list(stars.keys())
        coords = {sid: (float(stars[sid]["x"]), float(stars[sid]["y"]), float(stars[sid]["z"])) for sid in star_ids}
        
        for i, src_id in enumerate(star_ids):
            src_coords = coords[src_id]
            dists = []
            for j, tgt_id in enumerate(star_ids):
                if i == j:
                    continue
                tgt_coords = coords[tgt_id]
                dx = src_coords[0] - tgt_coords[0]
                dy = src_coords[1] - tgt_coords[1]
                dz = src_coords[2] - tgt_coords[2]
                d = math.sqrt(dx*dx + dy*dy + dz*dz)
                if d <= 120.0:  # Warp range limit
                    dists.append((tgt_id, d))
            
            dists.sort(key=lambda x: x[1])
            # Add top 3 warp neighbors
            for tgt_id, dist in dists[:3]:
                travel_time = dist / warp_speed
                # Add edge (if FTL speed is faster, it will overwrite or add duplicate which we handle by taking min)
                self.graph.add_edge(src_id, tgt_id, weight=travel_time, route_type="Warp Flight")

        # 2. Hyperlane Network (Speed = 5.0 LY/year)
        hyperlane_speed = 5.0
        for lane in hyperlanes:
            travel_time = lane.route_length / hyperlane_speed
            # Check if this edge is already added and if hyperlane is faster
            existing = self.graph.get_edge_data(lane.source_star_id, lane.target_star_id)
            if not existing or travel_time < existing["weight"]:
                self.graph.add_edge(
                    lane.source_star_id,
                    lane.target_star_id,
                    weight=travel_time,
                    route_type="Hyperlane"
                )

        # 3. Wormhole Shortcuts (Instantly jumps with nominal queue delay: 0.05 years)
        for w in wormholes:
            if w.stability > 0.1:  # Only traverse stable or non-collapsed wormholes
                travel_time = 0.05
                existing = self.graph.get_edge_data(w.entry_system, w.exit_system)
                if not existing or travel_time < existing["weight"]:
                    self.graph.add_edge(
                        w.entry_system,
                        w.exit_system,
                        weight=travel_time,
                        route_type="Wormhole"
                    )

        # 4. Jump Gate Relays (Instantly jumps with activation cooldown: 0.02 years)
        for gate in gates.values():
            for target_star_id in gate.connected_systems:
                travel_time = 0.02
                existing = self.graph.get_edge_data(gate.star_id, target_star_id)
                if not existing or travel_time < existing["weight"]:
                    self.graph.add_edge(
                        gate.star_id,
                        target_star_id,
                        weight=travel_time,
                        route_type="Jump Gate"
                    )

    def calculate_transit(self, source_star: str, target_star: str) -> Tuple[List[str], float]:
        """Compute the shortest FTL transit path and travel time in years.

        Parameters
        ----------
        source_star : str
        target_star : str

        Returns
        -------
        Tuple[List[str], float]
            Optimal path (list of star IDs) and travel time in years.
        """
        try:
            path = nx.shortest_path(self.graph, source=source_star, target=target_star, weight="weight")
            time = nx.shortest_path_length(self.graph, source=source_star, target=target_star, weight="weight")
            return path, float(time)
        except (nx.NetworkXNoPath, KeyError):
            return [], 999.0
