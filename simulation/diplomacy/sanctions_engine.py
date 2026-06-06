# simulation/diplomacy/sanctions_engine.py
"""Sanctions engine – applies economic and military sanctions between empires.
Sanctions affect the `economic_dependency` and `military_parity` fields of a
Relation.
"""

from __future__ import annotations

import random
from typing import List

from ..models import Relation
from ..utils import logger, write_csv, read_csv

DATASET_PATH = "datasets/sanctions.csv"


def load_sanctions() -> List[dict]:
    return read_csv(DATASET_PATH)


def save_sanctions(sanctions: List[dict]) -> None:
    if not sanctions:
        logger.warning("No sanctions to save.")
        return
    header = list(sanctions[0].keys())
    write_csv(DATASET_PATH, sanctions, header)


def impose_sanction(relations: List[Relation], source_id: str, target_id: str, sanction_type: str = "Economic") -> None:
    """Impose a sanction on *target_id* by *source_id*.
    The function mutates the matching Relation in place.
    """
    for rel in relations:
        if (rel.empire_a == source_id and rel.empire_b == target_id) or (
            rel.empire_a == target_id and rel.empire_b == source_id
        ):
            if sanction_type == "Economic":
                rel.economic_dependency = max(0, rel.economic_dependency - random.uniform(5, 15))
                rel.trust = max(0, rel.trust - random.uniform(2, 8))
            elif sanction_type == "Military":
                rel.military_parity = max(0, rel.military_parity - random.uniform(5, 12))
                rel.influence = max(0, rel.influence - random.uniform(3, 9))
            logger.info(
                "Sanction (%s) imposed by %s on %s.", sanction_type, source_id, target_id
            )
            # Record sanction entry
            sanction_record = {
                "sanction_id": f"san_{random.randint(1000,9999)}",
                "source_empire": source_id,
                "target_empire": target_id,
                "sanction_type": sanction_type,
                "tick": 0,  # caller should set proper tick
            }
            existing = load_sanctions()
            existing.append(sanction_record)
            save_sanctions(existing)
            break


def run_sanctions_cycle(relations: List[Relation], tick: int) -> None:
    """Each tick a small chance to issue a sanction between hostile empires.
    """
    hostile_pairs = [
        (rel.empire_a, rel.empire_b)
        for rel in relations
        if rel.relation_score < -30
    ]
    if not hostile_pairs:
        return
    if random.random() < 0.04:  # 4% chance per tick
        source, target = random.choice(hostile_pairs)
        sanction_type = random.choice(["Economic", "Military"])
        impose_sanction(relations, source, target, sanction_type)
        # Update CSV after mutation
        from ..diplomacy.diplomacy_engine import save_relations
        save_relations(relations)
        logger.debug("Sanctions cycle completed for tick %d.", tick)
