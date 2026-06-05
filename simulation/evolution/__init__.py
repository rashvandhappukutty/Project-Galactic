"""
__init__.py — Initialization file for the evolution package in the Galactic Dream Engine.

Phase 4: Civilization Evolution Engine.
Exports TechnologyEngine, GovernmentEngine, and EnergyEngine.
"""

from simulation.evolution.technology_engine import TechnologyEngine
from simulation.evolution.government_engine import GovernmentEngine
from simulation.evolution.energy_engine import EnergyEngine

__all__ = [
    "TechnologyEngine",
    "GovernmentEngine",
    "EnergyEngine",
]
