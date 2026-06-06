"""
fleet_generator.py — Defines Fleet structures, class attributes, maintenance budgets, and dynamic construction.
"""

from dataclasses import dataclass, asdict
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np


@dataclass
class Fleet:
    """Represents a military space fleet."""
    fleet_id: str
    owner_empire_id: str
    fleet_name: str
    fleet_class: str  # "Scout Fleet", "Defense Fleet", "Assault Fleet", "Carrier Fleet", "Dreadnought Fleet", "Titan Fleet"
    fleet_power: float
    mobility: float
    firepower: float
    shield_strength: float
    logistics: float
    current_star_id: str
    status: str       # "Idle", "In Campaign", "In Battle", "Destroyed"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class FleetGenerator:
    """Handles fleet blueprints, upkeeps, and dynamic military assembly."""

    FLEET_CLASSES = {
        "Scout Fleet": {
            "power": 80.0, "mobility": 10.0, "firepower": 15.0, "shield": 20.0, "logistics": 10.0,
            "cost": 150.0, "upkeep": 5.0, "min_tech": 1.0
        },
        "Defense Fleet": {
            "power": 350.0, "mobility": 3.0, "firepower": 80.0, "shield": 120.0, "logistics": 5.0,
            "cost": 400.0, "upkeep": 15.0, "min_tech": 3.0
        },
        "Assault Fleet": {
            "power": 700.0, "mobility": 7.0, "firepower": 180.0, "shield": 150.0, "logistics": 20.0,
            "cost": 800.0, "upkeep": 30.0, "min_tech": 4.5
        },
        "Carrier Fleet": {
            "power": 1400.0, "mobility": 5.0, "firepower": 350.0, "shield": 300.0, "logistics": 35.0,
            "cost": 1600.0, "upkeep": 60.0, "min_tech": 6.0
        },
        "Dreadnought Fleet": {
            "power": 3000.0, "mobility": 3.0, "firepower": 850.0, "shield": 600.0, "logistics": 50.0,
            "cost": 3200.0, "upkeep": 120.0, "min_tech": 7.5
        },
        "Titan Fleet": {
            "power": 6500.0, "mobility": 1.5, "firepower": 2000.0, "shield": 1500.0, "logistics": 80.0,
            "cost": 7500.0, "upkeep": 250.0, "min_tech": 9.0
        }
    }

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.random = np.random.RandomState(seed)
        self.fleets: Dict[str, Fleet] = {}
        self.fleet_counter = 1

    def generate_initial_fleets(
        self,
        empires: List[Dict[str, Any]],
        capital_stars: Dict[str, str],
        civ_techs: Dict[str, float]
    ) -> None:
        """Create baseline fleets for all empires depending on their technology level and power/wealth index."""
        self.fleets.clear()

        for e in empires:
            cid = str(e["founding_civilization_id"])
            capital_star = capital_stars.get(cid)
            if not capital_star:
                continue

            tech = civ_techs.get(cid, 5.0)
            
            # Determine starting military capacity (power index proxy)
            # Make sure every active empire gets at least 2 fleets, up to 5-6 for superpowers
            gdp = float(e.get("gdp", e.get("gdp_volume", 5000.0)))
            num_fleets = 2
            if gdp > 30000.0:
                num_fleets = 5
            elif gdp > 15000.0:
                num_fleets = 4
            elif gdp > 8000.0:
                num_fleets = 3

            # Determine fleet class templates available
            available_classes = [
                cls for cls, stats in self.FLEET_CLASSES.items() if tech >= stats["min_tech"]
            ]
            if not available_classes:
                available_classes = ["Scout Fleet"]

            for f_idx in range(1, num_fleets + 1):
                # Choose class
                # Heaviest available with higher chance, scouts with lower
                probs = np.array([float(self.FLEET_CLASSES[cls]["min_tech"]) for cls in available_classes])
                probs /= probs.sum()
                f_class = str(self.random.choice(available_classes, p=probs))

                f_stats = self.FLEET_CLASSES[f_class]

                f_id = f"FLT-{self.fleet_counter:05d}"
                f_name = f"{e['empire_name']} {f_class.split()[0]} Force {f_idx}"

                # Add fleet
                self.fleets[f_id] = Fleet(
                    fleet_id=f_id,
                    owner_empire_id=cid,
                    fleet_name=f_name,
                    fleet_class=f_class,
                    fleet_power=f_stats["power"] * self.random.uniform(0.9, 1.1),
                    mobility=f_stats["mobility"],
                    firepower=f_stats["firepower"] * self.random.uniform(0.9, 1.1),
                    shield_strength=f_stats["shield"] * self.random.uniform(0.9, 1.1),
                    logistics=f_stats["logistics"],
                    current_star_id=capital_star,
                    status="Idle"
                )
                self.fleet_counter += 1

    def build_new_fleet(
        self,
        empire_id: str,
        empire_name: str,
        capital_star: str,
        tech_level: float,
        treasury: float
    ) -> Optional[Tuple[Fleet, float]]:
        """Construct a new fleet if the empire has sufficient treasury, returns fleet and deducted cost."""
        available = [
            cls for cls, stats in self.FLEET_CLASSES.items() 
            if tech_level >= stats["min_tech"] and treasury >= stats["cost"]
        ]
        if not available:
            return None

        # Prefer building the strongest affordable fleet class
        available.sort(key=lambda x: self.FLEET_CLASSES[x]["power"], reverse=True)
        f_class = available[0]
        f_stats = self.FLEET_CLASSES[f_class]

        # Name prefix
        f_id = f"FLT-{self.fleet_counter:05d}"
        f_name = f"{empire_name} {f_class.split()[0]} Force Build"

        new_f = Fleet(
            fleet_id=f_id,
            owner_empire_id=empire_id,
            fleet_name=f_name,
            fleet_class=f_class,
            fleet_power=f_stats["power"],
            mobility=f_stats["mobility"],
            firepower=f_stats["firepower"],
            shield_strength=f_stats["shield"],
            logistics=f_stats["logistics"],
            current_star_id=capital_star,
            status="Idle"
        )
        self.fleets[f_id] = new_f
        self.fleet_counter += 1
        
        return new_f, f_stats["cost"]

    def deduct_upkeep(self, treasury_registry: Dict[str, float]) -> None:
        """Deduct fleet upkeeps from empire treasury budgets."""
        for fleet in self.fleets.values():
            if fleet.status == "Destroyed":
                continue
            
            upkeep = self.FLEET_CLASSES[fleet.fleet_class]["upkeep"]
            cid = fleet.owner_empire_id
            if cid in treasury_registry:
                # Deduct upkeep, clamping treasury to 0 if they go bankrupt
                treasury_registry[cid] = max(0.0, treasury_registry[cid] - upkeep)

    def get_empire_fleet_power(self, empire_id: str) -> float:
        """Get sum of active fleet power for an empire."""
        return sum(
            f.fleet_power for f in self.fleets.values() 
            if f.owner_empire_id == empire_id and f.status != "Destroyed"
        )

    def export_fleets(self, file_path: str) -> None:
        """Save fleets database to CSV."""
        records = [f.to_dict() for f in self.fleets.values()]
        df = pd.DataFrame(records)
        if df.empty:
            df = pd.DataFrame(columns=["fleet_id", "owner_empire_id", "fleet_name", "fleet_class", "fleet_power", "mobility", "firepower", "shield_strength", "logistics", "current_star_id", "status"])
        df.to_csv(file_path, index=False)
