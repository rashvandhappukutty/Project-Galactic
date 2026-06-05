"""
decision_visualizer.py — Visualization engine for Phase 5 AI Decision Engine.

Generates dark space-themed dashboards and interactive timeline reports.
"""

import os
from typing import Dict, List, Any
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px


class DecisionVisualizer:
    """Generates space-themed matplotlib charts and interactive Plotly visualization reports."""

    def __init__(
        self,
        decisions_csv: str,
        threat_csv: str,
        opportunity_csv: str,
        megastructures_csv: str,
    ) -> None:
        self.decisions_csv = decisions_csv
        self.threat_csv = threat_csv
        self.opportunity_csv = opportunity_csv
        self.megastructures_csv = megastructures_csv

        # Color configurations for dark space theme
        self.bg_color = "#030308"
        self.grid_color = "#222233"
        self.spine_color = "#444455"
        self.text_color = "#cccccc"
        self.header_color = "#ffffff"

        # Action Colors
        self.action_colors = {
            "EXPAND": "#00ffcc",             # Cyan
            "COLONIZE": "#3399ff",           # Ocean Blue
            "RESEARCH": "#cc33ff",           # Purple
            "TRADE": "#66ff66",              # Light Green
            "ALLY": "#ff99ff",               # Pink
            "DEFEND": "#ffcc00",             # Gold
            "ATTACK": "#ff3333",             # Red
            "BUILD_MEGASTRUCTURE": "#ff9933", # Orange
            "EXPLORE": "#00ffff",            # Bright Cyan
            "ISOLATE": "#777788",            # Muted Grey
        }

        # Personality Colors
        self.personality_colors = {
            "Militaristic": "#ff3333",
            "Diplomatic": "#ff99ff",
            "Scientific": "#cc33ff",
            "Isolationist": "#777788",
            "Expansionist": "#3399ff",
            "Explorer": "#00ffff",
            "Industrialist": "#ff9933",
        }

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

    def plot_decision_distribution(self, output_dir: str = "datasets") -> None:
        """Create bar chart of strategic action frequencies."""
        os.makedirs(output_dir, exist_ok=True)
        df = pd.read_csv(self.decisions_csv)

        if df.empty:
            return

        action_counts = df["decision"].value_counts()
        labels = list(action_counts.index)
        counts = list(action_counts.values)
        colors = [self.action_colors.get(a, "#ffffff") for a in labels]

        fig, ax = plt.subplots(figsize=(10, 6), facecolor=self.bg_color)
        self._apply_dark_theme(fig, ax)

        bars = ax.bar(labels, counts, color=colors, edgecolor=self.spine_color, width=0.55)
        ax.set_ylabel("Decision Count", fontsize=11, color=self.text_color)
        ax.set_title("Strategic Action Distribution", fontsize=14, pad=15)
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

        plt.xticks(rotation=25, ha="right")
        plt.tight_layout()
        save_path = os.path.join(output_dir, "decision_distribution.png")
        plt.savefig(save_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_civilization_personalities(self, output_dir: str = "datasets") -> None:
        """Create bar chart of civilization personality distributions."""
        os.makedirs(output_dir, exist_ok=True)
        # Load threat or opportunity logs and slice tick=1 to get unique agent personalities
        df = pd.read_csv(self.threat_csv)
        if df.empty or "personality" not in df.columns:
            return

        unique_agents = df[df["tick"] == 1].drop_duplicates(subset=["civilization_id"])
        p_counts = unique_agents["personality"].value_counts()
        labels = list(p_counts.index)
        counts = list(p_counts.values)
        colors = [self.personality_colors.get(p, "#ffffff") for p in labels]

        fig, ax = plt.subplots(figsize=(10, 6), facecolor=self.bg_color)
        self._apply_dark_theme(fig, ax)

        bars = ax.bar(labels, counts, color=colors, edgecolor=self.spine_color, width=0.55)
        ax.set_ylabel("Agent Count", fontsize=11, color=self.text_color)
        ax.set_title("Civilization Agent Personalities", fontsize=14, pad=15)
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
        save_path = os.path.join(output_dir, "civilization_personalities.png")
        plt.savefig(save_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_threat_vs_opportunity(self, output_dir: str = "datasets") -> None:
        """Create scatter plot of Threat Score vs Opportunity Score for all agents."""
        os.makedirs(output_dir, exist_ok=True)
        threat_df = pd.read_csv(self.threat_csv)
        opp_df = pd.read_csv(self.opportunity_csv)

        if threat_df.empty or opp_df.empty:
            return

        # Use final tick
        final_tick = threat_df["tick"].max()
        final_threats = threat_df[threat_df["tick"] == final_tick]
        final_opps = opp_df[opp_df["tick"] == final_tick]

        merged = pd.merge(
            final_threats[["civilization_id", "civilization_name", "personality", "threat_score"]],
            final_opps[["civilization_id", "opportunity_score"]],
            on="civilization_id"
        )

        if merged.empty:
            return

        fig, ax = plt.subplots(figsize=(10, 7), facecolor=self.bg_color)
        self._apply_dark_theme(fig, ax)
        ax.grid(True, linestyle="--", alpha=0.1, color="#888888")

        # Scatter by personality type
        for p_type, group in merged.groupby("personality"):
            color = self.personality_colors.get(p_type, "#ffffff")
            ax.scatter(
                group["opportunity_score"],
                group["threat_score"],
                label=p_type,
                color=color,
                alpha=0.75,
                s=45,
                edgecolors="#111111",
                linewidths=0.5
            )

        ax.set_xlabel("Opportunity Score (0-100)", fontsize=11, color=self.text_color)
        ax.set_ylabel("Threat Score (0-100)", fontsize=11, color=self.text_color)
        ax.set_title(f"Threat vs Opportunity Space Mapping (Tick {final_tick})", fontsize=14, pad=15)
        ax.legend(
            facecolor=self.bg_color,
            edgecolor=self.spine_color,
            fontsize=9,
            labelcolor=self.text_color,
            loc="upper right"
        )

        plt.tight_layout()
        save_path = os.path.join(output_dir, "threat_vs_opportunity.png")
        plt.savefig(save_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_megastructure_progress(self, output_dir: str = "datasets") -> None:
        """Create horizontal bar chart of megastructures construction progress."""
        os.makedirs(output_dir, exist_ok=True)
        df = pd.read_csv(self.megastructures_csv)

        if df.empty:
            # Generate blank fallback
            fig, ax = plt.subplots(figsize=(10, 6), facecolor=self.bg_color)
            self._apply_dark_theme(fig, ax)
            ax.text(0.5, 0.5, "No megastructures constructed yet.", ha="center", va="center", color=self.text_color)
            ax.axis("off")
            plt.savefig(os.path.join(output_dir, "megastructure_progress.png"), dpi=150, facecolor=fig.get_facecolor())
            plt.close()
            return

        # Sort and select top 15 by progress/status
        df_sorted = df.sort_values(by=["construction_progress"], ascending=True).tail(15)

        fig, ax = plt.subplots(figsize=(10, 7), facecolor=self.bg_color)
        self._apply_dark_theme(fig, ax)
        ax.grid(True, axis="x", linestyle="--", alpha=0.1, color="#888888")

        # Color by completion status
        colors = ["#ff9933" if status == "Complete" else "#3399ff" for status in df_sorted["status"]]

        y_labels = [f"{row['civilization_name']} ({row['megastructure_type']})" for _, row in df_sorted.iterrows()]

        bars = ax.barh(y_labels, df_sorted["construction_progress"], color=colors, edgecolor=self.spine_color, height=0.55)
        ax.set_xlabel("Construction Progress (%)", fontsize=11, color=self.text_color)
        ax.set_title("Megastructures Engineering Progress Registry (Top 15)", fontsize=14, pad=15)
        ax.set_xlim(0, 105)

        # Label bars
        for bar in bars:
            width = bar.get_width()
            ax.annotate(
                f"{width:.1f}%",
                xy=(width, bar.get_y() + bar.get_height() / 2),
                xytext=(5, 0),
                textcoords="offset points",
                ha="left",
                va="center",
                color="#ffffff",
                fontsize=8,
            )

        plt.tight_layout()
        save_path = os.path.join(output_dir, "megastructure_progress.png")
        plt.savefig(save_path, dpi=150, facecolor=fig.get_facecolor(), bbox_inches="tight")
        plt.close()

    def plot_decision_timeline(self, output_dir: str = "datasets") -> None:
        """Create interactive Plotly HTML visualization of key decisions over ticks."""
        os.makedirs(output_dir, exist_ok=True)
        df = pd.read_csv(self.decisions_csv)

        if df.empty:
            # blank html
            with open(os.path.join(output_dir, "decision_timeline.html"), "w", encoding="utf-8") as f:
                f.write("<html><body><h1>No Decision Logs to Plot</h1></body></html>")
            return

        # Focus on major actions to keep plot readable (ATTACK, BUILD_MEGASTRUCTURE, ALLY, COLONIZE)
        major_actions = ["ATTACK", "BUILD_MEGASTRUCTURE", "ALLY", "COLONIZE"]
        df_filtered = df[df["decision"].isin(major_actions)].copy()

        # If filtered set is too small, fallback to all decisions
        if len(df_filtered) < 10:
            df_filtered = df.copy()

        # Let's display the top 30 most active civilizations to prevent timeline clutter
        active_civs = df_filtered["civilization_name"].value_counts().head(30).index
        df_filtered = df_filtered[df_filtered["civilization_name"].isin(active_civs)]

        fig_plotly = px.scatter(
            df_filtered,
            x="tick",
            y="civilization_name",
            color="decision",
            hover_name="civilization_name",
            hover_data={
                "tick": True,
                "decision": True,
                "reason": True,
                "result": True,
            },
            title="Strategic Decisions Timeline (Top Civilizations)",
            color_discrete_map=self.action_colors,
        )

        fig_plotly.update_layout(
            template="plotly_dark",
            paper_bgcolor=self.bg_color,
            plot_bgcolor=self.bg_color,
            xaxis=dict(gridcolor=self.grid_color, title="Simulation Tick (1 tick = 100 years)"),
            yaxis=dict(gridcolor=self.grid_color, title="Civilization Name"),
            title_font_color="#ffffff",
            legend_title_font_color="#ffffff",
        )

        # Update marker size
        fig_plotly.update_traces(marker=dict(size=12, symbol="diamond"))

        save_path = os.path.join(output_dir, "decision_timeline.html")
        fig_plotly.write_html(save_path)
