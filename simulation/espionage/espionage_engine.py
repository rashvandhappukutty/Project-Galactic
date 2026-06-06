# simulation/espionage/espionage_engine.py
"""Espionage engine orchestrating spy operations between empires.
Each tick a set of operations is generated based on diplomatic tension.
"""

from __future__ import annotations

import random
from typing import List

from ..models import Empire, EspionageOperation, Relation
from ..utils import write_csv, read_csv, random_probability, logger

DATASET_PATH = "datasets/espionage_operations.csv"


def load_operations() -> List[EspionageOperation]:
    rows = read_csv(DATASET_PATH)
    return [EspionageOperation(**r) for r in rows]


def save_operations(ops: List[EspionageOperation]) -> None:
    if not ops:
        logger.warning("No espionage operations to save.")
        return
    header = list(ops[0].to_dict().keys())
    rows = [op.to_dict() for op in ops]
    write_csv(DATASET_PATH, rows, header)


def generate_operations(empires: List[Empire], relations: List[Relation]) -> List[EspionageOperation]:
    """Generate espionage missions based on low relation scores.
    Empires with hostile relations are more likely to attempt sabotage or
    technology theft.
    """
    ops: List[EspionageOperation] = []
    for rel in relations:
        # Hostile threshold
        if rel.relation_score < -20:
            source = rel.empire_a
            target = rel.empire_b
            # Choose operation type weighted by hostility
            op_type = random.choices(
                ["Technology Theft", "Economic Sabotage", "Political Destabilization", "Military Intelligence"],
                weights=[0.4, 0.3, 0.2, 0.1],
            )[0]
            base_prob = 0.4  # baseline success chance
            # More hostile => lower success
            prob = max(0.05, base_prob - (abs(rel.relation_score) / 500))
            success = random.random() < prob
            op = EspionageOperation(
                source_empire=source,
                target_empire=target,
                operation_type=op_type,
                success_probability=prob,
                success_result="Success" if success else "Failure",
                damage_score=random.uniform(0, 100) if success else 0.0,
                intelligence_value=random.uniform(0, 200) if success else 0.0,
            )
            ops.append(op)
    logger.info("Generated %d espionage operations this tick.", len(ops))
    return ops


def run_espionage(empires: List[Empire], relations: List[Relation]) -> List[EspionageOperation]:
    ops = generate_operations(empires, relations)
    save_operations(ops)
    return ops
