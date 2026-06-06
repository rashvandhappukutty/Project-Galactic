"""
alliance_manager.py — Handles alliance lifecycles, federations, combined power calculations, and membership transitions.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Set
import pandas as pd
import numpy as np


@dataclass
class Alliance:
    """Represents a formal alliance treaty between multiple empires."""
    alliance_id: str
    alliance_name: str
    alliance_type: str  # "Military Alliance", "Trade Alliance", "Research Alliance", "Defense Pact", "Galactic Federation"
    member_empires: List[str]
    combined_gdp: float
    combined_population: float
    combined_fleet_power: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "alliance_id": self.alliance_id,
            "alliance_name": self.alliance_name,
            "alliance_type": self.alliance_type,
            "member_empires": ",".join(self.member_empires),
            "combined_gdp": round(self.combined_gdp, 2),
            "combined_population": round(self.combined_population, 2),
            "combined_fleet_power": round(self.combined_fleet_power, 2),
        }


class AllianceManager:
    """Manages the generation, updates, and dissolutions of alliances."""

    ALLIANCES_TYPES = [
        "Military Alliance",
        "Trade Alliance",
        "Research Alliance",
        "Defense Pact",
        "Galactic Federation"
    ]

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.random = np.random.RandomState(seed)
        self.alliances: List[Alliance] = []
        self.alliance_counter = 1

    def update_alliances(
        self,
        relations_dict: Dict[tuple[str, str], Any],
        empire_stats: Dict[str, Dict[str, Any]],
        fleet_power_map: Dict[str, float]
    ) -> None:
        """Form and dissolve alliances based on current bilateral relation scores and recalculate combined stats."""
        # 1. Update existing alliances and clean dead memberships
        active_empires = set(empire_stats.keys())
        alliances_to_keep: List[Alliance] = []

        for alliance in self.alliances:
            # Keep only members still active in simulation
            valid_members = [m for m in alliance.member_empires if m in active_empires]
            
            if len(valid_members) < 2:
                # Alliance dissolves
                continue
            
            alliance.member_empires = valid_members

            # Check if members still get along
            # If average bilateral relationship of members drops below 0, member leaves or alliance dissolves
            retaining_members = [valid_members[0]]
            for m in valid_members[1:]:
                # Check relation to first member (founder) or average relation
                total_rel = 0.0
                checks = 0
                for existing in retaining_members:
                    rel_val = relations_dict.get((m, existing))
                    if rel_val:
                        total_rel += rel_val.relation_score
                        checks += 1
                
                avg_rel = total_rel / checks if checks > 0 else 0.0
                if avg_rel >= 0.0:
                    retaining_members.append(m)

            if len(retaining_members) >= 2:
                alliance.member_empires = retaining_members
                # Recalculate stats
                alliance.combined_gdp = sum(float(empire_stats[m].get("gdp", 0.0)) for m in retaining_members)
                alliance.combined_population = sum(float(empire_stats[m].get("population", 0.0)) for m in retaining_members)
                alliance.combined_fleet_power = sum(fleet_power_map.get(m, 0.0) for m in retaining_members)
                alliances_to_keep.append(alliance)

        self.alliances = alliances_to_keep

        # 2. Evaluate new alliance formations
        # Check pairs of empires that have relation > 60 and high trust
        empire_ids = list(empire_stats.keys())
        num_empires = len(empire_ids)

        for i in range(num_empires):
            id_a = empire_ids[i]
            # Check if id_a is already in a Galactic Federation (which restricts other alliances)
            if self._in_federation(id_a):
                continue

            for j in range(i + 1, num_empires):
                id_b = empire_ids[j]
                if self._in_federation(id_b):
                    continue

                # Check if already allied in any alliance
                if self.are_allied(id_a, id_b):
                    continue

                rel_ab = relations_dict.get((id_a, id_b))
                rel_ba = relations_dict.get((id_b, id_a))

                if rel_ab and rel_ba and rel_ab.relation_score > 25.0 and rel_ba.relation_score > 25.0:
                    # Form alliance!
                    # Determine type based on traits
                    personality_a = str(empire_stats[id_a].get("personality", ""))
                    personality_b = str(empire_stats[id_b].get("personality", ""))

                    if "Militaristic" in [personality_a, personality_b] and self.random.random() < 0.4:
                        a_type = "Military Alliance"
                    elif "Scientific" in [personality_a, personality_b] and self.random.random() < 0.4:
                        a_type = "Research Alliance"
                    elif "Diplomatic" in [personality_a, personality_b] and self.random.random() < 0.3:
                        a_type = "Galactic Federation"
                    elif "Industrialist" in [personality_a, personality_b] or "Explorer" in [personality_a, personality_b]:
                        a_type = "Trade Alliance"
                    else:
                        a_type = "Defense Pact"

                    # Name generation
                    prefix = "The"
                    name_a = str(empire_stats[id_a].get("empire_name", empire_stats[id_a].get("name", "Empire")))
                    name_b = str(empire_stats[id_b].get("empire_name", empire_stats[id_b].get("name", "Empire")))
                    short_a = name_a.replace("The ", "").split()[0]
                    short_b = name_b.replace("The ", "").split()[0]

                    if a_type == "Military Alliance":
                        a_name = f"{prefix} {short_a}-{short_b} Defense Coalition"
                    elif a_type == "Research Alliance":
                        a_name = f"{prefix} {short_a}-{short_b} Scientific Alliance"
                    elif a_type == "Galactic Federation":
                        a_name = f"Unified Federation of {short_a} and {short_b}"
                    elif a_type == "Trade Alliance":
                        a_name = f"{short_a}-{short_b} Commercial Treaty Organization"
                    else:
                        a_name = f"{short_a}-{short_b} Defense Pact"

                    combined_gdp = float(empire_stats[id_a].get("gdp", 0.0)) + float(empire_stats[id_b].get("gdp", 0.0))
                    combined_pop = float(empire_stats[id_a].get("population", 0.0)) + float(empire_stats[id_b].get("population", 0.0))
                    combined_fleet = fleet_power_map.get(id_a, 0.0) + fleet_power_map.get(id_b, 0.0)

                    new_alliance = Alliance(
                        alliance_id=f"ALL-{self.alliance_counter:04d}",
                        alliance_name=a_name,
                        alliance_type=a_type,
                        member_empires=[id_a, id_b],
                        combined_gdp=combined_gdp,
                        combined_population=combined_pop,
                        combined_fleet_power=combined_fleet,
                    )
                    self.alliances.append(new_alliance)
                    self.alliance_counter += 1

    def are_allied(self, id_a: str, id_b: str) -> bool:
        """Check if two empires belong to the same alliance."""
        for alliance in self.alliances:
            if id_a in alliance.member_empires and id_b in alliance.member_empires:
                return True
        return False

    def are_defense_pact_aligned(self, id_a: str, id_b: str) -> bool:
        """Check if two empires have a defense pact or military alliance / federation together."""
        for alliance in self.alliances:
            if alliance.alliance_type in ["Defense Pact", "Military Alliance", "Galactic Federation"]:
                if id_a in alliance.member_empires and id_b in alliance.member_empires:
                    return True
        return False

    def get_allies(self, id_a: str) -> List[str]:
        """Get list of all allied empire IDs for a given empire."""
        allies = []
        for alliance in self.alliances:
            if id_a in alliance.member_empires:
                for member in alliance.member_empires:
                    if member != id_a and member not in allies:
                        allies.append(member)
        return allies

    def _in_federation(self, empire_id: str) -> bool:
        """Check if an empire is in a tight Galactic Federation."""
        for alliance in self.alliances:
            if alliance.alliance_type == "Galactic Federation" and empire_id in alliance.member_empires:
                return True
        return False

    def export_alliances(self, file_path: str) -> None:
        """Save alliances database to CSV."""
        records = [al.to_dict() for al in self.alliances]
        df = pd.DataFrame(records)
        if df.empty:
            df = pd.DataFrame(columns=["alliance_id", "alliance_name", "alliance_type", "member_empires", "combined_gdp", "combined_population", "combined_fleet_power"])
        df.to_csv(file_path, index=False)
