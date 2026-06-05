#!/usr/bin/env python
"""
Main pipeline runner for Phase 5: AI Decision Engine of The Galactic Dream Engine.
"""

import os
import sys
import io

# Set console encoding to UTF-8 to handle special symbols safely on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation):
    pass

from simulation.ai.ai_decision_engine import AIDecisionEngine
from simulation.analytics.ai_decision_analytics import AIDecisionAnalytics
from simulation.visualization.decision_visualizer import DecisionVisualizer


def main():
    print("=" * 80)
    print("        THE GALACTIC DREAM ENGINE - PHASE 5 PIPELINE")
    print("               Autonomous AI Decision Engine")
    print("=" * 80)

    output_dir = "datasets"
    os.makedirs(output_dir, exist_ok=True)

    # Input paths
    stars_csv = os.path.join(output_dir, "stars.csv")
    planets_csv = os.path.join(output_dir, "planets.csv")
    species_csv = os.path.join(output_dir, "species_catalog.csv")
    evolved_civs_csv = os.path.join(output_dir, "civilization_evolution.csv")

    # Outputs paths
    decisions_csv = os.path.join(output_dir, "ai_decisions.csv")
    threat_csv = os.path.join(output_dir, "threat_assessment.csv")
    opp_csv = os.path.join(output_dir, "opportunity_analysis.csv")
    megastructures_csv = os.path.join(output_dir, "megastructures.csv")

    # Validate inputs
    for path in [stars_csv, planets_csv, species_csv, evolved_civs_csv]:
        if not os.path.exists(path):
            print(f"Error: Required Phase 4 input dataset '{path}' not found.", file=sys.stderr)
            print("Please run the previous phases (run_simulation.py, run_phase3.py, run_phase4.py) first.", file=sys.stderr)
            sys.exit(1)

    # 1. Initialize and load datasets
    print("\n[Step 1/4] Initializing Agents from Evolved Databases...")
    engine = AIDecisionEngine(seed=42)
    engine.load_data(
        stars_csv=stars_csv,
        planets_csv=planets_csv,
        evolved_civs_csv=evolved_civs_csv,
        species_csv=species_csv,
    )
    print(f"  - Loaded {len(engine.agents)} civilization agents.")

    # 2. Run simulation ticks (20 ticks, 2000 years cumulative)
    print("\n[Step 2/4] Simulating 20 Ticks of Multi-Agent Decision Cycles...")
    engine.run_ticks(num_ticks=20, output_dir=output_dir)

    # 3. Generate Visualizations
    print("\n[Step 3/4] Rendering Visualizations and Dashboards...")
    try:
        visualizer = DecisionVisualizer(
            decisions_csv=decisions_csv,
            threat_csv=threat_csv,
            opportunity_csv=opp_csv,
            megastructures_csv=megastructures_csv,
        )
        visualizer.plot_decision_distribution(output_dir)
        visualizer.plot_civilization_personalities(output_dir)
        visualizer.plot_threat_vs_opportunity(output_dir)
        visualizer.plot_megastructure_progress(output_dir)
        visualizer.plot_decision_timeline(output_dir)

        print("  - Saved strategic action distribution → datasets/decision_distribution.png")
        print("  - Saved agent personality distribution → datasets/civilization_personalities.png")
        print("  - Saved threat vs opportunity scatter map → datasets/threat_vs_opportunity.png")
        print("  - Saved megastructures progress tracker → datasets/megastructure_progress.png")
        print("  - Saved interactive decision timeline viewer → datasets/decision_timeline.html")
    except Exception as e:
        print(f"Error during visualization generation: {e}", file=sys.stderr)
        sys.exit(1)

    # 4. Generate Reports and Superlatives
    print("\n[Step 4/4] Printing Multi-Agent Summary Analytics Report:")
    try:
        analytics = AIDecisionAnalytics(
            decisions_csv=decisions_csv,
            threat_csv=threat_csv,
            opportunity_csv=opp_csv,
            megastructures_csv=megastructures_csv,
        )
        analytics.print_summary(engine.agents)
    except Exception as e:
        print(f"Error during analytics reporting: {e}", file=sys.stderr)
        sys.exit(1)

    print("=" * 80)
    print("  PHASE 5 EXECUTION COMPLETE: AI DECISION Simulation")
    print("=" * 80)


if __name__ == "__main__":
    main()
