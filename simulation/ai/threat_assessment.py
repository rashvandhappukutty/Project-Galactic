"""
threat_assessment.py — Calculates threat scores for Civilization Agents.
"""

from typing import List, Dict, Any
import numpy as np
from simulation.ai.strategic_planner import CivilizationAgent


class ThreatAssessmentEngine:
    """Evaluates the internal and external threats facing a civilization agent."""

    def __init__(self, proximity_threshold: float = 150.0) -> None:
        """Initialize threat assessment engine.

        Parameters
        ----------
        proximity_threshold : float
            Maximum distance (in light-years) to consider a neighbor for threats.
        """
        self.proximity_threshold = proximity_threshold

    def calculate_distance(self, c1: tuple, c2: tuple) -> float:
        """Calculate Euclidean distance between two 3D coordinates.

        Parameters
        ----------
        c1 : tuple
        c2 : tuple

        Returns
        -------
        float
            Distance in light-years.
        """
        return float(np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2))

    def evaluate_threat(
        self,
        agent: CivilizationAgent,
        all_agents: Dict[str, CivilizationAgent],
        planet_resource_score: float,
    ) -> Dict[str, Any]:
        """Compute the threat score and return breakdown factors.

        Parameters
        ----------
        agent : CivilizationAgent
            The agent for whom the threat is calculated.
        all_agents : Dict[str, CivilizationAgent]
            Registry of all agents in the galaxy.
        planet_resource_score : float
            Home planet resource score (0.0 to 100.0).

        Returns
        -------
        Dict[str, Any]
            Containing 'threat_score' (0-100) and component weights.
        """
        if agent.is_extinct:
            return {
                "threat_score": 0.0,
                "rival_factor": 0.0,
                "instability_factor": 0.0,
                "resource_factor": 0.0,
                "tech_factor": 0.0,
            }

        # --- 1. External Rival Proximity Threat ---
        neighbor_threats = []
        tech_disparities = []

        for other_id, other in all_agents.items():
            if other_id == agent.civilization_id or other.is_extinct:
                continue

            dist = self.calculate_distance(agent.coordinates, other.coordinates)
            if dist > self.proximity_threshold:
                continue

            # Skip allies
            if other_id in agent.allies:
                continue

            # Calculate individual threat from this neighbor
            # Closer and more aggressive = higher threat
            closeness = 1.0 - (dist / self.proximity_threshold)
            
            # Base threat proportional to rival aggression and closeness
            base_threat = 100.0 * closeness * (other.aggression / 100.0)

            # Population ratio multiplier
            pop_ratio = other.population / max(1.0, agent.population)
            pop_mult = min(2.0, max(0.5, pop_ratio))
            base_threat *= pop_mult

            # Amplified if currently at war
            if other_id in agent.wars:
                base_threat *= 1.5

            neighbor_threats.append(base_threat)

            # Record tech disparities for neighbors
            if other.technology_level > agent.technology_level:
                tech_disparities.append(other.technology_level - agent.technology_level)

        # Calculate final rival threat factor (max 50 points)
        if neighbor_threats:
            # Maximum individual threat + 10% of sum of other threats, capped at 50
            rival_factor = max(neighbor_threats) + 0.1 * sum(neighbor_threats)
            rival_factor = min(50.0, rival_factor)
        else:
            rival_factor = 0.0

        # --- 2. Internal Instability Vulnerability (max 25 points) ---
        # Low stability = high vulnerability
        instability_factor = 25.0 * (1.0 - agent.stability / 100.0)

        # --- 3. Resource Scarcity Threat (max 15 points) ---
        # Combines own planet resource score and agent current resource stocks
        res_stock_factor = max(0.0, 1.0 - agent.resources / 1000.0)
        planet_res_factor = 1.0 - planet_resource_score / 100.0
        resource_factor = 15.0 * (0.4 * res_stock_factor + 0.6 * planet_res_factor)

        # --- 4. Asymmetric Tech Risk (max 10 points) ---
        # Disparity relative to neighbors
        if tech_disparities:
            max_disparity = max(tech_disparities)
            tech_factor = min(10.0, max_disparity * 2.0)
        else:
            tech_factor = 0.0

        # Total score
        threat_score = rival_factor + instability_factor + resource_factor + tech_factor
        threat_score = max(0.0, min(100.0, threat_score))

        return {
            "threat_score": round(threat_score, 2),
            "rival_factor": round(rival_factor, 2),
            "instability_factor": round(instability_factor, 2),
            "resource_factor": round(resource_factor, 2),
            "tech_factor": round(tech_factor, 2),
        }
