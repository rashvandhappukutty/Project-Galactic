"""
life_engine.py — Evaluates life emergence probability and stage for planets.

Contains the LifeEngine class which computes a 0-100 probability based on habitability,
water percentage, temperature, atmosphere type, and resources, and maps it to a life stage.

Phase 3: Life Emergence Engine.
"""

from typing import Dict, Any, Tuple, ClassVar


class LifeEngine:
    """
    Evaluates the probability of life emerging on a planet and determines its developmental stage.
    
    Attributes
    ----------
    thresholds : Dict[int, Tuple[float, float]]
        A dictionary mapping developmental stages (0 to 5) to their lower and upper bounds.
    """

    DEFAULT_THRESHOLDS: ClassVar[Dict[int, Tuple[float, float]]] = {
        0: (0.0, 15.0),
        1: (15.0, 40.0),
        2: (40.0, 65.0),
        3: (65.0, 85.0),
        4: (85.0, 95.0),
        5: (95.0, 100.0),
    }

    def __init__(self, thresholds: Dict[int, Tuple[float, float]] = None) -> None:
        """
        Initialize the LifeEngine with configurable thresholds.

        Parameters
        ----------
        thresholds : Dict[int, Tuple[float, float]], optional
            Custom thresholds for the stages. If None, default thresholds are used.
        """
        self.thresholds = thresholds if thresholds is not None else self.DEFAULT_THRESHOLDS.copy()

    def calculate_life_probability(self, planet: Any, star_system: Any) -> float:
        """
        Compute the 0-100 probability of life emerging on a planet.

        The probability is calculated using the following components:
        - habitability_score: 40%
        - water_percentage: 15% (optimal 30-80% gets 15, drops linearly to 0 at 0% or 100%)
        - temperature: 20% (optimal 260K-320K gets 20, drops to 0 below 150K or above 400K)
        - atmosphere_type: 15% (Moderate=15, Dense/Thin=10, Toxic/Reducing=5, None/Hydrogen-Helium=0)
        - resource_score: 10%
        - planet_type boost/clamp: Ocean, Rocky, Super Earth gets x1.0. Desert gets x0.6.
          Ice gets x0.2. Toxic gets x0.1. Gas Giant and Lava World clamp total probability to 0.0 immediately.

        Parameters
        ----------
        planet : Any
            The Planet object containing physical attributes.
        star_system : Any
            The StarSystem object containing astronomical environment attributes (e.g. system age).

        Returns
        -------
        float
            The final life probability rounded to 2 decimal places, clamped to [0, 100].
        """
        # 1. Planet type boost/clamp check
        ptype = planet.planet_type.value if hasattr(planet.planet_type, "value") else planet.planet_type
        if ptype in ("Gas Giant", "Lava World"):
            return 0.0

        type_factor = 1.0
        if ptype in ("Ocean", "Rocky", "Super Earth"):
            type_factor = 1.0
        elif ptype == "Desert":
            type_factor = 0.6
        elif ptype == "Ice":
            type_factor = 0.2
        elif ptype in ("Toxic World", "Toxic"):
            type_factor = 0.1

        # 2. Habitability score (40%)
        hab_score = max(0.0, min(100.0, planet.habitability_score))
        hab_contrib = 0.4 * hab_score

        # 3. Water percentage (15%)
        # Optimal 30-80% gets 15, drops linearly to 0 at 0% or 100%
        w = max(0.0, min(100.0, planet.water_percentage))
        if 30.0 <= w <= 80.0:
            water_contrib = 15.0
        elif w < 30.0:
            water_contrib = 15.0 * (w / 30.0)
        else:  # w > 80.0
            water_contrib = 15.0 * ((100.0 - w) / 20.0)

        # 4. Temperature (20%)
        # Optimal 260K-320K gets 20, drops to 0 below 150K or above 400K
        t = planet.temperature
        if t < 150.0 or t > 400.0:
            temp_contrib = 0.0
        elif 260.0 <= t <= 320.0:
            temp_contrib = 20.0
        elif 150.0 <= t < 260.0:
            temp_contrib = 20.0 * (t - 150.0) / (260.0 - 150.0)
        else:  # 320.0 < t <= 400.0
            temp_contrib = 20.0 * (400.0 - t) / (400.0 - 320.0)

        # 5. Atmosphere type (15%)
        # Moderate=15, Dense/Thin=10, Toxic/Reducing=5, None/Hydrogen-Helium=0
        atm = planet.atmosphere_type.value if hasattr(planet.atmosphere_type, "value") else planet.atmosphere_type
        if isinstance(atm, str):
            atm_str = atm.strip()
        else:
            atm_str = str(atm).strip()

        if atm_str == "Moderate":
            atm_contrib = 15.0
        elif atm_str in ("Dense", "Thin"):
            atm_contrib = 10.0
        elif atm_str in ("Toxic", "Reducing"):
            atm_contrib = 5.0
        else:  # "None", "Hydrogen-Helium", etc.
            atm_contrib = 0.0

        # 6. Resource score (10%)
        res_score = max(0.0, min(100.0, planet.resource_score))
        res_contrib = 0.1 * res_score

        # 7. Aggregate and apply type factor
        raw_prob = hab_contrib + water_contrib + temp_contrib + atm_contrib + res_contrib
        final_prob = raw_prob * type_factor

        # Clamp and round
        final_prob = max(0.0, min(100.0, final_prob))
        return round(final_prob, 2)

    def determine_life_stage(self, probability: float, system_age: float) -> int:
        """
        Map probability to a life stage (0-5) using thresholds.

        Apply age constraints:
        - If system_age < 0.1 Gyr: clamp stage to 0.
        - If system_age < 1.0 Gyr: clamp stage to max 1.

        Parameters
        ----------
        probability : float
            The computed life probability.
        system_age : float
            The age of the parent star system in billions of years (Gyr).

        Returns
        -------
        int
            The developmental stage of life, integer between 0 and 5.
        """
        prob = max(0.0, min(100.0, probability))

        # Find stage by range checks
        stage = 0
        for stg, (low, high) in self.thresholds.items():
            if stg == 0:
                if low <= prob <= high:
                    stage = stg
            else:
                if low < prob <= high:
                    stage = stg

        # Apply age constraints
        if system_age < 0.1:
            stage = 0
        elif system_age < 1.0:
            stage = min(stage, 1)

        return stage
