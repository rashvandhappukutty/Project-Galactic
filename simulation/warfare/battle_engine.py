# simulation/warfare/battle_engine.py
"""Battle engine – resolves battles for active wars.
Simplified implementation: for each ongoing war, generate a random number of battles.
Each battle updates casualties and fleet losses in the dataset.
"""

from __future__ import annotations

import random
from typing import List

from ..models import War, Battle, Fleet, Relation
from ..utils import write_csv, logger, read_csv

DATASET_PATH = "datasets/battles.csv"


def load_battles() -> List[Battle]:
    rows = read_csv(DATASET_PATH)
    return [Battle(**r) for r in rows]


def save_battles(battles: List[Battle]) -> None:
    if not battles:
        logger.warning("No battles to save.")
        return
    header = list(battles[0].to_dict().keys())
    rows = [b.to_dict() for b in battles]
    write_csv(DATASET_PATH, rows, header)


def resolve_battle(war: War, tick: int) -> Battle:
    battle_type = random.choice([
        "Deep Space Engagement",
        "Orbital Battle",
        "System Defense",
        "Planetary Invasion",
        "Colony Assault",
        "Megastructure Siege",
        "Wormhole Assault",
        "Jump Gate Defense",
    ])
    casualties = random.randint(0, 5000)
    fleet_losses = random.randint(0, 10)
    economic_damage = random.uniform(0, 1_000_000)
    infrastructure_damage = random.uniform(0, 500_000)
    territory_change = random.choice(["Gain", "Loss", "None"])
    battle = Battle(
        war_id=war.war_id,
        location="Sector " + str(random.randint(1, 1000)),
        battle_type=battle_type,
        casualties=casualties,
        fleet_losses=fleet_losses,
        economic_damage=economic_damage,
        infrastructure_damage=infrastructure_damage,
        territory_change=territory_change,
    )
    logger.info(
        "Battle resolved for war %s – type %s, casualties %d",
        war.war_id,
        battle_type,
        casualties,
    )
    return battle


def run_battle_engine(active_wars: List[War], current_tick: int) -> List[Battle]:
    battles: List[Battle] = load_battles()
    for war in active_wars:
        # Each active war generates 0-2 battles per tick.
        for _ in range(random.randint(0, 2)):
            battle = resolve_battle(war, current_tick)
            battles.append(battle)
    save_battles(battles)
    return battles
