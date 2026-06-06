# simulation/warfare/war_engine.py
"""War engine – decides when wars start based on diplomatic tensions and other triggers.
Generates War objects and writes them to `datasets/wars.csv`.
"""

from __future__ import annotations

import random
from typing import List

from ..models import Empire, Relation, War
from ..utils import write_csv, logger

DATASET_PATH = "datasets/wars.csv"


def load_existing_wars() -> List[War]:
    from ..utils import read_csv
    rows = read_csv(DATASET_PATH)
    return [War(**r) for r in rows]


def save_wars(wars: List[War]) -> None:
    if not wars:
        logger.warning("No wars to save.")
        return
    header = list(wars[0].to_dict().keys())
    rows = [w.to_dict() for w in wars]
    write_csv(DATASET_PATH, rows, header)


def evaluate_triggers(relations: List[Relation]) -> List[tuple]:
    """Return a list of (attacker_id, defender_id, reason) tuples for potential wars.
    Simple heuristic: hostile relation_score + random factor.
    """
    candidates = []
    for rel in relations:
        # Hostile threshold
        if rel.relation_score < -40:
            # 15% chance to trigger a war from the more aggressive side
            if random.random() < 0.15:
                reason = random.choice([
                    "Border Dispute",
                    "Resource Scarcity",
                    "Trade Conflict",
                    "Alliance Obligation",
                    "Ideological Difference",
                    "Territorial Claim",
                    "Spy Incident",
                    "Random Crisis",
                ])
                # Randomly pick attacker/defender based on influence
                attacker = rel.empire_a if rel.influence >= rel.trust else rel.empire_b
                defender = rel.empire_b if attacker == rel.empire_a else rel.empire_a
                candidates.append((attacker, defender, reason))
    return candidates


def create_war(attacker: str, defender: str, reason: str, start_year: int) -> War:
    scale = random.choice(["Limited", "Regional", "Galaxy‑wide"])
    war = War(
        attacker=attacker,
        defender=defender,
        war_reason=reason,
        war_scale=scale,
        start_year=start_year,
        duration_years=0,  # will be updated when war ends.
    )
    logger.info("War declared: %s vs %s – %s (%s)", attacker, defender, reason, scale)
    return war


def run_war_engine(relations: List[Relation], existing_wars: List[War], current_year: int) -> List[War]:
    # Update ongoing wars' duration
    for war in existing_wars:
        war.duration_years += 1
    # Evaluate new triggers
    new_triggers = evaluate_triggers(relations)
    for attacker, defender, reason in new_triggers:
        war = create_war(attacker, defender, reason, start_year=current_year)
        existing_wars.append(war)
    save_wars(existing_wars)
    return existing_wars
