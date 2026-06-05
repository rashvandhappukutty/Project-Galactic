"""
colony_generator.py — Defines the Colony dataclass and ColonyGenerator.
"""

import hashlib
from dataclasses import dataclass, asdict
from typing import Dict, Any, List
import numpy as np


@dataclass
class Colony:
    """Represents an interstellar colony established on a planet.

    Attributes
    ----------
    colony_id : str
        Unique identifier.
    colony_name : str
        Procedurally generated colony name.
    parent_civilization_id : str
        ID of the civilization that founded this colony.
    home_star_id : str
        ID of the star system this colony belongs to.
    target_planet_id : str
        ID of the planet this colony is established on.
    population : float
        Current population count.
    development_level : float
        Development / infrastructure index (0.0 to 100.0).
    resource_output : float
        Resource production rate per tick.
    colony_type : str
        Type of colony (e.g. Research, Mining, Trade Hub, Military Outpost).
    age : float
        Age of the colony in years.
    """

    colony_id: str
    colony_name: str
    parent_civilization_id: str
    home_star_id: str
    target_planet_id: str
    population: float
    development_level: float
    resource_output: float
    colony_type: str
    age: float

    def to_dict(self) -> Dict[str, Any]:
        """Convert colony fields into a plain dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Colony":
        """Reconstruct a Colony instance from a dictionary."""
        return cls(
            colony_id=str(data["colony_id"]),
            colony_name=str(data["colony_name"]),
            parent_civilization_id=str(data["parent_civilization_id"]),
            home_star_id=str(data["home_star_id"]),
            target_planet_id=str(data["target_planet_id"]),
            population=float(data["population"]),
            development_level=float(data["development_level"]),
            resource_output=float(data["resource_output"]),
            colony_type=str(data["colony_type"]),
            age=float(data["age"]),
        )


class ColonyGenerator:
    """Handles colony creation and naming logic for Phase 6."""

    COLONY_TYPES = [
        "Research Colony",
        "Mining Colony",
        "Trade Hub",
        "Military Outpost",
        "Industrial Colony",
        "Capital Colony",
        "Megastructure Colony",
    ]

    def __init__(self, seed: int = 42) -> None:
        self.random = np.random.RandomState(seed)

    def _determine_colony_type(
        self,
        planet: Dict[str, Any],
        civ_personality: str,
        has_megastructure: bool,
        is_frontier: bool,
    ) -> str:
        """Heuristically assign a colony type based on target environment and parent personality."""
        if has_megastructure:
            return "Megastructure Colony"
        
        if is_frontier and civ_personality in ["Militaristic", "Isolationist"]:
            return "Military Outpost"

        habitability = float(planet.get("habitability_score", 0.0))
        resources = float(planet.get("resource_score", 0.0))

        if habitability > 80.0 and civ_personality == "Diplomatic":
            return "Trade Hub"
        elif habitability > 75.0:
            return "Capital Colony"
        elif resources > 70.0 and habitability < 40.0:
            return "Mining Colony"
        elif civ_personality == "Scientific":
            return "Research Colony"
        elif resources > 60.0:
            return "Industrial Colony"
        else:
            # Weighted random choice based on personality
            weights = {t: 1.0 for t in self.COLONY_TYPES if t not in ["Capital Colony", "Megastructure Colony"]}
            if civ_personality == "Militaristic":
                weights["Military Outpost"] += 3.0
            elif civ_personality == "Scientific":
                weights["Research Colony"] += 3.0
            elif civ_personality == "Industrialist":
                weights["Industrial Colony"] += 2.0
                weights["Mining Colony"] += 2.0
            elif civ_personality == "Explorer":
                weights["Research Colony"] += 1.5

            types = list(weights.keys())
            probs = np.array([weights[t] for t in types])
            probs /= probs.sum()
            return str(self.random.choice(types, p=probs))

    def _generate_colony_name(self, planet_name: str, civ_name: str, colony_type: str) -> str:
        """Procedurally generate a colony name."""
        # Clean prefix/suffixes
        short_civ = civ_name.replace("The ", "").replace("Republic of ", "").replace("Federation", "").strip()
        words = short_civ.split()
        base_name = words[0] if words else short_civ

        templates = [
            f"{planet_name} Prime",
            f"{base_name} Colony",
            f"{planet_name} Sector",
            f"{base_name} Outpost {self.random.randint(10, 99)}",
        ]

        if colony_type == "Mining Colony":
            templates.append(f"{planet_name} Excavation")
        elif colony_type == "Research Colony":
            templates.append(f"{planet_name} Science Station")
        elif colony_type == "Trade Hub":
            templates.append(f"{planet_name} Exchange")
        elif colony_type == "Military Outpost":
            templates.append(f"Fort {base_name}")
        elif colony_type == "Megastructure Colony":
            templates.append(f"{planet_name} Core Hub")

        return str(self.random.choice(templates))

    def create_colony(
        self,
        civ_id: str,
        civ_name: str,
        civ_personality: str,
        planet: Dict[str, Any],
        has_megastructure: bool = False,
        is_frontier: bool = False,
    ) -> Colony:
        """Create a new Colony instance.

        Parameters
        ----------
        civ_id : str
        civ_name : str
        civ_personality : str
        planet : Dict[str, Any]
        has_megastructure : bool
        is_frontier : bool

        Returns
        -------
        Colony
        """
        planet_id = str(planet["planet_id"])
        star_id = str(planet["star_id"])
        planet_name = str(planet.get("planet_name", planet_id))

        colony_type = self._determine_colony_type(planet, civ_personality, has_megastructure, is_frontier)
        colony_name = self._generate_colony_name(planet_name, civ_name, colony_type)

        # Initial stats
        # Population starts at 1 Million to 50 Million (based on habitability)
        habitability = float(planet.get("habitability_score", 50.0))
        initial_pop = 1e6 + (habitability / 100.0) * 4.9e7 * self.random.uniform(0.8, 1.2)
        initial_pop = float(round(initial_pop))

        development_level = 10.0  # Out of 100
        
        # Resource output scales with planet resource score and dev level
        res_score = float(planet.get("resource_score", 50.0))
        resource_output = (res_score / 100.0) * development_level * 5.0

        colony_id = hashlib.sha256(
            f"{civ_id}-{planet_id}-{self.random.randint(1000000)}".encode()
        ).hexdigest()[:10]

        return Colony(
            colony_id=colony_id,
            colony_name=colony_name,
            parent_civilization_id=civ_id,
            home_star_id=star_id,
            target_planet_id=planet_id,
            population=initial_pop,
            development_level=development_level,
            resource_output=resource_output,
            colony_type=colony_type,
            age=0.0,
        )
