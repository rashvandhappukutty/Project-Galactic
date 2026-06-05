#!/usr/bin/env python
"""
Simulation pipeline runner for Phase 1 and Phase 2 of The Galactic Dream Engine.
Generates the galaxy, enrich star systems, generates planets, and outputs visualizations.
"""

import os
import sys
import pandas as pd
import io

# Set console encoding to UTF-8 to handle special symbols safely on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation):
    pass

from simulation.galaxy.galaxy_generator import GalaxyGenerator
from simulation.galaxy.visualization import GalaxyVisualizer
from simulation.systems.system_generator import SystemGenerator
from simulation.planets.planet_generator import PlanetGenerator
from simulation.planets.habitability import HabitabilityEngine
from simulation.visualization.system_visualizer import SystemVisualizer

def main():
    print("=" * 60)
    print("        THE GALACTIC DREAM ENGINE - SIMULATION PIPELINE")
    print("=" * 60)

    # Output directory setup
    output_dir = "datasets"
    os.makedirs(output_dir, exist_ok=True)

    stars_csv = os.path.join(output_dir, "stars.csv")
    systems_csv = os.path.join(output_dir, "star_systems.csv")
    planets_csv = os.path.join(output_dir, "planets.csv")

    # 1. Galaxy Generation (Phase 1)
    print("\n[Step 1/5] Generating Procedural Spiral Galaxy...")
    galaxy_gen = GalaxyGenerator(seed=42)
    stars = galaxy_gen.generate_galaxy(num_stars=1000)
    galaxy_gen.save_stars_to_csv(stars, stars_csv)

    # 2. Star Systems Enrichment (Phase 2)
    print("\n[Step 2/5] Enriching Stellar Catalog into Star Systems...")
    sys_gen = SystemGenerator(csv_path=stars_csv, seed=42)
    systems = sys_gen.generate_all_systems()
    sys_gen.save_to_csv(systems, systems_csv)
    print(f"Successfully enriched and saved {len(systems)} systems to {systems_csv}")

    # 3. Planet Generation & Habitability Scoring (Phase 2)
    print("\n[Step 3/5] Generating Planetary Bodies & Scoring Habitability...")
    planet_gen = PlanetGenerator(seed=42)
    planets = planet_gen.generate_all_planets(systems)
    
    hab_engine = HabitabilityEngine(seed=42)
    systems_dict = {s.star_id: s for s in systems}
    hab_engine.process_all_planets(planets, systems_dict)
    planet_gen.save_to_csv(planets, planets_csv)

    # 4. Visualization Generation
    print("\n[Step 4/5] Generating Graphical Visualizations...")
    try:
        # Galaxy Visualizations (Phase 1)
        galaxy_viz = GalaxyVisualizer(stars_csv)
        galaxy_viz.plot_matplotlib(output_dir=output_dir)
        plotly_3d_path = galaxy_viz.plot_plotly_3d(output_dir=output_dir)

        # Star System & Planet Visualizations (Phase 2)
        system_viz = SystemVisualizer(systems_csv, planets_csv)
        system_viz.plot_planet_statistics(output_dir=output_dir)
        
        # Select showcase star system containing the highest habitability planet
        planets_df = pd.read_csv(planets_csv)
        highly_habitable = planets_df[planets_df["habitability_score"] >= 80.0]
        if not highly_habitable.empty:
            showcase_row = highly_habitable.loc[highly_habitable["habitability_score"].idxmax()]
            showcase_star_id = str(showcase_row["star_id"])
        else:
            showcase_star_id = str(systems[0].star_id)
        
        system_viz.plot_star_system(showcase_star_id, output_dir=output_dir)
        plotly_sys_path = system_viz.plot_star_system_interactive(showcase_star_id, output_dir=output_dir)

    except Exception as e:
        encoding = sys.stderr.encoding or 'utf-8'
        err_msg = str(e).encode(encoding, errors='replace').decode(encoding)
        print(f"Error during visualization generation: {err_msg}", file=sys.stderr)
        sys.exit(1)

    # 5. Analyzing Distributions and Report Output
    print("\n[Step 5/5] Analyzing Stellar & Planetary Distributions...")
    
    # Load data for summary printout
    df_stars = pd.read_csv(stars_csv)
    df_planets = pd.read_csv(planets_csv)
    
    print("\n" + "-" * 40)
    print("           STELLAR POPULATION SUMMARY")
    print("-" * 40)
    print(f"Total Stars Generated : {len(df_stars)}")
    print("\nBreakdown by Spectral Type:")
    for star_type, count in df_stars["star_type"].value_counts().items():
        pct = (count / len(df_stars)) * 100
        print(f"  Class {star_type} : {count:3d} ({pct:5.2f}%)")
        
    print("\nBreakdown by Galaxy Component:")
    for region, count in df_stars["region"].value_counts().items():
        pct = (count / len(df_stars)) * 100
        print(f"  {region:18s} : {count:3d} ({pct:5.2f}%)")
    print("-" * 40)

    print("\n" + "-" * 40)
    print("           PLANET POPULATION SUMMARY")
    print("-" * 40)
    print(f"Total Planets Generated : {len(df_planets)}")
    print("\nBreakdown by Planet Type:")
    for p_type, count in df_planets["planet_type"].value_counts().items():
        pct = (count / len(df_planets)) * 100
        print(f"  {p_type:15s} : {count:4d} ({pct:5.2f}%)")
        
    avg_hab = df_planets["habitability_score"].mean()
    avg_res = df_planets["resource_score"].mean()
    
    print(f"\nAverage Habitability Score : {avg_hab:.2f}")
    if len(df_planets) > 0:
        best_idx = df_planets["habitability_score"].idxmax()
        best_planet = df_planets.loc[best_idx]
        best_star_name = df_stars[df_stars["id"].astype(str) == str(best_planet["star_id"])].iloc[0]["name"]
        print(f"Most Habitable Planet      : {best_planet['planet_name']} (score {best_planet['habitability_score']:.1f}, star: {best_star_name})")
    
    print(f"Average Resource Score     : {avg_res:.2f}")
    print("-" * 40)

    print(f"\n[Success] Execution complete! Outputs saved to the '{output_dir}/' directory:")
    print(f"  - Stars Catalog: {stars_csv}")
    print(f"  - Star Systems Enriched: {systems_csv}")
    print(f"  - Planets Catalog: {planets_csv}")
    print(f"  - Top-down View Plot: {os.path.join(output_dir, 'galaxy_top_down.png')}")
    print(f"  - Galaxy Stats Dashboard: {os.path.join(output_dir, 'galaxy_stats.png')}")
    print(f"  - Interactive 3D Viewer: {plotly_3d_path}")
    print(f"  - Showcase System Orbit Plot: {os.path.join(output_dir, 'sample_system.png')}")
    print(f"  - Showcase System Interactive Viewer: {plotly_sys_path}")
    print(f"  - Planet Stats Dashboard: {os.path.join(output_dir, 'planet_statistics.png')}")
    print("=" * 60)

if __name__ == "__main__":
    main()
