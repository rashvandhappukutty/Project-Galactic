"""
civilization_evolution.py — CivilizationEvolutionSimulator class for the Galactic Dream Engine.

Phase 4: Civilization Evolution Engine.
Manages the temporal simulation loop, logistic growth, political updates, tech tree advancement, and historical event triggers.
"""

import ast
import math
from typing import Any, Dict, List, Tuple
import pandas as pd
import numpy as np

from simulation.evolution.technology_engine import TechnologyEngine
from simulation.evolution.government_engine import GovernmentEngine
from simulation.evolution.energy_engine import EnergyEngine


class CivilizationEvolutionSimulator:
    """
    Orchestrates the evolution of civilizations over multiple epochs.

    Attributes
    ----------
    tech_engine : TechnologyEngine
    gov_engine : GovernmentEngine
    energy_engine : EnergyEngine
    random : np.random.RandomState
    """

    def __init__(self, seed: int = 42) -> None:
        """
        Initialize the simulator with required sub-engines and a consistent seed.
        """
        self.tech_engine = TechnologyEngine(seed=seed)
        self.gov_engine = GovernmentEngine(seed=seed)
        self.energy_engine = EnergyEngine(seed=seed)
        self.random = np.random.RandomState(seed)

    def calculate_carrying_capacity(
        self, planet_type: str, radius: float, habitability_score: float, tech_level: float
    ) -> float:
        """
        Compute the carrying capacity of a planet Homeworld.

        Parameters
        ----------
        planet_type : str
            The type of planet (e.g. ROCKY, OCEAN).
        radius : float
            Planet radius in Earth radii.
        habitability_score : float
            Planet habitability (0 to 100).
        tech_level : float
            Civilization technology level (1 to 10).

        Returns
        -------
        float
            The carrying capacity of the planet Homeworld.
        """
        ptype_upper = str(planet_type).upper()
        if "SUPER_EARTH" in ptype_upper or "SUPER EARTH" in ptype_upper:
            base_capacity = 12e9
        elif "OCEAN" in ptype_upper:
            base_capacity = 8e9
        elif "ROCKY" in ptype_upper:
            base_capacity = 6e9
        elif "DESERT" in ptype_upper:
            base_capacity = 3e9
        elif "ICE" in ptype_upper:
            base_capacity = 1e9
        elif "TOXIC" in ptype_upper:
            base_capacity = 5e8
        else:
            base_capacity = 1e9

        # Scale base capacity by habitability and technology level
        carrying_capacity = base_capacity * (habitability_score / 100.0) * (1.0 + tech_level * 0.2)
        return float(carrying_capacity)

    def simulate_civilization_step(
        self, civ: Dict[str, Any], planet: Dict[str, Any], species: Dict[str, Any], years: int, elapsed_year: int
    ) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
        """
        Simulate a single civilization's progress over a given number of years.

        Parameters
        ----------
        civ : Dict[str, Any]
            Civilization state variables.
        planet : Dict[str, Any]
            Planet astrophysical stats.
        species : Dict[str, Any]
            Sentient species biological stats.
        years : int
            Duration of the step in years.
        elapsed_year : int
            The current simulation year (timestamp for events).

        Returns
        -------
        Tuple[Dict[str, Any], List[Dict[str, Any]]]
            Updated civilization dictionary and list of historical events logged.
        """
        events_logged = []
        
        # If population is already zero, the civilization is extinct
        if civ["population"] <= 0:
            civ["population"] = 0.0
            civ["stability_score"] = 0.0
            civ["corruption_score"] = 0.0
            civ["innovation_score"] = 0.0
            return civ, events_logged

        # --- 1. Demographic Evolution (Logistic Growth) ---
        cc = self.calculate_carrying_capacity(
            planet.get("planet_type", "ROCKY"),
            float(planet.get("radius", 1.0)),
            float(planet.get("habitability_score", 50.0)),
            civ["tech_level"]
        )
        
        # Calculate growth rate 'r'
        r = 0.02 * (1.0 + float(planet.get("resource_score", 50.0)) / 100.0) * \
            (civ["stability_score"] / 100.0) * \
            (1.0 - civ["corruption_score"] / 200.0)
            
        r_scaled = r * (years / 100.0)
        
        # Apply logistic growth
        pop = civ["population"]
        if cc > 0:
            pop = pop + r_scaled * pop * (1.0 - pop / cc)
        else:
            pop = 0.0
            
        # Extinction check
        if pop < 1e5:
            pop = 0.0
            events_logged.append({
                "civilization_id": civ["civilization_id"],
                "civilization_name": civ["name"],
                "year": elapsed_year,
                "event_type": "Extinction",
                "description": "The population fell below critical thresholds, leading to complete planetary extinction.",
                "stability_impact": -100.0,
                "population_impact": -civ["population"]
            })
            civ["population"] = 0.0
            civ["stability_score"] = 0.0
            civ["corruption_score"] = 0.0
            civ["innovation_score"] = 0.0
            return civ, events_logged
        
        civ["population"] = float(pop)

        # --- 2. Political Evolution ---
        civ["corruption_score"] = self.gov_engine.update_corruption(
            civ["government_type"],
            civ["corruption_score"],
            pop,
            civ["stability_score"]
        )
        
        pop_carrying_ratio = pop / cc if cc > 0 else 1.0
        civ["stability_score"] = self.gov_engine.update_stability(
            civ["government_type"],
            civ["stability_score"],
            pop_carrying_ratio,
            civ["corruption_score"]
        )
        
        civ["innovation_score"] = self.gov_engine.update_innovation(
            civ["government_type"],
            float(species.get("intelligence", 50.0)),
            civ["corruption_score"]
        )
        
        # Roll for government reform or collapse
        reformed, new_gov = self.gov_engine.roll_government_reform(
            civ["government_type"],
            civ["stability_score"],
            float(species.get("cooperation", 50.0)),
            float(species.get("intelligence", 50.0)),
            float(species.get("aggression", 50.0))
        )
        
        if reformed:
            old_gov = civ["government_type"]
            civ["government_type"] = new_gov
            civ["stability_score"] = 50.0
            
            if civ["stability_score"] < 20.0:
                # Collapse!
                pop_loss = civ["population"] * 0.10
                civ["population"] = max(0.0, civ["population"] - pop_loss)
                events_logged.append({
                    "civilization_id": civ["civilization_id"],
                    "civilization_name": civ["name"],
                    "year": elapsed_year,
                    "event_type": "Government Collapse",
                    "description": f"Internal chaos sparked a regime collapse. Transitioned from {old_gov} to {new_gov}. Population fell by 10%.",
                    "stability_impact": 30.0,  # Reset to 50 from < 20
                    "population_impact": -pop_loss
                })
            else:
                # Standard peaceful reform
                events_logged.append({
                    "civilization_id": civ["civilization_id"],
                    "civilization_name": civ["name"],
                    "year": elapsed_year,
                    "event_type": "Government Reform",
                    "description": f"The political structures peacefully reformed. Transitioned from {old_gov} to {new_gov}.",
                    "stability_impact": 0.0,
                    "population_impact": 0.0
                })

        # --- 3. Technology Evolution ---
        research_pts_added = self.tech_engine.calculate_research_output(
            civ["population"],
            float(species.get("intelligence", 50.0)),
            civ["innovation_score"]
        ) * (years / 100.0)
        
        new_tech_level, new_res_points, stage_tier, stage_name = self.tech_engine.update_technology(
            civ["tech_level"],
            civ["research_points"],
            research_pts_added
        )
        
        civ["tech_level"] = new_tech_level
        civ["research_points"] = new_res_points
        civ["tech_tier"] = stage_tier
        civ["tech_stage_name"] = stage_name

        # --- 4. Energy & Kardashev Evolution ---
        new_source = self.energy_engine.update_energy_source(new_tech_level)
        energy_output, kardashev = self.energy_engine.calculate_kardashev(new_source, new_tech_level)
        
        civ["energy_source"] = new_source
        civ["energy_output_watts"] = energy_output
        civ["kardashev_rating"] = kardashev

        # --- 5. Random Events (10% chance) ---
        if self.random.random() < 0.10:
            event_types = [
                "Scientific Breakthrough", "Economic Boom", "Energy Crisis",
                "Technological Leap", "Planetary Disaster", "Civil War",
                "Golden Age", "Dark Age"
            ]
            event = self.random.choice(event_types)
            
            if event == "Scientific Breakthrough":
                civ["innovation_score"] = min(100.0, civ["innovation_score"] + 15.0)
                # Extra research points applied
                extra_pts = 2500.0
                new_t, new_r, st, st_n = self.tech_engine.update_technology(
                    civ["tech_level"], civ["research_points"], extra_pts
                )
                civ["tech_level"] = new_t
                civ["research_points"] = new_r
                civ["tech_tier"] = st
                civ["tech_stage_name"] = st_n
                events_logged.append({
                    "civilization_id": civ["civilization_id"],
                    "civilization_name": civ["name"],
                    "year": elapsed_year,
                    "event_type": event,
                    "description": "Scientists discovered major fundamental particles. Innovation and tech progress spiked.",
                    "stability_impact": 0.0,
                    "population_impact": 0.0
                })
                
            elif event == "Economic Boom":
                civ["stability_score"] = min(100.0, civ["stability_score"] + 10.0)
                civ["corruption_score"] = max(0.0, civ["corruption_score"] - 5.0)
                pop_gain = civ["population"] * 0.05
                civ["population"] += pop_gain
                events_logged.append({
                    "civilization_id": civ["civilization_id"],
                    "civilization_name": civ["name"],
                    "year": elapsed_year,
                    "event_type": event,
                    "description": "Trade networks and industrial automation boosted the planetary economy.",
                    "stability_impact": 10.0,
                    "population_impact": pop_gain
                })
                
            elif event == "Energy Crisis":
                civ["stability_score"] = max(0.0, civ["stability_score"] - 15.0)
                civ["innovation_score"] = max(0.0, civ["innovation_score"] - 10.0)
                pop_loss = civ["population"] * 0.05
                civ["population"] = max(0.0, civ["population"] - pop_loss)
                events_logged.append({
                    "civilization_id": civ["civilization_id"],
                    "civilization_name": civ["name"],
                    "year": elapsed_year,
                    "event_type": event,
                    "description": "Depletion of baseline power grids caused severe blackouts and standard of living drops.",
                    "stability_impact": -15.0,
                    "population_impact": -pop_loss
                })
                
            elif event == "Technological Leap":
                # Increase research points directly by 15%
                extra_pts = civ["research_points"] * 0.15
                new_t, new_r, st, st_n = self.tech_engine.update_technology(
                    civ["tech_level"], civ["research_points"], extra_pts
                )
                civ["tech_level"] = new_t
                civ["research_points"] = new_r
                civ["tech_tier"] = st
                civ["tech_stage_name"] = st_n
                events_logged.append({
                    "civilization_id": civ["civilization_id"],
                    "civilization_name": civ["name"],
                    "year": elapsed_year,
                    "event_type": event,
                    "description": "A paradigm-shifting breakthrough fast-forwarded research catalogs by 15%.",
                    "stability_impact": 0.0,
                    "population_impact": 0.0
                })
                
            elif event == "Planetary Disaster":
                civ["stability_score"] = max(0.0, civ["stability_score"] - 30.0)
                pop_loss = civ["population"] * 0.20
                civ["population"] = max(0.0, civ["population"] - pop_loss)
                events_logged.append({
                    "civilization_id": civ["civilization_id"],
                    "civilization_name": civ["name"],
                    "year": elapsed_year,
                    "event_type": event,
                    "description": "A massive meteor impact or climatic collapse ravaged cities across the hemisphere.",
                    "stability_impact": -30.0,
                    "population_impact": -pop_loss
                })
                
            elif event == "Civil War":
                civ["stability_score"] = max(0.0, civ["stability_score"] - 50.0)
                pop_loss = civ["population"] * 0.25
                civ["population"] = max(0.0, civ["population"] - pop_loss)
                # Force re-roll government
                _, new_gov_war = self.gov_engine.roll_government_reform(
                    civ["government_type"], 0.0,
                    float(species.get("cooperation", 50.0)),
                    float(species.get("intelligence", 50.0)),
                    float(species.get("aggression", 50.0))
                )
                civ["government_type"] = new_gov_war
                civ["stability_score"] = max(10.0, civ["stability_score"])  # Minimal structure remains
                events_logged.append({
                    "civilization_id": civ["civilization_id"],
                    "civilization_name": civ["name"],
                    "year": elapsed_year,
                    "event_type": event,
                    "description": f"Societal division erupted into widespread civil war. Transitioned to {new_gov_war}.",
                    "stability_impact": -50.0,
                    "population_impact": -pop_loss
                })
                
            elif event == "Golden Age":
                civ["stability_score"] = min(100.0, civ["stability_score"] + 20.0)
                civ["innovation_score"] = min(100.0, civ["innovation_score"] + 10.0)
                civ["corruption_score"] = max(0.0, civ["corruption_score"] - 10.0)
                events_logged.append({
                    "civilization_id": civ["civilization_id"],
                    "civilization_name": civ["name"],
                    "year": elapsed_year,
                    "event_type": event,
                    "description": "Artistic growth and trust in institutions generated a glorious Era of Harmony.",
                    "stability_impact": 20.0,
                    "population_impact": 0.0
                })
                
            elif event == "Dark Age":
                civ["stability_score"] = max(0.0, civ["stability_score"] - 20.0)
                civ["innovation_score"] = max(0.0, civ["innovation_score"] - 15.0)
                civ["corruption_score"] = min(100.0, civ["corruption_score"] + 15.0)
                events_logged.append({
                    "civilization_id": civ["civilization_id"],
                    "civilization_name": civ["name"],
                    "year": elapsed_year,
                    "event_type": event,
                    "description": "Scientific suppression and governance stagnation ushered in a dark epoch.",
                    "stability_impact": -20.0,
                    "population_impact": 0.0
                })

        return civ, events_logged

    def run_simulation(
        self,
        civilizations_df: pd.DataFrame,
        planets_df: pd.DataFrame,
        species_df: pd.DataFrame,
        timeframes: List[int]
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Run the evolution simulation loop across all civilizations and output three catalogs.

        Parameters
        ----------
        civilizations_df : pd.DataFrame
            Initial civilizations from Phase 3.
        planets_df : pd.DataFrame
            Planet database.
        species_df : pd.DataFrame
            Species database.
        timeframes : List[int]
            List of cumulative years to log (e.g. [100, 1000, 10000, 100000]).

        Returns
        -------
        Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
            - Evolved final civilizations DataFrame.
            - Technology & demographic progress timeline DataFrame.
            - Historic events logs DataFrame.
        """
        if civilizations_df.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

        # Build lookup tables for planets and species
        planets_dict = planets_df.set_index("planet_id").to_dict(orient="index")
        
        # Parse species list if it is a DataFrame
        species_dict = {}
        if not species_df.empty:
            species_dict = species_df.set_index("species_id").to_dict(orient="index")

        # Prepare initial state list of civilizations
        civ_records = []
        for _, row in civilizations_df.iterrows():
            # Parse species dictionary
            raw_species = row.get("species")
            s_dict = {}
            if isinstance(raw_species, str):
                try:
                    s_dict = ast.literal_eval(raw_species)
                except Exception:
                    s_dict = {}
            elif isinstance(raw_species, dict):
                s_dict = raw_species

            # Extract starting population from species metadata
            initial_population = float(s_dict.get("population", 1e9))
            
            # Map tech level from 0-100 to 1-10
            starting_tech_level = float(row.get("tech_level", 50.0)) / 10.0
            starting_tech_level = max(1.0, min(10.0, starting_tech_level))
            
            # Compute initial cumulative research points
            initial_research = self._tech_level_to_research(starting_tech_level)
            
            civ_id = str(row["civilization_id"])
            civ_records.append({
                "civilization_id": civ_id,
                "name": str(row["name"]),
                "species_id": s_dict.get("species_id", "unknown"),
                "species_name": s_dict.get("name", "unknown"),
                "planet_id": str(row["planet_id"]),
                "population": initial_population,
                "tech_level": starting_tech_level,
                "research_points": initial_research,
                "tech_tier": int(starting_tech_level),
                "tech_stage_name": self.tech_engine.tech_tiers.get(int(starting_tech_level), ("Industrial Age", 0))[0],
                "energy_source": str(row.get("energy_source", "Fossil")),
                "energy_output_watts": 1e11,
                "kardashev_rating": 0.5,
                "government_type": str(row.get("government_type", "Democracy")),
                "stability_score": 80.0,
                "corruption_score": 10.0,
                "innovation_score": 50.0,
                "civilization_age": float(row.get("civilization_age", 1000.0)),
                "species_metadata": s_dict  # Helper ref
            })

        # Progress logs setup (starts at Year 0)
        progress_timeline = []
        for c in civ_records:
            progress_timeline.append({
                "civilization_id": c["civilization_id"],
                "name": c["name"],
                "year": 0,
                "population": c["population"],
                "tech_level": c["tech_level"],
                "energy_source": c["energy_source"],
                "kardashev_rating": c["kardashev_rating"],
                "stability_score": c["stability_score"],
                "corruption_score": c["corruption_score"],
                "innovation_score": c["innovation_score"],
                "government_type": c["government_type"]
            })

        all_events = []
        event_counter = 1

        # Sort timeframes
        sorted_timeframes = sorted(timeframes)
        
        # Simulate each epoch
        current_time = 0
        for target_year in sorted_timeframes:
            years_to_simulate = target_year - current_time
            if years_to_simulate <= 0:
                continue

            for c in civ_records:
                p_dict = planets_dict.get(c["planet_id"], {})
                s_dict = c["species_metadata"]
                
                # Run step simulation
                updated_c, step_events = self.simulate_civilization_step(
                    c, p_dict, s_dict, years_to_simulate, target_year
                )
                
                # Update record in place
                c.update(updated_c)
                
                # Append events
                for e in step_events:
                    e["event_id"] = f"EVT-{event_counter:05d}"
                    all_events.append(e)
                    event_counter += 1
                
                # Append timeline entry
                progress_timeline.append({
                    "civilization_id": c["civilization_id"],
                    "name": c["name"],
                    "year": target_year,
                    "population": c["population"],
                    "tech_level": c["tech_level"],
                    "energy_source": c["energy_source"],
                    "kardashev_rating": c["kardashev_rating"],
                    "stability_score": c["stability_score"],
                    "corruption_score": c["corruption_score"],
                    "innovation_score": c["innovation_score"],
                    "government_type": c["government_type"]
                })

            current_time = target_year

        # Final evolved civilizations DataFrame
        final_civs_df = pd.DataFrame(civ_records)
        # Drop species_metadata column before saving
        if "species_metadata" in final_civs_df.columns:
            final_civs_df = final_civs_df.drop(columns=["species_metadata"])

        # Timeline progress DataFrame
        progress_df = pd.DataFrame(progress_timeline)

        # Events log DataFrame
        events_df = pd.DataFrame(all_events)
        if events_df.empty:
            events_df = pd.DataFrame(columns=[
                "event_id", "civilization_id", "civilization_name", "year",
                "event_type", "description", "stability_impact", "population_impact"
            ])

        return final_civs_df, progress_df, events_df

    def _tech_level_to_research(self, tech_level: float) -> float:
        """
        Calculate cumulative research points from a float tech level.
        """
        tech_level = max(1.0, tech_level)
        T = int(tech_level)
        tiers = self.tech_engine.tech_tiers
        
        if T >= 10:
            req_10 = tiers[10][1]
            return req_10 + (tech_level - 10.0) * req_10
        else:
            req_current = tiers[T][1]
            req_next = tiers[T + 1][1]
            return req_current + (tech_level - T) * (req_next - req_current)
