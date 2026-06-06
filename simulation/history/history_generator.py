# simulation/history/history_generator.py
"""Procedural history generator for long-term galactic simulation.
Creates realistic historical events across deep time.
"""

from __future__ import annotations
import random
from typing import List, Dict, Any
from ..utils import logger

class HistoryGenerator:
    """Procedurally simulates events for deep time spans (up to millions of years)."""

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)
        # Event templates and categories
        self.templates = {
            "Military": [
                "In Year {year}, the {empire} launched a surprise offensive against {participants} over territorial claims in the {location} sector.",
                "In Year {year}, a devastating fleet battle occurred in the {location} system where the forces of {empire} clashed with {participants}.",
                "In Year {year}, {empire} successfully annexed colonies of {participants} after a siege on their outer defense platforms.",
                "In Year {year}, a skirmish broke out in {location} between {empire} patrols and {participants} raiders.",
                "In Year {year}, the joint fleets of {empire} and {participants} conducted a major peacekeeping operation in {location}."
            ],
            "Diplomacy": [
                "In Year {year}, the {empire} and {participants} signed the historic Treaty of {location}, establishing a formal alliance.",
                "In Year {year}, diplomatic relations between {empire} and {participants} soured following a border dispute near {location}.",
                "In Year {year}, the {empire} and {participants} formed a unified economic bloc during the Summit of {location}.",
                "In Year {year}, {empire} acted as a peace mediator between {participants} and local independent factions."
            ],
            "Economy": [
                "In Year {year}, a gold rush of rare FTL fuel elements triggered an economic boom for {empire} in the {location} system.",
                "In Year {year}, {empire} experienced a massive hyperinflation crisis, destabilizing trade routes across {location}.",
                "In Year {year}, industrial megacorporations in {empire} completed a major FTL trade hub in {location}, boosting GDP.",
                "In Year {year}, resource depletion in the {location} sector caused trade disruptions for {empire}."
            ],
            "Science": [
                "In Year {year}, researchers in {empire} achieved a major scientific breakthrough in FTL navigation, shortening transit times.",
                "In Year {year}, the {empire} completed the construction of a stellar observatory in {location}, discovering new hyperspace routes.",
                "In Year {year}, a breakthrough in zero-point energy generation in {empire} boosted industrial capacity.",
                "In Year {year}, {empire} successfully completed a Kardashev Type II Dyson Swarm project around the star {location}."
            ],
            "Crisis": [
                "In Year {year}, a rogue AI network in {empire} initiated a localized machine uprising, causing widespread panic in {location}.",
                "In Year {year}, a mysterious cosmic pandemic swept through {location}, affecting the populations of {empire} and {participants}.",
                "In Year {year}, the FTL jump gate in {location} suffered a critical containment breach, isolating several systems.",
                "In Year {year}, a catastrophic solar flare in {location} destroyed major surface infrastructure belonging to {empire}."
            ],
            "Colonization": [
                "In Year {year}, colonial fleets from {empire} successfully terraformed and settled the prime world of {location}.",
                "In Year {year}, {empire} established a science outpost on a hostile frozen planet in the {location} system.",
                "In Year {year}, a joint colony was founded in {location} by settlers from both {empire} and {participants}."
            ]
        }

        # Event type map for categorization
        self.event_types = {
            "Military": ["Deep Space Engagement", "Orbital Battle", "War Declaration", "War End", "Colony Assault", "Planetary Invasion"],
            "Diplomacy": ["Alliance Formation", "Defense Pact", "Galactic Federation", "Peace Treaty Signing"],
            "Economy": ["Economic Event", "Trade Agreement", "Market Crash", "Economic Collapse"],
            "Science": ["Scientific Breakthrough", "Megastructure Completion"],
            "Crisis": ["AI Uprising", "Wormhole Collapse", "FTL Network Failure", "Resource Catastrophe", "Pandemic Event", "Refugee Crisis"],
            "Colonization": ["Colonization"]
        }

        # Location name generators
        self.system_suffixes = ["Prime", "Minor", "Major", "Beta", "Sigma", "Nebula", "Expanse", "Reach", "Arm"]
        self.system_names = [
            "Perseus", "Sagittarius", "Orion", "Centauri", "Vega", "Sirius", "Aldebaran", "Antares", 
            "Betelgeuse", "Rigel", "Polaris", "Arcturus", "Capella", "Procyon", "Castor", "Pollux"
        ]

    def generate_random_location(self) -> str:
        """Generates a procedural star system/sector name."""
        return f"{self.random.choice(self.system_names)} {self.random.choice(self.system_suffixes)}"

    def simulate_procedural_history(
        self, 
        start_year: int, 
        end_year: int, 
        empires: List[Dict[str, Any]], 
        acceleration: int = 100
    ) -> List[Dict[str, Any]]:
        """Simulates procedural history from start_year to end_year using macro-ticks."""
        procedural_events: List[Dict[str, Any]] = []
        if not empires:
            logger.warning("No empires supplied to procedural generator.")
            return []

        empire_names = [str(e.get("empire_name", e.get("name", "Empire"))) for e in empires]
        logger.info(f"Generating procedural history from Year {start_year} to Year {end_year}...")

        # Calculate density: scale events based on total years to keep dataset size under control
        total_years = end_year - start_year
        if total_years <= 1000:
            events_per_tick = 5
        elif total_years <= 10000:
            events_per_tick = 3
        elif total_years <= 100000:
            events_per_tick = 2
        else:
            events_per_tick = 1

        current_year = start_year
        while current_year < end_year:
            # We step by acceleration (e.g., 50 or 100 years per tick)
            tick_step = self.random.randint(max(10, acceleration // 2), max(20, acceleration))
            current_year += tick_step
            if current_year > end_year:
                break

            # Generate a few events for this year
            num_events = self.random.randint(1, events_per_tick)
            for _ in range(num_events):
                category = self.random.choice(list(self.templates.keys()))
                event_type = self.random.choice(self.event_types[category])
                template = self.random.choice(self.templates[category])

                # Pick primary empire
                emp = self.random.choice(empire_names)
                # Pick participant (must be different)
                other_empires = [e for e in empire_names if e != emp]
                participant = self.random.choice(other_empires) if other_empires else ""

                location = self.generate_random_location()
                desc = template.format(
                    year=current_year,
                    empire=emp,
                    participants=participant,
                    location=location
                )

                procedural_events.append({
                    "event_id": f"prc_{self.random.randint(100000, 999999)}",
                    "year": current_year,
                    "timestamp": f"Year {current_year}",
                    "event_type": event_type,
                    "event_category": category,
                    "empire": emp,
                    "participants": participant,
                    "location": location,
                    "impact_score": 0.0,  # scored later
                    "historical_significance": "Minor",  # scored later
                    "description": desc
                })

        logger.info(f"Generated {len(procedural_events)} procedural events for timeline extension.")
        return procedural_events
