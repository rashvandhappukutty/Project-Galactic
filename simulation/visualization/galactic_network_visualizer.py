"""
galactic_network_visualizer.py — Renders FTL infrastructure maps and HTML timelines.
"""

import os
import math
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from typing import Dict, Any, List


class GalacticNetworkVisualizer:
    """Generates high-fidelity visual overlays of the galactic transportation networks."""

    def __init__(self, datasets_dir: str = "datasets") -> None:
        self.datasets_dir = datasets_dir
        self.wormholes_csv = os.path.join(datasets_dir, "wormholes.csv")
        self.hyperlanes_csv = os.path.join(datasets_dir, "hyperlane_network.csv")
        self.gates_csv = os.path.join(datasets_dir, "jump_gates.csv")
        self.routes_csv = os.path.join(datasets_dir, "ftl_routes.csv")
        self.strategic_csv = os.path.join(datasets_dir, "strategic_systems.csv")
        self.events_csv = os.path.join(datasets_dir, "transport_events.csv")
        
        plt.style.use('dark_background')
        self.text_color = "#E0E0E0"
        self.grid_color = "#2A2A2A"

    def plot_wormhole_network(self, output_dir: str) -> None:
        """Plot natural, ancient, and artificial wormholes on the galactic map."""
        stars_df = pd.read_csv(os.path.join(self.datasets_dir, "stars.csv"))
        w_df = pd.read_csv(self.wormholes_csv)

        if stars_df.empty or w_df.empty:
            return

        fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
        
        # Draw background stars
        ax.scatter(stars_df["x"], stars_df["y"], s=2, color="#444444", alpha=0.3, label="Stars")

        # Map coords
        star_coords = stars_df.set_index("id")[["x", "y"]].to_dict(orient="index")

        # Draw wormholes as arc overlays
        for _, row in w_df.iterrows():
            src = str(row["entry_system"])
            tgt = str(row["exit_system"])
            w_type = str(row["wormhole_type"])

            if src in star_coords and tgt in star_coords:
                x1, y1 = star_coords[src]["x"], star_coords[src]["y"]
                x2, y2 = star_coords[tgt]["x"], star_coords[tgt]["y"]

                # Color coding
                if w_type == "Natural":
                    color = "#00FFFF"  # Cyan
                    ls = ":"
                    alpha = 0.5
                elif w_type == "Ancient":
                    color = "#FFD700"  # Gold
                    ls = "--"
                    alpha = 0.8
                else:  # Artificial
                    color = "#FF00FF"  # Magenta
                    ls = "-"
                    alpha = 0.7

                # Draw connection
                ax.plot([x1, x2], [y1, y2], color=color, linestyle=ls, alpha=alpha, linewidth=1.5)

        # Highlight endpoints
        natural_w = w_df[w_df["wormhole_type"] == "Natural"]
        ancient_w = w_df[w_df["wormhole_type"] == "Ancient"]
        art_w = w_df[w_df["wormhole_type"] == "Artificial"]

        for subset, color, label in [(natural_w, "#00FFFF", "Natural Wormholes"),
                                     (ancient_w, "#FFD700", "Ancient Gateways"),
                                     (art_w, "#FF00FF", "Artificial Portals")]:
            if not subset.empty:
                nodes = list(subset["entry_system"].values) + list(subset["exit_system"].values)
                nodes = list(set([n for n in nodes if n in star_coords]))
                if nodes:
                    ax.scatter(
                        [star_coords[n]["x"] for n in nodes],
                        [star_coords[n]["y"] for n in nodes],
                        s=15,
                        color=color,
                        alpha=0.9,
                        edgecolors="white",
                        linewidths=0.3,
                        label=label
                    )

        ax.set_title("Procedural Wormhole Shortcuts & Core Relics Map", fontsize=14, color=self.text_color, pad=15)
        ax.set_xlabel("Galactic X-Coordinate (LY)", color=self.text_color)
        ax.set_ylabel("Galactic Y-Coordinate (LY)", color=self.text_color)
        ax.legend(loc="upper right", frameon=False)
        ax.grid(True, linestyle="--", color=self.grid_color, alpha=0.3)

        plt.tight_layout()
        out_path = os.path.join(output_dir, "wormhole_network_map.png")
        plt.savefig(out_path, transparent=True)
        plt.close()

    def plot_hyperlane_grid(self, output_dir: str) -> None:
        """Plot the hyperlane grid network."""
        stars_df = pd.read_csv(os.path.join(self.datasets_dir, "stars.csv"))
        l_df = pd.read_csv(self.hyperlanes_csv)

        if stars_df.empty or l_df.empty:
            return

        fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
        ax.scatter(stars_df["x"], stars_df["y"], s=1, color="#333333", alpha=0.3)

        star_coords = stars_df.set_index("id")[["x", "y"]].to_dict(orient="index")

        # Plot corridors
        for _, row in l_df.iterrows():
            src = str(row["source_star_id"])
            tgt = str(row["target_star_id"])
            l_type = str(row["lane_type"])

            if src in star_coords and tgt in star_coords:
                x1, y1 = star_coords[src]["x"], star_coords[src]["y"]
                x2, y2 = star_coords[tgt]["x"], star_coords[tgt]["y"]

                if l_type == "Trade Artery":
                    color = "#2ECC71"  # Emerald
                    width = 1.0
                    alpha = 0.8
                elif l_type == "Military Corridor":
                    color = "#E74C3C"  # Crimson
                    width = 0.8
                    alpha = 0.7
                elif l_type == "Deep Space Corridor":
                    color = "#95A5A6"  # Grey
                    width = 0.4
                    alpha = 0.4
                else:
                    color = "#3498DB"  # Blue
                    width = 0.6
                    alpha = 0.5

                ax.plot([x1, x2], [y1, y2], color=color, linewidth=width, alpha=alpha)

        # Draw dummy lines for legend
        ax.plot([], [], color="#2ECC71", label="Trade Arteries")
        ax.plot([], [], color="#E74C3C", label="Military Corridors")
        ax.plot([], [], color="#3498DB", label="Hyperlane Grid")
        ax.plot([], [], color="#95A5A6", label="Deep Space Corridors")

        ax.set_title("Galactic FTL Hyperlane Grid & Patrol Corridors", fontsize=14, color=self.text_color, pad=15)
        ax.set_xlabel("Galactic X-Coordinate (LY)", color=self.text_color)
        ax.set_ylabel("Galactic Y-Coordinate (LY)", color=self.text_color)
        ax.legend(loc="upper right", frameon=False)
        ax.grid(True, linestyle="--", color=self.grid_color, alpha=0.3)

        plt.tight_layout()
        out_path = os.path.join(output_dir, "hyperlane_grid.png")
        plt.savefig(out_path, transparent=True)
        plt.close()

    def plot_jump_gate_map(self, output_dir: str) -> None:
        """Plot the jump gate network and relay relay links."""
        stars_df = pd.read_csv(os.path.join(self.datasets_dir, "stars.csv"))
        g_df = pd.read_csv(self.gates_csv)

        if stars_df.empty or g_df.empty:
            return

        fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
        ax.scatter(stars_df["x"], stars_df["y"], s=2, color="#444444", alpha=0.3)

        star_coords = stars_df.set_index("id")[["x", "y"]].to_dict(orient="index")

        # Map stars of gates to coords
        gate_stars = g_df.merge(stars_df, left_on="star_id", right_on="id")
        
        # Color codes per gate type
        g_colors = {
            "Quantum Relay Gate": "#E67E22",  # Orange
            "Galactic Gate": "#FF1493",       # Deep Pink
            "Empire Gate": "#9B59B6",         # Amethyst
            "Regional Gate": "#3498DB"        # Blue
        }

        # Plot connections
        # Relays are instant jumps, so we draw relays connecting gate stars
        for g_type, color in g_colors.items():
            subset = gate_stars[gate_stars["gate_type"] == g_type]
            if not subset.empty:
                ax.scatter(
                    subset["x"],
                    subset["y"],
                    s=40,
                    color=color,
                    edgecolors="white",
                    linewidths=0.5,
                    label=g_type,
                    zorder=3
                )

        ax.set_title("Jump Gate Relays & Interstellar Gateway Grid", fontsize=14, color=self.text_color, pad=15)
        ax.set_xlabel("Galactic X-Coordinate (LY)", color=self.text_color)
        ax.set_ylabel("Galactic Y-Coordinate (LY)", color=self.text_color)
        ax.legend(loc="upper right", frameon=False)
        ax.grid(True, linestyle="--", color=self.grid_color, alpha=0.3)

        plt.tight_layout()
        out_path = os.path.join(output_dir, "jump_gate_map.png")
        plt.savefig(out_path, transparent=True)
        plt.close()

    def plot_strategic_chokepoints(self, output_dir: str) -> None:
        """Plot chokepoints based on betweenness centrality."""
        stars_df = pd.read_csv(os.path.join(self.datasets_dir, "stars.csv"))
        s_df = pd.read_csv(self.strategic_csv)

        if stars_df.empty or s_df.empty:
            return

        fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
        ax.scatter(stars_df["x"], stars_df["y"], s=2, color="#444444", alpha=0.3)

        # Merge coords
        s_coords = s_df.merge(stars_df, left_on="star_id", right_on="id")
        
        # Divide into tiers
        high_tier = s_coords[s_coords["strategic_value_score"] >= 70.0]
        med_tier = s_coords[(s_coords["strategic_value_score"] < 70.0) & (s_coords["strategic_value_score"] >= 35.0)]
        low_tier = s_coords[s_coords["strategic_value_score"] < 35.0]

        if not high_tier.empty:
            ax.scatter(high_tier["x"], high_tier["y"], s=high_tier["strategic_value_score"] * 1.5, color="#E74C3C", edgecolors="white", linewidths=0.5, label="High Strategic Bottleneck", zorder=4)
        if not med_tier.empty:
            ax.scatter(med_tier["x"], med_tier["y"], s=med_tier["strategic_value_score"] * 1.2, color="#F39C12", edgecolors="white", linewidths=0.3, label="Secondary Chokepoint", zorder=3)
        if not low_tier.empty:
            ax.scatter(low_tier["x"], low_tier["y"], s=low_tier["strategic_value_score"] * 0.8, color="#3498DB", edgecolors="white", linewidths=0.2, label="Standard FTL Intersection", zorder=2)

        ax.set_title("Strategic Chokepoint Systems & FTL Bottlenecks Map", fontsize=14, color=self.text_color, pad=15)
        ax.set_xlabel("Galactic X-Coordinate (LY)", color=self.text_color)
        ax.set_ylabel("Galactic Y-Coordinate (LY)", color=self.text_color)
        ax.legend(loc="upper right", frameon=False)
        ax.grid(True, linestyle="--", color=self.grid_color, alpha=0.3)

        plt.tight_layout()
        out_path = os.path.join(output_dir, "strategic_chokepoints.png")
        plt.savefig(out_path, transparent=True)
        plt.close()

    def plot_galactic_connectivity(self, output_dir: str) -> None:
        """Plot travel time contour heatmap from all stars to the central capital."""
        stars_df = pd.read_csv(os.path.join(self.datasets_dir, "stars.csv"))
        r_df = pd.read_csv(self.routes_csv)

        if stars_df.empty or r_df.empty:
            return

        fig, ax = plt.subplots(figsize=(10, 10), dpi=150)
        
        # Calculate average travel time from each capital/world to the core/center
        # For simplicity, color code each star node by its FTL travel time to core
        # Let's merge routes with stars coords
        # s_routes contains the travel_time_years per star
        mean_times = r_df.groupby("source_star_name")["travel_time_years"].mean().reset_index()
        merged = mean_times.merge(stars_df, left_on="source_star_name", right_on="name")

        if merged.empty:
            return

        # Scatter plot colored by travel time (inverse of connectivity)
        # Low travel time (blue/green) = high connectivity. High travel time (red/yellow) = isolated.
        sc = ax.scatter(
            merged["x"],
            merged["y"],
            c=merged["travel_time_years"],
            cmap=plt.cm.plasma_r,
            s=12,
            edgecolors="none",
            alpha=0.9
        )
        
        cbar = fig.colorbar(sc, ax=ax, shrink=0.7, pad=0.03)
        cbar.set_label("Average FTL Travel Time to Other Capitals (Years)", color=self.text_color, rotation=270, labelpad=15)
        cbar.ax.yaxis.set_tick_params(color=self.text_color)
        plt.setp(plt.getp(cbar.ax.axes, 'yticklabels'), color=self.text_color)

        ax.set_title("Galactic FTL Connectivity Heatmap", fontsize=14, color=self.text_color, pad=15)
        ax.set_xlabel("Galactic X-Coordinate (LY)", color=self.text_color)
        ax.set_ylabel("Galactic Y-Coordinate (LY)", color=self.text_color)
        ax.grid(True, linestyle="--", color=self.grid_color, alpha=0.3)

        plt.tight_layout()
        out_path = os.path.join(output_dir, "galactic_connectivity.png")
        plt.savefig(out_path, transparent=True)
        plt.close()

    def generate_ftl_timeline(self, output_dir: str) -> None:
        """Create a beautiful dark space themed interactive HTML timeline of transportation history."""
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

            color_class = "info"
            if e_type in ["Wormhole Collapse", "Gate Failure", "Navigation Crisis"]:
                color_class = "danger"
            elif e_type in ["Hyperlane Expansion", "Ancient Gateway Discovery", "Transit Revolution", "Quantum Network Upgrade"]:
                color_class = "success"

            timeline_items_html += f"""
            <div class="timeline-item border-{color_class}">
                <div class="time-header text-{color_class}">Year {year} (Tick {row['tick']})</div>
                <div class="event-title">{e_type}</div>
                <div class="event-body">{desc}</div>
                <div class="event-meta">Actor Empire ID: <span class="badge bg-secondary">{cid}</span></div>
            </div>
            """

        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Galactic Transportation History Timeline</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
    <style>
        body {{
            background-color: #080B10;
            color: #E2E8F0;
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
            border-left: 2px solid #1A202C;
        }}
        .timeline-item {{
            background: rgba(26, 32, 44, 0.4);
            border-left: 5px solid;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 25px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.2);
            transition: all 0.3s ease;
        }}
        .timeline-item:hover {{
            transform: translateX(8px);
            background: rgba(26, 32, 44, 0.6);
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
            color: #CBD5E0;
            margin-bottom: 12px;
        }}
        .event-meta {{
            font-size: 0.8rem;
            color: #718096;
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
        <h1>FTL TRANSPORTATION & RELAYS TIMELINE</h1>
        <p class="text-muted">A Historical Register of Jump Gate failure anomalies, Wormhole Collapses, and navigation achievements</p>
        <hr style="border-color: #1A202C;">
    </div>
    
    <div class="timeline-container">
        {timeline_items_html}
    </div>
</body>
</html>
"""
        out_path = os.path.join(output_dir, "ftl_timeline.html")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"  - Saved HTML timeline: {out_path}")
