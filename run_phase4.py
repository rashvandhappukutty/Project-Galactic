#!/usr/bin/env python
"""
Main pipeline runner for Phase 4: Civilization Evolution Engine.

This script:
1. Loads civilizations, species, planets, and systems catalogs from Phase 3.
2. Runs the temporal simulation loop over epochs (100 yr, 1K yr, 10K yr, 100K yr).
3. Simulates demographics (logistic growth), technology, energy, and governance shifts.
4. Logs historical events (breakthroughs, crises, disasters, reforms).
5. Saves catalogs:
   - datasets/civilization_evolution.csv
   - datasets/technology_progress.csv
   - datasets/civilization_events.csv
6. Produces visualizations (growth curves, tech progress, gov bar chart, Kardashev hist, timeline HTML).
7. Prints a comprehensive analytical report.
"""

import os
import sys
import io
import pandas as pd

# Adjust console encoding to UTF-8 to handle special characters on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation):
    pass

from simulation.evolution.civilization_evolution import CivilizationEvolutionSimulator
from simulation.analytics.civilization_analytics import CivilizationAnalytics
from simulation.visualization.civilization_visualizer import CivilizationVisualizer


def main():
    print("=" * 70)
    print("        THE GALACTIC DREAM ENGINE - PHASE 4 EVOLUTION PIPELINE")
    print("             Civilization Evolution & History Simulator")
    print("=" * 70)

    # Directories setup
    output_dir = "datasets"
    os.makedirs(output_dir, exist_ok=True)

    # Input CSV paths
    planets_csv = os.path.join(output_dir, "planets.csv")
    species_csv = os.path.join(output_dir, "species_catalog.csv")
    civs_csv = os.path.join(output_dir, "civilizations.csv")
    systems_csv = os.path.join(output_dir, "star_systems.csv")

    # Output CSV paths
    evolved_csv = os.path.join(output_dir, "civilization_evolution.csv")
    tech_progress_csv = os.path.join(output_dir, "technology_progress.csv")
    events_csv = os.path.join(output_dir, "civilization_events.csv")

    # Validation of inputs
    for path in [planets_csv, species_csv, civs_csv, systems_csv]:
        if not os.path.exists(path):
            print(f"Error: Required Phase 3 dataset '{path}' not found.", file=sys.stderr)
            print("Please run the Phase 3 pipeline first.", file=sys.stderr)
            sys.exit(1)

    print("\n[Step 1/4] Loading Phase 3 Galactic Databases...")
    planets_df = pd.read_csv(planets_csv)
    species_df = pd.read_csv(species_csv)
    civs_df = pd.read_csv(civs_csv)
    systems_df = pd.read_csv(systems_csv)

    print(f"  - Loaded {len(civs_df)} initial civilizations.")
    print(f"  - Loaded {len(planets_df)} planets.")
    print(f"  - Loaded {len(species_df)} species profiles.")

    # 2. Run simulation
    print("\n[Step 2/4] Simulating 100,000 Years of Civilizational Evolution...")
    timeframes = [100, 1000, 10000, 100000]
    
    # Instantiate the simulator
    simulator = CivilizationEvolutionSimulator(seed=42)
    
    evolved_df, progress_df, events_df = simulator.run_simulation(
        civs_df, planets_df, species_df, timeframes
    )

    # 3. Export datasets
    print("\n[Step 3/4] Exporting Evolved Catalogs to datasets/...")
    evolved_df.to_csv(evolved_csv, index=False)
    progress_df.to_csv(tech_progress_csv, index=False)
    events_df.to_csv(events_csv, index=False)

    print(f"  - Saved evolved civilizations: {evolved_csv} ({len(evolved_df)} entries)")
    print(f"  - Saved technology & growth progress log: {tech_progress_csv} ({len(progress_df)} entries)")
    print(f"  - Saved historical events catalog: {events_csv} ({len(events_df)} entries)")

    # 4. Generate Visualizations
    print("\n[Step 4/4] Generating Graphical Visualizations...")
    try:
        visualizer = CivilizationVisualizer(evolved_csv, tech_progress_csv, events_csv)
        visualizer.plot_civilization_growth(output_dir)
        visualizer.plot_technology_progress(output_dir)
        visualizer.plot_government_distribution(output_dir)
        visualizer.plot_kardashev_scale_distribution(output_dir)
        visualizer.plot_civilization_timeline(output_dir)
        
        print("  - Saved population growth curves → datasets/civilization_growth.png")
        print("  - Saved tech progression timeline → datasets/technology_progress.png")
        print("  - Saved government distribution bar chart → datasets/government_distribution.png")
        print("  - Saved Kardashev scale histogram → datasets/kardashev_scale_distribution.png")
        print("  - Saved interactive history timeline viewer → datasets/civilization_timeline.html")
    except Exception as e:
        print(f"Error during visualization rendering: {e}", file=sys.stderr)
        sys.exit(1)

    # Output Console Summary Analytics Report
    analytics = CivilizationAnalytics(evolved_csv, tech_progress_csv, events_csv)
    analytics.print_summary()

    print("=" * 70)
    print("  PHASE 4 EXECUTION COMPLETE: CIVILIZATION EVOLUTION SIMULATOR")
    print("=" * 70)


if __name__ == "__main__":
    main()
