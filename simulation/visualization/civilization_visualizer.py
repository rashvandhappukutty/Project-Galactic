"""
civilization_visualizer.py — CivilizationVisualizer class for the Galactic Dream Engine.

Phase 4: Civilization Evolution Engine.
Generates space-themed line plots, histograms, bar charts, and interactive timelines of historical progress.
"""

from __future__ import annotations

import os
from typing import Dict, List
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go


class CivilizationVisualizer:
    """
    Visualization engine to render demographic trends, technological curves, and event logs.

    Parameters
    ----------
    civs_csv : str
        Path to civilization_evolution.csv.
    tech_csv : str
        Path to technology_progress.csv.
    events_csv : str
        Path to civilization_events.csv.
    """

    def __init__(self, civs_csv: str, tech_csv: str, events_csv: str) -> None:
        self.civs_csv = civs_csv
        self.tech_csv = tech_csv
        self.events_csv = events_csv

        # Color configurations for dark space theme
        self.bg_color = "#030308"
        self.grid_color = "#1e1e2f"
        self.spine_color = "#444455"
        self.text_color = "#cccccc"
        self.header_color = "#ffffff"
        
        # Consistent palette for government types
        self.gov_colors = {
            "Democracy": "#4169E1",         # Royal Blue
            "Technocracy": "#00FFFF",       # Cyan
            "Federation": "#32CD32",        # Lime Green
            "Monarchy": "#FFD700",          # Gold
            "Collective": "#FF8C00",        # Dark Orange
            "AI Governance": "#9400D3",      # Dark Violet
            "Scientific Council": "#FF1493", # Deep Pink
        }

    def plot_civilization_growth(self, output_dir: str = "datasets") -> None:
        """
        Generate a line chart of population growth over time for top 5 largest civilizations.
        """
        if not os.path.exists(self.tech_csv) or not os.path.exists(self.civs_csv):
            return

        civs_df = pd.read_csv(self.civs_csv)
        tech_df = pd.read_csv(self.tech_csv)
        if civs_df.empty or tech_df.empty:
            return

        # Find top 5 largest civilizations by final population
        top_5_ids = civs_df.sort_values(by="population", ascending=False).head(5)["civilization_id"].tolist()

        fig, ax = plt.subplots(figsize=(10, 6), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)

        for cid in top_5_ids:
            civ_timeline = tech_df[tech_df["civilization_id"] == cid].sort_values(by="year")
            if civ_timeline.empty:
                continue
            name = civ_timeline.iloc[0].get("name", cid)
            if pd.isna(name) or name is None or str(name).strip() == "":
                name = cid
            ax.plot(
                civ_timeline["year"],
                civ_timeline["population"] / 1e9,
                marker="o",
                markersize=4,
                linewidth=2,
                label=name
            )

        # Style chart
        ax.set_title("Demographic Growth of Top 5 Largest Civilizations", fontsize=14, color=self.header_color, pad=15)
        ax.set_xlabel("Time (Years)", color=self.text_color, labelpad=10)
        ax.set_ylabel("Population (Billions)", color=self.text_color, labelpad=10)
        
        ax.tick_params(colors=self.text_color)
        ax.grid(color=self.grid_color, linestyle="--", alpha=0.5)
        
        # Legend styling
        legend = ax.legend(facecolor=self.bg_color, edgecolor=self.spine_color, loc="upper left")
        for text in legend.get_texts():
            text.set_color(self.text_color)

        for spine in ["top", "right", "left", "bottom"]:
            ax.spines[spine].set_color(self.spine_color)

        save_path = os.path.join(output_dir, "civilization_growth.png")
        plt.savefig(save_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_technology_progress(self, output_dir: str = "datasets") -> None:
        """
        Generate a line chart of technology progression over time for top 5 advanced civilizations.
        """
        if not os.path.exists(self.tech_csv) or not os.path.exists(self.civs_csv):
            return

        civs_df = pd.read_csv(self.civs_csv)
        tech_df = pd.read_csv(self.tech_csv)
        if civs_df.empty or tech_df.empty:
            return

        # Find top 5 most advanced civilizations by final tech level
        top_5_ids = civs_df.sort_values(by="tech_level", ascending=False).head(5)["civilization_id"].tolist()

        fig, ax = plt.subplots(figsize=(10, 6), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)

        for cid in top_5_ids:
            civ_timeline = tech_df[tech_df["civilization_id"] == cid].sort_values(by="year")
            if civ_timeline.empty:
                continue
            name = civ_timeline.iloc[0].get("name", cid)
            if pd.isna(name) or name is None or str(name).strip() == "":
                name = cid
            ax.plot(
                civ_timeline["year"],
                civ_timeline["tech_level"],
                marker="^",
                markersize=4,
                linewidth=2,
                label=name
            )

        # Style chart
        ax.set_title("Technological Progression of Top 5 Advanced Civilizations", fontsize=14, color=self.header_color, pad=15)
        ax.set_xlabel("Time (Years)", color=self.text_color, labelpad=10)
        ax.set_ylabel("Technology level (Tiers 1-10+)", color=self.text_color, labelpad=10)
        
        ax.tick_params(colors=self.text_color)
        ax.grid(color=self.grid_color, linestyle="--", alpha=0.5)
        
        legend = ax.legend(facecolor=self.bg_color, edgecolor=self.spine_color, loc="upper left")
        for text in legend.get_texts():
            text.set_color(self.text_color)

        for spine in ["top", "right", "left", "bottom"]:
            ax.spines[spine].set_color(self.spine_color)

        save_path = os.path.join(output_dir, "technology_progress.png")
        plt.savefig(save_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_government_distribution(self, output_dir: str = "datasets") -> None:
        """
        Generate a bar chart of government type distribution.
        """
        if not os.path.exists(self.civs_csv):
            return

        civs_df = pd.read_csv(self.civs_csv)
        if civs_df.empty:
            return

        gov_counts = civs_df["government_type"].value_counts()
        
        fig, ax = plt.subplots(figsize=(8, 5), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)

        # Apply specific government colors
        colors = [self.gov_colors.get(gov, "#777788") for gov in gov_counts.index]

        bars = ax.bar(gov_counts.index, gov_counts.values, color=colors, edgecolor=self.spine_color, width=0.6)

        # Label values on top of bars
        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{int(height)}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),  # 3 points vertical offset
                textcoords="offset points",
                ha="center",
                va="bottom",
                color=self.text_color,
                fontsize=9
            )

        ax.set_title("Distribution of Government Types in the Galaxy", fontsize=14, color=self.header_color, pad=15)
        ax.set_xlabel("Government Structure", color=self.text_color, labelpad=10)
        ax.set_ylabel("Number of Civilizations", color=self.text_color, labelpad=10)
        
        ax.tick_params(colors=self.text_color)
        plt.xticks(rotation=20)
        ax.grid(color=self.grid_color, axis="y", linestyle="--", alpha=0.5)

        for spine in ["top", "right", "left", "bottom"]:
            ax.spines[spine].set_color(self.spine_color)

        save_path = os.path.join(output_dir, "government_distribution.png")
        plt.savefig(save_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_kardashev_scale_distribution(self, output_dir: str = "datasets") -> None:
        """
        Generate a histogram of Kardashev scale ratings for all active civilizations.
        """
        if not os.path.exists(self.civs_csv):
            return

        civs_df = pd.read_csv(self.civs_csv)
        if civs_df.empty:
            return

        # Filters only civilizations that haven't gone extinct
        active_ratings = civs_df[civs_df["population"] > 0]["kardashev_rating"]

        fig, ax = plt.subplots(figsize=(8, 5), facecolor=self.bg_color)
        ax.set_facecolor(self.bg_color)

        n, bins, patches = ax.hist(
            active_ratings,
            bins=20,
            color="#9b59b6",  # Violet/Purple
            edgecolor=self.bg_color,
            alpha=0.85
        )

        ax.set_title("Distribution of Civilization Energy Capacities (Kardashev Scale)", fontsize=14, color=self.header_color, pad=15)
        ax.set_xlabel("Kardashev Scale Rating", color=self.text_color, labelpad=10)
        ax.set_ylabel("Civilization Count", color=self.text_color, labelpad=10)
        
        ax.tick_params(colors=self.text_color)
        ax.grid(color=self.grid_color, linestyle="--", alpha=0.5)

        for spine in ["top", "right", "left", "bottom"]:
            ax.spines[spine].set_color(self.spine_color)

        save_path = os.path.join(output_dir, "kardashev_scale_distribution.png")
        plt.savefig(save_path, dpi=300, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_civilization_timeline(self, output_dir: str = "datasets") -> None:
        """
        Generate an interactive Plotly HTML scatter timeline plot showing major historical events
        for the top 5 civilizations.
        """
        if not os.path.exists(self.events_csv) or not os.path.exists(self.civs_csv):
            return

        civs_df = pd.read_csv(self.civs_csv)
        events_df = pd.read_csv(self.events_csv)
        if civs_df.empty or events_df.empty:
            return

        # Find top 5 largest civilizations by final population
        top_5_civs = civs_df.sort_values(by="population", ascending=False).head(5)
        top_5_ids = top_5_civs["civilization_id"].tolist()

        # Filter events for these top 5 civilizations
        timeline_events = events_df[events_df["civilization_id"].isin(top_5_ids)].copy()
        if timeline_events.empty:
            return

        # Ensure all columns exist for Plotly hover and labels
        if "civilization_name" not in timeline_events.columns:
            if "name" in civs_df.columns:
                name_map = civs_df.set_index("civilization_id")["name"].to_dict()
                timeline_events["civilization_name"] = timeline_events["civilization_id"].map(name_map).fillna(timeline_events["civilization_id"])
            else:
                timeline_events["civilization_name"] = timeline_events["civilization_id"]
        
        if "stability_impact" not in timeline_events.columns:
            timeline_events["stability_impact"] = 0.0
            
        if "population_impact" not in timeline_events.columns:
            timeline_events["population_impact"] = 0.0

        # Map event types to nice visual colors
        event_colors = {
            "Government Collapse": "#e74c3c",       # Red
            "Government Reform": "#3498db",         # Light Blue
            "Scientific Breakthrough": "#2ecc71",   # Emerald Green
            "Economic Boom": "#f1c40f",             # Yellow
            "Energy Crisis": "#e67e22",             # Orange
            "Technological Leap": "#1abc9c",        # Turquoise
            "Planetary Disaster": "#95a5a6",        # Amethyst/Gray
            "Civil War": "#c0392b",                 # Dark Red
            "Golden Age": "#9b59b6",                # Purple
            "Dark Age": "#34495e",                  # Wet Asphalt
            "Extinction": "#000000"                 # Black
        }

        # Create Plotly interactive scatter chart
        fig = px.scatter(
            timeline_events,
            x="year",
            y="civilization_name",
            color="event_type",
            hover_name="event_type",
            hover_data={
                "civilization_name": True,
                "year": ":d",
                "description": True,
                "stability_impact": ":+.1f",
                "population_impact": ":+,.0f"
            },
            title="Interactive Historical Event Timeline (Top 5 Empires)",
            labels={
                "year": "Simulation Year",
                "civilization_name": "Civilization",
                "event_type": "Historical Event"
            },
            color_discrete_map=event_colors
        )

        # Sizing and styling markers
        fig.update_traces(
            marker=dict(size=14, line=dict(width=1, color="white")),
            selector=dict(mode="markers")
        )

        # Style Layout
        fig.update_layout(
            paper_bgcolor="#030308",
            plot_bgcolor="#030308",
            font_color="#cccccc",
            title_font_color="#ffffff",
            xaxis=dict(
                gridcolor="#1e1e2f",
                linecolor="#444455",
                tickfont=dict(color="#cccccc")
            ),
            yaxis=dict(
                gridcolor="#1e1e2f",
                linecolor="#444455",
                tickfont=dict(color="#cccccc")
            ),
            legend=dict(
                bgcolor="rgba(3,3,8,0.8)",
                bordercolor="#444455",
                borderwidth=1
            )
        )

        save_path = os.path.join(output_dir, "civilization_timeline.html")
        fig.write_html(save_path)
