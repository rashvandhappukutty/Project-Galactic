"""
evolution_engine.py — EvolutionEngine class for the Galactic Dream Engine.

Phase 3 – Life Emergence Engine
"""

import numpy as np
from typing import Any, Dict


class EvolutionEngine:
    """Simulates biological evolution, stage progression, and extinction events.

    Uses a seeded NumPy RandomState for reproducible rolls.

    Parameters
    ----------
    seed : int, default 42
        Random seed for reproducibility.
    """

    def __init__(self, seed: int = 42) -> None:
        self.random = np.random.RandomState(seed)

    def simulate_evolution(
        self, planet: Any, star_system: Any, years: int
    ) -> Dict[str, Any]:
        """Simulate evolution on a planet over a given timeframe.

        Parameters
        ----------
        planet : Any
            The Planet object (e.g. simulation.planets.planet.Planet).
        star_system : Any
            The StarSystem object containing astrophysical parameters.
        years : int
            The timeframe in years (e.g., 1000, 10000, 100000, 1000000).

        Returns
        -------
        Dict[str, Any]
            A dictionary containing:
            - 'updated_stage' : int (0-5)
            - 'evolution_progress' : float (0-100)
            - 'extinction_occurred' : bool
            - 'species_complexity' : float (0-100)
            - 'technology_potential' : float (0-100)
        """
        # Fetch current stage and progress or default them
        current_stage = int(getattr(planet, "life_stage", 0))
        current_progress = float(getattr(planet, "evolution_progress", 0.0))

        # 1. Extinction Probability (P_ext)
        # Base: 0.01 per 100,000 years. Scale to simulation duration
        base_extinction_rate = 0.01 * (years / 100000.0)
        rate = base_extinction_rate

        # Modifiers
        # Host star type: M-type has flare risk (* 1.5). O/B has high UV (* 2.0)
        star_type = str(getattr(star_system, "star_type", "")).upper()
        if star_type.startswith("M"):
            rate *= 1.5
        elif star_type.startswith("O") or star_type.startswith("B"):
            rate *= 2.0

        # Radiation level: multiply by (1.0 + radiation_level / 100.0)
        radiation = float(getattr(star_system, "radiation_level", 0.0))
        rate *= (1.0 + radiation / 100.0)

        # Temperature: extreme (< 180K or > 380K) multiply by 1.3
        temperature = float(getattr(planet, "temperature", 288.0))
        if temperature < 180.0 or temperature > 380.0:
            rate *= 1.3

        # Clamp rate to [0.0, 1.0] for safe probability roll
        rate = max(0.0, min(rate, 1.0))

        # Roll for extinction event
        extinction_occurred = bool(self.random.uniform(0.0, 1.0) < rate)

        if extinction_occurred:
            # Reduce life stage by 1 or 2 (clamped to min 0)
            reduction = int(self.random.choice([1, 2]))
            current_stage = max(0, current_stage - reduction)
            new_progress = 0.0
        else:
            # Calculate evolution progress delta
            # delta = base_rate * (habitability_score / 50.0) * (1.0 + metallicity) * (years / 10,000)
            base_rate = 10.0
            habitability_score = float(getattr(planet, "habitability_score", 0.0))
            metallicity = float(getattr(star_system, "metallicity", 0.0))
            delta = (
                base_rate
                * (habitability_score / 50.0)
                * (1.0 + metallicity)
                * (years / 10000.0)
            )

            new_progress = current_progress + delta

            # Age restrictions:
            # stage cannot exceed 1 if system_age < 1.0 Gyr
            # stage cannot exceed 0 if system_age < 0.1 Gyr
            system_age = float(getattr(star_system, "age_billion_years", 0.0))
            if system_age < 0.1:
                max_allowed_stage = 0
            elif system_age < 1.0:
                max_allowed_stage = 1
            else:
                max_allowed_stage = 5

            if new_progress >= 100.0:
                if current_stage < max_allowed_stage:
                    stages_gained = int(new_progress // 100.0)
                    potential_stage = current_stage + stages_gained
                    if potential_stage > max_allowed_stage:
                        current_stage = max_allowed_stage
                        new_progress = 99.9  # Capped because we hit age limits
                    else:
                        current_stage = potential_stage
                        new_progress = new_progress % 100.0
                else:
                    # Already at or above age-limited stage
                    current_stage = min(current_stage, max_allowed_stage)
                    new_progress = 99.9

        # Ensure correct type/clamps for stage and progress
        current_stage = max(0, min(current_stage, 5))
        new_progress = max(0.0, min(new_progress, 100.0))

        # Calculate species complexity (0-100, scaling with stage and age)
        # stage * 15 + min(system_age * 2, 25)
        system_age = float(getattr(star_system, "age_billion_years", 0.0))
        species_complexity = current_stage * 15.0 + min(system_age * 2.0, 25.0)
        species_complexity = max(0.0, min(species_complexity, 100.0))

        # Calculate technology potential
        # 0 for stages < 4, otherwise: stage * 10 + resource_score * 0.3 + U(0, 20)
        if current_stage < 4:
            technology_potential = 0.0
        else:
            resource_score = float(getattr(planet, "resource_score", 0.0))
            u_val = float(self.random.uniform(0.0, 20.0))
            technology_potential = (
                current_stage * 10.0 + resource_score * 0.3 + u_val
            )
            technology_potential = max(0.0, min(technology_potential, 100.0))

        # Update planet state dynamically
        setattr(planet, "life_stage", current_stage)
        setattr(planet, "evolution_progress", new_progress)
        setattr(planet, "extinction_occurred", extinction_occurred)
        setattr(planet, "species_complexity", species_complexity)
        setattr(planet, "technology_potential", technology_potential)

        return {
            "updated_stage": current_stage,
            "evolution_progress": new_progress,
            "extinction_occurred": extinction_occurred,
            "species_complexity": species_complexity,
            "technology_potential": technology_potential,
        }
