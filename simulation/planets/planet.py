"""
Planet data model for The Galactic Dream Engine.

Defines the Planet dataclass representing a single planetary body orbiting a
star, along with supporting enumerations for planet types and atmosphere
classifications.

Phase 2 – Planetary Generation & Habitability
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class PlanetType(str, Enum):
    """Classification of a planet's dominant physical composition."""

    ROCKY = "Rocky"
    OCEAN = "Ocean"
    ICE = "Ice"
    DESERT = "Desert"
    GAS_GIANT = "Gas Giant"
    LAVA_WORLD = "Lava World"
    TOXIC_WORLD = "Toxic World"
    SUPER_EARTH = "Super Earth"


class AtmosphereType(str, Enum):
    """Classification of a planet's atmospheric envelope."""

    NONE = "None"
    THIN = "Thin"
    MODERATE = "Moderate"
    DENSE = "Dense"
    TOXIC = "Toxic"
    REDUCING = "Reducing"
    HYDROGEN_HELIUM = "Hydrogen-Helium"


# ---------------------------------------------------------------------------
# Planet Dataclass
# ---------------------------------------------------------------------------

@dataclass
class Planet:
    """
    Represents a single planet orbiting a parent star in the simulation.

    Attributes
    ----------
    planet_id : str
        Unique identifier for this planet (hex hash).
    planet_name : str
        Human-readable designation, e.g. ``'GX-1023-b'``.
    star_id : str
        Unique identifier of the parent star this planet orbits.
    planet_type : PlanetType
        Dominant composition / class of the planet.
    orbital_distance_au : float
        Semi-major axis of the orbit in Astronomical Units (AU).
    mass : float
        Mass of the planet in Earth masses (M⊕).
    radius : float
        Equatorial radius of the planet in Earth radii (R⊕).
    gravity : float
        Surface gravity relative to Earth (g, where Earth = 1.0).
    temperature : float
        Equilibrium surface temperature in Kelvin (K).
    water_percentage : float
        Fraction of the surface covered by liquid water, 0–100 %.
    atmosphere_type : AtmosphereType
        Classification of the planet's atmospheric envelope.
    resource_score : float
        Aggregate resource richness score, 0–100.  Computed externally
        by :class:`HabitabilityEngine`.
    habitability_score : float
        Aggregate habitability score, 0–100.  Computed externally by
        :class:`HabitabilityEngine`.
    """

    planet_id: str
    planet_name: str
    star_id: str
    planet_type: PlanetType
    orbital_distance_au: float
    mass: float            # Earth masses (M⊕)
    radius: float          # Earth radii (R⊕)
    gravity: float         # Surface gravity (g, Earth = 1.0)
    temperature: float     # Kelvin
    water_percentage: float  # 0–100
    atmosphere_type: AtmosphereType
    resource_score: float    # 0–100
    habitability_score: float  # 0–100

    # ----- Serialisation helpers ------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialise the planet to a plain dictionary.

        Enum fields are stored as their string values so the dictionary is
        directly JSON / CSV-safe.

        Returns
        -------
        Dict[str, Any]
            Dictionary representation of all planet fields.
        """
        data: Dict[str, Any] = asdict(self)
        data["planet_type"] = self.planet_type.value
        data["atmosphere_type"] = self.atmosphere_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Planet":
        """
        Reconstruct a :class:`Planet` instance from a dictionary.

        Parameters
        ----------
        data : Dict[str, Any]
            Dictionary containing all planet fields.  ``planet_type`` and
            ``atmosphere_type`` may be either enum members or their string
            values.

        Returns
        -------
        Planet
            Fully initialised ``Planet`` instance.
        """
        return cls(
            planet_id=str(data["planet_id"]),
            planet_name=str(data["planet_name"]),
            star_id=str(data["star_id"]),
            planet_type=PlanetType(data["planet_type"]),
            orbital_distance_au=float(data["orbital_distance_au"]),
            mass=float(data["mass"]),
            radius=float(data["radius"]),
            gravity=float(data["gravity"]),
            temperature=float(data["temperature"]),
            water_percentage=float(data["water_percentage"]),
            atmosphere_type=AtmosphereType(data["atmosphere_type"]),
            resource_score=float(data["resource_score"]),
            habitability_score=float(data["habitability_score"]),
        )

    # ----- Display --------------------------------------------------------

    def __str__(self) -> str:
        """Return a concise, human-readable summary of the planet."""
        return (
            f"Planet {self.planet_name} [{self.planet_type.value}] | "
            f"Orbit: {self.orbital_distance_au:.2f} AU | "
            f"M: {self.mass:.2f} Me | R: {self.radius:.2f} Re | "
            f"g: {self.gravity:.2f} | T: {self.temperature:,.0f} K | "
            f"H2O: {self.water_percentage:.1f}% | "
            f"Atm: {self.atmosphere_type.value} | "
            f"Hab: {self.habitability_score:.1f} | "
            f"Res: {self.resource_score:.1f}"
        )
