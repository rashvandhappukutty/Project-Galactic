# simulation/history/era_classifier.py
"""Era Classification Engine.
Segments galactic history into thematic eras based on event densities.
Outputs to datasets/era_history.csv.
"""

from __future__ import annotations
import os
import pandas as pd
from typing import List, Dict, Any
from ..utils import write_csv, logger

class EraClassifier:
    """Classifies segments of galactic history into developmental epochs."""

    def __init__(self, datasets_dir: str = "datasets", window_size: int = 500):
        self.datasets_dir = datasets_dir
        self.window_size = window_size

    def classify_eras(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Segments history into eras based on event distributions over time windows."""
        if not events:
            logger.warning("No events available to classify eras.")
            return []

        # Sort events by year
        sorted_events = sorted(events, key=lambda x: x["year"])
        start_year = sorted_events[0]["year"]
        end_year = sorted_events[-1]["year"]

        # Ensure we have at least one window
        if end_year == start_year:
            end_year = start_year + self.window_size

        eras: List[Dict[str, Any]] = []
        current_year = start_year

        # 1. Classify each window
        while current_year <= end_year:
            window_end = current_year + self.window_size
            window_events = [e for e in sorted_events if current_year <= e["year"] < window_end]

            if not window_events:
                # If no events, classify as Expansion or same as last
                era_name = eras[-1]["era_name"] if eras else "Age of Exploration"
                dominant = "None"
                major = "Peaceful vacuum."
            else:
                era_name, dominant, major = self._analyze_window(window_events, current_year)

            eras.append({
                "era_name": era_name,
                "start_year": current_year,
                "end_year": window_end,
                "dominant_empire": dominant,
                "major_events": major
            })
            current_year = window_end

        # 2. Merge contiguous duplicate eras to create cleaner blocks
        merged_eras: List[Dict[str, Any]] = []
        for era in eras:
            if not merged_eras:
                merged_eras.append(era)
            else:
                last_era = merged_eras[-1]
                if last_era["era_name"] == era["era_name"]:
                    # Merge
                    last_era["end_year"] = era["end_year"]
                    # Combined dominant empire logic: choose the one with longer dominance or merge
                    if last_era["dominant_empire"] == "None":
                        last_era["dominant_empire"] = era["dominant_empire"]
                    # Concat major events
                    last_era["major_events"] += f" | {era['major_events']}"
                else:
                    merged_eras.append(era)

        # Truncate final end_year to max event year
        if merged_eras:
            merged_eras[-1]["end_year"] = max(merged_eras[-1]["end_year"], sorted_events[-1]["year"])

        # 3. Save to datasets/era_history.csv
        out_path = os.path.join(self.datasets_dir, "era_history.csv")
        header = ["era_name", "start_year", "end_year", "dominant_empire", "major_events"]
        write_csv(out_path, merged_eras, header)
        logger.info(f"Saved era history classification to {out_path}")

        return merged_eras

    def _analyze_window(self, window_events: List[Dict[str, Any]], start_year: int) -> tuple[str, str, str]:
        """Classify a single window based on categories of events."""
        category_counts = {
            "Civilization": 0,
            "Colonization": 0,
            "Economy": 0,
            "Logistics": 0,
            "Military": 0,
            "Diplomacy": 0,
            "Espionage": 0,
            "Science": 0,
            "Crisis": 0
        }
        empire_counts: Dict[str, int] = {}
        top_events = sorted(window_events, key=lambda x: x["impact_score"], reverse=True)

        for event in window_events:
            cat = event.get("event_category", "Civilization")
            if cat in category_counts:
                category_counts[cat] += 1
            
            # Count dominant empires
            emp = event.get("empire")
            if emp and emp != "Unknown" and emp != "Galaxy":
                empire_counts[emp] = empire_counts.get(emp, 0) + 1
            part = event.get("participants")
            if part and part != "Unknown" and part != "":
                for p in part.split("|"):
                    p_clean = p.strip()
                    if p_clean:
                        empire_counts[p_clean] = empire_counts.get(p_clean, 0) + 1

        # Determine dominant empire
        dominant_empire = "None"
        if empire_counts:
            dominant_empire = max(empire_counts, key=empire_counts.get)

        # Classification rules
        total = len(window_events)
        mil_ratio = category_counts["Military"] / total if total > 0 else 0
        col_ratio = category_counts["Colonization"] / total if total > 0 else 0
        dip_ratio = category_counts["Diplomacy"] / total if total > 0 else 0
        eco_ratio = category_counts["Economy"] / total if total > 0 else 0

        # High-level era name decisions
        if start_year < 1000:
            era_name = "Age of Exploration"
        elif col_ratio > 0.35:
            era_name = "Age of Colonization"
        elif mil_ratio > 0.40:
            era_name = "Age of Conflict"
        elif dip_ratio > 0.30:
            era_name = "Age of Federations"
        elif eco_ratio > 0.25:
            era_name = "Age of Trade"
        elif any("megastructure" in e["description"].lower() for e in window_events):
            era_name = "Age of Megastructures"
        elif any("transcendence" in e["description"].lower() or "singularity" in e["description"].lower() for e in window_events):
            era_name = "Age of Transcendence"
        elif any("crisis" in e["description"].lower() or "collapse" in e["description"].lower() for e in window_events):
            era_name = "Age of Collapse"
        else:
            era_name = "Age of Expansion"

        # Summarize top 2 events
        summaries = []
        for e in top_events[:2]:
            tstamp = e.get('timestamp', f"Year {e.get('year', 0)}")
            summaries.append(f"{e.get('event_type', 'Event')} ({tstamp}): {e.get('description', '')[:60]}...")
        major_events_str = " | ".join(summaries) if summaries else "Routine galactic cycles."

        return era_name, dominant_empire, major_events_str
