"""
invasion_engine.py — Manages planetary invasions, ground combat power checks, and colony capture operations.
"""

from dataclasses import dataclass
from typing import Dict, List, Any
import pandas as pd
import numpy as np


@dataclass
class Conquest:
    """Represents a territorial capture or sovereignty shift event."""
    conquest_id: str
    war_id: str
    attacker_id: str
    defender_id: str
    target_id: str
    action: str  # "Capture Colony", "Capture System", "Annex Territory", "Liberate System", "Destroy Infrastructure", "Collapse Rival"
    year: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "conquest_id": self.conquest_id,
            "war_id": self.war_id,
            "attacker_id": self.attacker_id,
            "defender_id": self.defender_id,
            "target_id": self.target_id,
            "action": self.action,
            "year": round(self.year, 2),
        }


class InvasionEngine:
    """Handles ground troop landings, orbital planetary sieges, and border shifts."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.random = np.random.RandomState(seed)
        self.conquests: List[Conquest] = []
        self.conquest_counter = 1

    def resolve_invasion(
        self,
        war_id: str,
        attacker_id: str,
        defender_id: str,
        colony: Any,  # Colony
        planet: Dict[str, Any],
        invading_fleet_power: float,
        year: float,
        attacker_personality: str
    ) -> bool:
        """Resolve a ground invasion of a colony. Returns True if captured, False otherwise."""
        # Calculate defense value based on population, development level, and colony type
        pop_factor = float(colony.population) / 1.0e7  # 1 point per 10 million pop
        dev_factor = float(colony.development_level) * 5.0
        
        colony_type = str(colony.colony_type)
        defense_bonus = 100.0 if colony_type == "Military Outpost" else 10.0
        if colony_type == "Capital Colony":
            defense_bonus = 200.0
        
        defense_value = pop_factor + dev_factor + defense_bonus
        invasion_power = invading_fleet_power * self.random.uniform(0.8, 1.5)
        defense_roll = defense_value * self.random.uniform(0.8, 1.2)

        success = invasion_power > defense_roll

        if success:
            # Transfer sovereignty
            old_parent = colony.parent_civilization_id
            colony.parent_civilization_id = attacker_id

            # Determine action based on attacker personality
            if attacker_personality == "Militaristic":
                action = "Annex Territory"
            elif attacker_personality == "Industrialist" and self.random.random() < 0.4:
                action = "Destroy Infrastructure"
                # Sabotage development level
                colony.development_level = max(5.0, colony.development_level - 30.0)
            elif attacker_personality == "Diplomatic" and self.random.random() < 0.3:
                action = "Liberate System"
            else:
                action = "Capture Colony"

            conquest = Conquest(
                conquest_id=f"CON-{self.conquest_counter:05d}",
                war_id=war_id,
                attacker_id=attacker_id,
                defender_id=defender_id,
                target_id=colony.target_planet_id,
                action=action,
                year=year
            )
            self.conquests.append(conquest)
            self.conquest_counter += 1
            return True
        else:
            # Defended successfully, but dev level drops due to bombing
            colony.development_level = max(5.0, colony.development_level - 10.0)
            return False

    def record_system_conquest(
        self,
        war_id: str,
        attacker_id: str,
        defender_id: str,
        star_id: str,
        year: float
    ) -> None:
        """Log system annexation without specific colonies."""
        conquest = Conquest(
            conquest_id=f"CON-{self.conquest_counter:05d}",
            war_id=war_id,
            attacker_id=attacker_id,
            defender_id=defender_id,
            target_id=star_id,
            action="Annex Territory",
            year=year
        )
        self.conquests.append(conquest)
        self.conquest_counter += 1

    def record_empire_collapse(
        self,
        war_id: str,
        attacker_id: str,
        defender_id: str,
        year: float
    ) -> None:
        """Log the complete political collapse and capitulation of an empire."""
        conquest = Conquest(
            conquest_id=f"CON-{self.conquest_counter:05d}",
            war_id=war_id,
            attacker_id=attacker_id,
            defender_id=defender_id,
            target_id="Empire Capital",
            action="Collapse Rival",
            year=year
        )
        self.conquests.append(conquest)
        self.conquest_counter += 1

    def export_conquests(self, file_path: str) -> None:
        """Save conquests database to CSV."""
        records = [c.to_dict() for c in self.conquests]
        df = pd.DataFrame(records)
        if df.empty:
            df = pd.DataFrame(columns=["conquest_id", "war_id", "attacker_id", "defender_id", "target_id", "action", "year"])
        df.to_csv(file_path, index=False)
