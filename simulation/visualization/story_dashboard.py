# simulation/visualization/story_dashboard.py
"""Storytelling Visualizer and HTML Dashboard Engine.
Renders Plotly timelines, news dashboards, and Matplotlib figure reports.
"""

from __future__ import annotations
import os
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
from typing import Dict, Any
from ..utils import logger, ensure_dir

class StoryDashboard:
    """Generates visual assets and web dashboards for Phase 11 lore databases."""

    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = datasets_dir
        plt.style.use("ggplot")
        self.colors = ["#3498db", "#2ecc71", "#9b59b6", "#e67e22", "#e74c3c", "#1abc9c", "#34495e"]

    def generate_all_dashboards(self) -> None:
        """Runs the entire story dashboard drawing subroutines."""
        logger.info("Generating storytelling dashboards...")
        
        # Load necessary data
        figures_path = os.path.join(self.datasets_dir, "historical_figures.csv")
        news_path = os.path.join(self.datasets_dir, "galactic_news.csv")
        chronicles_path = os.path.join(self.datasets_dir, "empire_chronicles.csv")
        legendary_path = os.path.join(self.datasets_dir, "legendary_stories.csv")

        df_fig = pd.read_csv(figures_path) if os.path.exists(figures_path) else pd.DataFrame()
        df_news = pd.read_csv(news_path) if os.path.exists(news_path) else pd.DataFrame()
        df_chron = pd.read_csv(chronicles_path) if os.path.exists(chronicles_path) else pd.DataFrame()
        df_leg = pd.read_csv(legendary_path) if os.path.exists(legendary_path) else pd.DataFrame()

        self._plot_legendary_timeline(df_leg)
        self._plot_empire_chronicles_png(df_chron)
        self._plot_historical_figures_png(df_fig)
        self._generate_story_dashboard_html(df_chron, df_fig)
        self._generate_news_dashboard_html(df_news)

    def _plot_legendary_timeline(self, df: pd.DataFrame) -> None:
        """Generates legendary_events_timeline.html (interactive Plotly timeline)."""
        try:
            if df.empty:
                return
            fig = px.scatter(
                df,
                x="year",
                y="impact_score",
                color="legendary_type",
                size="impact_score",
                hover_name="legendary_type",
                hover_data=["empire_involved", "description", "prose_narrative"],
                title="Galactic Timeline of Legendary Achievements",
                labels={"year": "Galactic Year", "impact_score": "Impact Score"},
                color_discrete_sequence=self.colors
            )
            fig.update_layout(
                plot_bgcolor="rgba(24, 28, 36, 1)",
                paper_bgcolor="rgba(24, 28, 36, 1)",
                font_color="white"
            )
            out_path = os.path.join(self.datasets_dir, "legendary_events_timeline.html")
            fig.write_html(out_path)
            logger.info(f"Saved interactive legendary timeline to {out_path}")
        except Exception as e:
            logger.error(f"Error rendering legendary timeline HTML: {e}")

    def _plot_empire_chronicles_png(self, df: pd.DataFrame) -> None:
        """Generates empire_chronicles.png (Matplotlib report chart)."""
        try:
            if df.empty:
                return
            # Plot length of chronicles as a proxy for lore depth
            df["chronicle_length"] = df["origin_story"].str.len() + df["expansion_era"].str.len() + df["golden_age"].str.len()

            plt.figure(figsize=(10, 6))
            # Sort and plot top 10
            top_df = df.sort_values(by="chronicle_length", ascending=False).head(10)
            
            plt.barh(
                top_df["empire_name"],
                top_df["chronicle_length"],
                color="#3498db",
                edgecolor="black",
                height=0.6,
                alpha=0.8
            )
            plt.title("Narrative Chronicle Depth of Major Empires", fontsize=14, fontweight="bold", color="#2c3e50")
            plt.xlabel("Total Chronicle String Length (Characters)", fontsize=12)
            plt.ylabel("Empire", fontsize=12)
            plt.grid(True, axis="x")
            plt.tight_layout()

            out_path = os.path.join(self.datasets_dir, "empire_chronicles.png")
            plt.savefig(out_path, dpi=150)
            plt.close()
            logger.info(f"Saved chronicles chart to {out_path}")
        except Exception as e:
            logger.error(f"Error rendering chronicles chart: {e}")

    def _plot_historical_figures_png(self, df: pd.DataFrame) -> None:
        """Generates historical_figures.png (Matplotlib report chart)."""
        try:
            if df.empty:
                return
            # Plot distribution of characters by role and average legacy score
            grouped = df.groupby("role")["legacy_score"].mean().sort_values(ascending=False)

            plt.figure(figsize=(10, 6))
            plt.bar(
                grouped.index,
                grouped.values,
                color="#e67e22",
                edgecolor="black",
                width=0.5,
                alpha=0.8
            )
            plt.title("Average Legacy Score of Historical Figures by Role", fontsize=14, fontweight="bold", color="#2c3e50")
            plt.xlabel("Role", fontsize=12)
            plt.ylabel("Mean Legacy Score", fontsize=12)
            plt.grid(True, axis="y")
            plt.tight_layout()

            out_path = os.path.join(self.datasets_dir, "historical_figures.png")
            plt.savefig(out_path, dpi=150)
            plt.close()
            logger.info(f"Saved historical figures report to {out_path}")
        except Exception as e:
            logger.error(f"Error rendering figures chart: {e}")

    def _generate_story_dashboard_html(self, df_chron: pd.DataFrame, df_fig: pd.DataFrame) -> None:
        """Generates story_dashboard.html listing books, figures, and chronicles."""
        try:
            out_path = os.path.join(self.datasets_dir, "story_dashboard.html")
            
            # Simple bootstrap-styled card layouts
            fig_rows = ""
            for _, row in df_fig.head(15).iterrows():
                fig_rows += f"""
                <div class="col-md-4 mb-3">
                    <div class="card bg-dark text-white border-primary">
                        <div class="card-body">
                            <h5 class="card-title text-primary">{row['name']}</h5>
                            <h6 class="card-subtitle mb-2 text-muted">{row['role']} ({row['civilization']})</h6>
                            <p class="card-text">{row['achievements']}</p>
                            <span class="badge bg-warning text-dark">Legacy Score: {row['legacy_score']}</span>
                        </div>
                    </div>
                </div>
                """

            chron_rows = ""
            for _, row in df_chron.head(5).iterrows():
                chron_rows += f"""
                <div class="accordion-item bg-dark text-white border-secondary">
                    <h2 class="accordion-header" id="heading_{row['empire_id']}">
                        <button class="accordion-button collapsed bg-dark text-primary" type="button" data-bs-toggle="collapse" data-bs-target="#collapse_{row['empire_id']}">
                            <strong>{row['empire_name']} Chronicles</strong>
                        </button>
                    </h2>
                    <div id="collapse_{row['empire_id']}" class="accordion-collapse collapse" data-bs-parent="#chroniclesAccordion">
                        <div class="accordion-body">
                            <p><strong>Origin Story:</strong> {row['origin_story']}</p>
                            <p><strong>Expansion:</strong> {row['expansion_era']}</p>
                            <p><strong>Golden Age:</strong> {row['golden_age']}</p>
                            <p><strong>Major Wars:</strong> {row['major_wars']}</p>
                            <p><strong>Peak:</strong> {row['peak_influence']}</p>
                            <p><strong>Legacy:</strong> {row['legacy']}</p>
                        </div>
                    </div>
                </div>
                """

            html_content = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Galactic Story Dashboard</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ background-color: #12161A; color: white; }}
                    .accordion-button:not(.collapsed) {{ background-color: #1B242C; color: #3498db; }}
                </style>
            </head>
            <body>
                <div class="container py-5">
                    <h1 class="text-center text-primary mb-5">THE GALACTIC STORY DASHBOARD</h1>
                    
                    <h3 class="mb-4 text-warning">Famous Historical Figures</h3>
                    <div class="row">
                        {fig_rows}
                    </div>
                    
                    <h3 class="mt-5 mb-4 text-warning">Empire Chronicles Anthology</h3>
                    <div class="accordion" id="chroniclesAccordion">
                        {chron_rows}
                    </div>
                </div>
                <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
            </body>
            </html>
            """
            
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"Saved story dashboard to {out_path}")
        except Exception as e:
            logger.error(f"Error generating story dashboard HTML: {e}")

    def _generate_news_dashboard_html(self, df_news: pd.DataFrame) -> None:
        """Generates galactic_news_dashboard.html (simulated news broadcast feed)."""
        try:
            out_path = os.path.join(self.datasets_dir, "galactic_news_dashboard.html")
            
            news_items = ""
            for _, row in df_news.head(30).iterrows():
                news_items += f"""
                <div class="list-group-item bg-dark text-white border-secondary mb-3 p-4">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1 text-info">{row['headline']}</h5>
                        <small class="text-warning">Year {row['year']}</small>
                    </div>
                    <p class="mb-2 mt-2">{row['body']}</p>
                    <small class="text-muted">Reported by: {row['spokesperson']} | Category: {row['category']}</small>
                </div>
                """

            html_content = f"""<!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <title>Galactic News Network Feed</title>
                <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
                <style>
                    body {{ background-color: #121212; color: #e0e0e0; }}
                    .container {{ max-width: 900px; }}
                </style>
            </head>
            <body>
                <div class="container py-5">
                    <div class="text-center mb-5">
                        <h1 class="text-danger fw-bold">GALACTIC NEWS NETWORK</h1>
                        <p class="text-muted">Real-time breaking bulletins from the Milky Way star corridors</p>
                    </div>
                    <div class="list-group">
                        {news_items}
                    </div>
                </div>
            </body>
            </html>
            """

            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logger.info(f"Saved GNN feed dashboard to {out_path}")
        except Exception as e:
            logger.error(f"Error generating GNN feed: {e}")
