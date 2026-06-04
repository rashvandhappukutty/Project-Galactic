"""
system_visualizer.py — Star-system and planet visualization for the Galactic Dream Engine.

Provides static Matplotlib charts (orbital map, statistics dashboard) and an
interactive Plotly viewer for exploring individual star systems and their
planetary populations.

Phase 2 — Planetary Visualization & Analytics
"""

from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Wedge
from matplotlib.collections import PatchCollection
import plotly.graph_objects as go


# ---------------------------------------------------------------------------
# Colour palettes
# ---------------------------------------------------------------------------

SPECTRAL_COLORS: Dict[str, str] = {
    "O": "#9bb0ff",
    "B": "#aabfff",
    "A": "#cad7ff",
    "F": "#f8f7ff",
    "G": "#fff4ea",
    "K": "#ffd2a1",
    "M": "#ff9e9e",
}

PLANET_TYPE_COLORS: Dict[str, str] = {
    "Rocky":       "#8B7355",
    "Ocean":       "#4169E1",
    "Ice":         "#ADD8E6",
    "Desert":      "#DEB887",
    "Gas Giant":   "#FF8C00",
    "Lava World":  "#FF4500",
    "Toxic World": "#9ACD32",
    "Super Earth": "#32CD32",
}

# Background colour shared across all space-themed plots.
_SPACE_BG: str = "#030308"
_PANEL_BG: str = "#0e0e1a"


