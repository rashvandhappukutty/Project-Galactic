# simulation/warfare/fleet_engine.py
"""Fleet generation engine for Phase 9.
Each empire receives a set of fleets based on its GDP and `fleet_budget_factor`.
The generated fleets are written to `datasets/fleet_registry.csv`.
"""

from __future__ import annotations

import random
from typing import List

from ..models import Empire, Fleet
from ..utils import write_csv, logger, ensure_dir
from ..enums import FleetType

DATASET_PATH = "datasets/fleet_registry.csv"


def load_fleets() -> List[Fleet]:
    """Load existing fleets from CSV. Returns empty list if file missing."""
    try:
        from ..utils import read_csv
        rows = read_csv(DATASET_PATH)
        return [Fleet(**r) for r in rows]
    except Exception:
        logger.warning("Fleet registry not found, starting fresh.")
        return []


def save_fleets(fleets: List[Fleet]) -> None:
    if not fleets:
        logger.warning("No fleets to save.")
        return
    header = list(fleets[0].to_dict().keys())
    rows = [fleet.to_dict() for fleet in fleets]
    write_csv(DATASET_PATH, rows, header)


def generate_fleet_for_empire(empire: Empire) -> List[Fleet]:
    """Generate a list of fleets for a single empire.
    The number of fleets scales with the empire's GDP (larger economies have more fleets).
    """
    # Simple heuristic: 1 fleet per 10 billion GDP, minimum 1 fleet.
    fleet_budget = max(1, int(empire.gdp // 1e10))
    fleets: List[Fleet] = []
    for _ in range(fleet_budget):
        fleet_type = random.choice(list(FleetType))
        # Base power values per type (could be refined later).
        base_power = {
            "Scout": 10,
            "Patrol": 20,
            "Defense": 30,
            "Assault": 40,
            "Carrier": 60,
            "Titan": 80,
            "Dreadnought": 120,
            "Planet Killer": 200,
        }[fleet_type.value]
        # Scale by tech level and random factor.
        scale = 1 + (empire.tech_level * 0.05) + random.uniform(-0.1, 0.1)
        fleet_power = base_power * scale
        fleet = Fleet(
            owner_empire=empire.empire_id,
            fleet_type=fleet_type.value,
            fleet_power=fleet_power,
            firepower=fleet_power * 0.6,
            mobility=random.uniform(0.5, 1.5),
            shield_strength=fleet_power * 0.4,
            logistics_capacity=fleet_power * 0.3,
            commander_rating=random.uniform(0, 5),
        )
        fleets.append(fleet)
    logger.info("Generated %d fleets for empire %s", len(fleets), empire.name)
    return fleets


def run_fleet_engine(empires: List[Empire]) -> List[Fleet]:
    """Create fleets for all empires and persist them."""
    all_fleets: List[Fleet] = []
    for emp in empires:
        emp_fleets = generate_fleet_for_empire(emp)
        all_fleets.extend(emp_fleets)
    save_fleets(all_fleets)
    return all_fleets
