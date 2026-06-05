"""
ai_decision_engine.py — Core simulation loop and orchestrator for Phase 5.
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple

from simulation.ai.strategic_planner import CivilizationAgent, StrategicPlanner
from simulation.ai.threat_assessment import ThreatAssessmentEngine
from simulation.ai.opportunity_analyzer import OpportunityAnalyzer
from simulation.ai.diplomacy_engine import DiplomacyEngine


class AIDecisionEngine:
    """Orchestrates Phase 5 multi-agent AI simulations across all galactic civilizations."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.random = np.random.RandomState(seed)
        
        # Engines
        self.planner = StrategicPlanner()
        self.threat_engine = ThreatAssessmentEngine(proximity_threshold=150.0)
        self.opportunity_engine = OpportunityAnalyzer(proximity_threshold=150.0)
        self.diplomacy = DiplomacyEngine(seed=seed)

        # Registries
        self.agents: Dict[str, CivilizationAgent] = {}
        self.stars: Dict[str, Dict[str, Any]] = {}
        self.planets: List[Dict[str, Any]] = []
        self.planets_dict: Dict[str, Dict[str, Any]] = {}

        # Log databases
        self.decision_logs: List[Dict[str, Any]] = []
        self.threat_logs: List[Dict[str, Any]] = []
        self.opportunity_logs: List[Dict[str, Any]] = []
        self.megastructure_logs: List[Dict[str, Any]] = []

    def load_data(
        self,
        stars_csv: str,
        planets_csv: str,
        evolved_civs_csv: str,
        species_csv: str,
    ) -> None:
        """Load data catalogs and initialize CivilizationAgent registry.

        Parameters
        ----------
        stars_csv : str
        planets_csv : str
        evolved_civs_csv : str
        species_csv : str
        """
        # 1. Load stars for coordinate lookup
        stars_df = pd.read_csv(stars_csv)
        self.stars = stars_df.set_index("id").to_dict(orient="index")

        # 2. Load planets
        planets_df = pd.read_csv(planets_csv)
        self.planets = planets_df.to_dict(orient="records")
        self.planets_dict = planets_df.set_index("planet_id").to_dict(orient="index")

        # 3. Load species traits
        species_df = pd.read_csv(species_csv)
        species_lookup = species_df.set_index("species_id").to_dict(orient="index")

        # 4. Load evolved civilizations
        civs_df = pd.read_csv(evolved_civs_csv)

        # Clear existing agents
        self.agents.clear()

        # Initialize agents
        for _, row in civs_df.iterrows():
            civ_id = str(row["civilization_id"])
            species_id = str(row["species_id"])
            planet_id = str(row["planet_id"])

            # Proximity coordinate resolution
            planet_info = self.planets_dict.get(planet_id, {})
            star_id = str(planet_info.get("star_id", "unknown"))
            star_info = self.stars.get(star_id, {"x": 0.0, "y": 0.0, "z": 0.0})
            coords = (float(star_info["x"]), float(star_info["y"]), float(star_info["z"]))

            # Extract base traits from species
            spec = species_lookup.get(species_id, {})
            base_aggr = float(spec.get("aggression", 50.0))
            base_coop = float(spec.get("cooperation", 50.0))
            base_curi = float(spec.get("intelligence", 50.0))
            base_risk = float(spec.get("adaptability", 50.0))

            # Apply scatter to make traits dynamic
            aggr = max(1.0, min(100.0, base_aggr + self.random.normal(0.0, 5.0)))
            coop = max(1.0, min(100.0, base_coop + self.random.normal(0.0, 5.0)))
            curi = max(1.0, min(100.0, base_curi + self.random.normal(0.0, 5.0)))
            risk = max(1.0, min(100.0, base_risk + self.random.normal(0.0, 5.0)))

            agent = CivilizationAgent(
                civilization_id=civ_id,
                name=str(row["name"]),
                technology_level=float(row["tech_level"]),
                population=float(row["population"]),
                resources=1000.0,  # Starting baseline resources
                government=str(row["government_type"]),
                energy_system=str(row["energy_source"]),
                kardashev_rating=float(row["kardashev_rating"]),
                aggression=aggr,
                curiosity=curi,
                cooperation=coop,
                risk_tolerance=risk,
                home_planet_id=planet_id,
                home_star_id=star_id,
                coordinates=coords,
                stability=float(row.get("stability_score", 80.0)),
            )

            # Assign strategic personality
            self.planner.assign_personality(agent)

            self.agents[civ_id] = agent

    def run_ticks(self, num_ticks: int = 20, output_dir: str = "datasets") -> None:
        """Run Phase 5 multi-agent decision cycle simulation.

        Parameters
        ----------
        num_ticks : int
            Number of strategic ticks to simulate.
        output_dir : str
            Directory to export the resulting datasets.
        """
        os.makedirs(output_dir, exist_ok=True)
        self.decision_logs.clear()
        self.threat_logs.clear()
        self.opportunity_logs.clear()
        self.megastructure_logs.clear()

        print(f"Starting Phase 5 Decision Loop across {len(self.agents)} civilizations for {num_ticks} ticks...")

        for tick in range(1, num_ticks + 1):
            year_timestamp = tick * 100  # Each tick is 100 years
            
            # Prune relations and update alliances
            self.diplomacy.update_relationships(self.agents)

            # Store agents in a list to iterate stably
            agent_ids = list(self.agents.keys())
            
            # Keep track of wars resolved in this tick to avoid duplicate triggers
            tick_wars_fought = set()

            for civ_id in agent_ids:
                agent = self.agents.get(civ_id)
                if not agent or agent.is_extinct:
                    continue

                # 1. Threat Assessment
                planet_info = self.planets_dict.get(agent.home_planet_id, {})
                planet_res = float(planet_info.get("resource_score", 50.0))
                threat_res = self.threat_engine.evaluate_threat(agent, self.agents, planet_res)
                
                # Log Threat
                self.threat_logs.append({
                    "tick": tick,
                    "year": year_timestamp,
                    "civilization_id": civ_id,
                    "civilization_name": agent.name,
                    "personality": agent.personality,
                    "threat_score": threat_res["threat_score"],
                    "rival_factor": threat_res["rival_factor"],
                    "instability_factor": threat_res["instability_factor"],
                    "resource_factor": threat_res["resource_factor"],
                    "tech_factor": threat_res["tech_factor"],
                })

                # 2. Opportunity Analyzer
                opp_res = self.opportunity_engine.evaluate_opportunity(agent, self.agents, self.planets, self.stars)
                
                # Log Opportunity
                self.opportunity_logs.append({
                    "tick": tick,
                    "year": year_timestamp,
                    "civilization_id": civ_id,
                    "civilization_name": agent.name,
                    "personality": agent.personality,
                    "opportunity_score": opp_res["opportunity_score"],
                    "expansion_factor": opp_res["expansion_factor"],
                    "trade_factor": opp_res["trade_factor"],
                    "tech_factor": opp_res["tech_factor"],
                    "energy_factor": opp_res["energy_factor"],
                })

                # 3. Nearby uninhabited habitable planets count
                nearby_habitable_count = self._get_nearby_habitable_count(agent)

                # 4. Action Selection
                action = self.planner.select_action(
                    agent,
                    threat_res["threat_score"],
                    opp_res["opportunity_score"],
                    nearby_habitable_count,
                    self.random,
                )

                # 5. Action Execution
                reason, result = self._execute_action(
                    agent, action, threat_res, opp_res, tick, year_timestamp, tick_wars_fought
                )

                # Log Decision
                self.decision_logs.append({
                    "tick": tick,
                    "year": year_timestamp,
                    "civilization_id": civ_id,
                    "civilization_name": agent.name,
                    "decision": action,
                    "reason": reason,
                    "result": result,
                })

                # Passive tick resource accumulation & population growth
                if not agent.is_extinct:
                    agent.resources += 50.0 + (agent.technology_level * 10.0)
                    agent.population = float(round(agent.population * 1.005))  # Passive 0.5% growth

        # Prune dead megastructure projects and write final registries
        self._save_output_catalogs(output_dir)

    def _get_nearby_habitable_count(self, agent: CivilizationAgent) -> int:
        """Helper to count uninhabited habitable planets within proximity threshold."""
        count = 0
        occupied_planets = set()
        for other in self.agents.values():
            if other.is_extinct:
                continue
            occupied_planets.add(other.home_planet_id)
            for col in other.colonies:
                occupied_planets.add(col)

        for p in self.planets:
            planet_id = str(p["planet_id"])
            if planet_id in occupied_planets:
                continue
            if float(p.get("habitability_score", 0.0)) < 50.0:
                continue

            star_id = str(p["star_id"])
            star_info = self.stars.get(star_id)
            if not star_info:
                continue

            p_coords = (float(star_info["x"]), float(star_info["y"]), float(star_info["z"]))
            dist = self.threat_engine.calculate_distance(agent.coordinates, p_coords)
            if dist <= 150.0:
                count += 1
        return count

    def _execute_action(
        self,
        agent: CivilizationAgent,
        action: str,
        threat: Dict[str, float],
        opp: Dict[str, float],
        tick: int,
        year: int,
        tick_wars: set,
    ) -> Tuple[str, str]:
        """Resolve the consequences of a selected action."""
        if action == "RESEARCH":
            # Boost tech level
            tech_increase = 0.05 + 0.01 * (agent.curiosity / 10.0)
            agent.technology_level = round(agent.technology_level + tech_increase, 3)
            
            # Recalculate Kardashev rating based on energy source
            # Higher tech level raises Kardashev index slightly
            agent.kardashev_rating = round(agent.kardashev_rating + 0.01, 3)
            agent.stability = min(100.0, agent.stability + 2.0)
            
            reason = f"Research priorities chosen due to curiosity ({agent.curiosity:.1f}) and tech potential ({opp['tech_factor']:.1f})."
            result = f"Technological level increased by {tech_increase:.3f} to {agent.technology_level:.3f}."
            return reason, result

        elif action == "EXPAND":
            # Inward expand: build infrastructure, boost resource production
            agent.resources += 300.0
            agent.stability = min(100.0, agent.stability + 5.0)
            reason = f"Domestic infrastructure expansion chosen to leverage opportunity score ({opp['opportunity_score']:.1f})."
            result = "Gained 300.0 resource units and +5.0 stability."
            return reason, result

        elif action == "COLONIZE":
            # Attempt to claim closest habitable world
            occupied_planets = set()
            for other in self.agents.values():
                if other.is_extinct:
                    continue
                occupied_planets.add(other.home_planet_id)
                for col in other.colonies:
                    occupied_planets.add(col)

            closest_p = None
            closest_dist = float("inf")

            for p in self.planets:
                planet_id = str(p["planet_id"])
                if planet_id in occupied_planets:
                    continue
                if float(p.get("habitability_score", 0.0)) < 50.0:
                    continue

                star_id = str(p["star_id"])
                star_info = self.stars.get(star_id)
                if not star_info:
                    continue

                p_coords = (float(star_info["x"]), float(star_info["y"]), float(star_info["z"]))
                dist = self.threat_engine.calculate_distance(agent.coordinates, p_coords)
                
                if dist < closest_dist and dist <= 150.0:
                    closest_dist = dist
                    closest_p = p

            if closest_p and agent.resources >= 400.0:
                agent.resources -= 400.0
                planet_id = str(closest_p["planet_id"])
                agent.colonies.append(planet_id)
                
                # Stability hit due to expansion logistics, population expands
                agent.stability = max(30.0, agent.stability - 5.0)
                new_pop_colony = agent.population * 0.05
                agent.population = float(round(agent.population + new_pop_colony))
                
                reason = f"Colonization wave initiated targeting nearby unoccupied system at distance {closest_dist:.1f} LY."
                result = f"Successfully established colony on planet {closest_p['planet_name']}. Spent 400 resources."
                return reason, result
            else:
                # Fallback to EXPAND
                agent.resources += 150.0
                reason = "Attempted colonization but lacked resources or local targets."
                result = "Fell back to local expansion: gained 150 resources."
                return reason, result

        elif action == "TRADE":
            # Pick closest non-extinct, non-trade partner within 150 LY
            closest_neighbor = None
            closest_dist = float("inf")

            for other_id, other in self.agents.items():
                if other_id == agent.civilization_id or other.is_extinct:
                    continue
                if other_id in agent.trading_partners:
                    continue

                dist = self.threat_engine.calculate_distance(agent.coordinates, other.coordinates)
                if dist < closest_dist and dist <= 150.0:
                    closest_dist = dist
                    closest_neighbor = other

            if closest_neighbor:
                accepted, msg = self.diplomacy.propose_trade(agent, closest_neighbor)
                reason = f"Proposed trade agreement to neighbor {closest_neighbor.name} (distance: {closest_dist:.1f} LY)."
                result = msg
                return reason, result
            else:
                # Fallback to EXPAND
                agent.resources += 150.0
                reason = "No eligible trading partners within proximity."
                result = "Fell back to local expansion: gained 150 resources."
                return reason, result

        elif action == "ALLY":
            # Pick closest trade partner that is not allied yet
            closest_neighbor = None
            closest_dist = float("inf")

            for other_id, other in self.agents.items():
                if other_id == agent.civilization_id or other.is_extinct:
                    continue
                if other_id in agent.allies:
                    continue

                dist = self.threat_engine.calculate_distance(agent.coordinates, other.coordinates)
                if dist < closest_dist and dist <= 150.0:
                    closest_dist = dist
                    closest_neighbor = other

            if closest_neighbor:
                accepted, msg = self.diplomacy.propose_alliance(agent, closest_neighbor)
                reason = f"Diplomatic outreach for alliance sent to {closest_neighbor.name} (distance: {closest_dist:.1f} LY)."
                result = msg
                return reason, result
            else:
                # Fallback to DEFEND
                agent.stability = min(100.0, agent.stability + 10.0)
                reason = "No alliance targets found within proximity."
                result = "Fell back to defense posturing: boosted stability by +10.0."
                return reason, result

        elif action == "DEFEND":
            # Boost stability and resources to fortify borders
            agent.stability = min(100.0, agent.stability + 15.0)
            agent.resources += 100.0
            
            # Make peace with one random enemy if relationship score isn't at bottom
            if agent.wars:
                enemy_id = agent.wars[0]
                enemy = self.agents.get(enemy_id)
                if enemy:
                    # Peace agreement check (if relationship decays above -90 or randomly)
                    if self.random.random() < 0.20:
                        agent.wars.remove(enemy_id)
                        if agent.civilization_id in enemy.wars:
                            enemy.wars.remove(agent.civilization_id)
                        reason = f"Strategic defense posture and peace initiative."
                        result = f"Fortified defenses (+15.0 stability) and signed peace treaty with {enemy.name}."
                        return reason, result

            reason = f"High threat ({threat['threat_score']:.1f}) triggered defensive military consolidation."
            result = "Stability boosted by +15.0 and stockpiled 100 resources."
            return reason, result

        elif action == "ATTACK":
            # Pick a target. Priority: active wars, or closest neighbor with worst relationship score
            target = None
            worst_rel = float("inf")
            closest_dist = float("inf")

            # First priority: existing wars
            for enemy_id in agent.wars:
                enemy = self.agents.get(enemy_id)
                if enemy and not enemy.is_extinct:
                    dist = self.threat_engine.calculate_distance(agent.coordinates, enemy.coordinates)
                    if dist <= 150.0:
                        target = enemy
                        break

            # Second priority: hostile neighbors
            if not target:
                for other_id, other in self.agents.items():
                    if other_id == agent.civilization_id or other.is_extinct:
                        continue
                    if other_id in agent.allies:
                        continue
                    
                    dist = self.threat_engine.calculate_distance(agent.coordinates, other.coordinates)
                    if dist <= 150.0:
                        rel = self.diplomacy.get_relationship(agent, other)
                        if rel < worst_rel:
                            worst_rel = rel
                            target = other

            # If a valid target is identified and not already fought in this tick
            if target and (agent.civilization_id, target.civilization_id) not in tick_wars and (target.civilization_id, agent.civilization_id) not in tick_wars:
                tick_wars.add((agent.civilization_id, target.civilization_id))
                msg = self.diplomacy.resolve_war(agent, target, self.agents)
                reason = f"Military conquest declared due to aggression ({agent.aggression:.1f}) and poor relationships."
                result = msg
                return reason, result
            else:
                # Fallback to DEFEND
                agent.stability = min(100.0, agent.stability + 10.0)
                reason = "Military attack intended, but no targets were viable."
                result = "Fell back to defense consolidation: gained +10.0 stability."
                return reason, result

        elif action == "BUILD_MEGASTRUCTURE":
            # Check tech limit
            if agent.technology_level < 5.0:
                # Force fallback to RESEARCH
                tech_increase = 0.05
                agent.technology_level = round(agent.technology_level + tech_increase, 3)
                reason = "Attempted megastructure building but lacked tech level (< 5.0)."
                result = f"Fell back to research. Tech increased to {agent.technology_level:.3f}."
                return reason, result

            # Resolve megastructure tier
            tiers = [
                ("Stellar Engine", 10.0, 1e30),
                ("Matrioshka Brain", 9.5, 1e28),
                ("Ringworld", 9.0, 1e27),
                ("Dyson Sphere", 8.5, 1e26),
                ("Dyson Swarm", 7.0, 1e16),
                ("Orbital Ring", 5.0, 1e13),
            ]
            
            allowed_type = None
            allowed_energy = 0.0
            for name, min_tech, energy in tiers:
                if agent.technology_level >= min_tech:
                    allowed_type = name
                    allowed_energy = energy
                    break

            if not allowed_type:
                allowed_type = "Orbital Ring"
                allowed_energy = 1e13

            if not agent.megastructure_type:
                # Cost is 800 resources to start
                if agent.resources >= 800.0:
                    agent.resources -= 800.0
                    agent.megastructure_type = allowed_type
                    agent.megastructure_progress = 10.0
                    reason = f"Started construction of {allowed_type} to boost galactic Kardashev footprint."
                    result = f"Initiated {allowed_type} project (progress: 10%). Spent 800 resources."
                    return reason, result
                else:
                    # Lacked resources, fallback to EXPAND
                    agent.resources += 150.0
                    reason = "Lacked resource reserves (need 800) to begin megastructure project."
                    result = "Fell back to local expansion: gained 150 resources."
                    return reason, result
            else:
                # Already constructing one
                if agent.megastructure_progress < 100.0:
                    # Cost is 200 to advance
                    if agent.resources >= 200.0:
                        agent.resources -= 200.0
                        planet_info = self.planets_dict.get(agent.home_planet_id, {})
                        planet_res = float(planet_info.get("resource_score", 50.0))
                        
                        progress_step = 10.0 + (agent.technology_level * 0.5) + (planet_res * 0.1)
                        agent.megastructure_progress = min(100.0, agent.megastructure_progress + progress_step)
                        
                        result = f"Advanced {agent.megastructure_type} construction progress by {progress_step:.1f}% to {agent.megastructure_progress:.1f}%."
                        
                        # Completion check
                        if agent.megastructure_progress >= 100.0:
                            agent.megastructure_energy = allowed_energy
                            # Update Kardashev
                            new_kardashev = (np.log10(allowed_energy) - 6.0) / 10.0
                            agent.kardashev_rating = round(new_kardashev, 3)
                            agent.energy_system = f"Completed {agent.megastructure_type}"
                            result += f" Project COMPLETE! Energy output boosted to {allowed_energy:.1e} Watts. Kardashev scale updated to {agent.kardashev_rating:.3f}."
                        
                        reason = f"Advanced megastructure engineering for {agent.megastructure_type}."
                        return reason, result
                    else:
                        # Fallback to trade/expand
                        agent.resources += 150.0
                        reason = "Lacked resource reserves (need 200) to advance megastructure project."
                        result = "Fell back to local expansion: gained 150 resources."
                        return reason, result
                else:
                    # Already completed. Upgrade project if tech permits
                    if allowed_type != agent.megastructure_type:
                        # Propose upgrade to next tier
                        if agent.resources >= 1000.0:
                            agent.resources -= 1000.0
                            old_type = agent.megastructure_type
                            agent.megastructure_type = allowed_type
                            agent.megastructure_progress = 10.0
                            reason = f"Initiated megastructure upgrade from {old_type} to {allowed_type}."
                            result = f"Started upgrading to {allowed_type} (progress: 10%). Spent 1000 resources."
                            return reason, result
                    
                    # Already maxed for current tech, do expand
                    agent.resources += 200.0
                    reason = f"Megastructure ({agent.megastructure_type}) is complete. Construction crew redirected."
                    result = "Redirected resources to local economy (+200 resources)."
                    return reason, result

        elif action == "EXPLORE":
            # Boost curiosity and resource finding
            agent.curiosity = min(100.0, agent.curiosity + 3.0)
            agent.resources += 250.0
            reason = f"Planetary explorer teams sent out to scout local quadrant."
            result = "Discovered cache of rare isotopes (+250 resources). Gained curiosity."
            return reason, result

        elif action == "ISOLATE":
            # Pull back from treaties, boost stability
            agent.stability = min(100.0, agent.stability + 12.0)
            agent.cooperation = max(1.0, agent.cooperation - 5.0)
            
            # Drop trade partners and allies to isolate borders
            dropped = []
            if agent.trading_partners:
                partner_id = agent.trading_partners.pop(0)
                partner = self.agents.get(partner_id)
                if partner and agent.civilization_id in partner.trading_partners:
                    partner.trading_partners.remove(agent.civilization_id)
                dropped.append(partner.name if partner else partner_id)

            dropped_str = f" Broke trade treaties with {', '.join(dropped)}." if dropped else ""
            reason = f"Governance reform focused on absolute isolationism and border control."
            result = f"Stability boosted (+12.0).{dropped_str}"
            return reason, result

        else:
            return "Strategic focus.", "Maintained status quo."

    def _save_output_catalogs(self, output_dir: str) -> None:
        """Export logged simulation records to CSV files."""
        # 1. AI Decisions Log
        dec_df = pd.DataFrame(self.decision_logs)
        dec_csv = os.path.join(output_dir, "ai_decisions.csv")
        dec_df.to_csv(dec_csv, index=False)
        print(f"  - Saved decision history: {dec_csv} ({len(dec_df)} entries)")

        # 2. Threat Assessments Log
        threat_df = pd.DataFrame(self.threat_logs)
        threat_csv = os.path.join(output_dir, "threat_assessment.csv")
        threat_df.to_csv(threat_csv, index=False)
        print(f"  - Saved threat assessment history: {threat_csv} ({len(threat_df)} entries)")

        # 3. Opportunity Analyses Log
        opp_df = pd.DataFrame(self.opportunity_logs)
        opp_csv = os.path.join(output_dir, "opportunity_analysis.csv")
        opp_df.to_csv(opp_csv, index=False)
        print(f"  - Saved opportunity analysis history: {opp_csv} ({len(opp_df)} entries)")

        # 4. Megastructures Status Registry
        megastructures_records = []
        for agent in self.agents.values():
            if agent.megastructure_type:
                megastructures_records.append({
                    "civilization_id": agent.civilization_id,
                    "civilization_name": agent.name,
                    "megastructure_type": agent.megastructure_type,
                    "construction_progress": agent.megastructure_progress,
                    "energy_output_watts": agent.megastructure_energy,
                    "status": "Complete" if agent.megastructure_progress >= 100.0 else "In Progress",
                })
        
        meg_df = pd.DataFrame(megastructures_records)
        if meg_df.empty:
            meg_df = pd.DataFrame(columns=["civilization_id", "civilization_name", "megastructure_type", "construction_progress", "energy_output_watts", "status"])
        meg_csv = os.path.join(output_dir, "megastructures.csv")
        meg_df.to_csv(meg_csv, index=False)
        print(f"  - Saved megastructures registry: {meg_csv} ({len(meg_df)} entries)")
