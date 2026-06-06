"""
espionage_engine.py — Simulates covert operations, technological theft, economic sabotage, and security breaches.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np


@dataclass
class EspionageOperation:
    """Represents a covert spy mission executed by one empire against another."""
    operation_id: str
    tick: int
    attacker_id: str
    target_id: str
    operation_type: str  # "Technology Theft", "Economic Sabotage", "Political Manipulation", "Intelligence Gathering", "Infrastructure Disruption", "Spy Recruitment"
    success_rate: float
    success: bool
    damage: float
    intelligence_gain: float
    counterintelligence_score: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operation_id": self.operation_id,
            "tick": self.tick,
            "attacker_id": self.attacker_id,
            "target_id": self.target_id,
            "operation_type": self.operation_type,
            "success_rate": round(self.success_rate, 3),
            "success": self.success,
            "damage": round(self.damage, 2),
            "intelligence_gain": round(self.intelligence_gain, 2),
            "counterintelligence_score": round(self.counterintelligence_score, 2),
        }


class EspionageEngine:
    """Simulates covert strikes, intelligence gathering, and security defense."""

    OPERATIONS = [
        "Technology Theft",
        "Economic Sabotage",
        "Political Manipulation",
        "Intelligence Gathering",
        "Infrastructure Disruption",
        "Spy Recruitment"
    ]

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.random = np.random.RandomState(seed)
        self.operations: List[EspionageOperation] = []
        self.op_counter = 1

    def run_tick_operations(
        self,
        tick: int,
        empires: List[Dict[str, Any]],
        relations_dict: Dict[Tuple[str, str], Any],
        empire_stats: Dict[str, Dict[str, Any]],
        treasury_registry: Dict[str, float],
        stability_registry: Dict[str, float],
        civ_techs: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Identify rivals, execute spy missions, apply damages, and return list of event logs."""
        logs = []
        empire_ids = [str(e["founding_civilization_id"]) for e in empires]
        
        # Empires with relation_score < -30 are considered rivals
        for id_a in empire_ids:
            if id_a not in empire_stats:
                continue

            personality_a = str(empire_stats[id_a].get("personality", ""))
            
            # Base spy capacity: militaristic or scientific empires spy more
            spy_chance = 0.05
            if personality_a == "Militaristic":
                spy_chance = 0.15
            elif personality_a == "Scientific":
                spy_chance = 0.12
            elif personality_a == "Isolationist":
                spy_chance = 0.02  # focusing on counterintelligence

            for id_b in empire_ids:
                if id_a == id_b or id_b not in empire_stats:
                    continue

                rel_ab = relations_dict.get((id_a, id_b))
                if rel_ab and rel_ab.relation_score < -15.0:
                    # Rolling for spy operation
                    if self.random.random() < spy_chance:
                        op_type = str(self.random.choice(self.OPERATIONS))
                        
                        # Calculate success rate
                        # Attacker factor: tech_level + scientific trait influence
                        tech_a = civ_techs.get(id_a, 5.0)
                        tech_b = civ_techs.get(id_b, 5.0)
                        
                        # Target counterintelligence score: tech + security rating
                        # Isolationist empires get a +15% counterintelligence bonus
                        ci_score = tech_b * 10.0
                        personality_b = str(empire_stats[id_b].get("personality", ""))
                        if personality_b == "Isolationist":
                            ci_score += 15.0
                        
                        success_rate = 0.50 + (tech_a - tech_b) * 0.05
                        success_rate = max(0.10, min(0.90, success_rate))
                        
                        success = float(self.random.random()) < success_rate
                        damage = 0.0
                        intel_gain = 0.0
                        
                        if success:
                            # Apply effects
                            if op_type == "Technology Theft":
                                # Transfer 0.05 tech level
                                tech_gain = 0.05
                                civ_techs[id_a] = round(civ_techs.get(id_a, 5.0) + tech_gain, 3)
                                civ_techs[id_b] = round(max(1.0, civ_techs.get(id_b, 5.0) - tech_gain), 3)
                                intel_gain = 30.0
                                logs.append({
                                    "tick": tick,
                                    "civilization_id": id_a,
                                    "event_type": "Espionage",
                                    "description": f"{empire_stats[id_a]['empire_name']} successfully stole technology research notes from {empire_stats[id_b]['empire_name']}.",
                                })
                            elif op_type == "Economic Sabotage":
                                # Transfer credits
                                amount = min(treasury_registry.get(id_b, 0.0), 600.0)
                                if amount > 0:
                                    treasury_registry[id_b] -= amount
                                    treasury_registry[id_a] += amount
                                damage = amount
                                logs.append({
                                    "tick": tick,
                                    "civilization_id": id_a,
                                    "event_type": "Espionage",
                                    "description": f"{empire_stats[id_a]['empire_name']} completed an economic heist against {empire_stats[id_b]['empire_name']}, siphoning {amount:.1f} credits.",
                                })
                            elif op_type == "Political Manipulation":
                                # Query a random sample of candidates to find a friend to manipulate
                                # This avoids looping over all relations (which is extremely slow)
                                candidates = self.random.choice(empire_ids, size=min(15, len(empire_ids)), replace=False)
                                for cand in candidates:
                                    if cand != id_b:
                                        r = relations_dict.get((id_b, cand))
                                        if r and r.relation_score > 30.0:
                                            r.relation_score = max(-100.0, r.relation_score - 25.0)
                                            break
                                logs.append({
                                    "tick": tick,
                                    "civilization_id": id_a,
                                    "event_type": "Espionage",
                                    "description": f"{empire_stats[id_a]['empire_name']} sowed political discord between {empire_stats[id_b]['empire_name']} and their trading partners.",
                                })
                            elif op_type == "Infrastructure Disruption":
                                # Deduct stability
                                stab = stability_registry.get(id_b, 80.0)
                                stability_registry[id_b] = max(10.0, stab - 15.0)
                                damage = 15.0
                                logs.append({
                                    "tick": tick,
                                    "civilization_id": id_a,
                                    "event_type": "Espionage",
                                    "description": f"{empire_stats[id_a]['empire_name']} agents sabotaged production grids in {empire_stats[id_b]['empire_name']}, reducing core stability.",
                                })
                            elif op_type == "Intelligence Gathering":
                                intel_gain = 80.0
                            elif op_type == "Spy Recruitment":
                                intel_gain = 15.0
                        else:
                            # Catch chance if fail: 60% chance relations drop
                            if self.random.random() < 0.60:
                                rel_ab.relation_score = max(-100.0, rel_ab.relation_score - 40.0)
                                rel_ab.trust = max(0.0, rel_ab.trust - 30.0)
                                # Mirror
                                rel_ba = relations_dict.get((id_b, id_a))
                                if rel_ba:
                                    rel_ba.relation_score = max(-100.0, rel_ba.relation_score - 40.0)
                                    rel_ba.trust = max(0.0, rel_ba.trust - 30.0)

                                logs.append({
                                    "tick": tick,
                                    "civilization_id": id_b,
                                    "event_type": "Diplomatic Crisis",
                                    "description": f"SECURITY ALERT: {empire_stats[id_b]['empire_name']} caught a covert spy operation from {empire_stats[id_a]['empire_name']}. Bilateral relations collapsed.",
                                })
                        
                        op = EspionageOperation(
                            operation_id=f"ESP-{self.op_counter:05d}",
                            tick=tick,
                            attacker_id=id_a,
                            target_id=id_b,
                            operation_type=op_type,
                            success_rate=success_rate,
                            success=success,
                            damage=damage,
                            intelligence_gain=intel_gain,
                            counterintelligence_score=ci_score,
                        )
                        self.operations.append(op)
                        self.op_counter += 1

        return logs

    def export_operations(self, file_path: str) -> None:
        """Save espionage operations database to CSV."""
        records = [op.to_dict() for op in self.operations]
        df = pd.DataFrame(records)
        if df.empty:
            df = pd.DataFrame(columns=["operation_id", "tick", "attacker_id", "target_id", "operation_type", "success_rate", "success", "damage", "intelligence_gain", "counterintelligence_score"])
        df.to_csv(file_path, index=False)
