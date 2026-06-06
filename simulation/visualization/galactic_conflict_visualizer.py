"""
galactic_conflict_visualizer.py — Generates conflict maps, alliance networks, casualty plots, and timeline HTML.
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import networkx as nx


class GalacticConflictVisualizer:
    """Generates space-dark visualization boards for Phase 9 political and conflict assets."""

    def __init__(self, datasets_dir: str = "datasets") -> None:
        self.datasets_dir = datasets_dir
        
        # Apply space dark styling
        plt.style.use("dark_background")
        self.bg_color = "#0B0B1E"
        self.accent_color = "#FF3366"  # Deep red/pink for conflict
        self.primary_color = "#00D2FF"  # Cyan for alliances
        
        # Setup fonts
        plt.rcParams['font.sans-serif'] = 'Inter'
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['axes.facecolor'] = self.bg_color
        plt.rcParams['figure.facecolor'] = self.bg_color
        plt.rcParams['grid.color'] = "#1E1E38"
        plt.rcParams['text.color'] = "#E0E0FF"
        plt.rcParams['axes.labelcolor'] = "#E0E0FF"
        plt.rcParams['xtick.color'] = "#A0A0C0"
        plt.rcParams['ytick.color'] = "#A0A0C0"

    def plot_alliance_network(self, output_dir: str) -> None:
        """Create a node-link network map of alliances."""
        alliances_df = self._load_csv("alliances.csv")
        empires_df = self._load_csv("empires.csv")

        plt.figure(figsize=(10, 8))
        G = nx.Graph()

        if not empires_df.empty:
            for _, row in empires_df.iterrows():
                G.add_node(str(row["founding_civilization_id"]), name=str(row["empire_name"]))

        if not alliances_df.empty:
            for _, row in alliances_df.iterrows():
                members = str(row["member_empires"]).split(",")
                for i in range(len(members)):
                    for j in range(i + 1, len(members)):
                        G.add_edge(members[i], members[j], label=str(row["alliance_type"]))

        # Remove isolated nodes to make plot cleaner
        isolated = list(nx.isolates(G))
        G.remove_nodes_from(isolated)

        if G.number_of_nodes() > 0:
            pos = nx.spring_layout(G, k=0.15, seed=42)
            
            # Nodes color: cyan for alliances
            nx.draw_networkx_nodes(G, pos, node_size=80, node_color=self.primary_color, alpha=0.8)
            nx.draw_networkx_edges(G, pos, edge_color="#303060", alpha=0.5, width=1.5)
            
            # Label top 10 nodes with name
            labels = {n: G.nodes[n].get("name", n)[:10] for n in G.nodes() if G.degree(n) > 1}
            nx.draw_networkx_labels(G, pos, labels=labels, font_size=7, font_color="#E0E0FF")

        plt.title("Galactic Alliance & Treaty Networks", fontsize=14, color=self.primary_color, pad=15)
        plt.axis("off")
        plt.tight_layout()
        
        path = os.path.join(output_dir, "alliance_network.png")
        plt.savefig(path, dpi=150, facecolor=self.bg_color)
        plt.close()

    def plot_galactic_wars_map(self, output_dir: str) -> None:
        """Plot coordinate grid of active battles and conflict locations."""
        battles_df = self._load_csv("battles.csv")
        stars_df = self._load_csv("stars.csv")

        plt.figure(figsize=(10, 8))
        
        # Draw background stars in light gray
        if not stars_df.empty:
            plt.scatter(stars_df["x"], stars_df["y"], s=1.0, color="#303050", alpha=0.5, label="Systems")

        # Map battle location star coords
        if not battles_df.empty and not stars_df.empty:
            stars_dict = stars_df.set_index("id").to_dict(orient="index")
            battle_coords = []
            
            for _, row in battles_df.iterrows():
                sid = str(row["location_star_id"])
                if sid in stars_dict:
                    battle_coords.append((stars_dict[sid]["x"], stars_dict[sid]["y"], float(row["casualties"])))

            if battle_coords:
                bx, by, casualties = zip(*battle_coords)
                
                # Scale marker sizes based on casualties
                sizes = np.array(casualties) / 1.0e6  # 1 Million casualties = 1 unit size
                sizes = np.clip(sizes, 20, 500)
                
                scatter = plt.scatter(bx, by, s=sizes, color=self.accent_color, alpha=0.7, edgecolors="#FFFFFF", linewidths=0.5, label="Battles")
                
                # Add size legend
                handles, labels = scatter.legend_elements(prop="sizes", alpha=0.6)
                plt.legend(handles, ["10M", "30M", "50M", "80M", "100M+"], loc="upper right", title="Casualties Scale")

        plt.title("Galactic Warfare Conflict Zones", fontsize=14, color=self.accent_color, pad=15)
        plt.xlabel("X-Coordinate (LY)", fontsize=10)
        plt.ylabel("Y-Coordinate (LY)", fontsize=10)
        plt.grid(True, linestyle="--", alpha=0.1)
        plt.tight_layout()

        path = os.path.join(output_dir, "galactic_wars_map.png")
        plt.savefig(path, dpi=150, facecolor=self.bg_color)
        plt.close()

    def plot_fleet_power_distribution(self, output_dir: str) -> None:
        """Create fleet power distribution histogram across active fleets."""
        fleets_df = self._load_csv("fleets.csv")

        plt.figure(figsize=(10, 6))

        if not fleets_df.empty:
            active_f = fleets_df[fleets_df["status"] != "Destroyed"]
            if not active_f.empty:
                sns.histplot(data=active_f, x="fleet_power", hue="fleet_class", multiple="stack", palette="flare", bins=30)
                plt.xlabel("Fleet Power Index", fontsize=10)
                plt.ylabel("Count of active Fleets", fontsize=10)
            else:
                plt.text(0.5, 0.5, "No Active Fleets to Display", ha="center", va="center")
        else:
            plt.text(0.5, 0.5, "No Fleets Database Found", ha="center", va="center")

        plt.title("Galactic Fleet Power Distribution", fontsize=14, color=self.primary_color, pad=15)
        plt.grid(True, linestyle="--", alpha=0.1)
        plt.tight_layout()

        path = os.path.join(output_dir, "fleet_power_distribution.png")
        plt.savefig(path, dpi=150, facecolor=self.bg_color)
        plt.close()

    def plot_battle_casualties(self, output_dir: str) -> None:
        """Plot battle casualties accumulated over ticks."""
        battles_df = self._load_csv("battles.csv")

        plt.figure(figsize=(10, 6))

        if not battles_df.empty:
            battles_df = battles_df.sort_values(by="year")
            battles_df["cum_casualties"] = battles_df["casualties"].cumsum() / 1.0e6  # to Millions
            
            plt.plot(battles_df["year"], battles_df["cum_casualties"], color=self.accent_color, linewidth=2.0, marker="o", markersize=4)
            plt.fill_between(battles_df["year"], battles_df["cum_casualties"], color=self.accent_color, alpha=0.15)
            plt.xlabel("Timeline Year", fontsize=10)
            plt.ylabel("Cumulative Casualties (Millions)", fontsize=10)
        else:
            plt.text(0.5, 0.5, "No Battles Simulated Yet", ha="center", va="center")

        plt.title("Interstellar War Casualties Timeline", fontsize=14, color=self.accent_color, pad=15)
        plt.grid(True, linestyle="--", alpha=0.1)
        plt.tight_layout()

        path = os.path.join(output_dir, "battle_casualties.png")
        plt.savefig(path, dpi=150, facecolor=self.bg_color)
        plt.close()

    def plot_territorial_changes(self, output_dir: str) -> None:
        """Create bar chart of conquests/territory transfers over ticks."""
        conquests_df = self._load_csv("conquests.csv")

        plt.figure(figsize=(10, 6))

        if not conquests_df.empty:
            # Group by year/tick and count actions
            # Determine ticks roughly by dividing year by 100
            conquests_df["tick"] = (conquests_df["year"] // 100).astype(int)
            counts = conquests_df.groupby(["tick", "action"])["conquest_id"].count().unstack().fillna(0)
            
            counts.plot(kind="bar", stacked=True, colormap="viridis", ax=plt.gca(), edgecolor="none")
            plt.xlabel("Simulation Tick", fontsize=10)
            plt.ylabel("Conquest Events Count", fontsize=10)
            plt.xticks(rotation=0)
            plt.legend(title="Conquest Action", loc="upper left")
        else:
            plt.text(0.5, 0.5, "No conquests recorded during campaign ticks", ha="center", va="center")

        plt.title("Galactic Border Sovereignty Shifts", fontsize=14, color=self.primary_color, pad=15)
        plt.grid(True, linestyle="--", alpha=0.1)
        plt.tight_layout()

        path = os.path.join(output_dir, "territorial_changes.png")
        plt.savefig(path, dpi=150, facecolor=self.bg_color)
        plt.close()

    def plot_diplomacy_heatmap(self, output_dir: str) -> None:
        """Plot bilateral relationships matrix between major economic blocs or random superpowers sample."""
        relations_df = self._load_csv("diplomatic_relations.csv")
        empires_df = self._load_csv("empires.csv")

        plt.figure(figsize=(10, 8))

        if not relations_df.empty and not empires_df.empty:
            # Take top 15 empires by GDP to make heatmap readable
            top_empires = empires_df.sort_values(by="gdp", ascending=False).head(15)
            top_ids = list(top_empires["founding_civilization_id"])
            top_names = {row["founding_civilization_id"]: row["empire_name"][:15] for _, row in top_empires.iterrows()}

            # Filter relations
            filtered = relations_df[relations_df["empire_a"].isin(top_ids) & relations_df["empire_b"].isin(top_ids)]
            
            # Pivot table
            pivot = filtered.pivot(index="empire_a", columns="empire_b", values="relation_score").fillna(0)
            # Reorder indexes to match top_ids
            pivot = pivot.reindex(index=top_ids, columns=top_ids).fillna(0)
            
            # Rename headers
            pivot = pivot.rename(index=top_names, columns=top_names)

            sns.heatmap(pivot, cmap="coolwarm_r", vmin=-100, vmax=100, annot=True, fmt=".0f", 
                        cbar_kws={'label': 'Relation Score'}, annot_kws={"size": 8}, ax=plt.gca())
            plt.xlabel("Target Empire", fontsize=10)
            plt.ylabel("Source Empire", fontsize=10)
        else:
            plt.text(0.5, 0.5, "Bilateral Relations Matrix Missing", ha="center", va="center")

        plt.title("Superpowers Diplomatic Relations Heatmap", fontsize=14, color=self.primary_color, pad=15)
        plt.tight_layout()

        path = os.path.join(output_dir, "diplomacy_heatmap.png")
        plt.savefig(path, dpi=150, facecolor=self.bg_color)
        plt.close()

    def generate_war_timeline(self, output_dir: str) -> None:
        """Renders interactive HTML Timeline mapping political milestones and battles."""
        wars_df = self._load_csv("wars.csv")
        battles_df = self._load_csv("battles.csv")
        espionage_df = self._load_csv("espionage_operations.csv")
        empires_df = self._load_csv("empires.csv")

        emp_names = {}
        if not empires_df.empty:
            emp_names = empires_df.set_index("founding_civilization_id")["empire_name"].to_dict()

        events = []

        if not wars_df.empty:
            for _, row in wars_df.iterrows():
                year = float(row["start_year"])
                att_name = emp_names.get(str(row["attacker"]), str(row["attacker"]))
                def_name = emp_names.get(str(row["defender"]), str(row["defender"]))
                events.append({
                    "year": year,
                    "type": "War Declaration",
                    "badge": "danger",
                    "title": f"The War of {att_name} and {def_name}",
                    "desc": f"War declared due to {row['cause']}. Scale index calculated at {row['war_scale']}.",
                })

        if not battles_df.empty:
            for _, row in battles_df.iterrows():
                year = float(row["year"])
                att_name = emp_names.get(str(row["attacker_id"]), str(row["attacker_id"]))
                def_name = emp_names.get(str(row["defender_id"]), str(row["defender_id"]))
                events.append({
                    "year": year,
                    "type": "Interstellar Battle",
                    "badge": "warning",
                    "title": f"{row['battle_type']} in System {row['location_star_id']}",
                    "desc": f"Attacking fleets of {att_name} engaged defending forces of {def_name}. Casualties totaled {int(row['casualties']):,}.",
                })

        if not espionage_df.empty:
            for _, row in espionage_df.iterrows():
                # Caught spies only
                if not row["success"]:
                    year = int(row["tick"]) * 100
                    att_name = emp_names.get(str(row["attacker_id"]), str(row["attacker_id"]))
                    def_name = emp_names.get(str(row["target_id"]), str(row["target_id"]))
                    events.append({
                        "year": year,
                        "type": "Espionage Breach",
                        "badge": "info",
                        "title": f"Spy Network Discovered",
                        "desc": f"Counterintelligence teams in {def_name} intercepted a covert '{row['operation_type']}' operation by {att_name}.",
                    })

        # Sort events by year
        events.sort(key=lambda x: x["year"])

        # Create interactive HTML string
        html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Galactic Political & Conflict Timeline</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap" rel="stylesheet">
    <style>
        body {
            font-family: 'Inter', sans-serif;
            background-color: #0B0B1E;
            color: #E0E0FF;
            margin: 0;
            padding: 40px;
        }
        h1 {
            color: #00D2FF;
            text-align: center;
            font-size: 2.5em;
            margin-bottom: 5px;
        }
        .tagline {
            text-align: center;
            color: #A0A0C0;
            font-size: 1.1em;
            margin-bottom: 40px;
        }
        .timeline {
            position: relative;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px 0;
        }
        .timeline::before {
            content: '';
            position: absolute;
            width: 2px;
            background-color: #1E1E38;
            top: 0;
            bottom: 0;
            left: 50%;
            margin-left: -1px;
        }
        .container {
            padding: 15px 30px;
            position: relative;
            background-color: inherit;
            width: 42%;
        }
        .container::after {
            content: '';
            position: absolute;
            width: 12px;
            height: 12px;
            right: -6px;
            background-color: #0B0B1E;
            border: 3px solid #00D2FF;
            top: 25px;
            border-radius: 50%;
            z-index: 1;
        }
        .left {
            left: 0;
        }
        .right {
            left: 50%;
        }
        .right::after {
            left: -6px;
        }
        .content {
            padding: 20px;
            background-color: #11112C;
            position: relative;
            border-radius: 8px;
            border: 1px solid #1E1E38;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }
        .badge {
            display: inline-block;
            padding: 4px 8px;
            font-size: 0.8em;
            font-weight: 600;
            border-radius: 4px;
            margin-bottom: 10px;
            text-transform: uppercase;
        }
        .danger { background-color: #FF3366; color: white; }
        .warning { background-color: #FFA500; color: black; }
        .info { background-color: #00D2FF; color: black; }
        .year {
            font-size: 1.2em;
            font-weight: 700;
            color: #00D2FF;
            margin-bottom: 5px;
        }
        .title {
            font-size: 1.1em;
            font-weight: 600;
            margin-bottom: 8px;
            color: #FFFFFF;
        }
        .desc {
            font-size: 0.9em;
            color: #A0A0C0;
            line-height: 1.4;
        }
        @media screen and (max-width: 600px) {
            .timeline::before { left: 31px; }
            .container { width: 100%; padding-left: 70px; padding-right: 25px; }
            .container::after { left: 15px; }
            .left { left: 0; }
            .right { left: 0; }
        }
    </style>
</head>
<body>
    <h1>Galactic Conflict & Politics Timeline</h1>
    <div class="tagline">Interactive Log of Wars, Battles, and Espionage Discoveries</div>
    <div class="timeline">
"""

        for idx, ev in enumerate(events):
            side = "left" if idx % 2 == 0 else "right"
            badge_class = ev["badge"]
            
            html += f"""
        <div class="container {side}">
            <div class="content">
                <div class="year">Year {ev['year']:.0f}</div>
                <span class="badge {badge_class}">{ev['type']}</span>
                <div class="title">{ev['title']}</div>
                <div class="desc">{ev['desc']}</div>
            </div>
        </div>"""

        html += """
    </div>
</body>
</html>"""

        path = os.path.join(output_dir, "war_timeline.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    def _load_csv(self, filename: str) -> pd.DataFrame:
        path = os.path.join(self.datasets_dir, filename)
        if os.path.exists(path):
            return pd.read_csv(path)
        return pd.DataFrame()
