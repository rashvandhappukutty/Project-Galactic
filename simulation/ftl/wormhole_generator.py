"""
wormhole_generator.py — Defines Wormhole dataclasses and procedural generation algorithms.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional
import numpy as np


@dataclass
class Wormhole:
    """Represents an interstellar wormhole shortcut.

    Attributes
    ----------
    wormhole_id : str
    wormhole_type : str
        "Natural", "Artificial", or "Ancient"
    stability_type : str
        "Stable" or "Unstable"
    entry_system : str
        Star ID of entry point.
    exit_system : str
        Star ID of exit point.
    distance_reduction : float
        Credits/light-years equivalent saved.
    stability : float
        Current stability (0.0 to 1.0).
    capacity : float
        Maximum traffic throughput.
    owner_empire : str
        Empire ID owning this wormhole, or "None".
    """

    wormhole_id: str
    wormhole_type: str
    stability_type: str
    entry_system: str
    exit_system: str
    distance_reduction: float
    stability: float
    capacity: float
    owner_empire: str = "None"

    def to_dict(self) -> Dict[str, Any]:
        """Convert wormhole state into a serializable dictionary."""
        return {
            "wormhole_id": self.wormhole_id,
            "wormhole_type": self.wormhole_type,
            "stability_type": self.stability_type,
            "entry_system": self.entry_system,
            "exit_system": self.exit_system,
            "distance_reduction": round(self.distance_reduction, 2),
            "stability": round(self.stability, 3),
            "capacity": round(self.capacity, 2),
            "owner_empire": self.owner_empire,
        }


class WormholeGenerator:
    """Generates natural, ancient, and artificial wormholes across the galaxy."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.random = np.random.RandomState(seed)

    def generate_natural_wormholes(
        self,
        stars: Dict[str, Dict[str, Any]],
        num_wormholes: int = 60
    ) -> List[Wormhole]:
        """Generate random natural wormholes connecting distant star systems.

        Parameters
        ----------
        stars : Dict[str, Dict[str, Any]]
        num_wormholes : int

        Returns
        -------
        List[Wormhole]
            List of generated natural wormholes.
        """
        wormholes: List[Wormhole] = []
        star_ids = list(stars.keys())
        if len(star_ids) < 2:
            return wormholes

        wormhole_counter = 1
        attempts = 0
        max_attempts = num_wormholes * 10

        while len(wormholes) < num_wormholes and attempts < max_attempts:
            attempts += 1
            src_id = self.random.choice(star_ids)
            tgt_id = self.random.choice(star_ids)

            if src_id == tgt_id:
                continue

            # Check if this pair is already linked
            already_linked = False
            for w in wormholes:
                if (w.entry_system == src_id and w.exit_system == tgt_id) or \
                   (w.entry_system == tgt_id and w.exit_system == src_id):
                    already_linked = True
                    break
            if already_linked:
                continue

            src_star = stars[src_id]
            tgt_star = stars[tgt_id]
            
            # Calculate Euclidean distance
            dx = float(src_star["x"]) - float(tgt_star["x"])
            dy = float(src_star["y"]) - float(tgt_star["y"])
            dz = float(src_star["z"]) - float(tgt_star["z"])
            dist = math.sqrt(dx*dx + dy*dy + dz*dz)

            # Natural wormholes connect distant systems (distance > 200 LY)
            if dist > 200.0:
                # FTL shortcut length is 5 LY
                dist_reduction = dist - 5.0
                
                # Natural wormholes are mostly unstable
                is_stable = self.random.random() < 0.2
                stability_type = "Stable" if is_stable else "Unstable"
                stability = 1.0 if is_stable else float(self.random.uniform(0.4, 0.9))
                capacity = float(self.random.uniform(500.0, 2000.0))

                w = Wormhole(
                    wormhole_id=f"WRM-NAT-{wormhole_counter:04d}",
                    wormhole_type="Natural",
                    stability_type=stability_type,
                    entry_system=src_id,
                    exit_system=tgt_id,
                    distance_reduction=dist_reduction,
                    stability=stability,
                    capacity=capacity,
                )
                wormholes.append(w)
                wormhole_counter += 1

        return wormholes

    def generate_ancient_wormholes(
        self,
        stars: Dict[str, Dict[str, Any]],
        num_wormholes: int = 40
    ) -> List[Wormhole]:
        """Generate highly stable ancient wormhole gateways.

        Parameters
        ----------
        stars : Dict[str, Dict[str, Any]]
        num_wormholes : int

        Returns
        -------
        List[Wormhole]
            List of ancient wormholes.
        """
        wormholes: List[Wormhole] = []
        star_ids = list(stars.keys())
        if len(star_ids) < 2:
            return wormholes

        wormhole_counter = 1
        attempts = 0
        max_attempts = num_wormholes * 10

        while len(wormholes) < num_wormholes and attempts < max_attempts:
            attempts += 1
            src_id = self.random.choice(star_ids)
            tgt_id = self.random.choice(star_ids)

            if src_id == tgt_id:
                continue

            # Verify no existing duplicate links
            already_linked = False
            for w in wormholes:
                if (w.entry_system == src_id and w.exit_system == tgt_id) or \
                   (w.entry_system == tgt_id and w.exit_system == src_id):
                    already_linked = True
                    break
            if already_linked:
                continue

            src_star = stars[src_id]
            tgt_star = stars[tgt_id]

            # Ancient wormholes bridge outer Rim and Bulge/Core
            src_region = src_star.get("region", "Rim")
            tgt_region = tgt_star.get("region", "Bulge")

            is_rim_to_core = (src_region == "Rim" and tgt_region in ["Bulge", "Core"]) or \
                             (tgt_region == "Rim" and src_region in ["Bulge", "Core"])

            if is_rim_to_core:
                dx = float(src_star["x"]) - float(tgt_star["x"])
                dy = float(src_star["y"]) - float(tgt_star["y"])
                dz = float(src_star["z"]) - float(tgt_star["z"])
                dist = math.sqrt(dx*dx + dy*dy + dz*dz)

                dist_reduction = dist - 2.0  # Instant transit (cost equivalent of 2 LY)
                
                # Ancient wormholes are extremely stable relics
                w = Wormhole(
                    wormhole_id=f"WRM-ANC-{wormhole_counter:04d}",
                    wormhole_type="Ancient",
                    stability_type="Stable",
                    entry_system=src_id,
                    exit_system=tgt_id,
                    distance_reduction=dist_reduction,
                    stability=1.0,
                    capacity=5000.0,  # High throughput
                )
                wormholes.append(w)
                wormhole_counter += 1

        return wormholes

    def build_artificial_wormhole(
        self,
        wormhole_counter: int,
        entry_star_id: str,
        exit_star_id: str,
        stars: Dict[str, Dict[str, Any]],
        owner_empire_id: str
    ) -> Wormhole:
        """Construct a new artificial wormhole between two owned systems.

        Parameters
        ----------
        wormhole_counter : int
        entry_star_id : str
        exit_star_id : str
        stars : Dict[str, Dict[str, Any]]
        owner_empire_id : str

        Returns
        -------
        Wormhole
        """
        src_star = stars[entry_star_id]
        tgt_star = stars[exit_star_id]

        dx = float(src_star["x"]) - float(tgt_star["x"])
        dy = float(src_star["y"]) - float(tgt_star["y"])
        dz = float(src_star["z"]) - float(tgt_star["z"])
        dist = math.sqrt(dx*dx + dy*dy + dz*dz)

        # Artificial portals have a travel cost equivalent of 1 LY
        dist_reduction = dist - 1.0

        return Wormhole(
            wormhole_id=f"WRM-ART-{wormhole_counter:04d}",
            wormhole_type="Artificial",
            stability_type="Stable",
            entry_system=entry_star_id,
            exit_system=exit_star_id,
            distance_reduction=dist_reduction,
            stability=0.95,  # Needs maintenance but stable
            capacity=3000.0,
            owner_empire=owner_empire_id,
        )


import math
