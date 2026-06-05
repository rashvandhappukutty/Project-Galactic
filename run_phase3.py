#!/usr/bin/env python
"""
Main pipeline runner for Phase 3: Life Emergence & Evolution Engine.

This script:
1. Loads datasets/star_systems.csv and datasets/planets.csv (from Phase 2).
2. Calculates initial life emergence probabilities and life stages.
3. Simulates temporal biological evolution over epochs (1K, 10K, 100K, 1M years).
4. Generates procedural sentient species profiles for advanced worlds (Stage >= 4).
5. Seeds civilizations (Stage >= 4/5) with technology, energy, and governance.
6. Saves catalogs: datasets/life_catalog.csv, datasets/species_catalog.csv, datasets/civilizations.csv.
7. Produces visual distribution charts, factor dashboards, and galactic maps.
8. Prints a comprehensive analytical report.
"""

import os
import sys
import pandas as pd
import io

# Adjust encoding for Windows console
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation):
    pass

from simulation.systems.star_system import StarSystem
from simulation.planets.planet import Planet
from simulation.life.life_engine import LifeEngine
from simulation.life.evolution_engine import EvolutionEngine
from simulation.life.civilization_seed import CivilizationSeedGenerator
from simulation.analytics.life_analytics import LifeAnalytics
from simulation.visualization.life_visualizer import LifeVisualizer


