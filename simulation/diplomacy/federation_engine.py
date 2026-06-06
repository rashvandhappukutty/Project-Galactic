# simulation/diplomacy/federation_engine.py
"""Federation management for Phase 9.
A federation is a higher‑level political bloc that groups multiple alliances.
For now we implement a very light version that aggregates member alliances
and provides a simple strength metric.
"""

from __future__ import annotations

import random
from typing import List

from ..models import Alliance, Empire
from ..utils import write_csv, read_csv, logger

DATASET_PATH = "datasets/federations.csv"


def load_federations() -> List[dict]:
    """Load federation records from CSV.
    Returns a list of raw dictionaries; the real model can be added later.
    """
    rows = read_csv(DATASET_PATH)
    return rows


def save_federations(federations: List[dict]) -> None:
    if not federations:
        logger.warning("No federations to save.")
        return
    header = list(federations[0].keys())
    write_csv(DATASET_PATH, federations, header)


def create_federation(name: str, alliance_ids: List[str]) -> dict:
    """Create a federation from a list of alliance IDs.
    The federation dictionary stores the name, member alliance IDs, and a simple
    `federation_strength` calculated from the number of members.
    """
    federation = {
        "federation_id": f"fed_{random.randint(1000, 9999)}",
        "name": name,
        "members": "|".join(alliance_ids),
        "federation_strength": len(alliance_ids) * 10.0,
    }
    logger.info("Created federation %s with %d alliances.", name, len(alliance_ids))
    return federation


def run_federation_cycle(alliances: List[Alliance]) -> List[dict]:
    """Very simple cycle: occasionally group 2‑3 alliances into a federation.
    In a full system this would consider diplomatic scores and strategic goals.
    """
    federations = load_federations()
    if random.random() < 0.03 and len(alliances) >= 2:
        chosen = random.sample(alliances, k=random.randint(2, min(3, len(alliances))))
        alliance_ids = [a.alliance_id for a in chosen]
        new_fed = create_federation(name=f"Federation_{random.randint(100,999)}", alliance_ids=alliance_ids)
        federations.append(new_fed)
    save_federations(federations)
    return federations
