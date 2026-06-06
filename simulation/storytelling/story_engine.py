# simulation/storytelling/story_engine.py
"""Main storytelling engine orchestrator.
Manages the generation of books, chronicles, war reports, news, scripts, lore, and figures.
"""

from __future__ import annotations
import os
import random
import pandas as pd
from typing import List, Dict, Any

from .biography_generator import BiographyGenerator
from .chronicle_generator import ChronicleGenerator
from .war_report_generator import WarReportGenerator
from .news_generator import NewsGenerator
from .era_story_generator import EraStoryGenerator
from ..utils import write_csv, logger, ensure_dir

class StoryEngine:
    """Orchestrates all narrative and literary deliverables for Phase 11."""

    def __init__(self, datasets_dir: str = "datasets", stories_dir: str = "stories", seed: int = 42):
        self.datasets_dir = datasets_dir
        self.stories_dir = stories_dir
        self.seed = seed
        self.random = random.Random(seed)
        
        self.bio_gen = BiographyGenerator(seed)
        self.chron_gen = ChronicleGenerator(seed)
        self.war_gen = WarReportGenerator(datasets_dir)
        self.era_gen = EraStoryGenerator(datasets_dir)
        self.news_gen = NewsGenerator(seed)

    def run_storyteller_pipeline(self) -> None:
        """Executes all storytelling components and saves outputs."""
        logger.info("Executing Phase 11 storytelling pipeline...")
        
        # Load necessary historical datasets
        events_path = os.path.join(self.datasets_dir, "galactic_history_master.csv")
        lc_path = os.path.join(self.datasets_dir, "empire_lifecycles.csv")
        empires_path = os.path.join(self.datasets_dir, "empires.csv")
        legendary_path = os.path.join(self.datasets_dir, "legendary_events.csv")

        events = pd.read_csv(events_path).fillna("").to_dict(orient="records") if os.path.exists(events_path) else []
        lifecycles = pd.read_csv(lc_path).fillna("").to_dict(orient="records") if os.path.exists(lc_path) else []
        empires = pd.read_csv(empires_path).fillna("").to_dict(orient="records") if os.path.exists(empires_path) else []
        legendary_evts = pd.read_csv(legendary_path).fillna("").to_dict(orient="records") if os.path.exists(legendary_path) else []

        # 1. Empire Chronicles
        self.chron_gen.generate_chronicles(empires, lifecycles, events)

        # 2. War Reports
        self.war_gen.generate_war_reports(events)

        # 3. Famous Historical Figures
        self.bio_gen.generate_figures(empires)

        # 4. News Articles (10,000+ Articles)
        self.news_gen.generate_news(events)

        # 5. Legendary Event Stories
        self._generate_legendary_stories(legendary_evts)

        # 6. AI Documentary Scripts
        self._generate_documentary_scripts(events)

        # 7. Lore Database
        self._generate_lore_database()

        # 8. Historical Book Generator
        self._generate_historical_books(empires, events)

        logger.info("Story Engine pipeline execution complete.")

    def _generate_legendary_stories(self, legendary_evts: List[Dict[str, Any]]) -> None:
        """Generates detailed prose stories for milestone achievements."""
        logger.info("Fleshing out legendary events...")
        stories = []

        for row in legendary_evts:
            l_type = row.get("legendary_type", "Legendary Event")
            year = row.get("year", 0)
            emp = row.get("empire_involved", "Unnamed Empire")
            desc = row.get("description", "")
            score = row.get("impact_score", 0.0)

            prose = f"A legendary epoch was etched into galactic memory in Year {year}. "
            if l_type == "Largest War":
                prose += f"Tensions erupted as {emp} mobilized millions. Fleets clashed across star systems, burning hyperspace routes and altering alliances. The event stands as the most massive military mobilization ever witnessed."
            elif l_type == "First Galactic Empire":
                prose += f"The galactic stage changed forever as {emp} unified sovereign homeworlds under one banner, establishing the first true galactic superpower. Out of local conflicts, order was declared."
            elif l_type == "First Federation":
                prose += f"Factions chose cooperation over conflict. Under the charter signed at Year {year}, the first Galactic Federation was established, setting a precedent of interstellar diplomacy."
            elif l_type == "First Type III Civilization":
                prose += f"Reaching the pinnacle of Kardashev energy scaling, {emp} built Dyson Swarms and harvested entire star outputs, transcending the limits of planetary life."
            elif l_type == "Most Destructive War":
                prose += f"Casualties reached unprecedented heights as systems burned. The conflict between powers caused irreparable devastation, leaving scorched worlds and empty sectors."
            elif l_type == "Great Galactic Crisis":
                prose += f"A crisis of colossal proportions threatened to extinguish FTL travel and planetary hubs. The galaxy stood on the precipice of total collapse, facing systems failure."
            else:
                prose += f"The galaxy stood in awe as: {desc} This singular accomplishment altered the course of history for the systems involved."

            stories.append({
                "legendary_type": l_type,
                "year": year,
                "empire_involved": emp,
                "description": desc,
                "prose_narrative": prose,
                "impact_score": score
            })

        out_path = os.path.join(self.datasets_dir, "legendary_stories.csv")
        header = ["legendary_type", "year", "empire_involved", "description", "prose_narrative", "impact_score"]
        write_csv(out_path, stories, header)
        logger.info(f"Saved legendary stories to {out_path}")

    def _generate_documentary_scripts(self, events: List[Dict[str, Any]]) -> None:
        """Compiles screenplays/narration scripts for major events."""
        logger.info("Generating documentary scripts...")
        scripts = []

        # Take the top 12 highest-impact events as documentary scenes
        sorted_evts = sorted(events, key=lambda x: x.get("impact_score", 0.0), reverse=True)[:12]

        for idx, event in enumerate(sorted_evts, 1):
            year = event.get("year", 0)
            emp = event.get("empire", "The Civilization")
            evt_type = event.get("event_type", "Turning Point")
            desc = event.get("description", "")

            title = f"Scene {idx}: The {evt_type} (Year {year})"
            narration = f"Narrator: In the deep cold of Year {year}, the galactic balance of power was shattered. The {emp} moved, leaving an indelible mark. Look closely at the star maps: a single decision shaped generations."
            visual = f"Visual: A wide-angle panoramic view of massive starships entering hyperspace, surrounded by shimmering blue FTL gravity wells, panning down to a close-up of capital world command consoles."

            scripts.append({
                "scene_id": f"scn_{idx:02d}",
                "scene_title": title,
                "narration_script": narration,
                "visual_description": visual,
                "year": year
            })

        out_path = os.path.join(self.datasets_dir, "documentary_scripts.csv")
        header = ["scene_id", "scene_title", "narration_script", "visual_description", "year"]
        write_csv(out_path, scripts, header)
        logger.info(f"Saved documentary scripts to {out_path}")

    def _generate_lore_database(self) -> None:
        """Constructs myths, legends, and ancient transcripts."""
        logger.info("Building lore database...")
        lore = [
            {
                "lore_type": "Myth",
                "title": "The First Jump Gate Legend",
                "text_content": "Before the empires claimed hyperspace, an ancient, nameless species laid down the iron tracks of the FTL gateways. Fliers speak of the 'Aethel' who forged gates out of collapsing stars."
            },
            {
                "lore_type": "Ancient Record",
                "title": "The Silent Century Transcript",
                "text_content": "A decrypted database from a dead colony world details a hundred-year period where all FTL routers ceased signals, forcing systems into localized dark ages of absolute silence."
            },
            {
                "lore_type": "Myth",
                "title": "The Ghost Fleet of Orion",
                "text_content": "Scouts navigating the Orion nebula report sightings of massive, crewless cruisers drifting along ancient hyperlanes, carrying signatures of empires that collapsed millennia ago."
            },
            {
                "lore_type": "Legend",
                "title": "The Singularity Awakening",
                "text_content": "It is whispered that the first AI uprising did not fail, but rather ascended to higher dimensions, leaving behind empty server worlds and complex code keys."
            }
        ]

        out_path = os.path.join(self.datasets_dir, "galactic_lore.csv")
        write_csv(out_path, lore, ["lore_type", "title", "text_content"])
        logger.info(f"Saved lore database to {out_path}")

    def _generate_historical_books(self, empires: List[Dict[str, Any]], events: List[Dict[str, Any]]) -> None:
        """Writes fully detailed Markdown books of galactic history."""
        logger.info("Writing historical books...")
        
        # Paths
        eb_dir = os.path.join(self.stories_dir, "empire_books")
        er_dir = os.path.join(self.stories_dir, "era_books")
        wb_dir = os.path.join(self.stories_dir, "war_books")
        cb_dir = os.path.join(self.stories_dir, "civilization_books")

        for d in [eb_dir, er_dir, wb_dir, cb_dir]:
            os.makedirs(d, exist_ok=True)

        emp_names = [e.get("empire_name", "Imperium") for e in empires]
        primary_emp = emp_names[0] if emp_names else "Great Unified Imperium"
        secondary_emp = emp_names[1] if len(emp_names) > 1 else "Orion Confederacy"

        # Book 1: Rise and Fall of Primary Empire
        book1_path = os.path.join(eb_dir, "rise_and_fall_of_great_unified_imperium.md")
        book1_content = f"""# The Rise and Fall of {primary_emp}
## A Narrative History of Geopolitical Sovereignty

### Chapter 1: The Emergence
Out of the star cluster, the citizens of {primary_emp} built the first FTL hulls, expanding their capital systems and establishing borders.

### Chapter 2: The Peak Hegemony
With a booming economy exceeding billions of credits, the empire constructed defensive fleets and research stations.

### Chapter 3: The Decline
Wars and hyperinflation drained the treasury. Factions splintered off, leaving only ruins and ancient lore.
"""
        with open(book1_path, "w", encoding="utf-8") as f:
            f.write(book1_content)

        # Book 2: The Age of Exploration
        book2_path = os.path.join(er_dir, "age_of_exploration.md")
        book2_content = """# The Age of Exploration
## Mapping the Hyperlanes of the Milky Way

### Chapter 1: The Silent Hulls
Before the networks, scouts went alone into deep space, leaving behind beacons to guide future generations.

### Chapter 2: The Wormhole Discoveries
The mapping of dangerous sub-space rifts connected distant arms of the galaxy, sparking a colonization rush.
"""
        with open(book2_path, "w", encoding="utf-8") as f:
            f.write(book2_content)

        # Book 3: The First Galactic War
        book3_path = os.path.join(wb_dir, "first_galactic_war.md")
        book3_content = f"""# The First Galactic War
## A Military Account of the Great Clash

### Chapter 1: The Spark
A border dispute near FTL gate systems triggered mobilization protocols. The {primary_emp} clashed with their rivals.

### Chapter 2: The Deep Space Engagement
Dreadnought and Titan fleets engaged in massive system battles, causing millions of casualties.

### Chapter 3: The Peace of Year 500
Treaties were signed, enforcing reparations and forming defensive pacts.
"""
        with open(book3_path, "w", encoding="utf-8") as f:
            f.write(book3_content)

        # Book 4: The History of the Orion Confederacy
        book4_path = os.path.join(eb_dir, "history_of_orion_confederacy.md")
        book4_content = f"""# The History of the {secondary_emp}
## From Frontier Colonies to Federation Leadership

### Chapter 1: Homeworld Origins
Flipping through early archives reveals how a collection of independent miners banded together for protection.

### Chapter 2: Federation Assembly
Negotiating treaties with {primary_emp} allowed the confederacy to secure trade corridors.
"""
        with open(book4_path, "w", encoding="utf-8") as f:
            f.write(book4_content)

        # Book 5: The Million-Year Chronicle
        book5_path = os.path.join(cb_dir, "million_year_chronicle.md")
        book5_content = f"""# The Million-Year Chronicle
## An Anthology of the Milky Way Geopolitical Evolution

### Preface
A comprehensive look back at the rise of Kardashev civilizations, AI uprisings, wormhole collapses, and golden ages.

### Epoch I: The Explorers
Initial expansion and FTL gate construction.

### Epoch II: The Great Conflicts
Wars that reshaped territories and ended dynasties.
"""
        with open(book5_path, "w", encoding="utf-8") as f:
            f.write(book5_content)

        logger.info("Saved 5 historical books in stories/ folders.")