def main():
    print("=" * 70)
    print("        THE GALACTIC DREAM ENGINE - PHASE 3 PIPELINE")
    print("             Life Emergence & Evolution Simulator")
    print("=" * 70)

    output_dir = "datasets"
    os.makedirs(output_dir, exist_ok=True)

    systems_csv = os.path.join(output_dir, "star_systems.csv")
    planets_csv = os.path.join(output_dir, "planets.csv")

    life_csv = os.path.join(output_dir, "life_catalog.csv")
    species_csv = os.path.join(output_dir, "species_catalog.csv")
    civs_csv = os.path.join(output_dir, "civilizations.csv")

    # Verify input catalogs exist
    if not os.path.exists(systems_csv) or not os.path.exists(planets_csv):
        print("Error: Required input catalogs (star_systems.csv and planets.csv) not found.", file=sys.stderr)
        print("Please run Phase 1 & 2 first using 'python run_simulation.py'.", file=sys.stderr)
        sys.exit(1)

    # 1. Load data
    print("\n[Step 1/5] Loading Galactic Star Systems and Planets...")
    systems_df = pd.read_csv(systems_csv)
    planets_df = pd.read_csv(planets_csv)
    planets_df["atmosphere_type"] = planets_df["atmosphere_type"].fillna("None")
    print(f"  - Loaded {len(systems_df)} star systems and {len(planets_df)} planets.")

    # Create instances of models
    systems_dict = {
        str(row["star_id"]): StarSystem.from_dict(row.to_dict())
        for _, row in systems_df.iterrows()
    }
    planets = [
        Planet.from_dict(row.to_dict())
        for _, row in planets_df.iterrows()
    ]

    # 2. Life Emergence Engine Initialization
    print("\n[Step 2/5] Running Life Emergence Engine (Initial States)...")
    life_engine = LifeEngine()
    
    stage_labels = {
        0: "Dead World",
        1: "Microbial Life",
        2: "Simple Multi-cellular",
        3: "Complex Ecosystems",
        4: "Intelligent Species",
        5: "Spacefaring Civilization"
    }
    
    # Store initial stats
    initial_stages = {i: 0 for i in range(6)}
    
    for p in planets:
        system = systems_dict.get(p.star_id)
        if system is None:
            p.life_probability = 0.0
            p.life_stage = 0
            continue
        
        # Calculate emergence probability & initial stage
        prob = life_engine.calculate_life_probability(p, system)
        stage = life_engine.determine_life_stage(prob, system.age_billion_years)
        
        # Dynamically set initial attributes
        p.life_probability = prob
        p.life_stage = stage
        p.evolution_progress = 0.0
        p.extinction_occurred = False
        p.species_complexity = 0.0
        p.technology_potential = 0.0
        
        initial_stages[stage] += 1

    print("  - Initial Life Stage Distribution (t = 0):")
    for stage, count in initial_stages.items():
        print(f"    Stage {stage} ({stage_labels[stage]}): {count}")

    # 3. Evolution Engine (Step-wise epochs)
    print("\n[Step 3/5] Simulating Biological Evolution & Extinctions...")
    evolution_engine = EvolutionEngine(seed=42)
    
    # Define epochs (years to simulate incrementally)
    epochs = [
        ("1,000 Years", 1000),
        ("10,000 Years", 9000),      # cumulative 10,000
        ("100,000 Years", 90000),    # cumulative 100,000
        ("1,000,000 Years", 900000)  # cumulative 1,000,000
    ]

    # Loop over increments and output distributions
    for label, duration in epochs:
        print(f"  - Simulating next {duration:,} years (Epoch: {label})...")
        extinction_count = 0
        stage_counts = {i: 0 for i in range(6)}
        
        for p in planets:
            system = systems_dict.get(p.star_id)
            if p.life_stage == 0:
                stage_counts[0] += 1
                continue
                
            res = evolution_engine.simulate_evolution(p, system, duration)
            stage_counts[res["updated_stage"]] += 1
            if res["extinction_occurred"]:
                extinction_count += 1
                
        print(f"    Epoch complete. Extinctions triggered: {extinction_count}")
        print(f"    Distribution: Dead: {stage_counts[0]}, Microbial: {stage_counts[1]}, Multicellular: {stage_counts[2]}, Complex: {stage_counts[3]}, Intelligent: {stage_counts[4]}, Civilizations: {stage_counts[5]}")

    # 4. Species & Civilization Seeding
    print("\n[Step 4/5] Seeding Intelligent Species & Civilizations...")
    seed_gen = CivilizationSeedGenerator(seed=42)
    
    species_list = []
    civs_list = []

    for p in planets:
        if p.life_stage >= 4:
            system = systems_dict.get(p.star_id)
            # Procedurally generate species
            species = seed_gen.generate_species_for_planet(p, system)
            species_list.append(species.to_dict())
            
            # Seed civilization for Stage 4/5
            civ = seed_gen.seed_civilization(p, species, p.life_stage)
            civs_list.append(civ.to_dict())

    # Save outputs to datasets folder
    life_catalog_records = []
    for p in planets:
        p_dict = p.to_dict()
        p_dict["life_stage"] = p.life_stage
        p_dict["life_probability"] = p.life_probability
        p_dict["evolution_progress"] = getattr(p, "evolution_progress", 0.0)
        p_dict["extinction_occurred"] = getattr(p, "extinction_occurred", False)
        p_dict["species_complexity"] = getattr(p, "species_complexity", 0.0)
        p_dict["technology_potential"] = getattr(p, "technology_potential", 0.0)
        life_catalog_records.append(p_dict)
        
    pd.DataFrame(life_catalog_records).to_csv(life_csv, index=False)
    pd.DataFrame(species_list).to_csv(species_csv, index=False)
    pd.DataFrame(civs_list).to_csv(civs_csv, index=False)
    
    print(f"  - Saved planetary life catalog: {life_csv} ({len(life_catalog_records)} entries)")
    print(f"  - Saved species catalog: {species_csv} ({len(species_list)} entries)")
    print(f"  - Saved civilizations catalog: {civs_csv} ({len(civs_list)} entries)")

    # 5. Graphical Visualizations
    print("\n[Step 5/5] Generating Graphical Visualizations...")
    try:
        visualizer = LifeVisualizer(life_csv, species_csv, civs_csv)
        visualizer.plot_life_distribution(output_dir)
        visualizer.plot_life_probability_dashboard(output_dir)
        visualizer.plot_civilization_map(output_dir)
        visualizer.plot_civilization_statistics(output_dir)
        print("  - Visual charts and Plotly 3D maps successfully rendered in datasets/")
    except Exception as e:
        print(f"Error during visualization rendering: {e}", file=sys.stderr)
        sys.exit(1)

    # Output Console Analytics Summary
    analytics = LifeAnalytics(life_csv, species_csv, civs_csv)
    analytics.print_summary()

    print("=" * 70)
    print("  PHASE 3 EXECUTION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
