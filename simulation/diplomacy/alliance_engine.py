# simulation/diplomacy/alliance_engine.py
"""Alliance management for Phase 9.
Handles creation, dissolution, and metrics for alliances and federations.
"""

from __future__ import annotations

import random
from typing import List, Dict

from ..models import Empire, Alliance
from ..utils import write_csv, read_csv, logger

DATASET_PATH = "datasets/alliances.csv"


def load_alliances() -> List[Alliance]:
    rows = read_csv(DATASET_PATH)
    alliances = []
    for r in rows:
        # members stored as pipe‑separated string
        members = r.get("members", "").split("|") if r.get("members") else []
        r["members"] = members
        alliances.append(Alliance(**r))
    return alliances


def save_alliances(alliances: List[Alliance]) -> None:
    if not alliances:
        logger.warning("No alliances to save.")
        return
    # Convert members back to pipe‑separated string for CSV.
    rows = []
    for a in alliances:
        d = a.to_dict()
        rows.append(d)
    header = list(rows[0].keys())
    write_csv(DATASET_PATH, rows, header)


def create_alliance(name: str, member_ids: List[str], alliance_type: str = "Military") -> Alliance:
    alliance = Alliance(name=name, members=member_ids, alliance_type=alliance_type)
    # Simple aggregate calculations.
    alliance.combined_fleet_power = 0.0
    alliance.combined_gdp = 0.0
    alliance.combined_population = 0
    # In a real system we would look up Empire data; here we leave zeros.
    logger.info("Created alliance %s with %d members.", name, len(member_ids))
    return alliance


def dissolve_alliance(alliance_id: str) -> None:
    alliances = load_alliances()
    alliances = [a for a in alliances if a.alliance_id != alliance_id]
    save_alliances(alliances)
    logger.info("Dissolved alliance %s.", alliance_id)


def update_alliance_strength(alliance: Alliance) -> None:
    # Placeholder: strength is a function of member count and combined GDP.
    alliance.alliance_strength = (len(alliance.members) * 10) + (alliance.combined_gdp * 0.001)
    logger.debug("Updated strength for alliance %s to %f.", alliance.alliance_id, alliance.alliance_strength)

def run_alliance_cycle(empires: List[Empire]) -> List[Alliance]:
    """Simple cycle that occasionally creates a new alliance.
    In a full implementation this would consider diplomatic scores.
    """
    alliances = load_alliances()
    # 5% chance each tick to form a new random alliance of 3‑5 empires.
    if random.random() < 0.05:
        members = random.sample([e.empire_id for e in empires], k=random.randint(3, 5))
        new_alliance = create_alliance(name=f"Alliance_{random.randint(1000,9999)}", member_ids=members)
        alliances.append(new_alliance)
    # Update strength for existing alliances.
    for a in alliances:
        update_alliance_strength(a)
    save_alliances(alliances)
    return alliances
