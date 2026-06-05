"""
technology_engine.py — TechnologyEngine class for the Galactic Dream Engine.

Phase 4: Civilization Evolution Engine.
Manages technology tiers, research output calculations, and tech level progression.
"""

from typing import Tuple, Dict
import numpy as np


class TechnologyEngine:
    """
    Manages technology progression, tech tiers, and research calculations.

    Attributes
    ----------
    random : np.random.RandomState
        NumPy random number generator for reproducible rolls.
    tech_tiers : Dict[int, Tuple[str, int]]
        Mapping of tech tier numbers (1-10) to their name and minimum research points requirement.
    """

    def __init__(self, seed: int = 42) -> None:
        """
        Initialize the TechnologyEngine with a specific random seed.

        Parameters
        ----------
        seed : int, default 42
            Seed for the NumPy RandomState.
        """
        self.random = np.random.RandomState(seed)
        self.tech_tiers: Dict[int, Tuple[str, int]] = {
            1: ("Industrial Age", 0),
            2: ("Digital Age", 1000),
            3: ("Space Age", 5000),
            4: ("Interplanetary Age", 20000),
            5: ("Interstellar Age", 100000),
            6: ("Fusion Civilization", 500000),
            7: ("Antimatter Civilization", 2500000),
            8: ("Dyson Swarm Civilization", 12500000),
            9: ("Galactic Civilization", 62500000),
            10: ("Transcendent Civilization", 312500000),
        }

    def calculate_research_output(
        self, population: float, intelligence: float, innovation_score: float
    ) -> float:
        """
        Compute the research points generated per simulation step.

        Parameters
        ----------
        population : float
            The current population of the civilization.
        intelligence : float
            The biological or artificial intelligence score of the species.
        innovation_score : float
            The governance innovation score (0 to 100).

        Returns
        -------
        float
            Research points generated, rounded to 2 decimal places.
        """
        research = population * 1e-9 * intelligence * (1.0 + innovation_score / 100.0)
        return float(round(research, 2))

    def update_technology(
        self, current_tech_level: float, current_research_points: float, research_added: float
    ) -> Tuple[float, float, int, str]:
        """
        Add research points and calculate new tech level, stage tier, and name.

        Parameters
        ----------
        current_tech_level : float
            The current float tech level of the civilization.
        current_research_points : float
            The current accumulated research points.
        research_added : float
            Research points to add.

        Returns
        -------
        Tuple[float, float, int, str]
            New tech level (float), new total research points, stage tier (int 1-10), and tier name.
        """
        new_research = max(0.0, current_research_points + research_added)
        
        # Determine the current tier (1-10) based on new research points
        stage_tier = 1
        for tier in sorted(self.tech_tiers.keys()):
            req = self.tech_tiers[tier][1]
            if new_research >= req:
                stage_tier = tier
            else:
                break
        
        stage_name = self.tech_tiers[stage_tier][0]
        
        # Calculate tech_level as a float
        if stage_tier < 10:
            req_current = self.tech_tiers[stage_tier][1]
            req_next = self.tech_tiers[stage_tier + 1][1]
            new_tech_level = stage_tier + (new_research - req_current) / (req_next - req_current)
        else:
            req_10 = self.tech_tiers[10][1]
            # Transcendence can go slightly above 10
            new_tech_level = 10.0 + (new_research - req_10) / req_10
            
        return float(round(new_tech_level, 4)), float(round(new_research, 2)), stage_tier, stage_name
