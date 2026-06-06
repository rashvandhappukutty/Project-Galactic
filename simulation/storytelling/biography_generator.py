# simulation/storytelling/biography_generator.py
"""Historical Figures and Biography Generator.
Generates famous emperors, scientists, military leaders, diplomats, and explorers.
Outputs to datasets/historical_figures.csv.
"""

from __future__ import annotations
import os
import random
import pandas as pd
from typing import List, Dict, Any
from ..utils import write_csv, logger

class BiographyGenerator:
    """Procedurally generates notable historical figures from the galaxy's timeline."""

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)
        self.first_names = [
            "Telas", "Kaelen", "Valerius", "Zephyr", "Aethelgard", "Vanya", "Sariel", "Xerxes",
            "Cassian", "Lyra", "Eldrin", "Nyx", "Orion", "Thalia", "Kael", "Sylas", "Myra",
            "Rylan", "Elora", "Dorian", "Aurelia", "Caelum", "Jesper", "Vesper", "Sienna", "Taron"
        ]
        self.last_names = [
            "Vex", "Valerius", "Thorne", "Helios", "Kaelis", "Sterling", "Starfall", "Nox",
            "Aethel", "Sovereign", "Voidwalker", "Nova", "Starlight", "Skyward", "Sol", "Vanguard",
            "Rifts", "Storm", "Frost", "Ironclad", "Shadow", "Crown", "Dawn", "Apex", "Zenith"
        ]

        self.roles = ["Emperor", "Scientist", "Military Leader", "Explorer", "Diplomat"]

        self.achievement_templates = {
            "Emperor": [
                "Led the civilization during a golden age of economic expansion, doubling planetary GDP.",
                "Decreed the construction of defensive platforms across key FTL chokepoint systems.",
                "Unified multiple warring factions under a centralized federal sovereignty.",
                "Survived three major destabilization espionage operations planned by rival empires.",
                "Formed a lasting defensive coalition that successfully deterred external invasions."
            ],
            "Scientist": [
                "Discovered new sub-space anomalies that revolutionized hyperlane navigation calculations.",
                "Directed the engineering projects that completed the first Type II Dyson Swarm.",
                "Created advanced cybernetic upgrades that increased species intelligence and longevity.",
                "Pioneered FTL research that unlocked advanced shielding modules for combat fleets.",
                "Discovered ancient pre-space ruins containing lost technologies in deep space."
            ],
            "Military Leader": [
                "Commanded the forces that achieved victory in a legendary fleet battle in {location}.",
                "Successfully repelled a planetary invasion by rival coalition fleets, saving billions.",
                "Successfully coordinated deep space offensives that annexed three key resource sectors.",
                "Led the defense of a FTL jump gate system during a regional crisis.",
                "De-escalated potential civil conflict through decisive action against rogue factions."
            ],
            "Explorer": [
                "Mapped five previously uncharted wormhole connections in the outer galactic rim.",
                "First to land on and survey a highly habitable prime world, enabling immediate colonization.",
                "Discovered three new hyperlane FTL paths, shortening trade routes by decades.",
                "Survived a hazardous navigation crisis inside a collapsing gravitational nebula.",
                "Mapped the strategic chokepoints of the Perseus Arm, securing military logistics."
            ],
            "Diplomat": [
                "Negotiated a historic peace treaty ending a destructive multi-decade war.",
                "Drafted the original charter that established the first Galactic Federation.",
                "De-escalated severe trade conflicts through complex commercial agreements.",
                "Formed a network of trade and research agreements spanning three star sectors.",
                "Successfully exposed covert espionage networks before they could trigger war."
            ]
        }

    def generate_figures(self, empires: List[Dict[str, Any]], count: int = 1050) -> List[Dict[str, Any]]:
        """Generates a list of historical figures from the supplied empires."""
        figures: List[Dict[str, Any]] = []
        if not empires:
            logger.warning("No empires available. Using placeholder civilizations for figure generation.")
            empires = [{"empire_name": "Orion Council"}, {"empire_name": "Alpha Coalition"}]

        empire_names = [str(e.get("empire_name", e.get("name", "Empire"))) for e in empires]

        logger.info(f"Generating {count} historical figures...")

        for i in range(count):
            name = f"{self.random.choice(self.first_names)} {self.random.choice(self.last_names)}"
            civ = self.random.choice(empire_names)
            role = self.random.choice(self.roles)
            legacy_score = self.random.randint(20, 100)

            # Pick template and fill location placeholder if needed
            template = self.random.choice(self.achievement_templates[role])
            location = f"{self.random.choice(['Perseus', 'Sagittarius', 'Orion', 'Centauri'])} Sector"
            achievements = template.format(location=location)

            figures.append({
                "name": name,
                "civilization": civ,
                "role": role,
                "achievements": achievements,
                "legacy_score": legacy_score
            })

        # Save to datasets/historical_figures.csv
        out_path = os.path.join("datasets", "historical_figures.csv")
        header = ["name", "civilization", "role", "achievements", "legacy_score"]
        write_csv(out_path, figures, header)
        logger.info(f"Saved historical figures catalog to {out_path}")

        return figures
