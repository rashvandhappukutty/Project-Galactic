"""
colonization_engine.py — Core simulation engine for Phase 6.
"""

import os
import math
import hashlib
import pandas as pd
import numpy as np
import networkx as nx
from typing import Dict, List, Any, Tuple, Set

from simulation.ai.strategic_planner import CivilizationAgent
from simulation.colonization.colony_generator import Colony, ColonyGenerator
from simulation.colonization.territory_manager import Territory, TerritoryManager
from simulation.colonization.expansion_planner import ExpansionPlanner


class ColonizationEngine:
    """Manages the tick-based galactic colonization simulation, routes, and empire creation."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.random = np.random.RandomState(seed)
        
        # Engines
        self.colony_gen = ColonyGenerator(seed=seed)
        self.territory_mgr = TerritoryManager(proximity_threshold=150.0)
        self.planner = ExpansionPlanner(max_range_ly=250.0)

        # Registries
        self.agents: Dict[str, CivilizationAgent] = {}
        self.stars: Dict[str, Dict[str, Any]] = {}
        self.planets: List[Dict[str, Any]] = []
        self.planets_dict: Dict[str, Dict[str, Any]] = {}

        # Mappings
        self.planet_star_coords: Dict[str, Tuple[float, float, float]] = {}

        # Outputs logs
        self.colonies_db: Dict[str, Colony] = {}
        self.empires_db: List[Dict[str, Any]] = []
        self.territories_db: Dict[str, Territory] = {}
        self.routes_db: List[Dict[str, Any]] = []
        self.events_db: List[Dict[str, Any]] = []

    def load_data(
        self,
        stars_csv: str,
        planets_csv: str,
        evolved_civs_csv: str,
        species_csv: str,
        ai_decisions_csv: str,
    ) -> None:
        """Load Phase 5 catalogs and map structures.

        Parameters
        ----------
        stars_csv : str
        planets_csv : str
        evolved_civs_csv : str
        species_csv : str
        ai_decisions_csv : str
        """
        # 1. Load stars
        stars_df = pd.read_csv(stars_csv)
        self.stars = stars_df.set_index("id").to_dict(orient="index")

        # 2. Load planets
        planets_df = pd.read_csv(planets_csv)
        self.planets = planets_df.to_dict(orient="records")
        self.planets_dict = planets_df.set_index("planet_id").to_dict(orient="index")

        # Pre-calculate planet star coordinates map for fast lookup in target selection AI
        self.planet_star_coords.clear()
        for p in self.planets:
            star_id = str(p["star_id"])
            star_info = self.stars.get(star_id)
            if star_info:
                coords = (float(star_info["x"]), float(star_info["y"]), float(star_info["z"]))
                self.planet_star_coords[p["planet_id"]] = coords

        # 3. Load species
        species_df = pd.read_csv(species_csv)
        species_lookup = species_df.set_index("species_id").to_dict(orient="index")

        # 4. Load evolved civilizations (contains Phase 5 baseline stats)
        civs_df = pd.read_csv(evolved_civs_csv)

        # 5. Load AI decisions to check intent
        decisions_df = pd.read_csv(ai_decisions_csv)
        # Store set of civilization IDs that decided to COLONIZE or EXPAND in the final tick
        last_tick = decisions_df["tick"].max() if not decisions_df.empty else 1
        final_decisions = decisions_df[decisions_df["tick"] == last_tick]
        expansionist_intent_civs = set(final_decisions[final_decisions["decision"].isin(["COLONIZE", "EXPAND"])]["civilization_id"])

        # Clear registries
        self.agents.clear()
        self.colonies_db.clear()
        self.empires_db.clear()
        self.territories_db.clear()
        self.routes_db.clear()
        self.events_db.clear()

        # Initialize agents
        for _, row in civs_df.iterrows():
            civ_id = str(row["civilization_id"])
            species_id = str(row["species_id"])
            planet_id = str(row["planet_id"])

            planet_info = self.planets_dict.get(planet_id, {})
            star_id = str(planet_info.get("star_id", "unknown"))
            star_info = self.stars.get(star_id, {"x": 0.0, "y": 0.0, "z": 0.0})
            coords = (float(star_info["x"]), float(star_info["y"]), float(star_info["z"]))

            spec = species_lookup.get(species_id, {})
            aggr = float(spec.get("aggression", 50.0))
            coop = float(spec.get("cooperation", 50.0))
            curi = float(spec.get("intelligence", 50.0))
            risk = float(spec.get("adaptability", 50.0))

            agent = CivilizationAgent(
                civilization_id=civ_id,
                name=str(row["name"]),
                technology_level=float(row["tech_level"]),
                population=float(row["population"]),
                resources=float(row.get("resources", 1000.0)),
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
            traits = {
                "Militaristic": agent.aggression,
                "Diplomatic": agent.cooperation,
                "Scientific": agent.curiosity,
                "Isolationist": 100.0 - agent.cooperation,
                "Expansionist": (agent.risk_tolerance + agent.aggression) / 2.0,
                "Explorer": (agent.curiosity + agent.risk_tolerance) / 2.0,
                "Industrialist": (100.0 - agent.risk_tolerance + agent.curiosity) / 2.0,
            }
            agent.personality = max(traits, key=traits.get)

            # Restore colonies and treaties if present
            # We start with empty colonies and rebuild dynamically or load from column if serialized
            if "colonies" in row and isinstance(row["colonies"], str):
                try:
                    import ast
                    agent.colonies = ast.literal_eval(row["colonies"])
                except Exception:
                    agent.colonies = []

            # Add fallback if civ was expansionist in Phase 5 decisions
            if civ_id in expansionist_intent_civs:
                # Give starting resources boost to ensure they can expand
                agent.resources = max(agent.resources, 800.0)

            self.agents[civ_id] = agent

        # Parse Phase 5 decisions to populate allies and trading partners
        name_to_id = {agent.name: cid for cid, agent in self.agents.items()}

        if os.path.exists(ai_decisions_csv):
            dec_df = pd.read_csv(ai_decisions_csv)
            for _, row in dec_df.iterrows():
                cid = str(row["civilization_id"])
                agent = self.agents.get(cid)
                if not agent:
                    continue
                
                result_text = str(row.get("result", ""))
                dec_type = str(row.get("decision", ""))

                if dec_type == "TRADE" and "established between" in result_text:
                    # Find receiver
                    for name, other_id in name_to_id.items():
                        if other_id != cid and name in result_text:
                            if other_id not in agent.trading_partners:
                                agent.trading_partners.append(other_id)
                            other_agent = self.agents.get(other_id)
                            if other_agent and cid not in other_agent.trading_partners:
                                other_agent.trading_partners.append(cid)
                            break

                elif dec_type == "ALLY" and "formed between" in result_text:
                    for name, other_id in name_to_id.items():
                        if other_id != cid and name in result_text:
                            if other_id not in agent.allies:
                                agent.allies.append(other_id)
                            if other_id not in agent.trading_partners:
                                agent.trading_partners.append(other_id)
                            other_agent = self.agents.get(other_id)
                            if other_agent:
                                if cid not in other_agent.allies:
                                    other_agent.allies.append(cid)
                                if cid not in other_agent.trading_partners:
                                    other_agent.trading_partners.append(cid)
                            break

                elif dec_type == "ISOLATE" and "Broke trade treaties with" in result_text:
                    for name, other_id in name_to_id.items():
                        if other_id != cid and name in result_text:
                            if other_id in agent.trading_partners:
                                agent.trading_partners.remove(other_id)
                            other_agent = self.agents.get(other_id)
                            if other_agent and cid in other_agent.trading_partners:
                                other_agent.trading_partners.remove(cid)

    def run_ticks(self, num_ticks: int = 10, output_dir: str = "datasets") -> None:
        """Run Phase 6 galactic colonization loop.

        Parameters
        ----------
        num_ticks : int
            Number ofTicks to simulate expansion (typically 10 ticks).
        output_dir : str
        """
        os.makedirs(output_dir, exist_ok=True)
        event_counter = 1

        print(f"Starting Phase 6 Colonization simulation across {len(self.agents)} civilizations for {num_ticks} ticks...")

        for tick in range(1, num_ticks + 1):
            year_timestamp = tick * 100  # Each tick is 100 years

            # Build list of occupied planets in this tick to prevent overlap
            occupied_planets = set()
            for agent in self.agents.values():
                if agent.is_extinct:
                    continue
                occupied_planets.add(agent.home_planet_id)
                for col_id in agent.colonies:
                    occupied_planets.add(col_id)

            agent_ids = list(self.agents.keys())
            self.random.shuffle(agent_ids)  # Randomize order of operations per tick

            for civ_id in agent_ids:
                agent = self.agents.get(civ_id)
                if not agent or agent.is_extinct:
                    continue

                # --- 1. Growth & Development update for existing colonies ---
                for col_planet_id in list(agent.colonies):
                    colony = self.colonies_db.get(col_planet_id)
                    if not colony:
                        continue
                    
                    colony.age += 100.0
                    planet_info = self.planets_dict.get(col_planet_id, {})
                    p_hab = float(planet_info.get("habitability_score", 50.0))
                    p_res = float(planet_info.get("resource_score", 50.0))

                    # Growth rules: carrying capacity scales with habitability and tech
                    cc = 1e9 * (p_hab / 100.0) * (1.0 + agent.technology_level * 0.2)
                    r = 0.03 * (colony.development_level / 100.0)
                    colony.population = float(round(colony.population + r * colony.population * (1.0 - colony.population / cc)))

                    # Development level increases
                    colony.development_level = min(100.0, colony.development_level + 2.0 + agent.technology_level * 0.5)

                    # Output updates
                    colony.resource_output = (p_res / 100.0) * colony.development_level * 10.0
                    
                    # Yield resources back to parent agent (100 years of output)
                    agent.resources += colony.resource_output * 2.0

                # --- 2. Evaluate Colonization Criteria & Attempt Expansion ---
                meet_tech = agent.technology_level >= 4.0
                meet_pop = agent.population >= 1e7
                meet_res = agent.resources >= 500.0
                expansionist_personality = agent.personality in ["Expansionist", "Explorer", "Industrialist", "Militaristic"]
                
                # Base probability check: 40% chance if expansionist, 15% otherwise
                prob = 0.40 if expansionist_personality else 0.15
                roll_expand = self.random.random() < prob

                if meet_tech and meet_pop and meet_res and roll_expand:
                    # Resolve unoccupied candidate planets
                    candidates = [p for p in self.planets if p["planet_id"] not in occupied_planets]
                    
                    # Score targets using Target Selection AI
                    scored = self.planner.score_targets(
                        agent, candidates, self.stars, self.agents, self.planet_star_coords
                    )

                    if scored:
                        target_planet, score = scored[0]
                        
                        # Only colonize if score is high enough (> 40.0)
                        if score >= 40.0:
                            # Deduct colonization cost
                            agent.resources -= 500.0
                            target_id = str(target_planet["planet_id"])

                            # Create Colony
                            is_frontier = score < 60.0
                            new_col = self.colony_gen.create_colony(
                                civ_id=civ_id,
                                civ_name=agent.name,
                                civ_personality=agent.personality,
                                planet=target_planet,
                                has_megastructure=(agent.megastructure_progress >= 100.0 and agent.home_planet_id == target_id),
                                is_frontier=is_frontier
                            )

                            self.colonies_db[target_id] = new_col
                            agent.colonies.append(target_id)
                            occupied_planets.add(target_id)

                            # Record first colony event
                            e_type = "First Colony" if len(agent.colonies) == 1 else "Expansion Boom"
                            e_desc = f"{agent.name} established colony '{new_col.colony_name}' on planet {target_planet['planet_name']} (score: {score:.1f})."
                            
                            self.events_db.append({
                                "event_id": f"COL-EVT-{event_counter:05d}",
                                "tick": tick,
                                "year": year_timestamp,
                                "civilization_id": civ_id,
                                "civilization_name": agent.name,
                                "event_type": e_type,
                                "description": e_desc,
                            })
                            event_counter += 1

                # --- 3. Process Expansion Events & Crises ---
                # A. Rebellion check: low stability and multiple colonies
                if agent.stability < 35.0 and len(agent.colonies) >= 2 and self.random.random() < 0.15:
                    rebel_planet_id = self.random.choice(agent.colonies)
                    colony = self.colonies_db.get(rebel_planet_id)
                    
                    if colony:
                        agent.colonies.remove(rebel_planet_id)
                        del self.colonies_db[rebel_planet_id]
                        occupied_planets.remove(rebel_planet_id)
                        
                        agent.stability = min(100.0, agent.stability + 10.0)  # Reassert control locally
                        agent.population = max(0.0, agent.population * 0.95)

                        self.events_db.append({
                            "event_id": f"COL-EVT-{event_counter:05d}",
                            "tick": tick,
                            "year": year_timestamp,
                            "civilization_id": civ_id,
                            "civilization_name": agent.name,
                            "event_type": "Colony Rebellion",
                            "description": f"The colony '{colony.colony_name}' rebelled against {agent.name} due to low stability and declared independence.",
                        })
                        event_counter += 1

                # B. Resource Rush check
                if len(agent.colonies) > 0 and self.random.random() < 0.05:
                    rush_planet_id = self.random.choice(agent.colonies)
                    col = self.colonies_db.get(rush_planet_id)
                    planet_info = self.planets_dict.get(rush_planet_id, {})
                    
                    if col and float(planet_info.get("resource_score", 0.0)) > 75.0:
                        col.development_level = min(100.0, col.development_level + 20.0)
                        col.resource_output *= 1.5
                        agent.resources += 400.0

                        self.events_db.append({
                            "event_id": f"COL-EVT-{event_counter:05d}",
                            "tick": tick,
                            "year": year_timestamp,
                            "civilization_id": civ_id,
                            "civilization_name": agent.name,
                            "event_type": "Resource Rush",
                            "description": f"A massive resource rush was declared on colony '{col.colony_name}' due to high mineral deposits.",
                        })
                        event_counter += 1

                # C. Overextension Collapse (Stability < 25 and large colony count)
                if agent.stability < 25.0 and len(agent.colonies) >= 3 and self.random.random() < 0.20:
                    lost_colonies = []
                    # Fragment 1 to 2 colonies
                    num_lost = min(2, len(agent.colonies) - 1)
                    for _ in range(num_lost):
                        lost_id = agent.colonies.pop()
                        lost_col = self.colonies_db.pop(lost_id, None)
                        if lost_col:
                            lost_colonies.append(lost_col.colony_name)
                            if lost_id in occupied_planets:
                                occupied_planets.remove(lost_id)

                    self.events_db.append({
                        "event_id": f"COL-EVT-{event_counter:05d}",
                        "tick": tick,
                        "year": year_timestamp,
                        "civilization_id": civ_id,
                        "civilization_name": agent.name,
                        "event_type": "Empire Fragmentation",
                        "description": f"Internal fragmentation caused {agent.name} to lose control of outlying colonies: {', '.join(lost_colonies)}.",
                    })
                    event_counter += 1

            # End of tick loop processes
            
        # --- 4. Resolve Territory Spheres & Empire Networks ---
        print("\nResolving territorial claims and border consolidation...")
        self.territories_db = self.territory_mgr.update_territories(self.agents, self.stars, self.planets)

        print("Generating route mapping networks...")
        self._generate_interstellar_routes()

        print("Consolidating galactic empires...")
        self._generate_empires()

        # Save logs to file
        self._save_catalogs(output_dir)

    def _generate_interstellar_routes(self) -> None:
        """Map trade, migration, and exploration routes using NetworkX."""
        G = nx.Graph()

        # Add nodes for active systems
        settled_stars = set()
        for agent in self.agents.values():
            if agent.is_extinct:
                continue
            settled_stars.add(agent.home_star_id)
            for col_planet_id in agent.colonies:
                p_info = self.planets_dict.get(col_planet_id)
                if p_info:
                    settled_stars.add(str(p_info["star_id"]))

        for star_id in settled_stars:
            G.add_node(star_id)

        route_id_counter = 1

        # 1. Migration/Military Routes: Connect Capital to Colonies
        for agent in self.agents.values():
            if agent.is_extinct or not agent.colonies:
                continue

            cap_star_id = agent.home_star_id
            cap_star = self.stars.get(cap_star_id)
            if not cap_star:
                continue
            cap_coords = (float(cap_star["x"]), float(cap_star["y"]), float(cap_star["z"]))

            for col_planet_id in agent.colonies:
                colony = self.colonies_db.get(col_planet_id)
                if not colony:
                    continue
                
                col_star_id = colony.home_star_id
                col_star = self.stars.get(col_star_id)
                if not col_star or col_star_id == cap_star_id:
                    continue

                col_coords = (float(col_star["x"]), float(col_star["y"]), float(col_star["z"]))
                dist = self.territory_mgr.calculate_distance(cap_coords, col_coords)

                # Add edge to NetworkX
                G.add_edge(cap_star_id, col_star_id, weight=dist)

                traffic = (agent.population + colony.population) / 1e8
                economic_value = traffic * 20.0

                self.routes_db.append({
                    "route_id": f"RTE-{route_id_counter:05d}",
                    "route_type": "Migration Route",
                    "source_star_id": cap_star_id,
                    "source_star_name": cap_star["name"],
                    "target_star_id": col_star_id,
                    "target_star_name": col_star["name"],
                    "route_length_ly": round(dist, 2),
                    "traffic_index": round(traffic, 2),
                    "economic_value": round(economic_value, 2),
                })
                route_id_counter += 1

        # 2. Trade Routes: Connect trading partners within 200 LY
        # Retrieve trade partnerships resolved in Phase 5
        for agent1 in self.agents.values():
            if agent1.is_extinct:
                continue
            
            star1_info = self.stars.get(agent1.home_star_id)
            if not star1_info:
                continue
            coords1 = (float(star1_info["x"]), float(star1_info["y"]), float(star1_info["z"]))

            for partner_id in agent1.trading_partners:
                agent2 = self.agents.get(partner_id)
                if not agent2 or agent2.is_extinct:
                    continue

                # Ensure unique pairs by ID comparison
                if agent1.civilization_id >= agent2.civilization_id:
                    continue

                star2_info = self.stars.get(agent2.home_star_id)
                if not star2_info:
                    continue
                coords2 = (float(star2_info["x"]), float(star2_info["y"]), float(star2_info["z"]))

                dist = self.territory_mgr.calculate_distance(coords1, coords2)
                
                if dist <= 200.0:
                    G.add_edge(agent1.home_star_id, agent2.home_star_id, weight=dist)

                    traffic = (agent1.population + agent2.population) / 1e8
                    economic_value = traffic * 50.0

                    self.routes_db.append({
                        "route_id": f"RTE-{route_id_counter:05d}",
                        "route_type": "Trade Route",
                        "source_star_id": agent1.home_star_id,
                        "source_star_name": star1_info["name"],
                        "target_star_id": agent2.home_star_id,
                        "target_star_name": star2_info["name"],
                        "route_length_ly": round(dist, 2),
                        "traffic_index": round(traffic, 2),
                        "economic_value": round(economic_value, 2),
                    })
                    route_id_counter += 1

    def _generate_empires(self) -> None:
        """Create Galactic Empires from successful civilizations."""
        empire_id_counter = 1
        
        for agent_id, agent in self.agents.items():
            if agent.is_extinct:
                continue

            # Criteria to form an Empire:
            # - At least 1 colony established and technology level >= 5.0,
            # - OR territory size > 1.0e6 ly^3
            territory = self.territories_db.get(agent_id)
            t_size = territory.territory_size if territory else 0.0

            if len(agent.colonies) >= 1 or t_size >= 1.0e6:
                # Procedural empire naming based on government type
                gov = agent.government.upper()
                if "TECHNOCRACY" in gov:
                    name_template = "The {civ} Technocracy"
                elif "DEMOCRACY" in gov or "FEDERATION" in gov:
                    name_template = "The Consolidated {civ} Systems"
                elif "MONARCHY" in gov or "EMPIRE" in gov:
                    name_template = "The {civ} Star Empire"
                elif "AI" in gov:
                    name_template = "The {civ} AI Hegemony"
                else:
                    name_template = "The Great {civ} Imperium"

                short_civ = agent.name.replace("The ", "").replace("Republic of ", "").replace("Federation", "").strip()
                words = short_civ.split()
                base_name = words[0] if words else short_civ
                emp_name = name_template.format(civ=base_name)

                # Sum population: homeworld + colonies
                total_population = agent.population
                for col_planet_id in agent.colonies:
                    colony = self.colonies_db.get(col_planet_id)
                    if colony:
                        total_population += colony.population

                # Calculate power index
                # Power Index = (population/1e9) + tech_level * 5 + colonies_count * 10 + territory_size / 2e5
                power_index = (total_population / 1e9) + (agent.technology_level * 5.0) + (len(agent.colonies) * 10.0) + (t_size / 2.0e5)

                home_planet_info = self.planets_dict.get(agent.home_planet_id, {"planet_name": "Homeworld"})
                cap_name = str(home_planet_info.get("planet_name"))

                self.empires_db.append({
                    "empire_id": f"EMP-{empire_id_counter:03d}",
                    "empire_name": emp_name,
                    "founding_civilization": agent.name,
                    "founding_civilization_id": agent.civilization_id,
                    "capital_world": cap_name,
                    "territory_size_ly3": round(t_size, 2),
                    "population": float(total_population),
                    "power_index": round(power_index, 2),
                    "colonies_count": len(agent.colonies),
                })
                empire_id_counter += 1

    def _save_catalogs(self, output_dir: str) -> None:
        """Export catalogs to CSV files."""
        # 1. Colonies
        col_records = []
        for colony in self.colonies_db.values():
            col_records.append(colony.to_dict())
        
        col_df = pd.DataFrame(col_records)
        if col_df.empty:
            col_df = pd.DataFrame(columns=["colony_id", "colony_name", "parent_civilization_id", "home_star_id", "target_planet_id", "population", "development_level", "resource_output", "colony_type", "age"])
        col_csv = os.path.join(output_dir, "colonies.csv")
        col_df.to_csv(col_csv, index=False)
        print(f"  - Saved colonies catalog: {col_csv} ({len(col_df)} entries)")

        # 2. Empires
        emp_df = pd.DataFrame(self.empires_db)
        if emp_df.empty:
            emp_df = pd.DataFrame(columns=["empire_id", "empire_name", "founding_civilization", "founding_civilization_id", "capital_world", "territory_size_ly3", "population", "power_index", "colonies_count"])
        emp_csv = os.path.join(output_dir, "empires.csv")
        emp_df.to_csv(emp_csv, index=False)
        print(f"  - Saved empires catalog: {emp_csv} ({len(emp_df)} entries)")

        # 3. Territories
        terr_records = []
        for terr in self.territories_db.values():
            terr_records.append(terr.to_dict())
        
        terr_df = pd.DataFrame(terr_records)
        if terr_df.empty:
            terr_df = pd.DataFrame(columns=["civilization_id", "controlled_systems_count", "controlled_planets_count", "territory_size_ly3", "sphere_of_influence_ly", "frontier_regions_count"])
        terr_csv = os.path.join(output_dir, "territories.csv")
        terr_df.to_csv(terr_csv, index=False)
        print(f"  - Saved territories catalog: {terr_csv} ({len(terr_df)} entries)")

        # 4. Interstellar Routes
        routes_df = pd.DataFrame(self.routes_db)
        if routes_df.empty:
            routes_df = pd.DataFrame(columns=["route_id", "route_type", "source_star_id", "source_star_name", "target_star_id", "target_star_name", "route_length_ly", "traffic_index", "economic_value"])
        routes_csv = os.path.join(output_dir, "interstellar_routes.csv")
        routes_df.to_csv(routes_csv, index=False)
        print(f"  - Saved interstellar routes catalog: {routes_csv} ({len(routes_df)} entries)")

        # 5. Colonization Events
        events_df = pd.DataFrame(self.events_db)
        if events_df.empty:
            events_df = pd.DataFrame(columns=["event_id", "tick", "year", "civilization_id", "civilization_name", "event_type", "description"])
        events_csv = os.path.join(output_dir, "colonization_events.csv")
        events_df.to_csv(events_csv, index=False)
        print(f"  - Saved colonization events catalog: {events_csv} ({len(events_df)} entries)")
