"""
hyperlane_network.py — Hyperlane grid creation, patrolled corridors, and classifications.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Tuple
import math
import numpy as np


@dataclass
class Hyperlane:
    """Represents a standard hyperlane transit connection between two stars.

    Attributes
    ----------
    lane_id : str
    lane_type : str
        "Hyperlane Route", "Deep Space Corridor", "Trade Artery", or "Military Corridor"
    source_star_id : str
    target_star_id : str
    route_length : float
        Euclidean distance in light-years.
    traffic : float
        Ships traversal index per tick.
    economic_value : float
        Economic value carried per tick.
    security_level : float
        Patrol safety rating (0.0 to 1.0).
    """

    lane_id: str
    lane_type: str
    source_star_id: str
    target_star_id: str
    route_length: float
    traffic: float
    economic_value: float
    security_level: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert hyperlane state into a serializable dictionary."""
        return {
            "lane_id": self.lane_id,
            "lane_type": self.lane_type,
            "source_star_id": self.source_star_id,
            "target_star_id": self.target_star_id,
            "route_length_ly": round(self.route_length, 2),
            "traffic_index": round(self.traffic, 2),
            "economic_value": round(self.economic_value, 2),
            "security_level": round(self.security_level, 3),
        }


class HyperlaneNetwork:
    """Generates K-Nearest Neighbors hyperlane network meshes across the galaxy."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.random = np.random.RandomState(seed)

    def generate_hyperlanes(
        self,
        stars: Dict[str, Dict[str, Any]],
        empires: List[Dict[str, Any]],
        colonies: List[Dict[str, Any]],
        k_neighbors: int = 3,
        max_distance: float = 60.0
    ) -> List[Hyperlane]:
        """Generate a hyperlane network mesh linking adjacent systems.

        Parameters
        ----------
        stars : Dict[str, Dict[str, Any]]
        empires : List[Dict[str, Any]]
        colonies : List[Dict[str, Any]]
        k_neighbors : int
            K parameter for nearest neighbor links.
        max_distance : float
            Maximum distance constraint in light-years.

        Returns
        -------
        List[Hyperlane]
            List of generated hyperlanes.
        """
        hyperlanes: List[Hyperlane] = []
        star_ids = list(stars.keys())
        num_stars = len(star_ids)

        if num_stars < 2:
            return hyperlanes

        # Pre-cache coordinates
        coords = {sid: (float(stars[sid]["x"]), float(stars[sid]["y"]), float(stars[sid]["z"])) for sid in star_ids}
        
        # Build maps of capitals and colony systems
        capital_stars = {str(e["founding_civilization_id"]): str(self._find_home_star(e, colonies, stars)) for e in empires}
        colony_stars = {str(col["target_planet_id"]): str(col["home_star_id"]) for col in colonies}

        # Build list of active border stars for militarized empires
        militaristic_capitals = set()
        for e in empires:
            # We classify militaristic based on names or power indicators
            if "Star Empire" in str(e["empire_name"]) or "Hegemony" in str(e["empire_name"]):
                militaristic_capitals.add(capital_stars.get(str(e["founding_civilization_id"])))

        # Track existing edges to avoid duplicates
        existing_edges = set()
        lane_counter = 1

        for i in range(num_stars):
            src_id = star_ids[i]
            src_coords = coords[src_id]
            src_star = stars[src_id]

            # Calculate distances to all other stars
            dists = []
            for j in range(num_stars):
                if i == j:
                    continue
                tgt_id = star_ids[j]
                tgt_coords = coords[tgt_id]
                dx = src_coords[0] - tgt_coords[0]
                dy = src_coords[1] - tgt_coords[1]
                dz = src_coords[2] - tgt_coords[2]
                d = math.sqrt(dx*dx + dy*dy + dz*dz)
                dists.append((tgt_id, d))

            # Sort by distance and take K nearest within max_distance threshold
            dists.sort(key=lambda x: x[1])
            nearest = [item for item in dists if item[1] <= max_distance][:k_neighbors]

            for tgt_id, dist in nearest:
                edge_key = tuple(sorted([src_id, tgt_id]))
                if edge_key in existing_edges:
                    continue

                existing_edges.add(edge_key)

                # Classify Lane Type
                tgt_star = stars[tgt_id]
                src_region = src_star.get("region", "Void")
                tgt_region = tgt_star.get("region", "Void")
                
                # Check if this lane links high-value capitals
                is_capital_link = (src_id in capital_stars.values() and tgt_id in capital_stars.values())
                is_colony_link = (src_id in capital_stars.values() and tgt_id in colony_stars.values()) or \
                                 (tgt_id in capital_stars.values() and src_id in colony_stars.values())

                if is_capital_link:
                    lane_type = "Trade Artery"
                    traffic = float(self.random.uniform(500.0, 1500.0))
                    econ_val = traffic * 2.5
                    security = float(self.random.uniform(0.80, 0.98))
                elif src_id in militaristic_capitals or tgt_id in militaristic_capitals:
                    lane_type = "Military Corridor"
                    traffic = float(self.random.uniform(300.0, 800.0))
                    econ_val = traffic * 1.0
                    security = float(self.random.uniform(0.85, 0.99))
                elif src_region == "Rim" or tgt_region == "Rim":
                    lane_type = "Deep Space Corridor"
                    traffic = float(self.random.uniform(10.0, 150.0))
                    econ_val = traffic * 0.5
                    security = float(self.random.uniform(0.15, 0.50))
                else:
                    lane_type = "Hyperlane Route"
                    traffic = float(self.random.uniform(100.0, 500.0))
                    econ_val = traffic * 1.2
                    security = float(self.random.uniform(0.50, 0.85))

                lane = Hyperlane(
                    lane_id=f"LAN-{lane_counter:05d}",
                    lane_type=lane_type,
                    source_star_id=src_id,
                    target_star_id=tgt_id,
                    route_length=dist,
                    traffic=traffic,
                    economic_value=econ_val,
                    security_level=security,
                )
                hyperlanes.append(lane)
                lane_counter += 1

        return hyperlanes

    def _find_home_star(self, empire: Dict[str, Any], colonies: List[Dict[str, Any]], stars: Dict[str, Dict[str, Any]]) -> str:
        """Helper to find home star of an empire capital."""
        cap_world = str(empire["capital_world"])
        # Check colonies first
        for col in colonies:
            if str(col["colony_name"]) == cap_world:
                return str(col["home_star_id"])
        
        # Fallback to matching coordinates or matching names in stars
        for sid, star in stars.items():
            if str(star["name"]) in cap_world:
                return sid
        
        # Default first star ID
        return list(stars.keys())[0]
