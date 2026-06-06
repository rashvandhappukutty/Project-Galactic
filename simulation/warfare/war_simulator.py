"""
war_simulator.py — Orchestrates war triggers, alliance mobilizations, fleet deployments, war weariness, and peace treaties.
"""

from dataclasses import dataclass
from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np


@dataclass
class War:
    """Represents an active or concluded interstellar conflict."""
    war_id: str
    attacker: str
    defender: str
    start_year: float
    end_year: Optional[float]
    cause: str  # "Border Conflict", "Resource Dispute", "Ideological Conflict", "Economic Competition", "Alliance Obligations", "Territorial Claims", "Random Crisis"
    war_scale: float
    status: str  # "Active", "Concluded"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "war_id": self.war_id,
            "attacker": self.attacker,
            "defender": self.defender,
            "start_year": round(self.start_year, 2),
            "end_year": round(self.end_year, 2) if self.end_year else "",
            "cause": self.cause,
            "war_scale": round(self.war_scale, 2),
            "status": self.status,
        }


class WarSimulator:
    """Manages the lifecycle of conflicts, campaign pathing, and peace resolutions."""

    CAUSES = [
        "Border Conflict",
        "Resource Dispute",
        "Ideological Conflict",
        "Economic Competition",
        "Alliance Obligations",
        "Territorial Claims",
        "Random Crisis"
    ]

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.random = np.random.RandomState(seed)
        self.wars: List[War] = []
        self.war_counter = 1
        self.war_weariness: Dict[str, float] = {}  # empire_id -> weariness (0 to 100)

    def trigger_new_wars(
        self,
        year: float,
        empires: List[Dict[str, Any]],
        relations_dict: Dict[Tuple[str, str], Any],
        alliance_mgr: Any,
        treaty_engine: Any,
        capital_stars: Dict[str, str],
        stars: Dict[str, Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Evaluate relations and personalities to trigger wars, call allies, and return log entries."""
        logs = []
        empire_ids = [str(e["founding_civilization_id"]) for e in empires]
        num_empires = len(empire_ids)

        empire_map = {str(e["founding_civilization_id"]): e for e in empires}

        # Build coordinate map of capitals
        coords = {}
        for eid in empire_ids:
            cap_star = capital_stars.get(eid)
            if cap_star and cap_star in stars:
                star = stars[cap_star]
                coords[eid] = (float(star["x"]), float(star["y"]), float(star["z"]))

        # Check for declarations
        for i in range(num_empires):
            id_a = empire_ids[i]
            if id_a not in empire_map:
                continue
            
            # Check if attacker is already in too many wars
            active_wars_a = [w for w in self.wars if w.status == "Active" and id_a in [w.attacker, w.defender]]
            if len(active_wars_a) >= 2:
                continue

            personality_a = str(empire_map[id_a].get("personality", ""))
            
            # militaristic empires declare war more easily
            base_declare_chance = 0.01
            if personality_a == "Militaristic":
                base_declare_chance = 0.08
            elif personality_a == "Diplomatic":
                base_declare_chance = 0.002

            for j in range(num_empires):
                if i == j:
                    continue
                id_b = empire_ids[j]
                if id_b not in empire_map:
                    continue

                # Check if there is already an active war between them
                already_war = False
                for w in self.wars:
                    if w.status == "Active" and ((w.attacker == id_a and w.defender == id_b) or \
                                                  (w.attacker == id_b and w.defender == id_a)):
                        already_war = True
                        break
                if already_war:
                    continue

                # Check for NAP or Alliance
                if alliance_mgr.are_allied(id_a, id_b) or treaty_engine.has_nap(id_a, id_b):
                    continue

                # Check relation
                rel_ab = relations_dict.get((id_a, id_b))
                if rel_ab and rel_ab.relation_score < -25.0:
                    if self.random.random() < base_declare_chance:
                        # Determine cause
                        gov_a = str(empire_map[id_a].get("government", empire_map[id_a].get("government_type", "")))
                        gov_b = str(empire_map[id_b].get("government", empire_map[id_b].get("government_type", "")))
                        
                        # Distance check
                        c_a = coords.get(id_a, (0.0, 0.0, 0.0))
                        c_b = coords.get(id_b, (0.0, 0.0, 0.0))
                        dist = np.sqrt((c_a[0]-c_b[0])**2 + (c_a[1]-c_b[1])**2 + (c_a[2]-c_b[2])**2)

                        if dist < 400.0:
                            cause = "Border Conflict" if self.random.random() < 0.5 else "Territorial Claims"
                        elif gov_a != gov_b and self.random.random() < 0.6:
                            cause = "Ideological Conflict"
                        elif self.random.random() < 0.5:
                            cause = "Economic Competition"
                        else:
                            cause = "Resource Dispute"

                        # Start War
                        war_id = f"WAR-{self.war_counter:04d}"
                        self.war_counter += 1

                        new_war = War(
                            war_id=war_id,
                            attacker=id_a,
                            defender=id_b,
                            start_year=year,
                            end_year=None,
                            cause=cause,
                            war_scale=float(self.random.uniform(20.0, 100.0)),
                            status="Active"
                        )
                        self.wars.append(new_war)
                        self.war_weariness[id_a] = 0.0
                        self.war_weariness[id_b] = 0.0

                        desc = f"DECLARATION OF WAR: {empire_map[id_a]['empire_name']} declared war on {empire_map[id_b]['empire_name']} citing a {cause}."
                        logs.append({
                            "tick": int(year // 100),
                            "civilization_id": id_a,
                            "event_type": "War Declaration",
                            "description": desc,
                        })

                        # Mobilize Allies (Defense Pact members join defender, Military Allies join attacker)
                        allies_def = alliance_mgr.get_allies(id_b)
                        for ally in allies_def:
                            if alliance_mgr.are_defense_pact_aligned(ally, id_b):
                                logs.append({
                                    "tick": int(year // 100),
                                    "civilization_id": ally,
                                    "event_type": "Alliance Mobilization",
                                    "description": f"{empire_map[ally]['empire_name']} joined the war to defend their ally {empire_map[id_b]['empire_name']}.",
                                })
                        
                        allies_att = alliance_mgr.get_allies(id_a)
                        for ally in allies_att:
                            if alliance_mgr.are_allied(ally, id_a) and self.random.random() < 0.5:
                                logs.append({
                                    "tick": int(year // 100),
                                    "civilization_id": ally,
                                    "event_type": "Alliance Mobilization",
                                    "description": f"{empire_map[ally]['empire_name']} joined the offensive with {empire_map[id_a]['empire_name']}.",
                                })

                        break  # Limit 1 war declaration per attacker per tick to avoid cascade

        return logs

    def run_campaign_movements(
        self,
        year: float,
        fleets: Dict[str, Any],  # Dict[fleet_id, Fleet]
        colonies: List[Any],     # List[Colony]
        planets_dict: Dict[str, Dict[str, Any]],
        stars: Dict[str, Dict[str, Any]],
        capital_stars: Dict[str, str],
        battle_engine: Any,
        invasion_engine: Any,
        empire_stats: Dict[str, Dict[str, Any]],
        treaty_engine: Any,
        treasury_registry: Dict[str, float]
    ) -> List[Dict[str, Any]]:
        """Deploy fleets, resolve combat when forces meet in campaign systems, and manage peace broker deals."""
        logs = []
        active_wars = [w for w in self.wars if w.status == "Active"]

        for war in active_wars:
            att_id = war.attacker
            def_id = war.defender

            if att_id not in empire_stats or def_id not in empire_stats:
                # One of them has collapsed
                self._resolve_peace(war, att_id, def_id, year, "White Peace", 0.0, treaty_engine, empire_stats, treasury_registry)
                continue

            # Update war weariness slowly per tick
            self.war_weariness[att_id] = self.war_weariness.get(att_id, 0.0) + self.random.uniform(2.0, 5.0)
            self.war_weariness[def_id] = self.war_weariness.get(def_id, 0.0) + self.random.uniform(2.0, 5.0)

            # Move attacker fleets to defender territory
            # Defender's territory systems are determined by defender colonies home_star_ids
            def_colony_stars = [c.home_star_id for c in colonies if c.parent_civilization_id == def_id]
            if not def_colony_stars:
                def_colony_stars = [capital_stars[def_id]] if def_id in capital_stars else []

            # Gather active attacker fleets
            att_fleets = [f for f in fleets.values() if f.owner_empire_id == att_id and f.status != "Destroyed"]
            def_fleets = [f for f in fleets.values() if f.owner_empire_id == def_id and f.status != "Destroyed"]

            # If defender has absolutely no fleets left, or weariness is max, declare peace
            if not def_fleets or self.war_weariness[def_id] >= 90.0:
                # Domination! Peace signed
                reparations = min(treasury_registry.get(def_id, 0.0), 3000.0)
                treasury_registry[def_id] -= reparations
                treasury_registry[att_id] += reparations
                self._resolve_peace(war, att_id, def_id, year, "Annexation", reparations, treaty_engine, empire_stats, treasury_registry)
                logs.append({
                    "tick": int(year // 100),
                    "civilization_id": att_id,
                    "event_type": "Peace Treaty",
                    "description": f"WAR CONCLUDED: {empire_stats[att_id]['empire_name']} forced {empire_stats[def_id]['empire_name']} to sign peace terms (Annexation), taking {reparations:.1f} credits in reparations.",
                })
                continue

            if self.war_weariness[att_id] >= 90.0:
                # Exhausted, White Peace
                self._resolve_peace(war, att_id, def_id, year, "White Peace", 0.0, treaty_engine, empire_stats, treasury_registry)
                logs.append({
                    "tick": int(year // 100),
                    "civilization_id": att_id,
                    "event_type": "Peace Treaty",
                    "description": f"WAR CONCLUDED: Exhausted combatants {empire_stats[att_id]['empire_name']} and {empire_stats[def_id]['empire_name']} signed a status quo White Peace.",
                })
                continue

            # Simulate Campaign movement
            if def_colony_stars:
                target_star = self.random.choice(def_colony_stars)

                # Move active attacker fleets to target star
                for f in att_fleets:
                    if f.status == "Idle":
                        f.current_star_id = target_star
                        f.status = "In Campaign"

                # Move active defender fleets to defend target star
                for f in def_fleets:
                    if f.status == "Idle":
                        f.current_star_id = target_star

                # Check if they meet at target_star to resolve battles
                local_att = [f for f in att_fleets if f.current_star_id == target_star and f.status != "Destroyed"]
                local_def = [f for f in def_fleets if f.current_star_id == target_star and f.status != "Destroyed"]

                if local_att and local_def:
                    # Battle triggers!
                    b_type = "Orbital Battle" if len(local_def) < len(local_att) else "System Defense"
                    battle = battle_engine.resolve_battle(
                        war_id=war.war_id,
                        attacker_id=att_id,
                        defender_id=def_id,
                        attacker_fleets=local_att,
                        defender_fleets=local_def,
                        star_id=target_star,
                        battle_type=b_type,
                        year=year
                    )

                    # Add weariness due to battle casualties
                    self.war_weariness[att_id] = min(100.0, self.war_weariness[att_id] + battle.fleet_losses_attacker * 0.05)
                    self.war_weariness[def_id] = min(100.0, self.war_weariness[def_id] + battle.fleet_losses_defender * 0.05)

                    logs.append({
                        "tick": int(year // 100),
                        "civilization_id": battle.winner_id,
                        "event_type": "Military Conflict",
                        "description": f"MILITARY BATTLE: Attacking fleets fought defending fleets in system {stars[target_star]['name']}. Winner: {empire_stats[battle.winner_id]['empire_name']}. Casualties: {int(battle.casualties):,}.",
                    })

                    # If attacker won, attempt ground invasion
                    if battle.winner_id == att_id:
                        # Find colonies in this system
                        system_colonies = [c for c in colonies if c.home_star_id == target_star and c.parent_civilization_id == def_id]
                        for col in system_colonies:
                            planet = planets_dict.get(col.target_planet_id, {})
                            inv_fleet_pow = sum(f.fleet_power for f in local_att if f.status != "Destroyed")
                            
                            success = invasion_engine.resolve_invasion(
                                war_id=war.war_id,
                                attacker_id=att_id,
                                defender_id=def_id,
                                colony=col,
                                planet=planet,
                                invading_fleet_power=inv_fleet_pow,
                                year=year,
                                attacker_personality=str(empire_stats[att_id].get("personality", ""))
                            )

                            if success:
                                logs.append({
                                    "tick": int(year // 100),
                                    "civilization_id": att_id,
                                    "event_type": "Conquest",
                                    "description": f"SYSTEM INVASION: {empire_stats[att_id]['empire_name']} successfully captured colony '{col.colony_name}' on planet {planet.get('planet_name', col.target_planet_id)}.",
                                })
                                # Check if defender is completely wiped out (has zero colonies left)
                                defender_active_cols = [c for c in colonies if c.parent_civilization_id == def_id]
                                if not defender_active_cols:
                                    # Complete Collapse
                                    invasion_engine.record_empire_collapse(war.war_id, att_id, def_id, year)
                                    self._resolve_peace(war, att_id, def_id, year, "Annexation", 0.0, treaty_engine, empire_stats, treasury_registry)
                                    # Mark defender as extinct or collapsed
                                    empire_stats.pop(def_id, None)
                                    logs.append({
                                        "tick": int(year // 100),
                                        "civilization_id": att_id,
                                        "event_type": "Empire Collapse",
                                        "description": f"TOTAL GEOPOLITICAL COLLAPSE: {empire_stats[att_id]['empire_name'] if att_id in empire_stats else 'Attacker'} completely annexed all remaining territories of {empire_stats[def_id]['empire_name'] if def_id in empire_stats else 'Defender'}. The empire collapsed.",
                                    })
                                    break
                            else:
                                logs.append({
                                    "tick": int(year // 100),
                                    "civilization_id": def_id,
                                    "event_type": "Military Conflict",
                                    "description": f"INVASION REPULSED: Defensive forces on '{col.colony_name}' repelled {empire_stats[att_id]['empire_name']}'s landing attempts.",
                                })

        return logs

    def _resolve_peace(
        self,
        war: War,
        attacker_id: str,
        defender_id: str,
        year: float,
        terms: str,
        reparations: float,
        treaty_engine: Any,
        empire_stats: Dict[str, Dict[str, Any]],
        treasury_registry: Dict[str, float]
    ) -> None:
        """Helper to sign treaty and transition war to Concluded."""
        war.status = "Concluded"
        war.end_year = year
        
        # Deduct / award reparations
        if reparations > 0.0:
            if defender_id in treasury_registry:
                treasury_registry[defender_id] = max(0.0, treasury_registry[defender_id] - reparations)
            if attacker_id in treasury_registry:
                treasury_registry[attacker_id] += reparations

        treaty_engine.sign_peace_treaty(
            war_id=war.war_id,
            attacker_id=attacker_id,
            defender_id=defender_id,
            terms=terms,
            reparations=reparations,
            year=year
        )

    def export_wars(self, file_path: str) -> None:
        """Save wars database to CSV."""
        records = [w.to_dict() for w in self.wars]
        df = pd.DataFrame(records)
        if df.empty:
            df = pd.DataFrame(columns=["war_id", "attacker", "defender", "start_year", "end_year", "cause", "war_scale", "status"])
        df.to_csv(file_path, index=False)
