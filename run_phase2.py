#!/usr/bin/env python
"""
Main pipeline runner for Phase 2 of The Galactic Dream Engine.

This script:
1. Reads datasets/stars.csv (from Phase 1).
2. Generates Star Systems using SystemGenerator, saving to datasets/star_systems.csv.
3. Generates Planets using PlanetGenerator.
4. Scores Habitability and Resources using HabitabilityEngine.
5. Saves all Planets to datasets/planets.csv.
6. Generates Matplotlib & Plotly visualizations via SystemVisualizer.
7. Prints a console summary report.
"""

import os
import sys
import pandas as pd

# Set console encoding to UTF-8 for nice star and astronomical symbols if supported
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation):
    pass

from simulation.systems.system_generator import SystemGenerator
from simulation.planets.planet_generator import PlanetGenerator
from simulation.planets.habitability import HabitabilityEngine
from simulation.visualization.system_visualizer import SystemVisualizer

def main():
    print("=" * 70)
    print("        THE GALACTIC DREAM ENGINE - PHASE 2 PIPELINE")
    print("        Star System, Planet Generation & Habitability scoring")
    print("=" * 70)

    output_dir = "datasets"
    os.makedirs(output_dir, exist_ok=True)

    stars_csv = os.path.join(output_dir, "stars.csv")
    systems_csv = os.path.join(output_dir, "star_systems.csv")
    planets_csv = os.path.join(output_dir, "planets.csv")

    # Verify input exists
    if not os.path.exists(stars_csv):
        print(f"Error: {stars_csv} not found. Please run Phase 1 first (run_simulation.py).", file=sys.stderr)
        sys.exit(1)

    # 1. Enrich Stars to Star Systems
    print("\n[Step 1/5] Enriching Stellar Catalog into Star Systems...")
    sys_gen = SystemGenerator(csv_path=stars_csv, seed=42)
    systems = sys_gen.generate_all_systems()
    sys_gen.save_to_csv(systems, systems_csv)
    print(f"  - Generated {len(systems)} star systems. Saved to {systems_csv}")

    # 2. Generate Planets
    print("\n[Step 2/5] Generating Planetary Bodies (Titius-Bode spacing)...")
    planet_gen = PlanetGenerator(seed=42)
    planets = planet_gen.generate_all_planets(systems)
    print(f"  - Generated {len(planets)} initial planets.")

    # 3. Calculate Habitability and Resources
    print("\n[Step 3/5] Evaluating Planetary Habitability & Resource Potential...")
    hab_engine = HabitabilityEngine(seed=42)
    systems_dict = {s.star_id: s for s in systems}
    hab_engine.process_all_planets(planets, systems_dict)
    
    # Save enriched planets to CSV
    planet_gen.save_to_csv(planets, planets_csv)
    print(f"  - Saved enriched planets to {planets_csv}")

    # 4. Generate Graphical Visualizations
    print("\n[Step 4/5] Generating Visualizations and Dashboards...")
    try:
        visualizer = SystemVisualizer(systems_csv, planets_csv)
        
        # Plot overall planet population statistics dashboard
        visualizer.plot_planet_statistics(output_dir=output_dir)
        print(f"  - Saved dashboard: {os.path.join(output_dir, 'planet_statistics.png')}")

        # Pick a system to showcase. Let's find one with a highly habitable planet if possible.
        # Otherwise, fall back to the first system in the catalog.
        planets_df = pd.read_csv(planets_csv)
        highly_habitable = planets_df[planets_df["habitability_score"] >= 80.0]
        
        if not highly_habitable.empty:
            # Pick the system with the highest habitability score
            showcase_row = highly_habitable.loc[highly_habitable["habitability_score"].idxmax()]
            showcase_star_id = str(showcase_row["star_id"])
            showcase_star_name = visualizer._lookup_star_name(showcase_star_id)
            print(f"  - Showcase star selected (Highly Habitable planet found!): {showcase_star_name} (ID: {showcase_star_id})")
        else:
            showcase_star_id = str(systems[0].star_id)
            showcase_star_name = systems[0].star_name
            print(f"  - Showcase star selected (Fallback to first star): {showcase_star_name} (ID: {showcase_star_id})")

        # Plot the single showcase star system
        visualizer.plot_star_system(showcase_star_id, output_dir=output_dir)
        plotly_path = visualizer.plot_star_system_interactive(showcase_star_id, output_dir=output_dir)
        print(f"  - Saved static orbit map: {os.path.join(output_dir, 'sample_system.png')}")
        print(f"  - Saved interactive system viewer: {plotly_path}")

    except Exception as e:
        print(f"Error during visualization generation: {e}", file=sys.stderr)
        sys.exit(1)

    # 5. Print Summary Statistics Report
    print("\n[Step 5/5] Stellar and Planetary Summary Report:")
    visualizer.print_statistics()

    print("=" * 70)
    print("  PHASE 2 EXECUTION COMPLETE")
    print("=" * 70)

if __name__ == "__main__":
    main()
