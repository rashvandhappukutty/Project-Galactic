# simulation/storytelling/era_story_generator.py
"""Era Story Generator.
Compiles high-level narrative overviews and books for each historical era.
"""

from __future__ import annotations
import os
import pandas as pd
from typing import List, Dict, Any
from ..utils import logger

class EraStoryGenerator:
    """Fleshes out historical epochs into rich prose accounts."""

    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = datasets_dir

    def generate_era_stories(self) -> List[Dict[str, Any]]:
        """Reads classified era database and constructs narrative logs."""
        logger.info("Generating era stories...")
        era_stories: List[Dict[str, Any]] = []

        eras_path = os.path.join(self.datasets_dir, "era_history.csv")
        if not os.path.exists(eras_path):
            logger.warning("No era history database available.")
            return []

        df = pd.read_csv(eras_path)
        for _, row in df.iterrows():
            era_name = row["era_name"]
            start = row["start_year"]
            end = row["end_year"]
            dominant = row["dominant_empire"]
            major = row["major_events"]

            prose = f"The {era_name} (spanning Year {start} to Year {end}) was defined by critical shifts in the galactic balance of power. "
            
            if era_name == "Age of Exploration":
                prose += f"It was a time of daring scouting operations. Out of their homeworlds, empires launched scout fleets to map the hyperlanes. Dominant influence during this dawn was held by {dominant}."
            elif era_name == "Age of Colonization":
                prose += f"A massive wave of outward expansion occurred. Colony ships landed on rich habitability worlds, claiming territories. Led primarily by the expansionist push of {dominant}."
            elif era_name == "Age of Trade":
                prose += f"Economic networks flourished. Under commercial treaty organizations, fleets of freighters shuttled goods across jump gates, heavily influenced by the trade networks of {dominant}."
            elif era_name == "Age of Conflict":
                prose += f"Tensions over borders and resource scarcity erupted into destructive galactic wars. Battles raged in deep space systems. Under the military shadow of {dominant}, systems traded hands through conquest."
            elif era_name == "Age of Federations":
                prose += f"Political centralization reached its peak. Alliances merged into galactic federations, establishing peaceful treaties, directed by {dominant}."
            elif era_name == "Age of Megastructures":
                prose += f"The galaxy witnessed wonders of engineering. Dyson swarms, orbital habitats, and jump gate networks were completed under the industrial might of {dominant}."
            elif era_name == "Age of Transcendence":
                prose += f"Scientific breakthroughs pushed civilizations toward technological singularities. Tech levels peaked under the guidance of {dominant}."
            elif era_name == "Age of Collapse":
                prose += f"Crises, AI uprisings, and economic market crashes fragmented empires. Power slipped away as {dominant} and others faced system fragmentation."
            else:
                prose += f"A era of steady expansion and consolidation, dominated by {dominant}."

            prose += f" Notable turning points during this epoch included: {major}."

            era_stories.append({
                "era_name": era_name,
                "start_year": start,
                "end_year": end,
                "dominant_empire": dominant,
                "story_narrative": prose
            })

        return era_stories
