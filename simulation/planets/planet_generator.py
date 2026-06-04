"""
Procedural planet generator for The Galactic Dream Engine.

Generates physically plausible planets for each star system using modified
Titius–Bode spacing, mass–radius relations, and equilibrium temperature
calculations.  Habitability and resource scores are left at 0.0 — they are
computed later by :class:`simulation.planets.habitability.HabitabilityEngine`.

Phase 2 – Planetary Generation & Habitability
"""

from __future__ import annotations

import hashlib
import math
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable

import numpy as np
import pandas as pd

from simulation.planets.planet import AtmosphereType, Planet, PlanetType


# ---------------------------------------------------------------------------
# Star system protocol – duck-typed interface expected by the generator
# ---------------------------------------------------------------------------

@runtime_checkable
class StarSystemLike(Protocol):
    """
    Structural sub-typing protocol that any "star system" object must satisfy
    in order to feed into :class:`PlanetGenerator`.

    This keeps the planet generator decoupled from a concrete StarSystem class
    that may live in a separate module (``simulation.systems.star_system``).
    """

    star_id: str
    star_name: str
    star_luminosity: float
    star_temperature: float
    hz_inner: float
    hz_outer: float
    planet_count: int


# ---------------------------------------------------------------------------
# Planet name suffixes (IAU convention: b, c, d, …)
# ---------------------------------------------------------------------------

_PLANET_SUFFIXES: List[str] = list("bcdefghijk")


# ---------------------------------------------------------------------------
# Mass ranges per planet type  (Earth masses, M⊕)
# ---------------------------------------------------------------------------

_MASS_RANGES: Dict[PlanetType, tuple[float, float]] = {
    PlanetType.ROCKY:       (0.1, 2.0),
    PlanetType.OCEAN:       (0.5, 4.0),
    PlanetType.ICE:         (0.3, 3.0),
    PlanetType.DESERT:      (0.2, 2.5),
    PlanetType.GAS_GIANT:   (15.0, 4000.0),
    PlanetType.LAVA_WORLD:  (0.3, 3.0),
    PlanetType.TOXIC_WORLD: (0.5, 5.0),
    PlanetType.SUPER_EARTH: (2.0, 10.0),
}


# ---------------------------------------------------------------------------
# PlanetGenerator
# ---------------------------------------------------------------------------

