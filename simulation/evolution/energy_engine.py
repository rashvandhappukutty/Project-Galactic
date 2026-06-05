"""
energy_engine.py — EnergyEngine class for the Galactic Dream Engine.

Phase 4: Civilization Evolution Engine.
Manages civilization energy sources, power output, and Kardashev rating calculations.
"""

import math
from typing import Tuple, List, Dict
import numpy as np


class EnergyEngine:
    """
    Manages energy technologies, calculating energy output and Kardashev ratings.

    Attributes
    ----------
    random : np.random.RandomState
        NumPy random number generator for reproducible rolls.
    energy_sources : List[str]
        List of supported energy source types.
    base_watts : Dict[str, float]
        Mapping of energy sources to their baseline power output in Watts.
    """

    def __init__(self, seed: int = 42) -> None:
        """
        Initialize the EnergyEngine with a specific random seed.

        Parameters
        ----------
        seed : int, default 42
            Seed for the NumPy RandomState.
        """
        self.random = np.random.RandomState(seed)
        self.energy_sources: List[str] = [
            "Fossil",
            "Nuclear",
            "Fusion",
            "Antimatter",
            "Dyson Swarm",
            "Dyson Sphere",
            "Galactic Energy Grid",
        ]
        self.base_watts: Dict[str, float] = {
            "Fossil": 1e11,
            "Nuclear": 1e14,
            "Fusion": 1e18,
            "Antimatter": 1e22,
            "Dyson Swarm": 1e26,
            "Dyson Sphere": 1e30,
            "Galactic Energy Grid": 1e35,
        }

    def update_energy_source(self, tech_level: float) -> str:
        """
        Determine the appropriate energy source based on the tech level.

        Parameters
        ----------
        tech_level : float
            The current tech level of the civilization.

        Returns
        -------
        str
            The primary energy source name.
        """
        if tech_level < 2.5:
            return "Fossil"
        elif tech_level < 4.5:
            return "Nuclear"
        elif tech_level < 6.5:
            return "Fusion"
        elif tech_level < 7.8:
            return "Antimatter"
        elif tech_level < 8.8:
            return "Dyson Swarm"
        elif tech_level < 9.5:
            return "Dyson Sphere"
        else:
            return "Galactic Energy Grid"

    def calculate_kardashev(self, energy_source: str, tech_level: float) -> Tuple[float, float]:
        """
        Compute energy output in Watts and the Kardashev scale rating.

        Parameters
        ----------
        energy_source : str
            The primary energy source type.
        tech_level : float
            The current tech level.

        Returns
        -------
        Tuple[float, float]
            A tuple of (energy output in Watts, Kardashev rating).
        """
        base = self.base_watts.get(energy_source, 1e11)
        # Power scales with tech level within its tier
        energy_output = base * (1.0 + tech_level * 0.5)
        
        # Kardashev scale formula: K = (log10(P) - 6) / 10
        kardashev_rating = (math.log10(energy_output) - 6.0) / 10.0
        
        return float(energy_output), float(round(kardashev_rating, 4))
