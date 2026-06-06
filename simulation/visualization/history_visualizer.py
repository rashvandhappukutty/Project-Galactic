# simulation/visualization/history_visualizer.py
"""Historical Conflict and Timeline Visualizer.
Generates PNG dashboards and interactive Plotly timelines.
"""

from __future__ import annotations
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.express as px
from typing import Dict, Any
from ..utils import logger, ensure_dir

class HistoryVisualizer:
    """Renders charts and dashboards for the galactic history."""

    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = datasets_dir
        # Modern color palette
        plt.style.use("ggplot")
        self.colors = ["#2980b9", "#27ae60", "#8e44ad", "#e67e22", "#c0392b", "#16a085", "#2c3e50", "#f39c12"]

    def generate_all_visuals(self) -> None:
        """Executes all visualization rendering subroutines."""
        logger.info("Generating historical visualizations...")
        
        # Load master CSV
        master_path = os.path.join(self.datasets_dir, "galactic_history_master.csv")
        if not os.path.exists(master_path):
            logger.error("Master history file not found. Cannot render visualizations.")
            return

        df = pd.read_csv(master_path)
        if df.empty:
            logger.warning("Master history file is empty. Skipping visual rendering.")
            return

        self._plot_plotly_timeline(df)
        self._plot_era_distribution()
        self._plot_empire_rise_fall()
        self._plot_legendary_events_dashboard()
        self._plot_historical_heatmap(df)
        self._plot_civilization_lifecycle()
        self._plot_historical_significance(df)

    def _plot_plotly_timeline(self, df: pd.DataFrame) -> None:
        """Generates galactic_history_timeline.html (interactive Plotly scatter)."""
        try:
            # Filter to top 500 significant events to avoid browser sluggishness
            plot_df = df.sort_values(by="impact_score", ascending=False).head(500)
            
            fig = px.scatter(
                plot_df,
                x="year",
                y="impact_score",
                color="event_category",
                size="impact_score",
                hover_name="event_type",
                hover_data=["empire", "participants", "location", "description"],
                title="Galactic History Timeline (Top 500 Events)",
                labels={"year": "Galactic Year", "impact_score": "Historical Significance Score (0-100)"},
                color_discrete_sequence=self.colors
            )
            fig.update_layout(
                plot_bgcolor="rgba(24, 28, 36, 1)",
                paper_bgcolor="rgba(24, 28, 36, 1)",
                font_color="white",
                xaxis=dict(showgrid=True, gridcolor="gray"),
                yaxis=dict(showgrid=True, gridcolor="gray")
            )
            out_path = os.path.join(self.datasets_dir, "galactic_history_timeline.html")
            fig.write_html(out_path)
            logger.info(f"Saved interactive timeline to {out_path}")
        except Exception as e:
            logger.error(f"Error rendering Plotly timeline: {e}")

    def _plot_era_distribution(self) -> None:
        """Generates era_distribution.png (pie chart of era duration ratio)."""
        try:
            eras_path = os.path.join(self.datasets_dir, "era_history.csv")
            if not os.path.exists(eras_path):
                return
            df = pd.read_csv(eras_path)
            if df.empty:
                return

            df["duration"] = df["end_year"] - df["start_year"]
            
            plt.figure(figsize=(10, 6))
            plt.pie(
                df["duration"],
                labels=df["era_name"],
                autopct="%1.1f%%",
                colors=self.colors[:len(df)],
                startangle=140,
                textprops={'fontsize': 12, 'color': 'black'}
            )
            plt.title("Distribution of Galactic Epochs (Duration Ratio)", fontsize=14, fontweight="bold", color="#2c3e50")
            plt.tight_layout()
            
            out_path = os.path.join(self.datasets_dir, "era_distribution.png")
            plt.savefig(out_path, dpi=150)
            plt.close()
            logger.info(f"Saved era distribution to {out_path}")
        except Exception as e:
            logger.error(f"Error rendering era distribution: {e}")

    def _plot_empire_rise_fall(self) -> None:
        """Generates empire_rise_fall.png (tracks empire GDP lifecycle paths)."""
        try:
            lc_path = os.path.join(self.datasets_dir, "empire_lifecycles.csv")
            if not os.path.exists(lc_path):
                return
            df = pd.read_csv(lc_path)
            if df.empty:
                return

            plt.figure(figsize=(12, 6))
            # Track top 6 empires by peak GDP
            top_empires = df.groupby("empire_name")["gdp"].max().nlargest(6).index
            
            for idx, emp in enumerate(top_empires):
                emp_df = df[df["empire_name"] == emp].sort_values(by="year")
                plt.plot(
                    emp_df["year"],
                    emp_df["gdp"],
                    label=emp,
                    marker="o",
                    color=self.colors[idx % len(self.colors)],
                    linewidth=2
                )

            plt.title("Civilization Rise & Fall (GDP Lifecycle)", fontsize=14, fontweight="bold", color="#2c3e50")
            plt.xlabel("Galactic Year", fontsize=12)
            plt.ylabel("GDP (Credits)", fontsize=12)
            plt.legend(loc="upper left")
            plt.grid(True)
            plt.tight_layout()
            
            out_path = os.path.join(self.datasets_dir, "empire_rise_fall.png")
            plt.savefig(out_path, dpi=150)
            plt.close()
            logger.info(f"Saved rise & fall GDP curve to {out_path}")
        except Exception as e:
            logger.error(f"Error rendering rise/fall curves: {e}")

    def _plot_legendary_events_dashboard(self) -> None:
        """Generates legendary_events_dashboard.png (an infographic scorecard)."""
        try:
            leg_path = os.path.join(self.datasets_dir, "legendary_events.csv")
            if not os.path.exists(leg_path):
                return
            df = pd.read_csv(leg_path)
            if df.empty:
                return

            fig, ax = plt.subplots(figsize=(12, 8))
            ax.axis('off')
            
            fig.patch.set_facecolor("#181c24")
            ax.set_facecolor("#181c24")

            title_text = "GALACTIC LEGENDARY ACHIEVEMENTS DASHBOARD"
            plt.text(0.5, 0.95, title_text, transform=ax.transAxes, fontsize=16, fontweight="bold", color="#f39c12", ha="center")

            # Render cards
            y_pos = 0.80
            for _, row in df.head(7).iterrows():
                card_title = f"{row['legendary_type']} - Year {row['year']} (Impact: {row['impact_score']:.1f})"
                card_body = f"Empire: {row['empire_involved']}\n{row['description']}"
                
                # Title
                plt.text(0.05, y_pos, card_title, transform=ax.transAxes, fontsize=11, fontweight="bold", color="#3498db")
                # Body
                plt.text(0.05, y_pos - 0.06, card_body, transform=ax.transAxes, fontsize=9, color="white", wrap=True)
                
                y_pos -= 0.11

            plt.tight_layout()
            out_path = os.path.join(self.datasets_dir, "legendary_events_dashboard.png")
            plt.savefig(out_path, dpi=150, facecolor=fig.get_facecolor(), edgecolor='none')
            plt.close()
            logger.info(f"Saved legendary achievements to {out_path}")
        except Exception as e:
            logger.error(f"Error rendering legendary events dashboard: {e}")

    def _plot_historical_heatmap(self, df: pd.DataFrame) -> None:
        """Generates historical_heatmap.png (event category density matrix)."""
        try:
            # Bin years into 10 intervals
            df = df.copy()
            bins = np.linspace(df["year"].min(), df["year"].max(), 11)
            labels = [f"Yr {int(bins[i])}-{int(bins[i+1])}" for i in range(10)]
            df["year_group"] = pd.cut(df["year"], bins=bins, labels=labels, include_lowest=True)

            pivot_table = df.pivot_table(
                index="event_category",
                columns="year_group",
                values="impact_score",
                aggfunc="count",
                fill_value=0
            )

            fig, ax = plt.subplots(figsize=(12, 6))
            cax = ax.imshow(pivot_table.values, cmap="YlOrRd", aspect="auto")
            fig.colorbar(cax, label="Event Count")

            ax.set_yticks(np.arange(len(pivot_table.index)))
            ax.set_yticklabels(pivot_table.index, fontsize=10)
            ax.set_xticks(np.arange(len(pivot_table.columns)))
            ax.set_xticklabels(pivot_table.columns, rotation=45, ha="right", fontsize=9)

            ax.set_title("Galactic History Event Density Heatmap", fontsize=14, fontweight="bold", color="#2c3e50")
            plt.tight_layout()

            out_path = os.path.join(self.datasets_dir, "historical_heatmap.png")
            plt.savefig(out_path, dpi=150)
            plt.close()
            logger.info(f"Saved event density heatmap to {out_path}")
        except Exception as e:
            logger.error(f"Error rendering heatmap: {e}")

    def _plot_civilization_lifecycle(self) -> None:
        """Generates civilization_lifecycle.png (Gantt-like status timeline)."""
        try:
            lc_path = os.path.join(self.datasets_dir, "empire_lifecycles.csv")
            if not os.path.exists(lc_path):
                return
            df = pd.read_csv(lc_path)
            if df.empty:
                return

            # Plot distribution of states
            plt.figure(figsize=(10, 6))
            state_counts = df["status"].value_counts()
            
            plt.bar(
                state_counts.index,
                state_counts.values,
                color=self.colors[:len(state_counts)],
                edgecolor="black",
                alpha=0.8
            )
            plt.title("Distribution of Civilizational Lifecycle Transitions", fontsize=14, fontweight="bold", color="#2c3e50")
            plt.xlabel("Lifecycle State", fontsize=12)
            plt.ylabel("Transition Event Count", fontsize=12)
            plt.tight_layout()

            out_path = os.path.join(self.datasets_dir, "civilization_lifecycle.png")
            plt.savefig(out_path, dpi=150)
            plt.close()
            logger.info(f"Saved lifecycle state distribution chart to {out_path}")
        except Exception as e:
            logger.error(f"Error rendering lifecycle chart: {e}")

    def _plot_historical_significance(self, df: pd.DataFrame) -> None:
        """Generates historical_significance.png (impact score bar chart)."""
        try:
            # Average impact score per category
            grouped = df.groupby("event_category")["impact_score"].mean().sort_values(ascending=False)

            plt.figure(figsize=(10, 6))
            plt.barh(
                grouped.index,
                grouped.values,
                color="#e74c3c",
                edgecolor="black",
                height=0.6,
                alpha=0.8
            )
            plt.title("Mean Historical Impact Score by Category", fontsize=14, fontweight="bold", color="#2c3e50")
            plt.xlabel("Mean Significance Score (0-100)", fontsize=12)
            plt.ylabel("Event Category", fontsize=12)
            plt.grid(True, axis="x")
            plt.tight_layout()

            out_path = os.path.join(self.datasets_dir, "historical_significance.png")
            plt.savefig(out_path, dpi=150)
            plt.close()
            logger.info(f"Saved impact score analysis to {out_path}")
        except Exception as e:
            logger.error(f"Error rendering significance visual: {e}")
