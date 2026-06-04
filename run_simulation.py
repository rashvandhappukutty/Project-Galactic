#!/usr/bin/env python
"""
Main pipeline runner for The Galactic Dream Engine.
Generates the procedural galaxy and outputs visual reports.
"""

import os
import sys
from simulation.galaxy.galaxy_generator import GalaxyGenerator
from simulation.galaxy.visualization import GalaxyVisualizer

def main():
    print("=" * 60)
    print("        THE GALACTIC DREAM ENGINE - SIMULATION PIPELINE")
    print("=" * 60)

    # 1. Paths setup
    output_dir = "datasets"
    os.makedirs(output_dir, exist_ok=True)
    csv_path = os.path.join(output_dir, "stars.csv")

    # 2. Galaxy Generation
    print("\n[Step 1/3] Generating Procedural Spiral Galaxy...")
    # Initialize with standard seed for reproducible physics
    generator = GalaxyGenerator(seed=42)
    stars = generator.generate_galaxy(num_stars=1000)
    
    # Save results
    generator.save_stars_to_csv(stars, csv_path)

    # 3. Visualization
    print("\n[Step 2/3] Generating Graphical Visualizations...")
    try:
        visualizer = GalaxyVisualizer(csv_path)
        
        # Static Matplotlib Plots
        visualizer.plot_matplotlib(output_dir=output_dir)
        
        # Interactive Plotly Web Plot
        plotly_path = visualizer.plot_plotly_3d(output_dir=output_dir)
        
    except Exception as e:
        # Avoid UnicodeEncodeError on Windows console by encoding safely
        encoding = sys.stderr.encoding or 'utf-8'
        err_msg = str(e).encode(encoding, errors='replace').decode(encoding)
        print(f"Error during visualization generation: {err_msg}", file=sys.stderr)
        sys.exit(1)

    # 4. Pipeline Completion Report
    print("\n[Step 3/3] Analyzing Stellar Distributions...")
    # Read back to display nice summary
    import pandas as pd
    df = pd.read_csv(csv_path)
    
    print("\n" + "-"*40)
    print("           STELLAR POPULATION SUMMARY")
    print("-"*40)
    print(f"Total Stars Generated : {len(df)}")
    print("\nBreakdown by Spectral Type:")
    for star_type, count in df["star_type"].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"  Class {star_type} : {count:3d} ({pct:5.2f}%)")
        
    print("\nBreakdown by Galaxy Component:")
    for region, count in df["region"].value_counts().items():
        pct = (count / len(df)) * 100
        print(f"  {region:18s} : {count:3d} ({pct:5.2f}%)")
    print("-" * 40)
    
    print(f"\n[Success] Execution complete! Outputs saved to the '{output_dir}/' directory:")
    print(f"  - Database: {csv_path}")
    print(f"  - Top-down View Plot: {os.path.join(output_dir, 'galaxy_top_down.png')}")
    print(f"  - Statistics Dashboard: {os.path.join(output_dir, 'galaxy_stats.png')}")
    print(f"  - Interactive 3D Viewer: {plotly_path}")
    print("=" * 60)

if __name__ == "__main__":
    main()
