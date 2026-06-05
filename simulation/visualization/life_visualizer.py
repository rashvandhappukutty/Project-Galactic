"""
life_visualizer.py - Visualization engine for Phase 3: Life Emergence Engine.

Generates space-themed dashboards and mapping plots for life distribution,
factors affecting life probability, and civilization structures.
"""

from __future__ import annotations

import os
from typing import Dict
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


class LifeVisualizer:
    """
    Visualization engine to plot life distributions, dashboards, and galactic maps.

    Parameters
    ----------
    life_catalog_csv : str
        Path to the planetary life states catalog.
    species_catalog_csv : str
        Path to the sentient species catalog.
    civilizations_csv : str
        Path to the civilizations catalog.
    """

    def __init__(
        self,
        life_catalog_csv: str,
        species_catalog_csv: str,
        civilizations_csv: str,
    ) -> None:
        self.life_catalog_csv = life_catalog_csv
        self.species_catalog_csv = species_catalog_csv
        self.civilizations_csv = civilizations_csv

        # Color configurations for dark space theme
        self.bg_color = "#030308"
        self.grid_color = "#222233"
        self.spine_color = "#444455"
        self.text_color = "#cccccc"
        self.header_color = "#ffffff"

        # Life Stage styling
        self.stage_labels: Dict[int, str] = {
            0: "Abiotic (0)",
            1: "Microbial (1)",
            2: "Simple Multicellular (2)",
            3: "Complex Ecosystems (3)",
            4: "Intelligent Life (4)",
            5: "Civilizations (5)",
        }
        self.stage_colors: Dict[int, str] = {
            0: "#222233",  # Dark blue-grey
            1: "#00ffcc",  # Cyan-green
            2: "#0099ff",  # Bright blue
            3: "#cc33ff",  # Purple
            4: "#ffcc00",  # Gold
            5: "#ff3366",  # Pink-red
        }

        # Planet type styling
        self.planet_type_colors: Dict[str, str] = {
            "Rocky": "#a8a8a8",
            "Ocean": "#3399ff",
            "Ice": "#99ccff",
            "Desert": "#e6b800",
            "Gas Giant": "#ff9933",
            "Lava World": "#ff3300",
            "Toxic World": "#33cc33",
            "Super Earth": "#9966ff",
        }

        # Government type styling
        self.government_colors: Dict[str, str] = {
            "Democracy": "#3399ff",
            "Technocracy": "#00ffcc",
            "Federation": "#9966ff",
            "Autocracy": "#ff3333",
            "Oligarchy": "#ffcc00",
            "Monarchy": "#ff9933",
            "Theocracy": "#cc33ff",
            "Hive Mind": "#66ff66",
        }

    def _apply_dark_theme(self, fig: plt.Figure, ax: plt.Axes) -> None:
        """Apply the space dark theme settings to a matplotlib Axes object."""
        fig.patch.set_facecolor(self.bg_color)
        ax.set_facecolor(self.bg_color)

        if hasattr(ax, "spines") and ax.spines:
            for spine in ax.spines.values():
                spine.set_color(self.spine_color)

        ax.tick_params(colors=self.text_color, which="both", labelsize=9)
        ax.xaxis.label.set_color(self.text_color)
        ax.yaxis.label.set_color(self.text_color)
        ax.title.set_color(self.header_color)

    def _load_and_merge_life_catalog(self) -> pd.DataFrame:
        """
        Load life catalog and enrich with planets.csv columns if missing.
        """
        if not os.path.exists(self.life_catalog_csv):
            raise FileNotFoundError(f"Life catalog not found at {self.life_catalog_csv}")

        life_df = pd.read_csv(self.life_catalog_csv)

        # Check if any plotting-critical columns are missing
        required_cols = {"habitability_score", "planet_type", "temperature", "water_percentage", "planet_name"}
        missing_cols = required_cols - set(life_df.columns)

        if missing_cols:
            planets_csv_path = None
            dir_name = os.path.dirname(self.life_catalog_csv)
            candidate_1 = os.path.join(dir_name, "planets.csv")
            if os.path.exists(candidate_1):
                planets_csv_path = candidate_1
            else:
                candidate_2 = os.path.join("datasets", "planets.csv")
                if os.path.exists(candidate_2):
                    planets_csv_path = candidate_2

            if planets_csv_path:
                planets_df = pd.read_csv(planets_csv_path)
                cols_to_merge = ["planet_id"] + [col for col in missing_cols if col in planets_df.columns]
                if len(cols_to_merge) > 1 and "planet_id" in life_df.columns:
                    life_df = life_df.merge(planets_df[cols_to_merge], on="planet_id", how="left")

        # Fill default columns if still missing to prevent plotting failure
        if "habitability_score" not in life_df.columns:
            life_df["habitability_score"] = 0.0
        if "planet_type" not in life_df.columns:
            life_df["planet_type"] = "Unknown"
        if "temperature" not in life_df.columns:
            life_df["temperature"] = 0.0
        if "water_percentage" not in life_df.columns:
            life_df["water_percentage"] = 0.0
        if "planet_name" not in life_df.columns:
            life_df["planet_name"] = life_df["planet_id"].astype(str)

        return life_df

    def _load_and_merge_civilizations(self) -> pd.DataFrame:
        """
        Load civilizations and resolve star_id / population relationships.
        """
        if not os.path.exists(self.civilizations_csv) or os.path.getsize(self.civilizations_csv) == 0:
            return pd.DataFrame()

        civs_df = pd.read_csv(self.civilizations_csv)
        if civs_df.empty:
            return civs_df

        # Resolve star_id if missing
        if "star_id" not in civs_df.columns:
            try:
                life_df = pd.read_csv(self.life_catalog_csv)
                if "planet_id" in civs_df.columns and "planet_id" in life_df.columns:
                    civs_df = civs_df.merge(life_df[["planet_id", "star_id"]], on="planet_id", how="left")
            except Exception:
                pass

        if "star_id" not in civs_df.columns:
            try:
                dir_name = os.path.dirname(self.civilizations_csv)
                candidate_1 = os.path.join(dir_name, "planets.csv")
                if not os.path.exists(candidate_1):
                    candidate_1 = os.path.join("datasets", "planets.csv")
                if os.path.exists(candidate_1):
                    planets_df = pd.read_csv(candidate_1)
                    if "planet_id" in civs_df.columns and "planet_id" in planets_df.columns:
                        civs_df = civs_df.merge(planets_df[["planet_id", "star_id"]], on="planet_id", how="left")
            except Exception:
                pass

        return civs_df

    def plot_life_distribution(self, output_dir: str = "datasets") -> None:
        """
        Matplotlib bar chart of planet count per Life Stage (0-5).

        Parameters
        ----------
        output_dir : str, default 'datasets'
            Directory where the output figure will be saved.
        """
        os.makedirs(output_dir, exist_ok=True)
        life_df = self._load_and_merge_life_catalog()

        stage_counts = life_df["life_stage"].value_counts()
        counts = [int(stage_counts.get(i, 0)) for i in range(6)]
        labels = [self.stage_labels[i] for i in range(6)]
        colors = [self.stage_colors[i] for i in range(6)]

        fig, ax = plt.subplots(figsize=(9, 6), facecolor=self.bg_color)
        self._apply_dark_theme(fig, ax)

        bars = ax.bar(labels, counts, color=colors, edgecolor=self.spine_color, width=0.6)
        ax.set_ylabel("Planet Count", fontsize=11, color=self.text_color)
        ax.set_title("Procedural Planet Count per Life Stage", fontsize=14, pad=15)
        ax.grid(True, axis="y", linestyle="--", alpha=0.1, color="#888888")

        # Label columns with values
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
                fontsize=10,
            )

        plt.xticks(rotation=15, ha="right")
        plt.tight_layout()
        save_path = os.path.join(output_dir, "life_distribution.png")
        plt.savefig(save_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_life_probability_dashboard(self, output_dir: str = "datasets") -> None:
        """
        2x2 Matplotlib dashboard showing relationship factors with life probability.

        Parameters
        ----------
        output_dir : str, default 'datasets'
            Directory where the dashboard image will be saved.
        """
        os.makedirs(output_dir, exist_ok=True)
        life_df = self._load_and_merge_life_catalog()

        # Check if life_probability exists
        if "life_probability" not in life_df.columns:
            raise KeyError("Column 'life_probability' not found in life catalog.")

        fig, axs = plt.subplots(2, 2, figsize=(14, 10), facecolor=self.bg_color)

        # Apply dark theme to all subplots
        for row in axs:
            for ax in row:
                self._apply_dark_theme(fig, ax)
                ax.grid(True, linestyle="--", alpha=0.1, color="#888888")

        # 1. Top-Left: life_probability vs habitability_score (colored by planet type)
        ax_tl = axs[0, 0]
        groups = life_df.groupby("planet_type")
        for name, group in groups:
            color = self.planet_type_colors.get(name, "#ffffff")
            ax_tl.scatter(
                group["habitability_score"],
                group["life_probability"],
                label=name,
                color=color,
                alpha=0.7,
                s=20,
                edgecolors="none",
            )
        ax_tl.set_xlabel("Habitability Score", color=self.text_color)
        ax_tl.set_ylabel("Life Probability", color=self.text_color)
        ax_tl.set_title("Life Probability vs Habitability", fontsize=11)
        ax_tl.legend(
            facecolor=self.bg_color,
            edgecolor=self.spine_color,
            fontsize=8,
            labelcolor=self.text_color,
            loc="upper left",
        )

        # 2. Top-Right: Histogram of life_probability on life-bearing worlds
        ax_tr = axs[0, 1]
        life_bearing = life_df[life_df["life_stage"] >= 1]
        if not life_bearing.empty:
            ax_tr.hist(
                life_bearing["life_probability"],
                bins=15,
                color="#00ffcc",
                edgecolor=self.spine_color,
                alpha=0.8,
            )
            ax_tr.set_xlabel("Life Probability", color=self.text_color)
            ax_tr.set_ylabel("Frequency", color=self.text_color)
            ax_tr.set_title("Life Probability on Life-Bearing Worlds", fontsize=11)
        else:
            ax_tr.text(
                0.5,
                0.5,
                "No life-bearing worlds (Stage >= 1) found.",
                ha="center",
                va="center",
                color="#ffffff",
            )

        # 3. Bottom-Left: Life probability vs Temperature
        ax_bl = axs[1, 0]
        ax_bl.scatter(
            life_df["temperature"],
            life_df["life_probability"],
            color="#ffcc00",
            alpha=0.6,
            s=15,
            edgecolors="none",
        )
        ax_bl.set_xlabel("Equilibrium Temperature (K)", color=self.text_color)
        ax_bl.set_ylabel("Life Probability", color=self.text_color)
        ax_bl.set_title("Life Probability vs Temperature", fontsize=11)

        # 4. Bottom-Right: Water percentage vs Life probability
        ax_br = axs[1, 1]
        ax_br.scatter(
            life_df["water_percentage"],
            life_df["life_probability"],
            color="#3399ff",
            alpha=0.6,
            s=15,
            edgecolors="none",
        )
        ax_br.set_xlabel("Water Surface Coverage (%)", color=self.text_color)
        ax_br.set_ylabel("Life Probability", color=self.text_color)
        ax_br.set_title("Life Probability vs Water Coverage", fontsize=11)

        fig.suptitle("Procedural Planetary Life Emergence Factors", fontsize=16, color="#ffffff", y=0.98)
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        save_path = os.path.join(output_dir, "life_probability_dashboard.png")
        plt.savefig(save_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_civilization_map(self, output_dir: str = "datasets") -> None:
        """
        Create 3D mapping of civilization positions in space.

        Merges star_systems.csv coordinates with civilizations, sized by tech level
        and colored by government type. Saves PNG and HTML.

        Parameters
        ----------
        output_dir : str, default 'datasets'
            Directory to save both civilization_map.png and civilization_map.html.
        """
        os.makedirs(output_dir, exist_ok=True)
        civs_df = self._load_and_merge_civilizations()

        # Find star_systems.csv
        star_systems_csv = None
        dir_name = os.path.dirname(self.civilizations_csv)
        candidate_1 = os.path.join(dir_name, "star_systems.csv")
        if os.path.exists(candidate_1):
            star_systems_csv = candidate_1
        else:
            candidate_2 = os.path.join("datasets", "star_systems.csv")
            if os.path.exists(candidate_2):
                star_systems_csv = candidate_2

        # Check if civilization data or coordinates are unavailable
        if civs_df.empty or not star_systems_csv:
            # Save fallback blank plots
            fig = plt.figure(figsize=(10, 8), facecolor=self.bg_color)
            ax = fig.add_subplot(111, facecolor=self.bg_color)
            ax.text(
                0.5,
                0.5,
                "No civilization coordinates available to plot.",
                ha="center",
                va="center",
                color="#ffffff",
                fontsize=14,
            )
            ax.axis("off")
            plt.savefig(
                os.path.join(output_dir, "civilization_map.png"),
                dpi=150,
                facecolor=fig.get_facecolor(),
                bbox_inches="tight",
            )
            plt.close()

            # Save empty html
            with open(os.path.join(output_dir, "civilization_map.html"), "w", encoding="utf-8") as f:
                f.write(
                    "<html><body style='background-color:#030308; color:#ffffff; font-family:sans-serif; text-align:center; padding-top:100px;'>"
                    "<h1>No Civilization Coordinates Found</h1></body></html>"
                )
            return

        # Load coordinates and merge
        systems_df = pd.read_csv(star_systems_csv)
        merged_df = civs_df.merge(systems_df[["star_id", "x", "y", "z", "star_name"]], on="star_id", how="inner")

        if merged_df.empty:
            # Fallback
            fig = plt.figure(figsize=(10, 8), facecolor=self.bg_color)
            ax = fig.add_subplot(111, facecolor=self.bg_color)
            ax.text(
                0.5,
                0.5,
                "Zero matching coordinate overlaps found between star systems and civilizations.",
                ha="center",
                va="center",
                color="#ffffff",
                fontsize=11,
            )
            ax.axis("off")
            plt.savefig(
                os.path.join(output_dir, "civilization_map.png"),
                dpi=150,
                facecolor=fig.get_facecolor(),
                bbox_inches="tight",
            )
            plt.close()
            return

        # Determine tech column name
        tech_col = "technology_level" if "technology_level" in merged_df.columns else "tech_level"

        # --- 1. MATPLOTLIB STATIC 3D PLOT ---
        fig = plt.figure(figsize=(10, 8), facecolor=self.bg_color)
        ax = fig.add_subplot(111, projection="3d", facecolor=self.bg_color)
        self._apply_dark_theme(fig, ax)

        # Style 3D grid/planes
        ax.xaxis.pane.fill = False
        ax.yaxis.pane.fill = False
        ax.zaxis.pane.fill = False
        ax.xaxis.pane.set_edgecolor(self.grid_color)
        ax.yaxis.pane.set_edgecolor(self.grid_color)
        ax.zaxis.pane.set_edgecolor(self.grid_color)
        ax.grid(True, linestyle="--", alpha=0.05, color="#888888")

        groups = merged_df.groupby("government_type")
        for name, group in groups:
            color = self.government_colors.get(name, "#ffffff")
            sizes = 20.0 + (group[tech_col] * 0.8)  # Scale points appropriately
            ax.scatter(
                group["x"],
                group["y"],
                group["z"],
                label=name,
                color=color,
                s=sizes,
                alpha=0.8,
                depthshade=True,
                edgecolors="none",
            )

        ax.set_xlabel("X coordinate (ly)", color=self.text_color)
        ax.set_ylabel("Y coordinate (ly)", color=self.text_color)
        ax.set_zlabel("Z coordinate (ly)", color=self.text_color)
        ax.set_title("3D Civilization Galactic Positions", fontsize=14, pad=15)
        ax.legend(facecolor=self.bg_color, edgecolor=self.spine_color, labelcolor=self.text_color)

        plt.savefig(
            os.path.join(output_dir, "civilization_map.png"),
            dpi=150,
            facecolor=fig.get_facecolor(),
            bbox_inches="tight",
        )
        plt.close()

        # --- 2. INTERACTIVE PLOTLY 3D PLOT ---
        fig_plotly = px.scatter_3d(
            merged_df,
            x="x",
            y="y",
            z="z",
            color="government_type",
            size=tech_col,
            hover_name="name",
            hover_data={
                "star_name": True,
                "energy_source": True,
                "civilization_age": True,
                tech_col: True,
            },
            title="Galactic Civilization Mapping Space",
            color_discrete_map=self.government_colors,
        )

        fig_plotly.update_layout(
            template="plotly_dark",
            scene=dict(
                xaxis=dict(backgroundcolor=self.bg_color, gridcolor=self.grid_color, showbackground=True),
                yaxis=dict(backgroundcolor=self.bg_color, gridcolor=self.grid_color, showbackground=True),
                zaxis=dict(backgroundcolor=self.bg_color, gridcolor=self.grid_color, showbackground=True),
            ),
            paper_bgcolor=self.bg_color,
            plot_bgcolor=self.bg_color,
            title_font_color="#ffffff",
            legend_title_font_color="#ffffff",
        )

        fig_plotly.write_html(os.path.join(output_dir, "civilization_map.html"))

    def plot_civilization_statistics(self, output_dir: str = "datasets") -> None:
        """
        Create a 2x2 dashboard of civilization properties:
        - Top-left: Government type distribution (bar).
        - Top-right: Energy source distribution (pie/bar).
        - Bottom-left: Tech level vs Age (scatter).
        - Bottom-right: Top 10 populations (horizontal bar).

        Parameters
        ----------
        output_dir : str, default 'datasets'
            Directory where civilization_statistics.png will be saved.
        """
        os.makedirs(output_dir, exist_ok=True)
        civs_df = self._load_and_merge_civilizations()

        if civs_df.empty:
            fig, ax = plt.subplots(figsize=(10, 8), facecolor=self.bg_color)
            ax.set_facecolor(self.bg_color)
            ax.text(
                0.5,
                0.5,
                "No civilization statistics available to plot.",
                ha="center",
                va="center",
                color="#ffffff",
                fontsize=14,
            )
            ax.axis("off")
            plt.savefig(
                os.path.join(output_dir, "civilization_statistics.png"),
                dpi=150,
                facecolor=fig.get_facecolor(),
                bbox_inches="tight",
            )
            plt.close()
            return

        fig, axs = plt.subplots(2, 2, figsize=(14, 10), facecolor=self.bg_color)

        # Apply dark theme
        for row in axs:
            for ax in row:
                self._apply_dark_theme(fig, ax)
                ax.grid(True, linestyle="--", alpha=0.1, color="#888888")

        # 1. Top-Left: Government type distribution
        ax_tl = axs[0, 0]
        gov_counts = civs_df["government_type"].value_counts()
        gov_colors = [self.government_colors.get(g, "#9999aa") for g in gov_counts.index]
        ax_tl.bar(gov_counts.index, gov_counts.values, color=gov_colors, edgecolor=self.spine_color, width=0.5)
        ax_tl.set_title("Governance Types Distribution", fontsize=11)
        ax_tl.set_ylabel("Civilization Count", color=self.text_color)
        ax_tl.tick_params(axis="x", rotation=30)

        # 2. Top-Right: Energy source distribution
        ax_tr = axs[0, 1]
        energy_counts = civs_df["energy_source"].value_counts()
        if len(energy_counts) > 0:
            # Use distinct color map
            colors_pie = plt.cm.Set3(np.linspace(0.1, 0.9, len(energy_counts)))
            ax_tr.pie(
                energy_counts.values,
                labels=energy_counts.index,
                autopct="%1.1f%%",
                startangle=90,
                colors=colors_pie,
                textprops={"color": self.text_color, "fontsize": 8},
            )
            ax_tr.set_title("Primary Energy Source Distribution", fontsize=11)
        else:
            ax_tr.text(0.5, 0.5, "No energy data available", ha="center", va="center", color="#ffffff")

        # 3. Bottom-Left: Tech level vs Age
        ax_bl = axs[1, 0]
        tech_col = "technology_level" if "technology_level" in civs_df.columns else "tech_level"
        if tech_col in civs_df.columns and "civilization_age" in civs_df.columns:
            ax_bl.scatter(
                civs_df["civilization_age"],
                civs_df[tech_col],
                color="#cc33ff",
                alpha=0.7,
                s=25,
                edgecolors="none",
            )
            ax_bl.set_xlabel("Civilization Age (years)", color=self.text_color)
            ax_bl.set_ylabel("Technology Level", color=self.text_color)
            ax_bl.set_title("Technology Development vs Age", fontsize=11)
        else:
            ax_bl.text(0.5, 0.5, "Age or Tech columns missing.", ha="center", va="center", color="#ffffff")

        # 4. Bottom-Right: Top 10 civilizations by population
        ax_br = axs[1, 1]
        pop_col = None
        for col in ["population", "species_population", "species.population"]:
            if col in civs_df.columns:
                pop_col = col
                break

        # If population is missing, try merging with species catalog
        if pop_col is None and os.path.exists(self.species_catalog_csv):
            try:
                species_df = pd.read_csv(self.species_catalog_csv)
                if "planet_id" in civs_df.columns and "planet_id" in species_df.columns:
                    target_pop = (
                        "population"
                        if "population" in species_df.columns
                        else ("species_population" if "species_population" in species_df.columns else None)
                    )
                    if target_pop:
                        merged_df = civs_df.merge(species_df[["planet_id", target_pop]], on="planet_id", how="left")
                        civs_df["population"] = merged_df[target_pop]
                        pop_col = "population"
            except Exception:
                pass

        if pop_col and pop_col in civs_df.columns:
            top_pop = civs_df.sort_values(by=pop_col, ascending=False).head(10)
            top_pop = top_pop.iloc[::-1]  # Plot largest on top
            if not top_pop.empty:
                ax_br.barh(top_pop["name"], top_pop[pop_col], color="#ffcc00", edgecolor=self.spine_color, height=0.5)
                ax_br.set_xlabel("Population", color=self.text_color)
                ax_br.set_title("Top 10 Populations", fontsize=11)
                ax_br.tick_params(axis="y", labelsize=8)
            else:
                ax_br.text(0.5, 0.5, "No civilizations found.", ha="center", va="center", color="#ffffff")
        else:
            ax_br.text(0.5, 0.5, "Population column not resolved.", ha="center", va="center", color="#ffffff")

        fig.suptitle("Procedural Civilizations Demographic Analysis", fontsize=16, color="#ffffff", y=0.98)
        fig.tight_layout(rect=[0, 0.03, 1, 0.95])

        save_path = os.path.join(output_dir, "civilization_statistics.png")
        plt.savefig(save_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()
