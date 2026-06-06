#!/usr/bin/env python
"""
Main pipeline runner for Phase 10: Grand Timeline Simulator of The Galactic Dream Engine.
Ingests base event catalogs, simulates procedural history forward, identifies eras and lifecycles,
computes historical analytics, and renders interactive timelines and Matplotlib plots.
"""

from __future__ import annotations
import os
import sys
import argparse
import io

# Set console encoding to UTF-8 to handle special symbols safely on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation):
    pass

from simulation.history.timeline_engine import TimelineEngine
from simulation.analytics.historical_analytics import HistoricalAnalytics
from simulation.visualization.history_visualizer import HistoryVisualizer
from simulation.utils import logger

def main():
    parser = argparse.ArgumentParser(description="Run Phase 10: Grand Timeline Simulator")
    parser.add_argument(
        "--years",
        type=int,
        default=10000,
        help="Total simulation timeline length in years (e.g. 100, 1000, 10000, 100000, 1000000). Default is 10000."
    )
    parser.add_argument(
        "--acceleration",
        type=int,
        default=100,
        help="Macro-simulation speed tick size in years. Default is 100."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic history generation."
    )
    args = parser.parse_args()

    print("=" * 80)
    print("        THE GALACTIC DREAM ENGINE - PHASE 10 PIPELINE")
    print("                 Grand Timeline Simulator")
    print("=" * 80)

    datasets_dir = "datasets"
    os.makedirs(datasets_dir, exist_ok=True)

    # 1. Initialize and run Timeline Simulator
    print(f"\n[Step 1/3] Simulating Continuous Galactic History (Target: {args.years} Years)...")
    engine = TimelineEngine(datasets_dir=datasets_dir, seed=args.seed)
    events = engine.run_pipeline(target_years=args.years, acceleration=args.acceleration)

    # 2. Run Historical Analytics
    print(f"\n[Step 2/3] Analyzing Historical Records & Compiling Rankings (Count: {len(events)})...")
    analytics = HistoricalAnalytics(datasets_dir=datasets_dir)
    results = analytics.run_analytics(events)
    analytics.print_summary(results)

    # 3. Render Visualizations
    print("\n[Step 3/3] Generating Geopolitical Timelines & Infographic Dashboards...")
    try:
        visualizer = HistoryVisualizer(datasets_dir=datasets_dir)
        visualizer.generate_all_visuals()
        print("  - Renders complete: plots saved to datasets/ and HTML timeline generated.")
    except Exception as e:
        print(f"Error during historical conflict rendering: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

    print("=" * 80)
    print("  PHASE 10 EXECUTION COMPLETE: GALACTIC HISTORY GENERATED")
    print("=" * 80)

if __name__ == "__main__":
    main()
