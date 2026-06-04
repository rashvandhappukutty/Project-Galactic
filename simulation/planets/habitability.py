"""
Habitability and resource scoring engine for The Galactic Dream Engine.

Evaluates every generated planet against six weighted habitability factors and
six resource categories to produce aggregate scores in the range 0–100.

Phase 2 – Planetary Generation & Habitability
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional

import numpy as np

from simulation.planets.planet import AtmosphereType, Planet, PlanetType


# ---------------------------------------------------------------------------
# Habitability classification bands
# ---------------------------------------------------------------------------

_HABITABILITY_BANDS: List[tuple[int, int, str]] = [
    (0, 20, "Uninhabitable"),
    (21, 40, "Harsh"),
    (41, 60, "Marginal"),
    (61, 80, "Potentially Habitable"),
    (81, 100, "Highly Habitable"),
]

# ---------------------------------------------------------------------------
# Planet-type scores for the "type" factor
# ---------------------------------------------------------------------------

_TYPE_SCORES: Dict[PlanetType, float] = {
    PlanetType.OCEAN:       15.0,
    PlanetType.SUPER_EARTH: 13.0,
    PlanetType.ROCKY:       10.0,
    PlanetType.DESERT:       5.0,
    PlanetType.ICE:          3.0,
    PlanetType.TOXIC_WORLD:  1.0,
    PlanetType.GAS_GIANT:    0.0,
    PlanetType.LAVA_WORLD:   0.0,
}

# ---------------------------------------------------------------------------
# Atmosphere-type scores for the "atmosphere" factor
# ---------------------------------------------------------------------------

_ATMOSPHERE_SCORES: Dict[AtmosphereType, float] = {
    AtmosphereType.MODERATE:         10.0,
    AtmosphereType.THIN:              7.0,
    AtmosphereType.DENSE:             5.0,
    AtmosphereType.REDUCING:          3.0,
    AtmosphereType.TOXIC:             1.0,
    AtmosphereType.HYDROGEN_HELIUM:   0.0,
    AtmosphereType.NONE:              0.0,
}


# ---------------------------------------------------------------------------
# HabitabilityEngine
# ---------------------------------------------------------------------------

class HabitabilityEngine:
    """
    Scores planets on habitability and resource richness.

    Parameters
    ----------
    seed : int, default ``42``
        Random seed for reproducible resource generation.
    """

    def __init__(self, seed: int = 42) -> None:
        self.seed: int = seed
        self.random_state: np.random.RandomState = np.random.RandomState(seed)

    # =====================================================================
    # HABITABILITY  (0 – 100)
    # =====================================================================

    def calculate_habitability(
        self,
        planet: Planet,
        hz_inner: float,
        hz_outer: float,
    ) -> float:
        """
        Compute an aggregate habitability score for *planet*.

        The score is the sum of six independently evaluated factors:

        1. Habitable-zone proximity (0–25)
        2. Temperature (0–20)
        3. Water availability (0–20)
        4. Planet type (0–15)
        5. Atmosphere (0–10)
        6. Gravity (0–10)

        Parameters
        ----------
        planet : Planet
            The planet to evaluate.
        hz_inner : float
            Inner edge of the host star's habitable zone (AU).
        hz_outer : float
            Outer edge of the host star's habitable zone (AU).

        Returns
        -------
        float
            Habitability score in the range [0, 100].
        """
        score: float = 0.0
        score += self._hz_proximity_score(planet.orbital_distance_au, hz_inner, hz_outer)
        score += self._temperature_score(planet.temperature)
        score += self._water_score(planet.water_percentage)
        score += self._type_score(planet.planet_type)
        score += self._atmosphere_score(planet.atmosphere_type)
        score += self._gravity_score(planet.gravity)
        return float(np.clip(round(score, 2), 0.0, 100.0))

    # ----- Factor 1: Habitable-zone proximity (0-25) ----------------------

    @staticmethod
    def _hz_proximity_score(
        orbital_distance: float,
        hz_inner: float,
        hz_outer: float,
    ) -> float:
        """
        Award up to 25 points for being inside or near the habitable zone.

        Full points when the planet lies between *hz_inner* and *hz_outer*.
        Points decay linearly as distance from the nearest HZ edge grows,
        reaching 0 when the planet is more than 1 HZ-width away.
        """
        if hz_inner <= orbital_distance <= hz_outer:
            return 25.0

        hz_width: float = max(hz_outer - hz_inner, 0.01)

        if orbital_distance < hz_inner:
            gap = hz_inner - orbital_distance
        else:
            gap = orbital_distance - hz_outer

        fraction = 1.0 - min(gap / hz_width, 1.0)
        return round(25.0 * fraction, 2)

    # ----- Factor 2: Temperature (0-20) -----------------------------------

    @staticmethod
    def _temperature_score(temperature: float) -> float:
        """
        Award up to 20 points based on temperature proximity to the
        optimal 260–310 K range.

        Deviation from the range reduces the score linearly over a
        200 K window.
        """
        if 260.0 <= temperature <= 310.0:
            return 20.0

        if temperature < 260.0:
            deviation = 260.0 - temperature
        else:
            deviation = temperature - 310.0

        fraction = 1.0 - min(deviation / 200.0, 1.0)
        return round(20.0 * fraction, 2)

    # ----- Factor 3: Water (0-20) -----------------------------------------

    @staticmethod
    def _water_score(water_percentage: float) -> float:
        """
        Award up to 20 points: ``water_percentage / 5``, capped at 20.
        """
        return float(min(water_percentage / 5.0, 20.0))

    # ----- Factor 4: Planet type (0-15) -----------------------------------

    @staticmethod
    def _type_score(planet_type: PlanetType) -> float:
        """Return the fixed habitability score for the planet's type."""
        return _TYPE_SCORES.get(planet_type, 0.0)

    # ----- Factor 5: Atmosphere (0-10) ------------------------------------

    @staticmethod
    def _atmosphere_score(atmosphere_type: AtmosphereType) -> float:
        """Return the fixed habitability score for the atmosphere class."""
        return _ATMOSPHERE_SCORES.get(atmosphere_type, 0.0)

    # ----- Factor 6: Gravity (0-10) ---------------------------------------

    @staticmethod
    def _gravity_score(gravity: float) -> float:
        """
        Award up to 10 points for surface gravity in the optimal 0.5–1.5 g
        range.  Below 0.3 g or above 3.0 g scores 0.
        """
        if 0.5 <= gravity <= 1.5:
            return 10.0

        if gravity < 0.3 or gravity > 3.0:
            return 0.0

        # Partial credit between 0.3–0.5 and 1.5–3.0
        if gravity < 0.5:
            fraction = (gravity - 0.3) / 0.2
        else:
            fraction = 1.0 - (gravity - 1.5) / 1.5

        return round(10.0 * max(fraction, 0.0), 2)

    # ----- Classification -------------------------------------------------

    @staticmethod
    def classify_habitability(score: float) -> str:
        """
        Map a numeric habitability score to a human-readable classification.

        Parameters
        ----------
        score : float
            Habitability score in [0, 100].

        Returns
        -------
        str
            One of ``'Uninhabitable'``, ``'Harsh'``, ``'Marginal'``,
            ``'Potentially Habitable'``, or ``'Highly Habitable'``.
        """
        for lo, hi, label in _HABITABILITY_BANDS:
            if lo <= score <= hi:
                return label
        return "Uninhabitable"

    # =====================================================================
    # RESOURCES  (0 – 100)
    # =====================================================================

    def calculate_resources(self, planet: Planet) -> float:
        """
        Compute an aggregate resource-richness score for *planet*.

        Six resource categories are evaluated individually (0–100 each),
        then combined via a weighted average.

        Categories and weights:
            - Iron (0.20)
            - Titanium (0.15)
            - Rare minerals (0.20)
            - Water (0.15)
            - Helium-3 (0.15)
            - Energy potential (0.15)

        Parameters
        ----------
        planet : Planet
            The planet to evaluate.

        Returns
        -------
        float
            Resource score in the range [0, 100].
        """
        iron = self._resource_iron(planet)
        titanium = self._resource_titanium(planet)
        rare = self._resource_rare_minerals(planet)
        water = self._resource_water(planet)
        he3 = self._resource_helium3(planet)
        energy = self._resource_energy(planet)

        weights = np.array([0.20, 0.15, 0.20, 0.15, 0.15, 0.15])
        values = np.array([iron, titanium, rare, water, he3, energy])

        score = float(np.dot(weights, values))
        return float(np.clip(round(score, 2), 0.0, 100.0))

    # ----- Individual resource components ---------------------------------

    def _resource_iron(self, planet: Planet) -> float:
        """Iron: higher for Rocky, Desert, SuperEarth; lower for Gas Giants."""
        base_map: Dict[PlanetType, float] = {
            PlanetType.ROCKY:       60.0,
            PlanetType.DESERT:      55.0,
            PlanetType.SUPER_EARTH: 65.0,
            PlanetType.LAVA_WORLD:  70.0,
            PlanetType.ICE:         20.0,
            PlanetType.OCEAN:       30.0,
            PlanetType.TOXIC_WORLD: 40.0,
            PlanetType.GAS_GIANT:    5.0,
        }
        base = base_map.get(planet.planet_type, 20.0)
        noise = self.random_state.uniform(-10.0, 10.0)
        mass_bonus = min(planet.mass * 2.0, 20.0)
        return float(np.clip(base + noise + mass_bonus, 0.0, 100.0))

    def _resource_titanium(self, planet: Planet) -> float:
        """Titanium: similar distribution to iron but ~30 % rarer."""
        base_map: Dict[PlanetType, float] = {
            PlanetType.ROCKY:       40.0,
            PlanetType.DESERT:      38.0,
            PlanetType.SUPER_EARTH: 45.0,
            PlanetType.LAVA_WORLD:  50.0,
            PlanetType.ICE:         12.0,
            PlanetType.OCEAN:       18.0,
            PlanetType.TOXIC_WORLD: 25.0,
            PlanetType.GAS_GIANT:    2.0,
        }
        base = base_map.get(planet.planet_type, 10.0)
        noise = self.random_state.uniform(-8.0, 8.0)
        mass_bonus = min(planet.mass * 1.5, 15.0)
        return float(np.clip(base + noise + mass_bonus, 0.0, 100.0))

    def _resource_rare_minerals(self, planet: Planet) -> float:
        """Rare minerals: random baseline boosted by mass."""
        base = self.random_state.uniform(5.0, 40.0)
        mass_bonus = min(planet.mass * 3.0, 30.0)
        # Slight type bonus for tectonically active worlds
        if planet.planet_type in (
            PlanetType.ROCKY,
            PlanetType.SUPER_EARTH,
            PlanetType.LAVA_WORLD,
        ):
            base += 15.0
        return float(np.clip(base + mass_bonus, 0.0, 100.0))

    def _resource_water(self, planet: Planet) -> float:
        """Water resource: directly derived from water_percentage and type."""
        base = planet.water_percentage
        if planet.planet_type == PlanetType.OCEAN:
            base = min(base * 1.2, 100.0)
        elif planet.planet_type == PlanetType.ICE:
            base = min(base * 1.1, 100.0)
        noise = self.random_state.uniform(-5.0, 5.0)
        return float(np.clip(base + noise, 0.0, 100.0))

    def _resource_helium3(self, planet: Planet) -> float:
        """Helium-3: abundant in Gas Giants and Ice worlds."""
        base_map: Dict[PlanetType, float] = {
            PlanetType.GAS_GIANT:   80.0,
            PlanetType.ICE:         45.0,
            PlanetType.OCEAN:       10.0,
            PlanetType.ROCKY:        5.0,
            PlanetType.SUPER_EARTH:  8.0,
            PlanetType.DESERT:       3.0,
            PlanetType.LAVA_WORLD:   2.0,
            PlanetType.TOXIC_WORLD: 12.0,
        }
        base = base_map.get(planet.planet_type, 5.0)
        noise = self.random_state.uniform(-10.0, 15.0)
        return float(np.clip(base + noise, 0.0, 100.0))

    def _resource_energy(self, planet: Planet) -> float:
        """
        Energy potential: based on temperature (radiation proximity),
        tidal forces (orbital distance), and atmospheric dynamics.
        """
        # Proximity to star → higher solar energy
        if planet.orbital_distance_au > 0.0:
            solar_factor = min(50.0 / planet.orbital_distance_au, 80.0)
        else:
            solar_factor = 80.0

        # High-temperature worlds have geothermal energy
        geothermal = 0.0
        if planet.temperature > 500.0:
            geothermal = min((planet.temperature - 500.0) / 20.0, 30.0)

        # Atmosphere allows wind energy
        atm_bonus: float = 0.0
        if planet.atmosphere_type in (AtmosphereType.MODERATE, AtmosphereType.DENSE):
            atm_bonus = 10.0

        combined = solar_factor + geothermal + atm_bonus
        noise = self.random_state.uniform(-5.0, 5.0)
        return float(np.clip(combined + noise, 0.0, 100.0))

    # =====================================================================
    # BATCH PROCESSING
    # =====================================================================

    def process_all_planets(
        self,
        planets: List[Planet],
        systems_dict: Dict[str, Any],
    ) -> List[Planet]:
        """
        Evaluate habitability and resources for every planet, updating
        the planet objects **in place**.

        Parameters
        ----------
        planets : List[Planet]
            Planets to score (modified in place).
        systems_dict : Dict[str, Any]
            Mapping of ``star_id`` → star-system-like object.  Each value
            must have ``hz_inner`` and ``hz_outer`` attributes.

        Returns
        -------
        List[Planet]
            The same list, with ``habitability_score`` and
            ``resource_score`` populated.
        """
        for planet in planets:
            system = systems_dict.get(planet.star_id)
            if system is None:
                # No matching system — leave scores at 0
                continue

            hz_inner: float = system.hz_inner
            hz_outer: float = system.hz_outer

            planet.habitability_score = self.calculate_habitability(
                planet, hz_inner, hz_outer
            )
            planet.resource_score = self.calculate_resources(planet)

        return planets


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from dataclasses import dataclass as _dc

    from simulation.planets.planet_generator import PlanetGenerator

    @_dc
    class _MockSystem:
        star_id: str
        star_name: str
        star_luminosity: float
        star_temperature: float
        hz_inner: float
        hz_outer: float
        planet_count: int

    mock = _MockSystem(
        star_id="abc123",
        star_name="GDE-4221",
        star_luminosity=1.0,
        star_temperature=5778.0,
        hz_inner=0.95,
        hz_outer=1.37,
        planet_count=6,
    )

    gen = PlanetGenerator(seed=42)
    planets = gen.generate_planets(mock)

    engine = HabitabilityEngine(seed=42)
    systems_dict = {mock.star_id: mock}
    engine.process_all_planets(planets, systems_dict)

    for p in planets:
        classification = engine.classify_habitability(p.habitability_score)
        print(f"{p}  →  {classification}")
