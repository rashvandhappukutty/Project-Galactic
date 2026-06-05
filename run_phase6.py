#!/usr/bin/env python
"""
Main pipeline runner for Phase 6: Galactic Colonization Engine of The Galactic Dream Engine.
"""

import os
import sys
import io

# Set console encoding to UTF-8 to handle special symbols safely on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation):
    pass

from simulation.colonization.colonization_engine import ColonizationEngine
from simulation.analytics.colonization_analytics import ColonizationAnalytics
from simulation.visualization.galactic_empire_visualizer import GalacticEmpireVisualizer


def main():
    print("=" * 80)
    print("        THE GALACTIC DREAM ENGINE - PHASE 6 PIPELINE")
    print("               Galactic Colonization Engine")
    print("=" * 80)

    output_dir = "datasets"
    os.makedirs(output_dir, exist_ok=True)

    # Input paths
    stars_csv = os.path.join(output_dir, "stars.csv")
    planets_csv = os.path.join(output_dir, "planets.csv")
    species_csv = os.path.join(output_dir, "species_catalog.csv")
    evolved_civs_csv = os.path.join(output_dir, "civilization_evolution.csv")
    ai_decisions_csv = os.path.join(output_dir, "ai_decisions.csv")

    # Output paths
    colonies_csv = os.path.join(output_dir, "colonies.csv")
    empires_csv = os.path.join(output_dir, "empires.csv")
    territories_csv = os.path.join(output_dir, "territories.csv")
    routes_csv = os.path.join(output_dir, "interstellar_routes.csv")
    events_csv = os.path.join(output_dir, "colonization_events.csv")

    # Validate inputs
    for path in [stars_csv, planets_csv, species_csv, evolved_civs_csv, ai_decisions_csv]:
        if not os.path.exists(path):
            print(f"Error: Required Phase 5 input dataset '{path}' not found.", file=sys.stderr)
            print("Please run Phase 5 (run_phase5.py) first.", file=sys.stderr)
            sys.exit(1)

    # 1. Initialize and load datasets
    print("\n[Step 1/4] Loading Phase 5 Galactic Datasets...")
    engine = ColonizationEngine(seed=42)
    engine.load_data(
        stars_csv=stars_csv,
        planets_csv=planets_csv,
        evolved_civs_csv=evolved_civs_csv,
        species_csv=species_csv,
        ai_decisions_csv=ai_decisions_csv,
    )
    print(f"  - Loaded {len(engine.agents)} civilization agents.")

    # 2. Run simulation ticks (10 ticks, 1000 years cumulative)
    print("\n[Step 2/4] Simulating 10 Ticks of Interstellar Expansion & Colonization...")
    engine.run_ticks(num_ticks=10, output_dir=output_dir)

    # 3. Generate Visualizations
    print("\n[Step 3/4] Rendering Visualizations and Imperial Borders Map...")
    try:
        visualizer = GalacticEmpireVisualizer(
            colonies_csv=colonies_csv,
            empires_csv=empires_csv,
            territories_csv=territories_csv,
            routes_csv=routes_csv,
            events_csv=events_csv,
            stars_csv=stars_csv,
        )
        visualizer.plot_galactic_empires_map(output_dir)
        visualizer.plot_trade_routes_map(output_dir)
        visualizer.plot_territory_growth(output_dir)
        visualizer.plot_colony_distribution(output_dir)
        visualizer.plot_empire_timeline(output_dir)

        print("  - Saved borders and sphere of influence map → datasets/galactic_empires_map.png")
        print("  - Saved connectivity grid network map → datasets/trade_routes_map.png")
        print("  - Saved imperial growth trendlines → datasets/territory_growth.png")
        print("  - Saved colony types breakdown bar chart → datasets/colony_distribution.png")
        print("  - Saved interactive timeline viewer → datasets/empire_timeline.html")
    except Exception as e:
        print(f"Error during visualization rendering: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Generate Reports and Imperial Analytics
    print("\n[Step 4/4] Printing Imperial Summary Analytics Report:")
    try:
        analytics = ColonizationAnalytics(
            colonies_csv=colonies_csv,
            empires_csv=empires_csv,
            territories_csv=territories_csv,
            routes_csv=routes_csv,
            events_csv=events_csv,
        )
        analytics.print_summary()
    except Exception as e:
        print(f"Error during analytics reporting: {e}", file=sys.stderr)
        sys.exit(1)

    print("=" * 80)
    print("  PHASE 6 EXECUTION COMPLETE: COLONIZATION ENGINE")
    print("=" * 80)


if __name__ == "__main__":
    main()
