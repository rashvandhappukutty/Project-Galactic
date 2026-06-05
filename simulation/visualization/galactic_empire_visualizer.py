"""
galactic_empire_visualizer.py — Visualization engine for Phase 6 Colonization Engine.

Generates space dark theme maps of star empires, networks, and timelines.
"""

import os
from typing import Dict, List, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


class GalacticEmpireVisualizer:
    """Renders charts and maps of space borders, routes, and history timelines."""

    def __init__(
        self,
        colonies_csv: str,
        empires_csv: str,
        territories_csv: str,
        routes_csv: str,
        events_csv: str,
        stars_csv: str,
    ) -> None:
        self.colonies_csv = colonies_csv
        self.empires_csv = empires_csv
        self.territories_csv = territories_csv
        self.routes_csv = routes_csv
        self.events_csv = events_csv
        self.stars_csv = stars_csv

        # Color configurations for dark space theme
        self.bg_color = "#030308"
        self.grid_color = "#222233"
        self.spine_color = "#444455"
        self.text_color = "#cccccc"
        self.header_color = "#ffffff"

        # Unique Colors for major empires
        self.empire_colors = [
            "#ff3366", "#3399ff", "#00ffcc", "#ffcc00", "#cc33ff",
            "#ff9933", "#00ffff", "#66ff66", "#ff55ff", "#ffff55"
        ]

    def _apply_dark_theme(self, fig: plt.Figure, ax: plt.Axes) -> None:
        """Apply space dark theme to a matplotlib Axes object."""
        fig.patch.set_facecolor(self.bg_color)
        ax.set_facecolor(self.bg_color)

        if hasattr(ax, "spines") and ax.spines:
            for spine in ax.spines.values():
                spine.set_color(self.spine_color)

        ax.tick_params(colors=self.text_color, which="both", labelsize=9)
        ax.xaxis.label.set_color(self.text_color)
        ax.yaxis.label.set_color(self.text_color)
        ax.title.set_color(self.header_color)

    def plot_galactic_empires_map(self, output_dir: str = "datasets") -> None:
        """Plot a 2D galactic border slice showing spheres of influence of the top empires."""
        os.makedirs(output_dir, exist_ok=True)
        
        stars_df = pd.read_csv(self.stars_csv)
        empires_df = pd.read_csv(self.empires_csv)
        territories_df = pd.read_csv(self.territories_csv)
        colonies_df = pd.read_csv(self.colonies_csv)

        fig, ax = plt.subplots(figsize=(10, 10), facecolor=self.bg_color)
        self._apply_dark_theme(fig, ax)

        # Plot all stars faintly in background
        ax.scatter(stars_df["x"], stars_df["y"], s=1, color="#333344", alpha=0.3, label="Stars")

        # Get top 8 empires by power index
        if not empires_df.empty:
            top_empires = empires_df.sort_values(by="power_index", ascending=False).head(8)
            
            for idx, (_, emp) in enumerate(top_empires.iterrows()):
                civ_id = emp["founding_civilization_id"]
                emp_name = emp["empire_name"]
                color = self.empire_colors[idx % len(self.empire_colors)]

                # Get coordinates of capital/founding civ home star
                # (Look up home star coordinates)
                founding_civ_id = str(civ_id)
                # Filter stars belonging to this civ's capital
                # Home star info can be found by matching the capital planet's star
                home_star_row = stars_df[stars_df["name"] == emp["capital_world"].replace(" e", "").replace(" f", "")]
                if home_star_row.empty:
                    # Fallback to matching capital name with stars
                    capital_base = emp["capital_world"].split("-")[0]
                    home_star_row = stars_df[stars_df["name"].str.contains(capital_base, case=False, na=False)]

                if not home_star_row.empty:
                    x_c = float(home_star_row.iloc[0]["x"])
                    y_c = float(home_star_row.iloc[0]["y"])

                    # Draw Capital marker
                    ax.scatter(x_c, y_c, s=60, color=color, marker="*", edgecolor="#ffffff", label=emp_name, zorder=5)

                    # Get sphere of influence radius from territories_df
                    terr_row = territories_df[territories_df["civilization_id"] == founding_civ_id]
                    if not terr_row.empty:
                        r = float(terr_row.iloc[0]["sphere_of_influence_ly"])
                        # Draw circle for SOI
                        circle = plt.Circle((x_c, y_c), r, color=color, alpha=0.08, zorder=2)
                        ax.add_patch(circle)
                        # Draw border line
                        border = plt.Circle((x_c, y_c), r, color=color, fill=False, linestyle="--", linewidth=0.8, alpha=0.4, zorder=2)
                        ax.add_patch(border)

                # Plot colonies of this empire
                emp_cols = colonies_df[colonies_df["parent_civilization_id"] == founding_civ_id]
                if not emp_cols.empty:
                    # Join with stars to get colony star coordinates
                    col_stars = stars_df[stars_df["id"].isin(emp_cols["home_star_id"])]
                    if not col_stars.empty:
                        ax.scatter(col_stars["x"], col_stars["y"], s=25, color=color, marker="o", edgecolor="#111111", zorder=4)

        ax.set_xlabel("Galactic X Coordinate (ly)", color=self.text_color)
        ax.set_ylabel("Galactic Y Coordinate (ly)", color=self.text_color)
        ax.set_title("Galactic Border and Empire Sphere of Influence Map", fontsize=14, pad=15)
        ax.legend(
            facecolor=self.bg_color,
            edgecolor=self.spine_color,
            fontsize=8,
            labelcolor=self.text_color,
            loc="upper right"
        )
        ax.set_aspect("equal")

        plt.tight_layout()
        save_path = os.path.join(output_dir, "galactic_empires_map.png")
        plt.savefig(save_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_trade_routes_map(self, output_dir: str = "datasets") -> None:
        """Plot the grid network of trade and migration routes connecting systems."""
        os.makedirs(output_dir, exist_ok=True)
        
        stars_df = pd.read_csv(self.stars_csv)
        routes_df = pd.read_csv(self.routes_csv)

        fig, ax = plt.subplots(figsize=(10, 10), facecolor=self.bg_color)
        self._apply_dark_theme(fig, ax)

        # Plot all stars faintly
        ax.scatter(stars_df["x"], stars_df["y"], s=1, color="#222233", alpha=0.3)

        if not routes_df.empty:
            # Group stars by ID for fast lookup
            stars_dict = stars_df.set_index("id").to_dict(orient="index")

            # Draw lines for routes
            for _, route in routes_df.iterrows():
                src_id = route["source_star_id"]
                tgt_id = route["target_star_id"]
                r_type = route["route_type"]
                traffic = float(route["traffic_index"])

                src_star = stars_dict.get(src_id)
                tgt_star = stars_dict.get(tgt_id)

                if src_star and tgt_star:
                    x_coords = [float(src_star["x"]), float(tgt_star["x"])]
                    y_coords = [float(src_star["y"]), float(tgt_star["y"])]

                    color = "#66ff66" if r_type == "Trade Route" else "#cc33ff"
                    alpha = min(0.8, 0.15 + (traffic / 10.0))  # Traffic governs alpha
                    linewidth = min(2.5, 0.5 + (traffic / 5.0)) # Traffic governs thickness

                    ax.plot(x_coords, y_coords, color=color, alpha=alpha, linewidth=linewidth, zorder=3)

            # Draw route markers
            active_route_star_ids = set(routes_df["source_star_id"]).union(set(routes_df["target_star_id"]))
            active_stars = stars_df[stars_df["id"].isin(active_route_star_ids)]
            ax.scatter(active_stars["x"], active_stars["y"], s=8, color="#00ffcc", zorder=4, label="Interstellar Hub")

        # Custom legends for routes
        from matplotlib.lines import Line2D
        custom_lines = [
            Line2D([0], [0], color="#66ff66", lw=1.5, label="Trade Route (Proximity Commerce)"),
            Line2D([0], [0], color="#cc33ff", lw=1.5, label="Migration Route (Metropolis Outposts)"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#00ffcc", markersize=6, label="Hub System")
        ]

        ax.set_xlabel("Galactic X Coordinate (ly)", color=self.text_color)
        ax.set_ylabel("Galactic Y Coordinate (ly)", color=self.text_color)
        ax.set_title("Interstellar Hub and Routes Connectivity Grid", fontsize=14, pad=15)
        ax.legend(
            handles=custom_lines,
            facecolor=self.bg_color,
            edgecolor=self.spine_color,
            fontsize=8,
            labelcolor=self.text_color,
            loc="upper right"
        )
        ax.set_aspect("equal")

        plt.tight_layout()
        save_path = os.path.join(output_dir, "trade_routes_map.png")
        plt.savefig(save_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_territory_growth(self, output_dir: str = "datasets") -> None:
        """Create a cumulative line chart of colony growth over ticks for the top empires."""
        os.makedirs(output_dir, exist_ok=True)
        
        empires_df = pd.read_csv(self.empires_csv)
        colonies_df = pd.read_csv(self.colonies_csv)

        fig, ax = plt.subplots(figsize=(10, 6), facecolor=self.bg_color)
        self._apply_dark_theme(fig, ax)
        ax.grid(True, linestyle="--", alpha=0.1, color="#888888")

        ticks = list(range(1, 11))

        if not empires_df.empty and not colonies_df.empty:
            # Sort top 5 empires by power index
            top_empires = empires_df.sort_values(by="power_index", ascending=False).head(5)

            for idx, (_, emp) in enumerate(top_empires.iterrows()):
                civ_id = emp["founding_civilization_id"]
                emp_name = emp["empire_name"]
                color = self.empire_colors[idx % len(self.empire_colors)]

                # Filter colonies owned by this civ
                emp_cols = colonies_df[colonies_df["parent_civilization_id"] == civ_id]
                
                # Reconstruct cumulative colonies over ticks
                # Tick 10 colony age = age, tick of foundation = 10 - age/100
                cumulative_counts = []
                for t in ticks:
                    # Founded at or before tick t
                    count = 0
                    for _, col in emp_cols.iterrows():
                        foundation_tick = 10 - (col["age"] / 100.0)
                        if foundation_tick <= t:
                            count += 1
                    cumulative_counts.append(count)

                # Add capital world (starts at tick 0)
                cumulative_counts = [c + 1 for c in cumulative_counts]

                ax.plot(ticks, cumulative_counts, marker="o", color=color, label=emp_name, linewidth=1.8, markersize=5)

        ax.set_xlabel("Simulation Tick (1 tick = 100 years)", color=self.text_color)
        ax.set_ylabel("Controlled Worlds (Capital + Colonies)", color=self.text_color)
        ax.set_title("Imperial Territory and Worlds Expansion Trend", fontsize=14, pad=15)
        ax.legend(facecolor=self.bg_color, edgecolor=self.spine_color, labelcolor=self.text_color, fontsize=8)
        ax.set_xticks(ticks)

        plt.tight_layout()
        save_path = os.path.join(output_dir, "territory_growth.png")
        plt.savefig(save_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_colony_distribution(self, output_dir: str = "datasets") -> None:
        """Create bar chart of colony types distribution across the galaxy."""
        os.makedirs(output_dir, exist_ok=True)
        
        df = pd.read_csv(self.colonies_csv)

        if df.empty:
            return

        col_types = df["colony_type"].value_counts()
        labels = list(col_types.index)
        counts = list(col_types.values)

        # Spacey theme colors
        colors = plt.cm.Set2(np.linspace(0.1, 0.9, len(labels)))

        fig, ax = plt.subplots(figsize=(10, 6), facecolor=self.bg_color)
        self._apply_dark_theme(fig, ax)

        bars = ax.bar(labels, counts, color=colors, edgecolor=self.spine_color, width=0.5)
        ax.set_ylabel("Establishments Count", fontsize=11, color=self.text_color)
        ax.set_title("Galactic Colony Composition Distribution", fontsize=14, pad=15)
        ax.grid(True, axis="y", linestyle="--", alpha=0.1, color="#888888")

        for bar in bars:
            height = bar.get_height()
            ax.annotate(
                f"{height}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                color="#ffffff",
                fontsize=9,
            )

        plt.xticks(rotation=20, ha="right")
        plt.tight_layout()
        save_path = os.path.join(output_dir, "colony_distribution.png")
        plt.savefig(save_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_empire_timeline(self, output_dir: str = "datasets") -> None:
        """Create Plotly HTML timeline displaying colonization events."""
        os.makedirs(output_dir, exist_ok=True)
        
        df = pd.read_csv(self.events_csv)

        if df.empty:
            with open(os.path.join(output_dir, "empire_timeline.html"), "w", encoding="utf-8") as f:
                f.write("<html><body><h1>No Empire Events Found</h1></body></html>")
            return

        # Focus on significant events to prevent timeline overlap
        significant_events = ["Colony Rebellion", "Empire Fragmentation", "First Colony", "Resource Rush"]
        df_filtered = df[df["event_type"].isin(significant_events)].copy()

        if len(df_filtered) < 10:
            df_filtered = df.copy()

        # Limit to top 25 active empires
        active_civs = df_filtered["civilization_name"].value_counts().head(25).index
        df_filtered = df_filtered[df_filtered["civilization_name"].isin(active_civs)]

        fig_plotly = px.scatter(
            df_filtered,
            x="tick",
            y="civilization_name",
            color="event_type",
            hover_name="civilization_name",
            hover_data={
                "tick": True,
                "event_type": True,
                "description": True,
            },
            title="Galactic Colonization and Imperial History Timeline",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )

        fig_plotly.update_layout(
            template="plotly_dark",
            paper_bgcolor=self.bg_color,
            plot_bgcolor=self.bg_color,
            xaxis=dict(gridcolor=self.grid_color, title="Simulation Tick (1 tick = 100 years)"),
            yaxis=dict(gridcolor=self.grid_color, title="Empire Founding Civilization"),
            title_font_color="#ffffff",
            legend_title_font_color="#ffffff",
        )

        fig_plotly.update_traces(marker=dict(size=12, symbol="triangle-up"))

        save_path = os.path.join(output_dir, "empire_timeline.html")
        fig_plotly.write_html(save_path)
