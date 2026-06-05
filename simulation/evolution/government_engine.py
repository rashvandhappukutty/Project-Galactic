"""
government_engine.py — GovernmentEngine class for the Galactic Dream Engine.

Phase 4: Civilization Evolution Engine.
Manages civilization politics, stability, corruption, innovation, and government reform rolls.
"""

import math
from typing import Tuple, Dict, NamedTuple
import numpy as np


class GovProfile(NamedTuple):
    """
    Profile defining a government type's modifiers.

    Attributes
    ----------
    stability_mod : float
        Modifier for stability updates.
    innovation_mod : float
        Modifier for innovation updates.
    corruption_mod : float
        Modifier for corruption updates.
    """
    stability_mod: float
    innovation_mod: float
    corruption_mod: float


class GovernmentEngine:
    """
    Simulates the internal politics, stability, corruption, and innovation of a civilization.

    Attributes
    ----------
    random : np.random.RandomState
        NumPy random number generator for reproducible rolls.
    profiles : Dict[str, GovProfile]
        Mapping of government type strings to their respective GovProfile modifiers.
    """

    DEFAULT_PROFILE = GovProfile(stability_mod=1.0, innovation_mod=1.0, corruption_mod=1.0)

    def __init__(self, seed: int = 42) -> None:
        """
        Initialize the GovernmentEngine with a specific random seed.

        Parameters
        ----------
        seed : int, default 42
            Seed for the NumPy RandomState.
        """
        self.random = np.random.RandomState(seed)
        self.profiles: Dict[str, GovProfile] = {
            "Democracy": GovProfile(stability_mod=1.0, innovation_mod=1.2, corruption_mod=0.7),
            "Technocracy": GovProfile(stability_mod=0.9, innovation_mod=1.5, corruption_mod=0.9),
            "Federation": GovProfile(stability_mod=1.2, innovation_mod=1.0, corruption_mod=0.8),
            "Monarchy": GovProfile(stability_mod=0.8, innovation_mod=0.7, corruption_mod=1.3),
            "Collective": GovProfile(stability_mod=1.1, innovation_mod=0.9, corruption_mod=1.1),
            "AI Governance": GovProfile(stability_mod=1.3, innovation_mod=1.3, corruption_mod=0.1),
            "Scientific Council": GovProfile(stability_mod=1.0, innovation_mod=1.4, corruption_mod=0.8),
        }

    def update_stability(
        self, gov_type: str, current_stability: float, pop_carrying_ratio: float, corruption: float
    ) -> float:
        """
        Calculate the updated stability score for a civilization.

        Parameters
        ----------
        gov_type : str
            The government type of the civilization.
        current_stability : float
            The current stability score (0 to 100).
        pop_carrying_ratio : float
            The ratio of population to carrying capacity.
        corruption : float
            The current corruption score (0 to 100).

        Returns
        -------
        float
            The updated stability score clamped to [0, 100].
        """
        pop_pressure = max(0.0, pop_carrying_ratio - 0.8) * 15.0
        corruption_penalty = corruption * 0.15
        base_change = float(self.random.uniform(-3.0, 3.0))
        profile = self.profiles.get(gov_type, self.DEFAULT_PROFILE)
        
        new_stability = current_stability + base_change * profile.stability_mod - pop_pressure - corruption_penalty
        return float(max(0.0, min(100.0, new_stability)))

    def update_corruption(
        self, gov_type: str, current_corruption: float, population: float, stability: float
    ) -> float:
        """
        Calculate the updated corruption score for a civilization.

        Parameters
        ----------
        gov_type : str
            The government type of the civilization.
        current_corruption : float
            The current corruption score (0 to 100).
        population : float
            The current population of the civilization.
        stability : float
            The current stability score (0 to 100).

        Returns
        -------
        float
            The updated corruption score clamped to [0, 100].
        """
        pop_factor = math.log10(max(1.0, population)) * 0.5
        stability_benefit = (stability - 50.0) * 0.1
        profile = self.profiles.get(gov_type, self.DEFAULT_PROFILE)
        base_change = float(self.random.uniform(0.5, 2.0)) * profile.corruption_mod
        
        new_corruption = current_corruption + base_change + pop_factor - stability_benefit
        return float(max(0.0, min(100.0, new_corruption)))

    def update_innovation(self, gov_type: str, intelligence: float, corruption: float) -> float:
        """
        Calculate the updated innovation score for a civilization.

        Parameters
        ----------
        gov_type : str
            The government type of the civilization.
        intelligence : float
            The species intelligence.
        corruption : float
            The current corruption score.

        Returns
        -------
        float
            The updated innovation score clamped to [0, 100].
        """
        profile = self.profiles.get(gov_type, self.DEFAULT_PROFILE)
        corruption_penalty = corruption * 0.2
        innovation = (intelligence * 0.5 + float(self.random.uniform(0.0, 15.0))) * profile.innovation_mod - corruption_penalty
        return float(max(0.0, min(100.0, innovation)))

    def roll_government_reform(
        self, gov_type: str, stability: float, cooperation: float, intelligence: float, aggression: float
    ) -> Tuple[bool, str]:
        """
        Evaluate if a government reform or collapse triggers and rolls the new government.

        Parameters
        ----------
        gov_type : str
            The current government type.
        stability : float
            The current stability score (0 to 100).
        cooperation : float
            The species cooperation score.
        intelligence : float
            The species intelligence score.
        aggression : float
            The species aggression score.

        Returns
        -------
        Tuple[bool, str]
            Whether a reform occurred (bool) and the new/existing government type (str).
        """
        reformed = False
        
        # 1. Check for collapse due to low stability (< 20.0 with 40% chance)
        if stability < 20.0:
            if self.random.random() < 0.4:
                reformed = True
        
        # 2. Check for periodic reform chance (2% chance)
        if not reformed and self.random.random() < 0.02:
            reformed = True

        if reformed:
            weights = {
                "Democracy": 10.0,
                "Technocracy": 10.0,
                "Federation": 10.0,
                "Monarchy": 10.0,
                "Collective": 10.0,
                "AI Governance": 5.0,
                "Scientific Council": 10.0,
            }
            if cooperation > 60.0:
                weights["Democracy"] += (cooperation - 60.0) * 1.5
                weights["Federation"] += (cooperation - 60.0) * 1.0
            if cooperation < 40.0:
                weights["Monarchy"] += (40.0 - cooperation) * 1.5
            if intelligence > 60.0:
                weights["Technocracy"] += (intelligence - 60.0) * 1.0
                weights["Scientific Council"] += (intelligence - 60.0) * 1.0
            if aggression > 60.0:
                weights["Collective"] += (aggression - 60.0) * 1.5
            if intelligence > 80.0:
                weights["AI Governance"] += (intelligence - 80.0) * 1.2
                
            gov_list = list(weights.keys())
            weight_values = np.array([weights[g] for g in gov_list], dtype=np.float64)
            weight_values = np.clip(weight_values, 0.1, None)  # Safety floor
            weight_values /= weight_values.sum()
            
            new_gov = str(self.random.choice(gov_list, p=weight_values))
            return True, new_gov

        return False, gov_type