class PlanetGenerator:
    """
    Procedurally generates planets for a given star system using
    astrophysically motivated heuristics.

    Parameters
    ----------
    seed : int, default ``42``
        Random seed for reproducibility.
    """

    def __init__(self, seed: int = 42) -> None:
        self.seed: int = seed
        self.random_state: np.random.RandomState = np.random.RandomState(seed)

    # ----- Public API -----------------------------------------------------

    def generate_planets(self, star_system: Any) -> List[Planet]:
        """
        Generate a list of planets for a single star system.

        Parameters
        ----------
        star_system
            Any object satisfying :class:`StarSystemLike`.  Must expose
            ``star_id``, ``star_name``, ``star_luminosity``,
            ``star_temperature``, ``hz_inner``, ``hz_outer``, and
            ``planet_count``.

        Returns
        -------
        List[Planet]
            Generated planets with ``resource_score`` and
            ``habitability_score`` set to ``0.0``.
        """
        planet_count: int = star_system.planet_count
        if planet_count <= 0:
            return []

        # Clamp to the number of available suffixes
        planet_count = min(planet_count, len(_PLANET_SUFFIXES))

        # ----- Generate orbital distances (Titius–Bode–like) -----
        distances: List[float] = self._generate_orbital_distances(planet_count)

        planets: List[Planet] = []
        for idx in range(planet_count):
            orbital_distance: float = distances[idx]
            suffix: str = _PLANET_SUFFIXES[idx]
            planet_name: str = f"{star_system.star_name}-{suffix}"
            planet_id: str = hashlib.sha256(
                f"{star_system.star_id}-planet-{idx}".encode()
            ).hexdigest()[:10]

            # Type
            planet_type: PlanetType = self._assign_planet_type(
                orbital_distance, star_system.hz_inner, star_system.hz_outer
            )

            # Mass
            mass: float = self._generate_mass(planet_type)

            # Radius
            radius: float = self._calculate_radius(mass, planet_type)

            # Gravity  (g = M / R² in Earth units)
            gravity: float = mass / (radius ** 2) if radius > 0.0 else 0.0

            # Equilibrium temperature
            temperature: float = self._calculate_temperature(
                star_system.star_luminosity, orbital_distance
            )

            # Water
            water_percentage: float = self._assign_water_percentage(
                planet_type, temperature
            )

            # Atmosphere
            atmosphere_type: AtmosphereType = self._assign_atmosphere(
                planet_type, mass, temperature
            )

            planet = Planet(
                planet_id=planet_id,
                planet_name=planet_name,
                star_id=star_system.star_id,
                planet_type=planet_type,
                orbital_distance_au=round(orbital_distance, 4),
                mass=round(mass, 4),
                radius=round(radius, 4),
                gravity=round(gravity, 4),
                temperature=round(temperature, 2),
                water_percentage=round(water_percentage, 2),
                atmosphere_type=atmosphere_type,
                resource_score=0.0,
                habitability_score=0.0,
            )
            planets.append(planet)

        return planets

    def generate_all_planets(self, systems: List[Any]) -> List[Planet]:
        """
        Generate planets for every star system in the list.

        Parameters
        ----------
        systems : List
            Iterable of objects satisfying :class:`StarSystemLike`.

        Returns
        -------
        List[Planet]
            Aggregated list of all generated planets.
        """
        all_planets: List[Planet] = []
        for system in systems:
            all_planets.extend(self.generate_planets(system))
        return all_planets

    def save_to_csv(self, planets: List[Planet], filepath: str) -> None:
        """
        Persist a list of planets to a CSV file.

        Parameters
        ----------
        planets : List[Planet]
            Planets to serialise.
        filepath : str
            Destination path for the CSV file.
        """
        data: List[Dict[str, Any]] = [p.to_dict() for p in planets]
        df = pd.DataFrame(data)
        columns = [
            "planet_id",
            "planet_name",
            "star_id",
            "planet_type",
            "orbital_distance_au",
            "mass",
            "radius",
            "gravity",
            "temperature",
            "water_percentage",
            "atmosphere_type",
            "resource_score",
            "habitability_score",
        ]
        df = df[columns]
        df.to_csv(filepath, index=False)
        print(
            f"Successfully generated and saved {len(planets)} planets to "
            f"{filepath}"
        )

    # ----- Internal: orbital mechanics ------------------------------------

    def _generate_orbital_distances(self, count: int) -> List[float]:
        """
        Generate sorted orbital distances using modified Titius–Bode spacing.

        The innermost planet starts at 0.1–0.5 AU.  Each subsequent planet
        is spaced by multiplying the previous distance by a factor of
        ``1.4 + U(0, 0.8)`` with a small random perturbation added.

        Parameters
        ----------
        count : int
            Number of orbital slots to generate.

        Returns
        -------
        List[float]
            Sorted orbital distances in AU.
        """
        distances: List[float] = []
        current: float = self.random_state.uniform(0.1, 0.5)

        for _ in range(count):
            # Small additive perturbation (± 5 % of current distance)
            perturbation: float = self.random_state.normal(0.0, 0.05 * current)
            distance: float = max(current + perturbation, 0.05)
            distances.append(distance)

            # Space the next planet outward
            spacing_factor: float = 1.4 + self.random_state.uniform(0.0, 0.8)
            current = distance * spacing_factor

        distances.sort()
        return distances

    # ----- Internal: type assignment --------------------------------------

    def _pick(self, options: List[PlanetType], weights: Optional[List[float]] = None) -> PlanetType:
        """
        Select a PlanetType from *options* using the internal random state.

        Unlike ``numpy.random.choice``, this always returns a genuine
        :class:`PlanetType` member rather than a numpy string.

        Parameters
        ----------
        options : List[PlanetType]
            Candidate planet types.
        weights : List[float] | None
            Optional probability weights (must sum to ~1).

        Returns
        -------
        PlanetType
        """
        if weights is not None:
            w = np.array(weights, dtype=np.float64)
            w /= w.sum()
            idx = int(self.random_state.choice(len(options), p=w))
        else:
            idx = int(self.random_state.randint(0, len(options)))
        return options[idx]

    def _assign_planet_type(
        self,
        orbital_distance: float,
        hz_inner: float,
        hz_outer: float,
    ) -> PlanetType:
        """
        Determine the planet type based on its orbital distance relative to
        the host star's habitable zone boundaries.

        A 5 % global chance of :attr:`PlanetType.TOXIC_WORLD` is applied
        regardless of distance.

        Parameters
        ----------
        orbital_distance : float
            Semi-major axis in AU.
        hz_inner : float
            Inner boundary of the habitable zone (AU).
        hz_outer : float
            Outer boundary of the habitable zone (AU).

        Returns
        -------
        PlanetType
        """
        # 5 % chance of Toxic World anywhere
        if self.random_state.rand() < 0.05:
            return PlanetType.TOXIC_WORLD

        if orbital_distance < 0.3 * hz_inner:
            return PlanetType.LAVA_WORLD

        if orbital_distance < hz_inner:
            return self._pick([PlanetType.DESERT, PlanetType.ROCKY])

        if orbital_distance <= hz_outer:
            # Inside the habitable zone — weighted draw
            return self._pick(
                [PlanetType.ROCKY, PlanetType.OCEAN, PlanetType.SUPER_EARTH],
                weights=[0.35, 0.40, 0.25],
            )

        if orbital_distance <= 3.0 * hz_outer:
            return self._pick([PlanetType.ICE, PlanetType.ROCKY])

        # Far outer system
        return self._pick([PlanetType.GAS_GIANT, PlanetType.ICE])

    # ----- Internal: mass & radius ----------------------------------------

    def _generate_mass(self, planet_type: PlanetType) -> float:
        """
        Sample a planet mass (Earth masses) using a log-uniform distribution
        within the type-specific range.

        Parameters
        ----------
        planet_type : PlanetType

        Returns
        -------
        float
            Mass in M⊕.
        """
        m_min, m_max = _MASS_RANGES[planet_type]
        return float(
            math.exp(
                self.random_state.uniform(math.log(m_min), math.log(m_max))
            )
        )

    @staticmethod
    def _calculate_radius(mass: float, planet_type: PlanetType) -> float:
        """
        Estimate planetary radius from mass using power-law relations.

        Parameters
        ----------
        mass : float
            Planet mass in M⊕.
        planet_type : PlanetType

        Returns
        -------
        float
            Radius in R⊕.
        """
        if planet_type in (PlanetType.ROCKY, PlanetType.DESERT, PlanetType.LAVA_WORLD):
            return float(mass ** 0.27)
        if planet_type in (PlanetType.OCEAN, PlanetType.ICE, PlanetType.SUPER_EARTH):
            return float(mass ** 0.30)
        if planet_type == PlanetType.GAS_GIANT:
            # Jupiter-like compression: radius saturates at high mass
            return float(mass ** 0.05 * 3.5)
        if planet_type == PlanetType.TOXIC_WORLD:
            return float(mass ** 0.28)

        # Fallback (should not be reached)
        return float(mass ** 0.27)

    # ----- Internal: temperature ------------------------------------------

    @staticmethod
    def _calculate_temperature(
        star_luminosity: float,
        orbital_distance_au: float,
    ) -> float:
        """
        Calculate equilibrium temperature of a planet.

        Uses the simplified relation::

            T_planet = 278.5 × L^0.25 / √d

        where *L* is the stellar luminosity in solar luminosities and *d* is
        the orbital distance in AU.

        Parameters
        ----------
        star_luminosity : float
            Host star luminosity in L☉.
        orbital_distance_au : float
            Orbital distance in AU.

        Returns
        -------
        float
            Equilibrium temperature in Kelvin.
        """
        if orbital_distance_au <= 0.0:
            orbital_distance_au = 0.01  # safety floor
        return 278.5 * (star_luminosity ** 0.25) / math.sqrt(orbital_distance_au)

    # ----- Internal: water ------------------------------------------------

    def _assign_water_percentage(
        self, planet_type: PlanetType, temperature: float
    ) -> float:
        """
        Estimate the surface water coverage of a planet based on its type
        and equilibrium temperature.

        Parameters
        ----------
        planet_type : PlanetType
        temperature : float
            Equilibrium temperature in K.

        Returns
        -------
        float
            Water coverage percentage (0–100).
        """
        if planet_type == PlanetType.OCEAN:
            base = self.random_state.uniform(50.0, 95.0)
        elif planet_type == PlanetType.ICE:
            base = self.random_state.uniform(20.0, 70.0)
        elif planet_type == PlanetType.ROCKY:
            base = self.random_state.uniform(0.0, 40.0)
        elif planet_type == PlanetType.SUPER_EARTH:
            base = self.random_state.uniform(10.0, 60.0)
        elif planet_type == PlanetType.DESERT:
            base = self.random_state.uniform(0.0, 5.0)
        elif planet_type == PlanetType.TOXIC_WORLD:
            base = self.random_state.uniform(0.0, 15.0)
        elif planet_type == PlanetType.LAVA_WORLD:
            base = 0.0
        elif planet_type == PlanetType.GAS_GIANT:
            base = 0.0
        else:
            base = 0.0

        # Temperature penalty: water boils away above ~373 K, freezes below 200 K
        if temperature > 373.0:
            # Exponential reduction for extreme heat
            reduction = min((temperature - 373.0) / 200.0, 1.0)
            base *= 1.0 - reduction
        elif temperature < 200.0:
            # Below freezing — water exists as ice but surface liquid reduced
            reduction = min((200.0 - temperature) / 200.0, 0.8)
            base *= 1.0 - reduction

        return float(np.clip(base, 0.0, 100.0))

    # ----- Internal: atmosphere -------------------------------------------

    def _assign_atmosphere(
        self,
        planet_type: PlanetType,
        mass: float,
        temperature: float,
    ) -> AtmosphereType:
        """
        Determine the atmospheric type of a planet.

        Heuristic considers the planet type, its mass (ability to retain an
        atmosphere), and temperature (atmospheric escape).

        Parameters
        ----------
        planet_type : PlanetType
        mass : float
            Planet mass in M⊕.
        temperature : float
            Equilibrium temperature in K.

        Returns
        -------
        AtmosphereType
        """
        # Gas giants always have thick H/He envelopes
        if planet_type == PlanetType.GAS_GIANT:
            return AtmosphereType.HYDROGEN_HELIUM

        # Very low-mass bodies cannot retain an atmosphere
        if mass < 0.15:
            return AtmosphereType.NONE

        # Toxic worlds
        if planet_type == PlanetType.TOXIC_WORLD:
            return AtmosphereType.TOXIC

        # Lava worlds — thin outgassed atmosphere or none
        if planet_type == PlanetType.LAVA_WORLD:
            return (
                AtmosphereType.THIN
                if self.random_state.rand() < 0.4
                else AtmosphereType.NONE
            )

        # Desert worlds — thin to moderate
        if planet_type == PlanetType.DESERT:
            return (
                AtmosphereType.THIN
                if mass < 0.8
                else AtmosphereType.MODERATE
            )

        # Ice worlds — thin or reducing
        if planet_type == PlanetType.ICE:
            return (
                AtmosphereType.THIN
                if mass < 1.0
                else AtmosphereType.REDUCING
            )

        # Ocean and Super-Earth — moderate to dense
        if planet_type in (PlanetType.OCEAN, PlanetType.SUPER_EARTH):
            if mass >= 5.0:
                return AtmosphereType.DENSE
            if mass >= 1.5:
                return AtmosphereType.MODERATE
            return AtmosphereType.THIN

        # Rocky worlds
        if planet_type == PlanetType.ROCKY:
            if temperature > 600.0 or mass < 0.3:
                return AtmosphereType.NONE
            if mass < 0.7:
                return AtmosphereType.THIN
            return AtmosphereType.MODERATE

        return AtmosphereType.NONE


# ---------------------------------------------------------------------------
# Standalone test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    from dataclasses import dataclass as _dc

    @_dc
    class _MockSystem:
        """Minimal stand-in for a StarSystem during local testing."""
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
    for p in planets:
        print(p)
