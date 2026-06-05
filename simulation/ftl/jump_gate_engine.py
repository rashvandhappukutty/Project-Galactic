"""
jump_gate_engine.py — Jump gate construction, Relays, and gateway linkages.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


@dataclass
class JumpGate:
    """Represents an empire-constructed jump gateway.

    Attributes
    ----------
    gate_id : str
    gate_type : str
        "Regional Gate", "Empire Gate", "Galactic Gate", or "Quantum Relay Gate"
    star_id : str
        Star system location.
    construction_cost : float
        GC cost to build.
    energy_usage : float
        Credits upkeep per tick.
    throughput : float
        Traffic throughput.
    connected_systems : List[str]
        Star IDs linked by gateway.
    owner_empire : str
        Founding empire ID.
    """

    gate_id: str
    gate_type: str
    star_id: str
    construction_cost: float
    energy_usage: float
    throughput: float
    connected_systems: List[str] = field(default_factory=list)
    owner_empire: str = "None"

    def to_dict(self) -> Dict[str, Any]:
        """Convert gate fields into a dictionary."""
        return {
            "gate_id": self.gate_id,
            "gate_type": self.gate_type,
            "star_id": self.star_id,
            "construction_cost": round(self.construction_cost, 2),
            "energy_usage": round(self.energy_usage, 2),
            "throughput": round(self.throughput, 2),
            "connected_count": len(self.connected_systems),
            "owner_empire": self.owner_empire,
        }


class JumpGateEngine:
    """Simulates jump gate engineering networks."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        
        # Registry
        self.gates: Dict[str, JumpGate] = {}  # star_id -> JumpGate

    def attempt_construction(
        self,
        gate_counter: int,
        star_id: str,
        tech_level: float,
        treasury: float,
        empire_id: str,
        colony_type: str
    ) -> tuple[bool, float, Optional["JumpGate"]]:
        """Attempt to construct a jump gate based on FTL technology level and treasury credits.

        Parameters
        ----------
        gate_counter : int
        star_id : str
        tech_level : float
        treasury : float
        empire_id : str
        colony_type : str

        Returns
        -------
        tuple[bool, float, Optional[JumpGate]]
            Success status, Credits cost deducted, and constructed JumpGate.
        """
        # Construction requirements:
        # - Jump Gates require Level 4+ FTL tech (Tech level >= 6.0)
        # - Must have sufficient treasury credits
        if tech_level < 6.0:
            return False, 0.0, None

        # Determine gate type based on Tech & Location
        # - Capitals get Empire Gates (standard) or Quantum Gates (L6+ tech)
        # - Colonies get Regional Gates
        if tech_level >= 8.5 and colony_type == "Capital Colony":
            g_type = "Quantum Relay Gate"
            cost = 8000.0
            upkeep = 400.0
            cap = 10000.0
        elif tech_level >= 7.0 and colony_type == "Capital Colony":
            g_type = "Galactic Gate"
            cost = 5000.0
            upkeep = 250.0
            cap = 5000.0
        elif colony_type == "Capital Colony":
            g_type = "Empire Gate"
            cost = 3000.0
            upkeep = 150.0
            cap = 2500.0
        else:
            g_type = "Regional Gate"
            cost = 1500.0
            upkeep = 75.0
            cap = 1000.0

        if treasury < cost:
            return False, 0.0, None

        # Build Gate
        gate = JumpGate(
            gate_id=f"GAT-{gate_counter:04d}",
            gate_type=g_type,
            star_id=star_id,
            construction_cost=cost,
            energy_usage=upkeep,
            throughput=cap,
            owner_empire=empire_id
        )
        self.gates[star_id] = gate
        return True, cost, gate

    def connect_gateways(self, stars: Dict[str, Dict[str, Any]]) -> None:
        """Establish relayer connections across all constructed jump gates.

        Parameters
        ----------
        stars : Dict[str, Dict[str, Any]]
        """
        # Clear connections
        for gate in self.gates.values():
            gate.connected_systems.clear()

        gate_list = list(self.gates.values())
        num_gates = len(gate_list)

        # Connect gate endpoints
        for i in range(num_gates):
            gate_a = gate_list[i]
            star_a = stars.get(gate_a.star_id)
            if not star_a:
                continue
            coords_a = (float(star_a["x"]), float(star_a["y"]), float(star_a["z"]))

            for j in range(i + 1, num_gates):
                gate_b = gate_list[j]
                star_b = stars.get(gate_b.star_id)
                if not star_b:
                    continue
                coords_b = (float(star_b["x"]), float(star_b["y"]), float(star_b["z"]))

                # Calculate distance
                dx = coords_a[0] - coords_b[0]
                dy = coords_a[1] - coords_b[1]
                dz = coords_a[2] - coords_b[2]
                d = math.sqrt(dx*dx + dy*dy + dz*dz)

                # Link rules:
                # 1. Quantum Relay Gates and Galactic Gates connect globally (any distance)
                if (gate_a.gate_type in ["Quantum Relay Gate", "Galactic Gate"]) and \
                   (gate_b.gate_type in ["Quantum Relay Gate", "Galactic Gate"]):
                    gate_a.connected_systems.append(gate_b.star_id)
                    gate_b.connected_systems.append(gate_a.star_id)
                    continue

                # 2. Empire Gates connect to all other gates owned by the same empire
                if gate_a.owner_empire == gate_b.owner_empire:
                    gate_a.connected_systems.append(gate_b.star_id)
                    gate_b.connected_systems.append(gate_a.star_id)
                    continue

                # 3. Regional Gates link to any gate within 100 LY
                if d <= 100.0:
                    gate_a.connected_systems.append(gate_b.star_id)
                    gate_b.connected_systems.append(gate_a.star_id)


import math
from typing import Optional
