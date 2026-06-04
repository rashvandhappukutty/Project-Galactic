"""
Visualization tools for the Galactic Dream Engine galaxy generator.
Provides both Matplotlib static plots and Plotly interactive 3D visualizations.
"""

import os
from typing import List
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import plotly.graph_objects as go
import plotly.express as px

from simulation.galaxy.constants import STELLAR_CLASSES
from simulation.galaxy.star import Star

class GalaxyVisualizer:
    """
    Handles plotting and visualization of procedurally generated stars.
    """

    def __init__(self, csv_path: str):
        if not os.path.exists(csv_path):
            raise FileNotFoundError(f"Stellar database not found at {csv_path}. Please generate it first.")
        self.df = pd.read_csv(csv_path)

        # Map stellar classes to their hex colors
        self.color_map = {k: v["color"] for k, v in STELLAR_CLASSES.items()}

    def _get_star_sizes(self, base_size: float = 1.0, scale_factor: float = 8.0) -> pd.Series:
        """
        Calculates marker sizes based on log-luminosity to make bright stars stand out
        without drowning out dim stars.
        """
        # Luminosity can span from 0.0001 to 1,000,000. We take the log10 and offset it
        # so it's always positive, then scale.
        min_lum = self.df["luminosity"].min()
        log_lum = np.log10(self.df["luminosity"] / min_lum + 1.0)
        return base_size + (log_lum * scale_factor)

    def plot_matplotlib(self, output_dir: str = ".") -> None:
        """
        Generates static Matplotlib plots of the galaxy structure and star distributions.
        Saves two figures:
        1. `galaxy_top_down.png`: 2D top-down view showing spiral arms and core.
        2. `galaxy_stats.png`: Breakdown of stellar classes and distributions.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # --- Plot 1: 2D Top-Down View ---
        fig, ax = plt.subplots(figsize=(12, 12), facecolor="#030308")
        ax.set_facecolor("#030308")

        # Sort stars by luminosity so brighter stars are drawn on top
        sorted_df = self.df.sort_values(by="luminosity")
        
        # Prepare sizes and colors
        sizes = sorted_df["luminosity"].apply(lambda l: 1.0 + np.log10(l + 1.0) * 4.0)
        colors = sorted_df["star_type"].map(self.color_map)

        # Plot star glow (larger, semi-transparent points behind bright stars)
        glow_mask = sorted_df["luminosity"] > 10.0
        if glow_mask.any():
            ax.scatter(
                sorted_df.loc[glow_mask, "x"],
                sorted_df.loc[glow_mask, "y"],
                s=sizes[glow_mask] * 4.0,
                c=colors[glow_mask],
                alpha=0.15,
                edgecolors="none"
            )

        # Plot core stars
        scatter = ax.scatter(
            sorted_df["x"],
            sorted_df["y"],
            s=sizes,
            c=colors,
            alpha=0.85,
            edgecolors="none"
        )

        # Aesthetic adjustments
        ax.set_title("The Galactic Dream Engine - Procedural Milky Way Generator", color="white", fontsize=16, pad=20)
        ax.set_xlabel("X (light-years)", color="gray", fontsize=12)
        ax.set_ylabel("Y (light-years)", color="gray", fontsize=12)
        ax.tick_params(colors="gray")
        
        # Grid lines (subtle)
        ax.grid(True, color="#151525", linestyle="--", alpha=0.5)

        # Scale limits (leave margin around the 50,000 ly radius)
        limit = 55000
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        
        # Set square aspect ratio
        ax.set_aspect("equal")

        # Legend creation
        legend_elements = [
            plt.Line2D([0], [0], marker="o", color="w", label=f"Class {k} ({v['temp_range'][0]:,.0f}K - {v['temp_range'][1]:,.0f}K)",
                       markerfacecolor=v["color"], markersize=8)
            for k, v in STELLAR_CLASSES.items()
        ]
        ax.legend(handles=legend_elements, loc="upper right", facecolor="#0e0e1a", edgecolor="#22223b", labelcolor="white")

        plt.tight_layout()
        top_down_path = os.path.join(output_dir, "galaxy_top_down.png")
        plt.savefig(top_down_path, dpi=300, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close()
        print(f"Saved Matplotlib top-down view to {top_down_path}")

        # --- Plot 2: Galaxy Statistics & Distributions ---
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6), facecolor="#030308")
        ax1.set_facecolor("#0e0e1a")
        ax2.set_facecolor("#0e0e1a")

        # Left: Stellar class frequency (pie chart or bar)
        class_counts = self.df["star_type"].value_counts().reindex(STELLAR_CLASSES.keys()).fillna(0)
        bars = ax1.bar(class_counts.index, class_counts.values, color=[self.color_map[c] for c in class_counts.index])
        ax1.set_title("Stellar Classification Frequency (MK System)", color="white", fontsize=14, pad=15)
        ax1.set_ylabel("Count", color="gray", fontsize=12)
        ax1.tick_params(colors="gray")
        ax1.grid(True, axis="y", color="#151525", linestyle="--")

        # Label counts on top of bars
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(f"{int(height)}",
                        xy=(bar.get_x() + bar.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha="center", va="bottom", color="gray")

        # Right: Star counts per structural region
        region_counts = self.df["region"].value_counts()
        colors_region = plt.cm.plasma(np.linspace(0.2, 0.8, len(region_counts)))
        ax2.pie(region_counts.values, labels=region_counts.index, colors=colors_region,
                autopct="%1.1f%%", textprops={"color": "white"}, startangle=140,
                wedgeprops={"edgecolor": "#030308", "linewidth": 1})
        ax2.set_title("Galactic Structural Allocations", color="white", fontsize=14, pad=15)

        fig.suptitle("The Galactic Dream Engine - Stellar Population Analysis", color="white", fontsize=18)
        plt.tight_layout()
        stats_path = os.path.join(output_dir, "galaxy_stats.png")
        plt.savefig(stats_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor="none")
        plt.close()
        print(f"Saved Matplotlib stats dashboard to {stats_path}")

    def plot_plotly_3d(self, output_dir: str = ".") -> str:
        """
        Creates an interactive 3D HTML scatter plot of the galaxy using Plotly.
        Saves the file to `galaxy_interactive_3d.html`.
        """
        os.makedirs(output_dir, exist_ok=True)

        # Sort so that brighter stars render on top/distinctly
        sorted_df = self.df.sort_values(by="luminosity")

        # Calculate marker sizes based on log10 of luminosity
        sizes = sorted_df["luminosity"].apply(lambda l: 2.0 + np.log10(l + 1.0) * 3.5)

        # Build Hover Text
        hover_texts = []
        for _, row in sorted_df.iterrows():
            text = (
                f"<b>{row['name']}</b><br>"
                f"Registry: {row['id']}<br>"
                f"Spectral Class: {row['star_type']}<br>"
                f"Region: {row['region']}<br><br>"
                f"Mass: {row['mass']:.2f} M☉<br>"
                f"Temp: {row['temperature']:,.0f} K<br>"
                f"Luminosity: {row['luminosity']:,.4f} L☉<br>"
                f"Coordinates (ly):<br>"
                f"  X: {row['x']:,.1f}<br>"
                f"  Y: {row['y']:,.1f}<br>"
                f"  Z: {row['z']:,.1f}"
            )
            hover_texts.append(text)

        # Define color map sequence to match star classes exactly
        color_seq = [self.color_map[c] for c in sorted_df["star_type"]]

        # Create Plotly Scatter3D trace
        fig = go.Figure(data=[
            go.Scatter3d(
                x=sorted_df["x"],
                y=sorted_df["y"],
                z=sorted_df["z"],
                mode="markers",
                text=hover_texts,
                hoverinfo="text",
                marker=dict(
                    size=sizes,
                    color=color_seq,
                    opacity=0.85,
                    line=dict(width=0),
                )
            )
        ])

        # Configure 3D layout (sleek space dark mode)
        fig.update_layout(
            title=dict(
                text="The Galactic Dream Engine - Interactive 3D Milky Way Simulator",
                font=dict(family="Arial, sans-serif", size=20, color="white"),
                x=0.5,
                y=0.95
            ),
            paper_bgcolor="#030308",
            scene=dict(
                xaxis=dict(
                    title=dict(text="X (light-years)", font=dict(color="gray")),
                    backgroundcolor="#030308",
                    gridcolor="#151525",
                    showbackground=True,
                    zerolinecolor="#151525",
                    tickfont=dict(color="gray")
                ),
                yaxis=dict(
                    title=dict(text="Y (light-years)", font=dict(color="gray")),
                    backgroundcolor="#030308",
                    gridcolor="#151525",
                    showbackground=True,
                    zerolinecolor="#151525",
                    tickfont=dict(color="gray")
                ),
                zaxis=dict(
                    title=dict(text="Z (light-years)", font=dict(color="gray")),
                    backgroundcolor="#030308",
                    gridcolor="#151525",
                    showbackground=True,
                    zerolinecolor="#151525",
                    tickfont=dict(color="gray"),
                    range=[-10000, 10000]  # Focus vertical view on disk height scale
                ),
                camera=dict(
                    eye=dict(x=0.0, y=0.0, z=1.8),  # Default top-down oblique view
                    up=dict(x=0, y=1, z=0)
                ),
                aspectratio=dict(x=1, y=1, z=0.35)  # Squish Z to accurately represent disk flatness
            ),
            margin=dict(l=0, r=0, b=0, t=50)
        )

        plotly_path = os.path.join(output_dir, "galaxy_interactive_3d.html")
        fig.write_html(plotly_path)
        print(f"Saved Plotly interactive 3D view to {plotly_path}")
        return plotly_path

if __name__ == "__main__":
    # Test visualization if csv exists
    csv_file = "stars_test.csv"
    if os.path.exists(csv_file):
        visualizer = GalaxyVisualizer(csv_file)
        visualizer.plot_matplotlib()
        visualizer.plot_plotly_3d()
    else:
        print("Run galaxy_generator.py first to produce stars_test.csv.")
