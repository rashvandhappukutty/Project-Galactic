# simulation/enums.py
"""Enum definitions for Phase 9 engines.
All enums inherit from `str` and `Enum` so that they are JSON‑serializable
and can be stored directly in CSV fields if needed.
"""

from enum import Enum, auto

class FleetType(str, Enum):
    SCOUT = "Scout"
    PATROL = "Patrol"
    DEFENSE = "Defense"
    ASSAULT = "Assault"
    CARRIER = "Carrier"
    TITAN = "Titan"
    DREADNOUGHT = "Dreadnought"
    PLANET_KILLER = "Planet Killer"

class WarTrigger(str, Enum):
    BORDER_DISPUTE = "Border Dispute"
    RESOURCE_SCARCITY = "Resource Scarcity"
    TRADE_CONFLICT = "Trade Conflict"
    ALLIANCE_OBLIGATION = "Alliance Obligation"
    IDEOLOGICAL_DIFFERENCE = "Ideological Difference"
    TERRITORIAL_CLAIM = "Territorial Claim"
    SPY_INCIDENT = "Spy Incident"
    RANDOM_CRISIS = "Random Crisis"

class BattleType(str, Enum):
    DEEP_SPACE = "Deep Space Engagement"
    ORBITAL = "Orbital Battle"
    SYSTEM_DEFENSE = "System Defense"
    PLANETARY_INVASION = "Planetary Invasion"
    COLONY_ASSAULT = "Colony Assault"
    MEGASTRUCTURE_SIEGE = "Megastructure Siege"
    WORMHOLE_ASSAULT = "Wormhole Assault"
    JUMP_GATE_DEFENSE = "Jump Gate Defense"

class CrisisType(str, Enum):
    GREAT_WAR = "Great Galactic War"
    AI_UPRISING = "AI Uprising"
    ECONOMIC_COLLAPSE = "Economic Collapse"
    WORMHOLE_COLLAPSE = "Wormhole Collapse"
    FTL_FAILURE = "FTL Network Failure"
    RESOURCE_CATASTROPHE = "Resource Catastrophe"
    PANDEMIC = "Pandemic Event"
    MEGASTRUCTURE_FAILURE = "Megastructure Failure"
    REFUGEE_CRISIS = "Refugee Crisis"
    POLITICAL_FRAGMENTATION = "Political Fragmentation"

class DiplomaticAction(str, Enum):
    TRADE_AGREEMENT = "Trade Agreement"
    TREATY = "Treaty"
    SANCTION = "Sanction"
    ALLIANCE_FORM = "Form Alliance"
    ALLIANCE_DISSOLVE = "Dissolve Alliance"
    FEDERATION_FORM = "Form Federation"
    FEDERATION_DISSOLVE = "Dissolve Federation"
