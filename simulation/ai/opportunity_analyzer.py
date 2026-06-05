"""
opportunity_analyzer.py — Calculates opportunity scores for Civilization Agents.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from simulation.ai.strategic_planner import CivilizationAgent


class OpportunityAnalyzer:
    """Evaluates the galactic opportunities available to a civilization agent."""

    def __init__(self, proximity_threshold: float = 150.0) -> None:
        """Initialize opportunity analyzer.

        Parameters
        ----------
        proximity_threshold : float
            Maximum distance (in light-years) to search for nearby opportunities.
        """
        self.proximity_threshold = proximity_threshold

    def calculate_distance(self, c1: tuple, c2: tuple) -> float:
        """Calculate Euclidean distance between two 3D coordinates."""
        return float(np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2))

    def evaluate_opportunity(
        self,
        agent: CivilizationAgent,
        all_agents: Dict[str, CivilizationAgent],
        all_planets: List[Dict[str, Any]],
        stars_dict: Dict[str, Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Compute the opportunity score and return breakdown factors.

        Parameters
        ----------
        agent : CivilizationAgent
            The agent for whom the opportunity is calculated.
        all_agents : Dict[str, CivilizationAgent]
            Registry of all agents in the galaxy.
        all_planets : List[Dict[str, Any]]
            List of all planet dictionaries.
        stars_dict : Dict[str, Dict[str, Any]]
            Lookup mapping star ID to star coordinates.

        Returns
        -------
        Dict[str, Any]
            Containing 'opportunity_score' (0-100) and component weights.
        """
        if agent.is_extinct:
            return {
                "opportunity_score": 0.0,
                "expansion_factor": 0.0,
                "trade_factor": 0.0,
                "tech_factor": 0.0,
                "energy_factor": 0.0,
            }

        # --- 1. Expansion Potential (max 40 points) ---
        # Search for unoccupied planets within proximity threshold with high habitability
        expansion_values = []
        
        # Track which planets are currently occupied by any active agents
        occupied_planets = set()
        for other in all_agents.values():
            if other.is_extinct:
                continue
            occupied_planets.add(other.home_planet_id)
            for col in other.colonies:
                occupied_planets.add(col)

        for p in all_planets:
            planet_id = str(p["planet_id"])
            if planet_id in occupied_planets:
                continue

            # Optimize by filtering out non-habitable planets before distance calculations!
            habitability = float(p.get("habitability_score", 0.0))
            if habitability <= 40.0:
                continue

            star_id = str(p["star_id"])
            star_info = stars_dict.get(star_id)
            if not star_info:
                continue

            p_coords = (float(star_info["x"]), float(star_info["y"]), float(star_info["z"]))
            dist = self.calculate_distance(agent.coordinates, p_coords)
            
            if dist > self.proximity_threshold:
                continue

            # Closer and more habitable = higher opportunity
            closeness = 1.0 - (dist / self.proximity_threshold)
            val = closeness * (habitability / 100.0) * 15.0
            expansion_values.append(val)

        # Sum values and clamp at 40
        expansion_factor = min(40.0, sum(expansion_values)) if expansion_values else 0.0

        # --- 2. Diplomatic & Trade Openings (max 30 points) ---
        # Search for cooperative, peaceful neighbors nearby
        diplomatic_values = []
        
        for other_id, other in all_agents.items():
            if other_id == agent.civilization_id or other.is_extinct:
                continue

            dist = self.calculate_distance(agent.coordinates, other.coordinates)
            if dist > self.proximity_threshold:
                continue

            # Neighbors we are already allied with or at war with offer different dynamics
            # Friendly neighbors represent an alliance/trade opportunity
            closeness = 1.0 - (dist / self.proximity_threshold)
            
            # Cooperative traits favor alliance/trade opportunities
            if other_id not in agent.wars:
                val = closeness * (other.cooperation / 100.0) * (1.0 - other.aggression / 200.0) * 10.0
                diplomatic_values.append(val)

        trade_factor = min(30.0, sum(diplomatic_values)) if diplomatic_values else 0.0

        # --- 3. Research & Technical Capacity (max 20 points) ---
        # High curiosity/intelligence and technological headroom
        tech_factor = 20.0 * (agent.curiosity / 100.0) * (0.5 + agent.technology_level / 20.0)
        tech_factor = min(20.0, tech_factor)

        # --- 4. Energy & Megastructure Construction Capacity (max 10 points) ---
        # If the agent has tech level >= 5.0 and is not currently building or has incomplete megastructure
        if agent.technology_level >= 5.0:
            if not agent.megastructure_type:
                energy_factor = 10.0
            elif agent.megastructure_progress < 100.0:
                energy_factor = 5.0 * (1.0 - agent.megastructure_progress / 100.0)
            else:
                energy_factor = 2.0  # Can build another upgrade later
        else:
            energy_factor = 0.0

        # Combined score
        opportunity_score = expansion_factor + trade_factor + tech_factor + energy_factor
        opportunity_score = max(0.0, min(100.0, opportunity_score))

        return {
            "opportunity_score": round(opportunity_score, 2),
            "expansion_factor": round(expansion_factor, 2),
            "trade_factor": round(trade_factor, 2),
            "tech_factor": round(tech_factor, 2),
            "energy_factor": round(energy_factor, 2),
        }
