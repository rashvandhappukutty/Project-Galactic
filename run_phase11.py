#!/usr/bin/env python
"""
Main pipeline runner for Phase 11: Galactic Story Generator of The Galactic Dream Engine.
Transforms historical timelines, lifecycles, and wars into chronicles, biographies, news, and documentaries.
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

from simulation.storytelling.story_engine import StoryEngine
from simulation.analytics.narrative_analytics import NarrativeAnalytics
from simulation.visualization.story_dashboard import StoryDashboard
from simulation.utils import logger

def main():
    parser = argparse.ArgumentParser(description="Run Phase 11: Galactic Story Generator")
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic storytelling generation."
    )
    args = parser.parse_args()

    print("=" * 80)
    print("        THE GALACTIC DREAM ENGINE - PHASE 11 PIPELINE")
    print("                 Galactic Story Generator")
    print("=" * 80)

    datasets_dir = "datasets"
    stories_dir = "stories"
    
    os.makedirs(datasets_dir, exist_ok=True)
    os.makedirs(stories_dir, exist_ok=True)

    # 1. Run Story Engine Pipeline (Generates news, books, lore, figures, chronicles, reports)
    print("\n[Step 1/3] Generating chronicles, books, news articles, and scripts...")
    engine = StoryEngine(datasets_dir=datasets_dir, stories_dir=stories_dir, seed=args.seed)
    engine.run_storyteller_pipeline()

    # 2. Run Narrative Analytics
    print("\n[Step 2/3] Analyzing generated histories & indexing legacies...")
    analytics = NarrativeAnalytics(datasets_dir=datasets_dir)
    results = analytics.run_narrative_analytics()
    analytics.print_summary(results)

    # 3. Render Web Dashboards and Reports
    print("\n[Step 3/3] Rendering interactive media dashboards & reports...")
    try:
        dashboard = StoryDashboard(datasets_dir=datasets_dir)
        dashboard.generate_all_dashboards()
        print("  - Renders complete: HTML dashboards and Matplotlib reports saved to datasets/.")
    except Exception as e:
        print(f"Error during storytelling dashboards rendering: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

    print("=" * 80)
    print("  PHASE 11 EXECUTION COMPLETE: GALACTIC STORIES GENERATED")
    print("=" * 80)

if __name__ == "__main__":
    main()
