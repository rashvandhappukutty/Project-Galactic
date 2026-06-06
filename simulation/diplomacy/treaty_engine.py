# simulation/diplomacy/treaty_engine.py
"""Treaty engine – creates peace treaties, trade agreements, and sanctions.
Only a minimal implementation is provided to generate CSV entries.
"""

from __future__ import annotations

import random
from typing import List

from ..models import Empire
from ..utils import write_csv, logger

DATASET_PATH = "datasets/peace_treaties.csv"


def generate_peace_treaty(empires: List[Empire]) -> dict:
    """Create a simple peace treaty between two random empires.
    Returns a dictionary representing the CSV row.
    """
    if len(empires) < 2:
        logger.warning("Not enough empires to create a treaty.")
        return {}
    a, b = random.sample(empires, 2)
    treaty = {
        "treaty_id": f"treat_{random.randint(1000,9999)}",
        "empire_a": a.empire_id,
        "empire_b": b.empire_id,
        "treaty_type": "Non‑Aggression Pact",
        "duration_years": random.randint(5, 30),
        "terms": "Mutual non‑hostility, open trade corridors",
    }
    return treaty


def run_treaty_cycle(empires: List[Empire]) -> List[dict]:
    """Each tick a small chance to generate a treaty.
    Returns list of generated treaty rows.
    """
    treaties: List[dict] = []
    if random.random() < 0.07:  # 7% chance per tick
        treaty = generate_peace_treaty(empires)
        if treaty:
            treaties.append(treaty)
            write_csv(DATASET_PATH, treaties, header=list(treaty.keys()))
            logger.info("Created peace treaty %s.", treaty["treaty_id"])
    return treaties
