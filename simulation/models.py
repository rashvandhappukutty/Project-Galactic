# simulation/models.py
"""Data models for the Galactic Dream Engine Phase 9.
All classes are simple dataclasses with type hints. They provide
serialization helpers to/from CSV rows.
"""

from __future__ import annotations

import dataclasses
from dataclasses import dataclass, field
from typing import List, Dict, Any
import uuid


def _new_id(prefix: str) -> str:
    """Generate a deterministic UUID based identifier with a prefix.
    The prefix helps to quickly identify the entity type in CSV files.
    """
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


@dataclass
class Empire:
    empire_id: str = field(default_factory=lambda: _new_id("emp"))
    name: str = "Unnamed Empire"
    population: int = 0
    gdp: float = 0.0
    tech_level: int = 0
    # Additional fields can be added as needed.

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)

    @staticmethod
    def from_dict(data: Dict[str, Any]) -> "Empire":
        return Empire(**data)


@dataclass
class Relation:
    relation_id: str = field(default_factory=lambda: _new_id("rel"))
    empire_a: str = ""
    empire_b: str = ""
    relation_score: float = 0.0  # -100 to 100
    trust: float = 0.0
    influence: float = 0.0
    cultural_similarity: float = 0.0
    economic_dependency: float = 0.0
    military_parity: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class Alliance:
    alliance_id: str = field(default_factory=lambda: _new_id("all"))
    name: str = "Unnamed Alliance"
    members: List[str] = field(default_factory=list)
    alliance_type: str = "Military"  # e.g., Military, Research, Trade, Defense, Federation
    combined_gdp: float = 0.0
    combined_population: int = 0
    combined_fleet_power: float = 0.0
    alliance_strength: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        # Store members as a pipe‑separated string for CSV compatibility.
        base = dataclasses.asdict(self)
        base["members"] = "|".join(self.members)
        return base


@dataclass
class Fleet:
    fleet_id: str = field(default_factory=lambda: _new_id("flt"))
    owner_empire: str = ""
    fleet_type: str = "Scout"
    fleet_power: float = 0.0
    firepower: float = 0.0
    mobility: float = 0.0
    shield_strength: float = 0.0
    logistics_capacity: float = 0.0
    commander_rating: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class War:
    war_id: str = field(default_factory=lambda: _new_id("war"))
    attacker: str = ""
    defender: str = ""
    war_reason: str = ""
    war_scale: str = ""
    start_year: int = 0
    duration_years: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class Battle:
    battle_id: str = field(default_factory=lambda: _new_id("bat"))
    war_id: str = ""
    location: str = ""
    battle_type: str = "Deep Space Engagement"
    casualties: int = 0
    fleet_losses: int = 0
    economic_damage: float = 0.0
    infrastructure_damage: float = 0.0
    territory_change: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class Conquest:
    conquest_id: str = field(default_factory=lambda: _new_id("cqt"))
    war_id: str = ""
    conquering_empire: str = ""
    conquered_entity: str = ""  # could be a colony, system, or whole empire
    territories_gained: int = 0
    population_shift: int = 0
    resource_shift: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class EspionageOperation:
    operation_id: str = field(default_factory=lambda: _new_id("esp"))
    source_empire: str = ""
    target_empire: str = ""
    operation_type: str = "Technology Theft"
    success_probability: float = 0.0
    success_result: str = ""
    damage_score: float = 0.0
    intelligence_value: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)


@dataclass
class Crisis:
    crisis_id: str = field(default_factory=lambda: _new_id("cri"))
    crisis_type: str = "Great Galactic War"
    start_year: int = 0
    end_year: int = 0
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return dataclasses.asdict(self)
