#!/usr/bin/env python
"""
Main pipeline runner for Phase 7: Galactic Economy Engine of The Galactic Dream Engine.
"""

import os
import sys
import argparse
import io

# Set console encoding to UTF-8 to handle special symbols safely on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation):
    pass

from simulation.economy.economy_engine import EconomyEngine
from simulation.analytics.economy_analytics import EconomyAnalytics
from simulation.visualization.economy_visualizer import EconomyVisualizer


def main():
    parser = argparse.ArgumentParser(description="Run Phase 7: Galactic Economy Simulation")
    parser.add_argument(
        "--ticks",
        type=int,
        default=10,
        help="Number of simulation ticks to run (1 tick = 100 years). Supported: 1 (100y), 10 (1000y), 100 (10000y)."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic economic operations."
    )
    args = parser.parse_args()

    print("=" * 80)
    print("        THE GALACTIC DREAM ENGINE - PHASE 7 PIPELINE")
    print("                Galactic Economy Engine")
    print("=" * 80)

    output_dir = "datasets"
    os.makedirs(output_dir, exist_ok=True)

    # Validate required Phase 6 inputs
    required_inputs = [
        "stars.csv",
        "planets.csv",
        "colonies.csv",
        "empires.csv",
        "interstellar_routes.csv",
        "civilization_evolution.csv",
        "ai_decisions.csv"
    ]
    for filename in required_inputs:
        path = os.path.join(output_dir, filename)
        if not os.path.exists(path):
            print(f"Error: Required Phase 6 input dataset '{path}' not found.", file=sys.stderr)
            print("Please execute the earlier simulation phases first.", file=sys.stderr)
            sys.exit(1)

    # 1. Initialize and load datasets
    print(f"\n[Step 1/4] Loading Phase 6 Galactic Datasets (Seed: {args.seed})...")
    engine = EconomyEngine(seed=args.seed)
    engine.load_datasets(datasets_dir=output_dir)
    print(f"  - Loaded {len(engine.empires)} Galactic Empires.")
    print(f"  - Loaded {len(engine.colonies)} Colonial Outposts.")
    print(f"  - Loaded {len(engine.routes)} Interstellar Trade/Migration Routes.")

    # 2. Run simulation ticks (advancing economic timeline)
    timescale_years = args.ticks * 100
    print(f"\n[Step 2/4] Simulating {args.ticks} Ticks of Interstellar Economic Activity ({timescale_years} Years)...")
    engine.run_ticks(num_ticks=args.ticks, output_dir=output_dir)

    # 3. Generate Visualizations
    print("\n[Step 3/4] Rendering Economic Visualizations and Dashboards...")
    try:
        visualizer = EconomyVisualizer(datasets_dir=output_dir)
        visualizer.plot_gdp_distribution(output_dir)
        visualizer.plot_market_dashboard(output_dir)
        visualizer.plot_trade_network_map(output_dir)
        visualizer.plot_economic_blocs(output_dir)
        visualizer.plot_wealth_distribution(output_dir)
        visualizer.generate_economic_timeline(output_dir)

        print("  - Saved GDP log-scale distribution → datasets/galactic_gdp_distribution.png")
        print("  - Saved commodity price trends & stockpiles → datasets/resource_market_dashboard.png")
        print("  - Saved weighted trade routing maps → datasets/trade_network_map.png")
        print("  - Saved trade alliance combined GDPs → datasets/economic_blocs.png")
        print("  - Saved Gini inequality Lorenz curves → datasets/wealth_distribution.png")
        print("  - Saved interactive timeline viewer → datasets/economic_timeline.html")
    except Exception as e:
        print(f"Error during visualization rendering: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # 4. Generate Reports and Imperial Analytics
    print("\n[Step 4/4] Printing Imperial Summary Analytics Report:")
    try:
        analytics = EconomyAnalytics(datasets_dir=output_dir)
        analytics.print_summary()
    except Exception as e:
        print(f"Error during analytics reporting: {e}", file=sys.stderr)
        sys.exit(1)

    print("=" * 80)
    print("  PHASE 7 EXECUTION COMPLETE: GALACTIC ECONOMY ENGINE")
    print("=" * 80)


if __name__ == "__main__":
    main()
