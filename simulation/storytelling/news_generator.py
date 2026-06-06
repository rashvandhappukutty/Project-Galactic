# simulation/storytelling/news_generator.py
"""Galactic News Network Article Generator.
Generates breaking news updates, political bulletins, and scientific reports.
Outputs to datasets/galactic_news.csv.
"""

from __future__ import annotations
import os
import random
import pandas as pd
from typing import List, Dict, Any
from ..utils import write_csv, logger

class NewsGenerator:
    """Simulates a real-time breaking news agency covering galactic events."""

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)
        self.categories = ["Breaking News", "Political Update", "Economic Report", "Scientific Discovery", "Military Bulletin"]

        # Fictional spokespersons by role
        self.spokespersons = {
            "Military": ["General Kaelen Thorne", "Fleet Admiral Cassian Nox", "Marshal Valerius Sterling"],
            "Political": ["Chancellor Telas Vex", "Consul Lyra Sovereign", "Prime Minister Sylas Rifts"],
            "Economic": ["Director Sienna Apex", "Treasurer Jesper Dawn", "Minister Taron Zenith"],
            "Scientific": ["Dr. Eldrin Voidwalker", "Professor Nyx Starfall", "Lead Engineer Zephyr Nova"]
        }

        # Quotes templates
        self.quotes = {
            "Military": [
                "Our space patrols will secure the sector at all costs.",
                "Tactical fleet coordination achieved our objective with minimal losses.",
                "Aggressors will find our defensive perimeter impregnable."
            ],
            "Political": [
                "This treaty marks the beginning of a secure alliance.",
                "Central authority will maintain stability across all colonies.",
                "Diplomacy remains our strongest shield in these uncertain times."
            ],
            "Economic": [
                "New FTL trade corridors will bolster local credits flow.",
                "Inflationary pressures are under control; market prices remain stable.",
                "Investment in infrastructure is paying off handsomely."
            ],
            "Scientific": [
                "This scientific breakthrough changes our understanding of sub-space travel.",
                "The completion of this megastructure project is a triumph of engineering.",
                "We are one step closer to becoming a Type III civilization."
            ]
        }

    def generate_news(self, events: List[Dict[str, Any]], target_count: int = 10100) -> List[Dict[str, Any]]:
        """Transforms timeline events into news articles and pads with generic news bulletins."""
        logger.info(f"Generating {target_count} news articles...")
        articles: List[Dict[str, Any]] = []

        # Convert events into articles
        for idx, event in enumerate(events):
            if len(articles) >= target_count:
                break

            year = event.get("year", 0)
            emp = event.get("empire", "Galaxy")
            part = event.get("participants", "Rival Factions")
            loc = event.get("location", "Deep Space")
            desc = event.get("description", "")
            cat = event.get("event_category", "Civilization")

            # Determine category
            news_cat = "Breaking News"
            role_key = "Political"
            if cat == "Military":
                news_cat = "Military Bulletin"
                role_key = "Military"
            elif cat == "Economy":
                news_cat = "Economic Report"
                role_key = "Economic"
            elif cat == "Science":
                news_cat = "Scientific Discovery"
                role_key = "Scientific"
            elif cat == "Diplomacy":
                news_cat = "Political Update"
                role_key = "Political"

            # Create procedural quotes
            spokesperson = self.random.choice(self.spokespersons[role_key])
            quote = f'"{self.random.choice(self.quotes[role_key])}"'

            headline = f"BREAKING: Event in the {loc} Sector!"
            if cat == "Military":
                headline = f"MILITARY BULLETIN: Force clash in {loc}!"
            elif cat == "Diplomacy":
                headline = f"DIPLOMATIC REPORT: {emp} Signs Agreement!"
            elif cat == "Science":
                headline = f"SCIENTIFIC REPORT: {emp} Achieves Breakthrough!"
            elif cat == "Economy":
                headline = f"FINANCIAL REPORT: Trade corridor opened by {emp}!"

            body = f"On Year {year}, the Galactic News Network reports that: {desc} Speaking on the situation, {spokesperson} remarked, {quote} Analysts suggest this will have long-term consequences for the local star systems."

            articles.append({
                "article_id": f"art_{idx:06d}",
                "year": year,
                "category": news_cat,
                "headline": headline,
                "body": body,
                "spokesperson": spokesperson
            })

        # Pad with procedural filler bulletins if target_count is not met
        filler_idx = len(articles)
        while len(articles) < target_count:
            year = self.random.randint(100, 100000)
            news_cat = self.random.choice(self.categories)
            role_key = "Political"
            if "Military" in news_cat:
                role_key = "Military"
            elif "Economic" in news_cat:
                role_key = "Economic"
            elif "Scientific" in news_cat:
                role_key = "Scientific"

            spokesperson = self.random.choice(self.spokespersons[role_key])
            quote = f'"{self.random.choice(self.quotes[role_key])}"'
            loc = f"Sector {self.random.randint(100, 999)}"

            headline = f"BREAKING NEWS: Developments reported in {loc}!"
            body = f"Reports reaching our galactic bureaus in {loc} indicate shifting conditions. Factions are currently evaluating regional security. {spokesperson} issued a brief statement: {quote} More details to follow."

            articles.append({
                "article_id": f"art_{filler_idx:06d}",
                "year": year,
                "category": news_cat,
                "headline": headline,
                "body": body,
                "spokesperson": spokesperson
            })
            filler_idx += 1

        # Save to datasets/galactic_news.csv
        out_path = os.path.join("datasets", "galactic_news.csv")
        header = ["article_id", "year", "category", "headline", "body", "spokesperson"]
        write_csv(out_path, articles, header)
        logger.info(f"Saved {len(articles)} news articles to {out_path}")

        return articles
