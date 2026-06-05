"""
species.py — Species and Civilization data models for the Galactic Dream Engine.

Phase 3 – Life Emergence Engine
"""

from dataclasses import dataclass, asdict
from typing import Dict, Any


@dataclass
class Species:
    """Represents a sentient species emerging on a planet.

    Attributes
    ----------
    species_id : str
        Unique identifier for the species (hex hash).
    name : str
        Procedurally generated name of the species.
    planet_id : str
        ID of the planet where this species evolved.
    intelligence : float
        Cognitive capacity, from 1.0 to 100.0.
    cooperation : float
        Propensity to work together, from 1.0 to 100.0.
    aggression : float
        Propensity for conflict/competition, from 1.0 to 100.0.
    adaptability : float
        Ability to survive environmental changes, from 1.0 to 100.0.
    lifespan : float
        Average individual lifespan in years, from 10.0 to 1000.0.
    population : float
        Current population on the planet.
    """

    species_id: str
    name: str
    planet_id: str
    intelligence: float
    cooperation: float
    aggression: float
    adaptability: float
    lifespan: float
    population: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert the species to a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Species":
        """Reconstruct a Species instance from a dictionary."""
        return cls(
            species_id=str(data["species_id"]),
            name=str(data["name"]),
            planet_id=str(data["planet_id"]),
            intelligence=float(data["intelligence"]),
            cooperation=float(data["cooperation"]),
            aggression=float(data["aggression"]),
            adaptability=float(data["adaptability"]),
            lifespan=float(data["lifespan"]),
            population=float(data["population"]),
        )


@dataclass
class Civilization:
    """Represents an organized civilization formed by a sentient species.

    Attributes
    ----------
    civilization_id : str
        Unique identifier for the civilization (hex hash).
    name : str
        Procedurally generated name of the civilization.
    species : Species
        The dominant species that founded this civilization.
    planet_id : str
        ID of the home planet.
    tech_level : float
        Technology level, from 10.0 to 100.0.
    energy_source : str
        Primary energy source (Fossil, Nuclear, Fusion, Antimatter, Dyson Swarm Prototype).
    government_type : str
        Structure of governance (e.g. Democracy, Technocracy, Federation).
    civilization_age : float
        Age of the civilization in years.
    """

    civilization_id: str
    name: str
    species: Species
    planet_id: str
    tech_level: float
    energy_source: str
    government_type: str
    civilization_age: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert the civilization to a plain dictionary."""
        data = asdict(self)
        data["species"] = self.species.to_dict()
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Civilization":
        """Reconstruct a Civilization instance from a dictionary."""
        species_data = data["species"]
        if isinstance(species_data, dict):
            species = Species.from_dict(species_data)
        else:
            species = species_data
        return cls(
            civilization_id=str(data["civilization_id"]),
            name=str(data["name"]),
            species=species,
            planet_id=str(data["planet_id"]),
            tech_level=float(data["tech_level"]),
            energy_source=str(data["energy_source"]),
            government_type=str(data["government_type"]),
            civilization_age=float(data["civilization_age"]),
        )
