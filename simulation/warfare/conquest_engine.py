# simulation/warfare/conquest_engine.py
"""Conquest engine – processes post‑battle territorial changes.
Creates Conquest entries and updates empire datasets accordingly.
"""

from __future__ import annotations

import random
from typing import List

from ..models import Empire, War, Conquest, Relation
from ..utils import write_csv, logger, read_csv

DATASET_PATH = "datasets/conquests.csv"


def load_conquests() -> List[Conquest]:
    rows = read_csv(DATASET_PATH)
    return [Conquest(**r) for r in rows]


def save_conquests(conquests: List[Conquest]) -> None:
    if not conquests:
        logger.warning("No conquests to save.")
        return
    header = list(conquests[0].to_dict().keys())
    rows = [c.to_dict() for c in conquests]
    write_csv(DATASET_PATH, rows, header)


def evaluate_conquest(war: War, battle_outcomes: List[dict]) -> List[Conquest]:
    """Based on battle outcomes, decide if territory changes occur.
    Simplified: each battle has a 20% chance to result in a conquest.
    """
    conquests: List[Conquest] = []
    for battle in battle_outcomes:
        if random.random() < 0.2:
            territories = random.randint(1, 5)
            pop_shift = random.randint(1000, 100000)
            res_shift = random.uniform(1000, 50000)
            c = Conquest(
                war_id=war.war_id,
                conquering_empire=war.attacker,
                conquered_entity=battle.get("location", "Unknown"),
                territories_gained=territories,
                population_shift=pop_shift,
                resource_shift=res_shift,
            )
            conquests.append(c)
    return conquests


def run_conquest_engine(active_wars: List[War], battles: List[Battle]) -> List[Conquest]:
    # Group battles by war_id
    war_to_battles = {}
    for b in battles:
        war_to_battles.setdefault(b.war_id, []).append(b)
    all_conquests: List[Conquest] = []
    for war in active_wars:
        battle_list = war_to_battles.get(war.war_id, [])
        new_cons = evaluate_conquest(war, [b.to_dict() for b in battle_list])
        all_conquests.extend(new_cons)
    save_conquests(all_conquests)
    return all_conquests
