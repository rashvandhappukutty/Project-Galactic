"""
economy_visualizer.py — Renders high-fidelity macroeconomic visualizations and HTML dashboards.
"""

import os
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict, Any


class EconomyVisualizer:
    """Generates high-fidelity visual representations of the galactic economy."""

    def __init__(self, datasets_dir: str = "datasets") -> None:
        self.datasets_dir = datasets_dir
        self.economy_csv = os.path.join(datasets_dir, "economy.csv")
        self.market_csv = os.path.join(datasets_dir, "market_prices.csv")
        self.agreements_csv = os.path.join(datasets_dir, "trade_agreements.csv")
        self.events_csv = os.path.join(datasets_dir, "economic_events.csv")
        self.blocs_csv = os.path.join(datasets_dir, "economic_blocs.csv")
        self.gdp_rankings_csv = os.path.join(datasets_dir, "gdp_rankings.csv")

        # Visual style: Dark premium space themes
        plt.style.use('dark_background')
        self.accent_color = "#00FFFF"  # Cyan
        self.text_color = "#E0E0E0"
        self.grid_color = "#2A2A2A"

    def plot_gdp_distribution(self, output_dir: str) -> None:
        """Plot a log-scale histogram of empire GDPs."""
        df = pd.read_csv(self.gdp_rankings_csv)
        if df.empty:
            return

        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        
        # Calculate log-scale bins
        min_gdp = max(1.0, df["gdp"].min())
        max_gdp = df["gdp"].max()
        bins = np.logspace(np.log10(min_gdp), np.log10(max_gdp), 25)

        n, _, patches = ax.hist(df["gdp"], bins=bins, color="#1F77B4", edgecolor="#00FFFF", alpha=0.7)
        
        # Apply gradient color to patches based on height
        fracs = n / n.max()
        norm = mcolors.Normalize(fracs.min(), fracs.max())
        for thisfrac, thispatch in zip(fracs, patches):
            color = plt.cm.plasma(norm(thisfrac))
            thispatch.set_facecolor(color)

        ax.set_xscale('log')
        ax.set_title("Galactic GDP Distribution across Empires", fontsize=14, color=self.text_color, pad=15)
        ax.set_xlabel("Gross Domestic Product (credits, log scale)", fontsize=11, color=self.text_color)
        ax.set_ylabel("Number of Empires", fontsize=11, color=self.text_color)
        
        ax.grid(True, which="both", linestyle="--", color=self.grid_color, alpha=0.5)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.grid_color)
        ax.spines['bottom'].set_color(self.grid_color)

        plt.tight_layout()
        out_path = os.path.join(output_dir, "galactic_gdp_distribution.png")
        plt.savefig(out_path, transparent=True)
        plt.close()

    def plot_market_dashboard(self, output_dir: str) -> None:
        """Generate a resource market dashboard with subplots."""
        mkt_df = pd.read_csv(self.market_csv)
        if mkt_df.empty:
            return

        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=False, dpi=150)

        # 1. Price Trends (group by tick & commodity to get galactic average price)
        price_trends = mkt_df.groupby(["tick", "commodity"])["price"].mean().unstack()
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(price_trends.columns)))
        for idx, col in enumerate(price_trends.columns):
            ax1.plot(price_trends.index * 100, price_trends[col], label=col, color=colors[idx], linewidth=2.0)

        ax1.set_yscale('log')
        ax1.set_title("Galactic Commodity Pricing Trends", fontsize=14, color=self.text_color, pad=15)
        ax1.set_ylabel("Average Price (Credits, log scale)", fontsize=11, color=self.text_color)
        ax1.legend(bbox_to_anchor=(1.02, 1), loc='upper left', frameon=False)
        ax1.grid(True, which="both", linestyle="--", color=self.grid_color, alpha=0.5)
        ax1.spines['top'].set_visible(False)
        ax1.spines['right'].set_visible(False)

        # 2. Final Stockpile Volumetrics
        final_tick = mkt_df["tick"].max()
        final_mkt = mkt_df[mkt_df["tick"] == final_tick]
        avg_inv = final_mkt.groupby("commodity")["inventory"].mean().sort_values(ascending=False)

        bars = ax2.bar(avg_inv.index, avg_inv.values, color="#9467BD", edgecolor="#00FFFF", alpha=0.8)
        
        # Color gradient on bars
        for idx, bar in enumerate(bars):
            color = plt.cm.viridis(idx / len(bars))
            bar.set_facecolor(color)

        ax2.set_title("Average Planetary Stockpiles (Final Year)", fontsize=13, color=self.text_color, pad=15)
        ax2.set_ylabel("Average Units", fontsize=11, color=self.text_color)
        ax2.tick_params(axis='x', rotation=45)
        ax2.spines['top'].set_visible(False)
        ax2.spines['right'].set_visible(False)
        ax2.grid(True, axis='y', linestyle="--", color=self.grid_color, alpha=0.5)

        plt.tight_layout()
        out_path = os.path.join(output_dir, "resource_market_dashboard.png")
        plt.savefig(out_path, transparent=True)
        plt.close()

    def plot_trade_network_map(self, output_dir: str) -> None:
        """Plot the trade routes overlay colored by traffic volume."""
        stars_df = pd.read_csv(os.path.join(self.datasets_dir, "stars.csv"))
        routes_df = pd.read_csv(os.path.join(self.datasets_dir, "interstellar_routes.csv"))
        
        if stars_df.empty or routes_df.empty:
            return

        fig, ax = plt.subplots(figsize=(10, 10), dpi=150)

        # Initialize networkx graph
        G = nx.Graph()
        pos = {}
        for _, row in stars_df.iterrows():
            sid = str(row["id"])
            G.add_node(sid)
            pos[sid] = (float(row["x"]), float(row["y"]))

        # Filter out route segments
        edges = []
        edge_weights = []
        for _, row in routes_df.iterrows():
            src = str(row["source_star_id"])
            tgt = str(row["target_star_id"])
            val = float(row.get("economic_value", 10.0))
            if src in pos and tgt in pos:
                G.add_edge(src, tgt, weight=val)
                edges.append((src, tgt))
                edge_weights.append(val)

        # Draw stars base (unconnected stellar background)
        ax.scatter(stars_df["x"], stars_df["y"], s=2, color="#555555", alpha=0.3, label="Stars Catalog")

        # Normalize edge colors based on economic_value/traffic
        if edge_weights:
            max_w = max(edge_weights)
            min_w = min(edge_weights)
            norm_w = [0.1 + 2.5 * (w - min_w) / (max_w - min_w + 1e-3) for w in edge_weights]
            
            # Draw edges
            nx.draw_networkx_edges(
                G, pos,
                edgelist=edges,
                width=norm_w,
                edge_color=edge_weights,
                edge_cmap=plt.cm.cool,
                ax=ax,
                alpha=0.8
            )

        # Highlight core trade hubs (nodes with high degrees)
        degrees = dict(G.degree())
        hubs = [n for n, d in degrees.items() if d >= 2]
        hub_pos = {n: pos[n] for n in hubs}
        hub_sizes = [degrees[n] * 12 for n in hubs]

        if hubs:
            ax.scatter(
                [pos[h][0] for h in hubs],
                [pos[h][1] for h in hubs],
                s=hub_sizes,
                color="#00FFFF",
                alpha=0.9,
                edgecolors="white",
                linewidths=0.5,
                label="Commerce Exchange Hubs"
            )

        ax.set_title("Interstellar Trade Route Network Flow Map", fontsize=14, color=self.text_color, pad=15)
        ax.set_xlabel("Galactic X-Coordinate (LY)", fontsize=11, color=self.text_color)
        ax.set_ylabel("Galactic Y-Coordinate (LY)", fontsize=11, color=self.text_color)
        ax.legend(loc="upper right", frameon=False)
        ax.grid(True, linestyle="--", color=self.grid_color, alpha=0.3)

        plt.tight_layout()
        out_path = os.path.join(output_dir, "trade_network_map.png")
        plt.savefig(out_path, transparent=True)
        plt.close()

    def plot_economic_blocs(self, output_dir: str) -> None:
        """Plot a bar chart of economic blocs and their combined GDPs."""
        blocs_df = pd.read_csv(self.blocs_csv)
        if blocs_df.empty:
            return

        final_tick = blocs_df["tick"].max()
        final_blocs = blocs_df[blocs_df["tick"] == final_tick].sort_values(by="combined_gdp", ascending=False)

        if final_blocs.empty:
            return

        fig, ax = plt.subplots(figsize=(10, 6), dpi=150)
        
        bars = ax.barh(final_blocs["bloc_name"], final_blocs["combined_gdp"], color="#2CA02C", edgecolor="#00FFFF", alpha=0.8)
        
        # Color gradient
        for idx, bar in enumerate(bars):
            color = plt.cm.winter(idx / len(bars))
            bar.set_facecolor(color)

        ax.set_title("Interstellar Economic Unions & Trade Blocs (GDP)", fontsize=14, color=self.text_color, pad=15)
        ax.set_xlabel("Combined GDP (Credits)", fontsize=11, color=self.text_color)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.grid(True, axis='x', linestyle="--", color=self.grid_color, alpha=0.5)

        plt.tight_layout()
        out_path = os.path.join(output_dir, "economic_blocs.png")
        plt.savefig(out_path, transparent=True)
        plt.close()

    def plot_wealth_distribution(self, output_dir: str) -> None:
        """Generate the Lorenz curve and calculate the Gini coefficient."""
        rank_df = pd.read_csv(self.gdp_rankings_csv)
        if rank_df.empty:
            return

        gdp = np.sort(rank_df["gdp"].values)
        n = len(gdp)
        
        # Cumulative share of wealth ( Lorenz curve )
        gdp_cumulative = np.cumsum(gdp)
        lorenz_curve = gdp_cumulative / gdp_cumulative[-1]
        
        # Population share
        population_share = np.arange(1, n + 1) / n

        # Area under Lorenz curve
        area_lorenz = np.trapz(lorenz_curve, population_share)
        # Gini Coefficient = (Area between line of equality and Lorenz curve) / (Area under line of equality)
        # Area under equality = 0.5
        gini = (0.5 - area_lorenz) / 0.5
        gini = max(0.0, min(1.0, gini))

        fig, ax = plt.subplots(figsize=(8, 8), dpi=150)
        
        # Perfect equality line
        ax.plot([0, 1], [0, 1], linestyle="--", color="#FF7F0E", label="Line of Perfect Equality")
        
        # Lorenz Curve
        ax.plot(np.insert(population_share, 0, 0), np.insert(lorenz_curve, 0, 0), color="#1F77B4", linewidth=2.5, label=" Lorenz Curve (GDP Share)")
        
        # Fill between
        ax.fill_between(np.insert(population_share, 0, 0), np.insert(population_share, 0, 0), np.insert(lorenz_curve, 0, 0), color="#1F77B4", alpha=0.15)

        ax.set_title(f"Galactic Wealth Equality (Gini Coefficient: {gini:.3f})", fontsize=14, color=self.text_color, pad=15)
        ax.set_xlabel("Cumulative Share of Empire Population", fontsize=11, color=self.text_color)
        ax.set_ylabel("Cumulative Share of Galactic GDP", fontsize=11, color=self.text_color)
        ax.legend(loc="upper left", frameon=False)
        ax.grid(True, linestyle="--", color=self.grid_color, alpha=0.5)
        
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['left'].set_color(self.grid_color)
        ax.spines['bottom'].set_color(self.grid_color)

        plt.tight_layout()
        out_path = os.path.join(output_dir, "wealth_distribution.png")
        plt.savefig(out_path, transparent=True)
        plt.close()

    def generate_economic_timeline(self, output_dir: str) -> None:
        """Create a beautiful dark space themed interactive economic timeline HTML page."""
        events_df = pd.read_csv(self.events_csv)
        if events_df.empty:
            return

        events_df = events_df.sort_values(by=["tick", "year"]).reset_index(drop=True)

        timeline_items_html = ""
        for _, row in events_df.iterrows():
            e_type = str(row["event_type"])
            year = int(row["year"])
            desc = str(row["description"])
            cid = str(row["civilization_id"])

            # Map category class icons/color borders
            color_class = "info"
            if e_type in ["Market Crash", "Economic Collapse", "Energy Crisis"]:
                color_class = "danger"
            elif e_type in ["Economic Boom", "Golden Age", "Industrial Revolution", "Technological Revolution"]:
                color_class = "success"
            elif e_type == "Hyperinflation":
                color_class = "warning"

            timeline_items_html += f"""
            <div class="timeline-item border-{color_class}">
                <div class="time-header text-{color_class}">Year {year} (Tick {row['tick']})</div>
                <div class="event-title">{e_type}</div>
                <div class="event-body">{desc}</div>
                <div class="event-meta">Subject Empire ID: <span class="badge bg-secondary">{cid}</span></div>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Galactic Economic History Timeline</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            background-color: #0B0E14;
            color: #E0E4EC;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 30px;
        }}
        h1 {{
            font-weight: 800;
            color: #00FFFF;
            text-shadow: 0 0 10px rgba(0, 255, 255, 0.4);
            margin-bottom: 25px;
        }}
        .timeline-container {{
            max-width: 900px;
            margin: 40px auto;
            position: relative;
            padding-left: 20px;
            border-left: 2px solid #1E2530;
        }}
        .timeline-item {{
            background: rgba(30, 37, 48, 0.4);
            border-left: 5px solid;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }}
        .timeline-item:hover {{
            transform: translateX(8px);
            background: rgba(30, 37, 48, 0.6);
        }}
        .time-header {{
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .event-title {{
            font-size: 1.25rem;
            font-weight: 700;
            color: white;
            margin-bottom: 8px;
        }}
        .event-body {{
            font-size: 0.95rem;
            line-height: 1.6;
            color: #C0C8D6;
            margin-bottom: 12px;
        }}
        .event-meta {{
            font-size: 0.8rem;
            color: #7A869A;
        }}
        .border-success {{ border-color: #2ECC71 !important; }}
        .border-danger {{ border-color: #E74C3C !important; }}
        .border-warning {{ border-color: #F39C12 !important; }}
        .border-info {{ border-color: #3498DB !important; }}
        .text-success {{ color: #2ECC71 !important; }}
        .text-danger {{ color: #E74C3C !important; }}
        .text-warning {{ color: #F39C12 !important; }}
        .text-info {{ color: #3498DB !important; }}
    </style>
</head>
<body>
    <div class="container text-center">
        <h1>GALACTIC ECONOMIC TIMELINE</h1>
        <p class="text-muted">A Historical Register of Interstellar Booms, Crises, and Financial Shocks</p>
        <hr style="border-color: #1E2530;">
    </div>
    
    <div class="timeline-container">
        {timeline_items_html}
    </div>
</body>
</html>
"""
        out_path = os.path.join(output_dir, "economic_timeline.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"  - Saved HTML timeline: {out_path}")
