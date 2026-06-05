"""
expansion_planner.py — Evaluates potential planet targets for colonization.
"""

import math
from typing import List, Dict, Any, Tuple
from simulation.ai.strategic_planner import CivilizationAgent


class ExpansionPlanner:
    """Calculates colonization scores for target planets to assist agent expansion choices."""

    def __init__(self, max_range_ly: float = 250.0) -> None:
        """Initialize expansion planner.

        Parameters
        ----------
        max_range_ly : float
            Maximum distance (in light-years) an agent can expand from its nearest settled star system.
        """
        self.max_range_ly = max_range_ly

    def calculate_distance(self, c1: Tuple[float, float, float], c2: Tuple[float, float, float]) -> float:
        """Calculate Euclidean distance between two 3D coordinates.

        Parameters
        ----------
        c1 : Tuple[float, float, float]
        c2 : Tuple[float, float, float]

        Returns
        -------
        float
        """
        return float(math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2))

    def score_targets(
        self,
        agent: CivilizationAgent,
        unoccupied_planets: List[Dict[str, Any]],
        stars_dict: Dict[str, Dict[str, Any]],
        all_agents: Dict[str, CivilizationAgent],
        planet_star_coords_map: Dict[str, Tuple[float, float, float]],
    ) -> List[Tuple[Dict[str, Any], float]]:
        """Score all unoccupied planets for colonization and sort by score.

        Parameters
        ----------
        agent : CivilizationAgent
            The agent looking to expand.
        unoccupied_planets : List[Dict[str, Any]]
            Planets currently unclaimed.
        stars_dict : Dict[str, Dict[str, Any]]
            Stars coordinate database.
        all_agents : Dict[str, CivilizationAgent]
            Active agents registry.
        planet_star_coords_map : Dict[str, Tuple[float, float, float]]
            Lookup mapping planet_id -> star (x, y, z) coordinates.

        Returns
        -------
        List[Tuple[Dict[str, Any], float]]
            List of (planet, score) sorted descending by score.
        """
        scored_targets = []

        # Resolve agent's settled system coordinates (home star + colonies' stars)
        settled_coords_list = []
        home_star = stars_dict.get(agent.home_star_id)
        if home_star:
            settled_coords_list.append((float(home_star["x"]), float(home_star["y"]), float(home_star["z"])))

        for col_planet_id in agent.colonies:
            coords = planet_star_coords_map.get(col_planet_id)
            if coords:
                settled_coords_list.append(coords)

        if not settled_coords_list:
            return []

        # Pre-calculate active rival positions (to calculate threat penalties)
        rivals = []
        for other_id, other in all_agents.items():
            if other_id == agent.civilization_id or other.is_extinct:
                continue
            other_home = stars_dict.get(other.home_star_id)
            if other_home:
                r_coords = (float(other_home["x"]), float(other_home["y"]), float(other_home["z"]))
                rivals.append((other_id, other.aggression, r_coords))

        for p in unoccupied_planets:
            # Optimize: filter out non-habitable targets before distance calculations
            habitability = float(p.get("habitability_score", 0.0))
            if habitability < 40.0:  # Ignore completely uninhabitable targets
                continue

            planet_id = str(p["planet_id"])
            p_coords = planet_star_coords_map.get(planet_id)
            if not p_coords:
                continue

            # 1. Proximity Check: find distance to nearest settled star system
            min_dist = min(self.calculate_distance(s_coords, p_coords) for s_coords in settled_coords_list)
            
            # If target exceeds maximum range, ignore
            if min_dist > self.max_range_ly:
                continue

            dist_factor = (1.0 - (min_dist / self.max_range_ly)) * 35.0
            habitability_factor = (habitability / 100.0) * 35.0

            # 3. Resource Factor (max 20 points)
            resources = float(p.get("resource_score", 0.0))
            resource_factor = (resources / 100.0) * 20.0

            # 4. Proximity threat penalty (max -15 points)
            # If target planet is close to aggressive neighbors, reduce score
            threat_penalty = 0.0
            for r_id, r_agg, r_coords in rivals:
                r_dist = self.calculate_distance(r_coords, p_coords)
                if r_dist < 100.0:
                    # Scale penalty with rival aggression and proximity
                    closeness = 1.0 - (r_dist / 100.0)
                    penalty = closeness * (r_agg / 100.0) * 10.0
                    
                    # Amplified if currently at war
                    if r_id in agent.wars:
                        penalty *= 1.5
                    
                    threat_penalty += penalty

            threat_penalty = min(15.0, threat_penalty)

            # 5. Strategic / Personality modifiers (max 10 points)
            personality_bonus = 0.0
            p_type = agent.personality
            if p_type == "Expansionist":
                personality_bonus += 5.0
            elif p_type == "Explorer":
                # Explorers prefer distant systems
                personality_bonus += (min_dist / self.max_range_ly) * 8.0
            elif p_type == "Militaristic":
                # Prefer resource-rich outposts
                personality_bonus += (resources / 100.0) * 6.0
            elif p_type == "Industrialist":
                personality_bonus += (resources / 100.0) * 5.0

            # Total score
            score = dist_factor + habitability_factor + resource_factor - threat_penalty + personality_bonus
            score = max(0.0, min(100.0, score))

            scored_targets.append((p, round(score, 2)))

        # Sort descending by score
        scored_targets.sort(key=lambda x: x[1], reverse=True)
        return scored_targets