class SystemVisualizer:
    """Visualization suite for star-system and planetary data.

    Reads pre-generated CSV catalogues (``star_systems.csv`` and
    ``planets.csv``) produced by the upstream generation pipeline and
    offers several rendering methods:

    * **plot_star_system** — static Matplotlib orbital diagram of a
      single star system.
    * **plot_star_system_interactive** — interactive Plotly version with
      hover tooltips.
    * **plot_planet_statistics** — four-panel Matplotlib dashboard of
      population-level planet statistics.
    * **print_statistics** — console summary of key metrics.

    Parameters
    ----------
    systems_csv : str
        Path to the star-systems catalogue CSV file.
    planets_csv : str
        Path to the planets catalogue CSV file.
    """

    def __init__(self, systems_csv: str, planets_csv: str) -> None:
        if not os.path.exists(systems_csv):
            raise FileNotFoundError(
                f"Star-systems CSV not found: {systems_csv}"
            )
        if not os.path.exists(planets_csv):
            raise FileNotFoundError(
                f"Planets CSV not found: {planets_csv}"
            )
        self.systems_df: pd.DataFrame = pd.read_csv(systems_csv)
        self.planets_df: pd.DataFrame = pd.read_csv(planets_csv)

    # ------------------------------------------------------------------
    # Matplotlib — single star-system orbital diagram
    # ------------------------------------------------------------------

    def plot_star_system(
        self,
        star_id: str,
        output_dir: str = "datasets",
    ) -> None:
        """Render a static Matplotlib orbital diagram for one star system.

        The figure features a central star coloured by spectral type,
        concentric orbit rings, planet markers sized by radius and
        coloured by type, and a semi-transparent habitable-zone annulus.

        Parameters
        ----------
        star_id : str
            Unique star identifier (``star_id`` column) to visualise.
        output_dir : str
            Directory where ``sample_system.png`` will be written.
            Created automatically if it does not exist.
        """
        os.makedirs(output_dir, exist_ok=True)

        # --- Retrieve data ------------------------------------------------
        system_row = self.systems_df[
            self.systems_df["star_id"].astype(str) == str(star_id)
        ]
        if system_row.empty:
            raise ValueError(f"Star ID '{star_id}' not found in systems CSV.")
        system: pd.Series = system_row.iloc[0]

        planets = self.planets_df[
            self.planets_df["star_id"].astype(str) == str(star_id)
        ].copy()

        # --- Canvas setup -------------------------------------------------
        fig, ax = plt.subplots(figsize=(14, 14), facecolor=_SPACE_BG)
        ax.set_facecolor(_SPACE_BG)
        ax.set_aspect("equal")

        # --- Star glow & disc ---------------------------------------------
        star_color: str = SPECTRAL_COLORS.get(
            str(system["star_type"]).strip().upper(), "#ffffff"
        )
        # Outer glow
        glow = Circle(
            (0, 0), 0.12, color=star_color, alpha=0.15, zorder=5
        )
        ax.add_patch(glow)
        # Inner disc
        star_disc = Circle(
            (0, 0), 0.06, color=star_color, alpha=0.95, zorder=6
        )
        ax.add_patch(star_disc)

        # --- Habitable zone -----------------------------------------------
        hz_inner: float = float(system.get("habitable_zone_inner_au", 0.0))
        hz_outer: float = float(system.get("habitable_zone_outer_au", 0.0))
        if hz_outer > hz_inner > 0:
            hz_ring = Wedge(
                center=(0, 0),
                r=hz_outer,
                theta1=0,
                theta2=360,
                width=hz_outer - hz_inner,
                facecolor="#00ff00",
                alpha=0.08,
                edgecolor="#00ff00",
                linewidth=0.5,
                linestyle="--",
                zorder=2,
            )
            ax.add_patch(hz_ring)

        # --- Orbit rings & planets ----------------------------------------
        legend_types_seen: Dict[str, str] = {}
        max_orbit: float = 0.5  # minimum view radius in AU

        for _, planet in planets.iterrows():
            orbital_r: float = float(planet["orbital_distance_au"])
            if orbital_r > max_orbit:
                max_orbit = orbital_r

            # Dashed orbit circle
            orbit_circle = Circle(
                (0, 0),
                orbital_r,
                fill=False,
                edgecolor="#444444",
                linewidth=0.6,
                linestyle="--",
                alpha=0.5,
                zorder=1,
            )
            ax.add_patch(orbit_circle)

            # Planet position — spread planets evenly around their orbits
            # using a deterministic angle derived from the planet index
            planet_index = planet.name  # DataFrame row index
            angle = (hash(str(planet.get("planet_id", planet_index))) % 360) * (
                math.pi / 180.0
            )
            px_pos: float = orbital_r * math.cos(angle)
            py_pos: float = orbital_r * math.sin(angle)

            # Planet size (marker radius proportional to planet radius)
            p_radius: float = float(planet.get("radius", 1.0))
            marker_size: float = max(40.0, min(p_radius * 30.0, 500.0))

            # Planet colour from type string
            raw_type: str = str(planet.get("planet_type", "Rocky"))
            planet_type_label: str = self._normalise_planet_type(raw_type)
            p_color: str = PLANET_TYPE_COLORS.get(planet_type_label, "#CCCCCC")

            ax.scatter(
                px_pos,
                py_pos,
                s=marker_size,
                c=p_color,
                edgecolors="white",
                linewidths=0.4,
                alpha=0.9,
                zorder=7,
            )
            # Label
            ax.annotate(
                str(planet.get("planet_name", "")),
                (px_pos, py_pos),
                textcoords="offset points",
                xytext=(8, 8),
                fontsize=7,
                color="white",
                alpha=0.85,
                zorder=8,
            )
            legend_types_seen[planet_type_label] = p_color

        # --- Axis limits --------------------------------------------------
        margin: float = max_orbit * 0.25
        lim: float = max_orbit + margin
        ax.set_xlim(-lim, lim)
        ax.set_ylim(-lim, lim)

        # --- Title --------------------------------------------------------
        title_text = (
            f"{system['star_name']}  (Type {system['star_type']} — "
            f"M={float(system['star_mass']):.2f} M☉ — "
            f"T={float(system['star_temperature']):,.0f} K)\n"
            f"{len(planets)} planet(s)  |  "
            f"HZ {hz_inner:.2f}–{hz_outer:.2f} AU  |  "
            f"Region: {system['region']}"
        )
        ax.set_title(title_text, color="white", fontsize=13, pad=20)

        # --- Axes styling -------------------------------------------------
        ax.set_xlabel("Distance (AU)", color="gray", fontsize=11)
        ax.set_ylabel("Distance (AU)", color="gray", fontsize=11)
        ax.tick_params(colors="gray")
        ax.grid(True, color="#151525", linestyle="--", alpha=0.35)

        # --- Legend -------------------------------------------------------
        legend_handles = [
            mpatches.Patch(color=color, label=label)
            for label, color in legend_types_seen.items()
        ]
        if legend_handles:
            ax.legend(
                handles=legend_handles,
                loc="upper right",
                facecolor=_PANEL_BG,
                edgecolor="#22223b",
                labelcolor="white",
                fontsize=9,
                title="Planet Types",
                title_fontsize=10,
            )
            # Style the legend title text colour
            legend = ax.get_legend()
            if legend is not None:
                legend.get_title().set_color("white")

        # --- Save ---------------------------------------------------------
        save_path: str = os.path.join(output_dir, "sample_system.png")
        plt.tight_layout()
        plt.savefig(
            save_path,
            dpi=300,
            facecolor=fig.get_facecolor(),
            edgecolor="none",
        )
        plt.close()
        print(f"[SystemVisualizer] Saved static orbital map → {save_path}")

    # ------------------------------------------------------------------
    # Plotly — interactive single-system viewer
    # ------------------------------------------------------------------

    def plot_star_system_interactive(
        self,
        star_id: str,
        output_dir: str = "datasets",
    ) -> str:
        """Generate an interactive Plotly HTML viewer for a single star system.

        Includes hover tooltips with full planet properties, orbit circles,
        and a shaded habitable zone.

        Parameters
        ----------
        star_id : str
            Unique star identifier.
        output_dir : str
            Output directory for the HTML file.

        Returns
        -------
        str
            Absolute path to the saved HTML file.
        """
        os.makedirs(output_dir, exist_ok=True)

        # --- Retrieve data ------------------------------------------------
        system_row = self.systems_df[
            self.systems_df["star_id"].astype(str) == str(star_id)
        ]
        if system_row.empty:
            raise ValueError(f"Star ID '{star_id}' not found in systems CSV.")
        system: pd.Series = system_row.iloc[0]

        planets = self.planets_df[
            self.planets_df["star_id"].astype(str) == str(star_id)
        ].copy()

        star_color: str = SPECTRAL_COLORS.get(
            str(system["star_type"]).strip().upper(), "#ffffff"
        )
        hz_inner: float = float(system.get("habitable_zone_inner_au", 0.0))
        hz_outer: float = float(system.get("habitable_zone_outer_au", 0.0))

        fig = go.Figure()

        # --- Orbit circles ------------------------------------------------
        theta = np.linspace(0, 2 * np.pi, 200)
        for _, planet in planets.iterrows():
            r: float = float(planet["orbital_distance_au"])
            fig.add_trace(
                go.Scatter(
                    x=(r * np.cos(theta)).tolist(),
                    y=(r * np.sin(theta)).tolist(),
                    mode="lines",
                    line=dict(color="#444444", width=1, dash="dash"),
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        # --- Habitable zone (shaded annulus) ------------------------------
        if hz_outer > hz_inner > 0:
            # Outer boundary
            fig.add_trace(
                go.Scatter(
                    x=(hz_outer * np.cos(theta)).tolist(),
                    y=(hz_outer * np.sin(theta)).tolist(),
                    mode="lines",
                    line=dict(color="rgba(0,255,0,0.3)", width=1),
                    showlegend=False,
                    hoverinfo="skip",
                    fill=None,
                )
            )
            # Inner boundary with fill to outer
            fig.add_trace(
                go.Scatter(
                    x=(hz_inner * np.cos(theta)).tolist(),
                    y=(hz_inner * np.sin(theta)).tolist(),
                    mode="lines",
                    line=dict(color="rgba(0,255,0,0.3)", width=1),
                    fill="tonexty",
                    fillcolor="rgba(0,255,0,0.06)",
                    showlegend=False,
                    hoverinfo="skip",
                )
            )

        # --- Star marker --------------------------------------------------
        fig.add_trace(
            go.Scatter(
                x=[0],
                y=[0],
                mode="markers",
                marker=dict(
                    size=22,
                    color=star_color,
                    line=dict(width=0),
                    opacity=0.95,
                ),
                name=str(system["star_name"]),
                hovertext=(
                    f"<b>{system['star_name']}</b><br>"
                    f"Type: {system['star_type']}<br>"
                    f"Mass: {float(system['star_mass']):.2f} M☉<br>"
                    f"Temp: {float(system['star_temperature']):,.0f} K<br>"
                    f"Luminosity: {float(system['star_luminosity']):.4f} L☉<br>"
                    f"Region: {system['region']}"
                ),
                hoverinfo="text",
                showlegend=False,
            )
        )

        # --- Planets ------------------------------------------------------
        for _, planet in planets.iterrows():
            orbital_r = float(planet["orbital_distance_au"])
            angle = (hash(str(planet.get("planet_id", ""))) % 360) * (
                math.pi / 180.0
            )
            px_pos = orbital_r * math.cos(angle)
            py_pos = orbital_r * math.sin(angle)

            raw_type = str(planet.get("planet_type", "Rocky"))
            planet_type_label = self._normalise_planet_type(raw_type)
            p_color = PLANET_TYPE_COLORS.get(planet_type_label, "#CCCCCC")

            p_radius = float(planet.get("radius", 1.0))
            marker_size = max(8.0, min(p_radius * 6.0, 40.0))

            hover = (
                f"<b>{planet.get('planet_name', 'N/A')}</b><br>"
                f"Type: {planet_type_label}<br>"
                f"Mass: {float(planet.get('mass', 0)):.2f} M⊕<br>"
                f"Radius: {p_radius:.2f} R⊕<br>"
                f"Gravity: {float(planet.get('gravity', 0)):.2f} g<br>"
                f"Temperature: {float(planet.get('temperature', 0)):,.0f} K<br>"
                f"Habitability: {float(planet.get('habitability_score', 0)):.1f}<br>"
                f"Resources: {float(planet.get('resource_score', 0)):.1f}<br>"
                f"Water: {float(planet.get('water_percentage', 0)):.1f}%<br>"
                f"Atmosphere: {planet.get('atmosphere_type', 'N/A')}<br>"
                f"Orbit: {orbital_r:.2f} AU"
            )

            fig.add_trace(
                go.Scatter(
                    x=[px_pos],
                    y=[py_pos],
                    mode="markers+text",
                    marker=dict(
                        size=marker_size,
                        color=p_color,
                        line=dict(width=1, color="white"),
                        opacity=0.9,
                    ),
                    text=[str(planet.get("planet_name", ""))],
                    textposition="top center",
                    textfont=dict(color="white", size=9),
                    hovertext=hover,
                    hoverinfo="text",
                    showlegend=False,
                )
            )

        # --- Layout -------------------------------------------------------
        title_text = (
            f"{system['star_name']}  "
            f"(Type {system['star_type']}) — "
            f"{len(planets)} planet(s)"
        )
        fig.update_layout(
            title=dict(
                text=title_text,
                font=dict(family="Arial, sans-serif", size=18, color="white"),
                x=0.5,
                y=0.97,
            ),
            paper_bgcolor=_SPACE_BG,
            plot_bgcolor=_SPACE_BG,
            xaxis=dict(
                title=dict(
                    text="Distance (AU)",
                    font=dict(color="gray"),
                ),
                gridcolor="#151525",
                zerolinecolor="#151525",
                tickfont=dict(color="gray"),
                scaleanchor="y",
                scaleratio=1,
            ),
            yaxis=dict(
                title=dict(
                    text="Distance (AU)",
                    font=dict(color="gray"),
                ),
                gridcolor="#151525",
                zerolinecolor="#151525",
                tickfont=dict(color="gray"),
            ),
            margin=dict(l=60, r=30, b=60, t=60),
            showlegend=False,
        )

        save_path: str = os.path.join(output_dir, "sample_system.html")
        fig.write_html(save_path)
        print(
            f"[SystemVisualizer] Saved interactive system view → {save_path}"
        )
        return save_path

    # ------------------------------------------------------------------
    # Matplotlib — population-level statistics dashboard
    # ------------------------------------------------------------------

    def plot_planet_statistics(
        self,
        output_dir: str = "datasets",
    ) -> None:
        """Render a 2×2 Matplotlib dashboard of planet population statistics.

        Panels
        ------
        1. **Top-left** — Planet Type Distribution (bar chart).
        2. **Top-right** — Habitability Score Distribution (histogram).
        3. **Bottom-left** — Resource Score vs. Habitability Score (scatter).
        4. **Bottom-right** — Top-10 Most Habitable Planets (horizontal bar).

        Parameters
        ----------
        output_dir : str
            Directory where ``planet_statistics.png`` will be saved.
        """
        os.makedirs(output_dir, exist_ok=True)
        df: pd.DataFrame = self.planets_df.copy()

        # Normalise type labels for grouping
        df["planet_type_label"] = df["planet_type"].apply(
            self._normalise_planet_type
        )

        fig, axes = plt.subplots(
            2, 2, figsize=(18, 14), facecolor=_SPACE_BG
        )
        for ax_row in axes:
            for ax in ax_row:
                ax.set_facecolor(_PANEL_BG)
                ax.tick_params(colors="gray")

        # ---- Panel 1: Planet Type Distribution ---------------------------
        ax1 = axes[0, 0]
        type_counts: pd.Series = df["planet_type_label"].value_counts()
        # Reindex to a canonical order where possible
        canonical_order = [
            t for t in PLANET_TYPE_COLORS if t in type_counts.index
        ]
        extra = [t for t in type_counts.index if t not in canonical_order]
        ordered = canonical_order + extra
        type_counts = type_counts.reindex(ordered).dropna()

        bar_colors = [
            PLANET_TYPE_COLORS.get(t, "#CCCCCC") for t in type_counts.index
        ]
        bars = ax1.bar(
            type_counts.index,
            type_counts.values,
            color=bar_colors,
            edgecolor="none",
        )
        ax1.set_title(
            "Planet Type Distribution", color="white", fontsize=14, pad=12
        )
        ax1.set_ylabel("Count", color="gray", fontsize=11)
        ax1.set_xticks(range(len(type_counts.index)))
        ax1.set_xticklabels(
            type_counts.index, rotation=35, ha="right", fontsize=9
        )
        ax1.grid(True, axis="y", color="#151525", linestyle="--", alpha=0.5)
        for bar in bars:
            height = bar.get_height()
            ax1.annotate(
                f"{int(height)}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 4),
                textcoords="offset points",
                ha="center",
                va="bottom",
                color="gray",
                fontsize=9,
            )

        # ---- Panel 2: Habitability Score Distribution --------------------
        ax2 = axes[0, 1]
        hab_scores = df["habitability_score"].dropna()
        ax2.hist(
            hab_scores,
            bins=25,
            color="#00cc88",
            edgecolor="#030308",
            alpha=0.85,
        )
        ax2.set_title(
            "Habitability Score Distribution",
            color="white",
            fontsize=14,
            pad=12,
        )
        ax2.set_xlabel("Habitability Score", color="gray", fontsize=11)
        ax2.set_ylabel("Frequency", color="gray", fontsize=11)
        ax2.axvline(
            hab_scores.mean(),
            color="#ff6666",
            linestyle="--",
            linewidth=1.2,
            label=f"Mean = {hab_scores.mean():.1f}",
        )
        ax2.legend(
            facecolor=_PANEL_BG,
            edgecolor="#22223b",
            labelcolor="white",
            fontsize=9,
        )
        ax2.grid(True, axis="y", color="#151525", linestyle="--", alpha=0.5)

        # ---- Panel 3: Resource vs. Habitability --------------------------
        ax3 = axes[1, 0]
        unique_types = df["planet_type_label"].unique()
        for ptype in unique_types:
            subset = df[df["planet_type_label"] == ptype]
            color = PLANET_TYPE_COLORS.get(ptype, "#CCCCCC")
            ax3.scatter(
                subset["habitability_score"],
                subset["resource_score"],
                c=color,
                label=ptype,
                alpha=0.7,
                s=25,
                edgecolors="none",
            )
        ax3.set_title(
            "Resource Score vs. Habitability Score",
            color="white",
            fontsize=14,
            pad=12,
        )
        ax3.set_xlabel("Habitability Score", color="gray", fontsize=11)
        ax3.set_ylabel("Resource Score", color="gray", fontsize=11)
        ax3.legend(
            facecolor=_PANEL_BG,
            edgecolor="#22223b",
            labelcolor="white",
            fontsize=8,
            loc="upper left",
            ncol=2,
        )
        ax3.grid(True, color="#151525", linestyle="--", alpha=0.5)

        # ---- Panel 4: Top 10 Most Habitable Planets ----------------------
        ax4 = axes[1, 1]
        top_hab = df.nlargest(10, "habitability_score")
        top_colors = [
            PLANET_TYPE_COLORS.get(t, "#CCCCCC")
            for t in top_hab["planet_type_label"]
        ]
        ax4.barh(
            top_hab["planet_name"],
            top_hab["habitability_score"],
            color=top_colors,
            edgecolor="none",
        )
        ax4.set_title(
            "Top 10 Most Habitable Planets",
            color="white",
            fontsize=14,
            pad=12,
        )
        ax4.set_xlabel("Habitability Score", color="gray", fontsize=11)
        ax4.invert_yaxis()  # highest on top
        ax4.grid(True, axis="x", color="#151525", linestyle="--", alpha=0.5)

        # ---- Global styling & save ---------------------------------------
        fig.suptitle(
            "The Galactic Dream Engine — Planet Population Statistics",
            color="white",
            fontsize=18,
            y=0.99,
        )
        plt.tight_layout(rect=[0, 0, 1, 0.96])
        save_path: str = os.path.join(output_dir, "planet_statistics.png")
        plt.savefig(
            save_path,
            dpi=150,
            facecolor=fig.get_facecolor(),
            edgecolor="none",
        )
        plt.close()
        print(
            f"[SystemVisualizer] Saved statistics dashboard → {save_path}"
        )

    # ------------------------------------------------------------------
    # Console statistics summary
    # ------------------------------------------------------------------

    def print_statistics(self) -> None:
        """Print a formatted console summary of the planet population.

        Includes total count, type distribution with percentages, average
        habitability and resource scores, and the single most habitable
        planet.
        """
        df: pd.DataFrame = self.planets_df.copy()
        total: int = len(df)

        df["planet_type_label"] = df["planet_type"].apply(
            self._normalise_planet_type
        )

        print()
        print("=" * 55)
        print("     GALACTIC DREAM ENGINE — PLANET STATISTICS")
        print("=" * 55)

        # Total
        print(f"\n  Total Planets Generated : {total}")

        # Type distribution
        print("\n  Planet Type Distribution:")
        type_counts: pd.Series = df["planet_type_label"].value_counts()
        for ptype, count in type_counts.items():
            pct: float = (count / total) * 100.0 if total > 0 else 0.0
            print(f"    {ptype:15s} : {count:4d}  ({pct:5.1f}%)")

        # Habitability
        avg_hab: float = float(df["habitability_score"].mean()) if total > 0 else 0.0
        print(f"\n  Avg Habitability Score  : {avg_hab:.2f}")

        # Most habitable
        if total > 0:
            best_idx = df["habitability_score"].idxmax()
            best = df.loc[best_idx]
            best_star_name = self._lookup_star_name(
                str(best["star_id"])
            )
            print(
                f"  Most Habitable Planet  : {best['planet_name']} "
                f"(score {float(best['habitability_score']):.1f}, "
                f"star: {best_star_name})"
            )

        # Resources
        avg_res: float = float(df["resource_score"].mean()) if total > 0 else 0.0
        print(f"\n  Avg Resource Score     : {avg_res:.2f}")

        print("\n  Resource Distribution Summary:")
        if total > 0:
            res = df["resource_score"]
            print(f"    Min    : {res.min():.2f}")
            print(f"    Median : {res.median():.2f}")
            print(f"    Max    : {res.max():.2f}")
            print(f"    Std    : {res.std():.2f}")

        print("=" * 55)
        print()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise_planet_type(raw: str) -> str:
        """Map CSV planet-type strings to canonical display labels.

        Handles both enum-value style (``'Rocky'``) and upper-snake-case
        style (``'ROCKY'``, ``'GAS_GIANT'``) found in CSV exports.

        Parameters
        ----------
        raw : str
            Raw type string from the CSV.

        Returns
        -------
        str
            Canonical display label matching the keys in
            :data:`PLANET_TYPE_COLORS`.
        """
        mapping: Dict[str, str] = {
            "ROCKY":       "Rocky",
            "OCEAN":       "Ocean",
            "ICE":         "Ice",
            "DESERT":      "Desert",
            "GAS_GIANT":   "Gas Giant",
            "GASGIANT":    "Gas Giant",
            "GAS GIANT":   "Gas Giant",
            "LAVA_WORLD":  "Lava World",
            "LAVAWORLD":   "Lava World",
            "LAVA WORLD":  "Lava World",
            "TOXIC_WORLD": "Toxic World",
            "TOXICWORLD":  "Toxic World",
            "TOXIC WORLD": "Toxic World",
            "SUPER_EARTH": "Super Earth",
            "SUPEREARTH":  "Super Earth",
            "SUPER EARTH": "Super Earth",
        }
        cleaned = str(raw).strip()
        # Try upper-case lookup first
        result = mapping.get(cleaned.upper())
        if result is not None:
            return result
        # Already in display form?
        if cleaned in PLANET_TYPE_COLORS:
            return cleaned
        # Fallback — title-case the raw string
        return cleaned.title()

    def _lookup_star_name(self, star_id: str) -> str:
        """Return the star name for a given star_id, or the id itself."""
        match = self.systems_df[
            self.systems_df["star_id"].astype(str) == star_id
        ]
        if not match.empty:
            return str(match.iloc[0]["star_name"])
        return star_id


# ---------------------------------------------------------------------------
# Standalone test entry-point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    systems_csv = os.path.join("datasets", "star_systems.csv")
    planets_csv = os.path.join("datasets", "planets.csv")

    if not os.path.exists(systems_csv) or not os.path.exists(planets_csv):
        print(
            "Run the planet generation pipeline first to produce "
            "star_systems.csv and planets.csv.",
            file=sys.stderr,
        )
        sys.exit(1)

    viz = SystemVisualizer(systems_csv, planets_csv)
    viz.print_statistics()

    # Pick the first star for a demo plot
    first_star_id = str(viz.systems_df.iloc[0]["star_id"])
    viz.plot_star_system(first_star_id)
    viz.plot_star_system_interactive(first_star_id)
    viz.plot_planet_statistics()
