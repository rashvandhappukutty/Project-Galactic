# simulation/storytelling/chronicle_generator.py
"""Empire Chronicles Generator.
Generates comprehensive narrative histories for every major empire.
Outputs to datasets/empire_chronicles.csv.
"""

from __future__ import annotations
import os
import random
import pandas as pd
from typing import List, Dict, Any
from ..utils import write_csv, logger

class ChronicleGenerator:
    """Reconstructs the multi-era narrative chronicles of empires."""

    def __init__(self, seed: int = 42):
        self.random = random.Random(seed)

    def generate_chronicles(
        self, 
        empires: List[Dict[str, Any]], 
        lifecycles: List[Dict[str, Any]], 
        events: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Compiles structural narratives from lifecycle states and events for all empires."""
        logger.info("Generating empire chronicles...")
        chronicles: List[Dict[str, Any]] = []

        # Convert lifecycles to DataFrame for easier grouping
        lc_df = pd.DataFrame(lifecycles)
        events_df = pd.DataFrame(events)

        for emp in empires:
            emp_id = str(emp.get("founding_civilization_id", emp.get("civilization_id", "emp_unknown")))
            emp_name = str(emp.get("empire_name", emp.get("name", "Unnamed Empire")))

            # Filter lifecycle entries for this empire
            emp_lc = pd.DataFrame()
            if not lc_df.empty:
                emp_lc = lc_df[lc_df["empire_name"] == emp_name].sort_values(by="year")

            # Filter events for this empire
            emp_events = pd.DataFrame()
            if not events_df.empty:
                emp_events = events_df[
                    (events_df["empire"] == emp_name) | 
                    (events_df["participants"].astype(str).str.contains(emp_name, na=False))
                ].sort_values(by="year")

            # Reconstruct origin
            origin_desc = f"The {emp_name} was founded around Year 0, establishing its capital system. Out of simple tribal origins, its citizens built FTL vessels to claim space."
            if not emp_lc.empty:
                births = emp_lc[emp_lc["status"] == "Birth"]
                if not births.empty:
                    origin_desc = births.iloc[0]["description"]

            # Reconstruct expansion
            expansion_desc = f"As FTL routes expanded, the {emp_name} colonized surrounding sectors, claiming resources."
            if not emp_lc.empty:
                expansions = emp_lc[emp_lc["status"] == "Expansion"]
                if not expansions.empty:
                    expansion_desc = expansions.iloc[0]["description"]

            # Golden Age
            golden_desc = f"During a era of peace, the economy grew, and trade hubs flourished, cementing their status."
            if not emp_lc.empty:
                peaks = emp_lc[emp_lc["status"] == "Peak"]
                if not peaks.empty:
                    golden_desc = peaks.iloc[0]["description"]

            # Major Wars
            wars_desc = "Border disputes occasionally flared, resolved by defensive military operations."
            if not emp_events.empty:
                mil_evts = emp_events[emp_events["event_category"] == "Military"].head(2)
                if not mil_evts.empty:
                    wars_desc = " | ".join(mil_evts["description"].tolist())

            # Peak Influence
            peak_desc = f"At their zenith, the {emp_name} exerted significant economic and political influence."
            if not emp_lc.empty:
                peaks = emp_lc[emp_lc["status"] == "Peak"]
                if not peaks.empty:
                    peak_desc = f"Reaching peak GDP of {peaks.iloc[0]['gdp']} credits with colonies."

            # Decline
            decline_desc = "In later periods, trade routes decayed and external pressures reduced central authority."
            if not emp_lc.empty:
                declines = emp_lc[emp_lc["status"] == "Decline"]
                if not declines.empty:
                    decline_desc = declines.iloc[0]["description"]
                collapses = emp_lc[emp_lc["status"] == "Collapse"]
                if not collapses.empty:
                    decline_desc += " " + collapses.iloc[0]["description"]

            # Legacy
            legacy_desc = f"Today, the ruins of jump gates and structures of {emp_name} stand as monuments to their ancient legacy."
            if not emp_lc.empty:
                extinctions = emp_lc[emp_lc["status"] == "Extinction"]
                if not extinctions.empty:
                    legacy_desc = f"The civilization became extinct in Year {extinctions.iloc[0]['year']}. {extinctions.iloc[0]['description']}"

            chronicles.append({
                "empire_id": emp_id,
                "empire_name": emp_name,
                "origin_story": origin_desc,
                "expansion_era": expansion_desc,
                "golden_age": golden_desc,
                "major_wars": wars_desc,
                "peak_influence": peak_desc,
                "decline": decline_desc,
                "legacy": legacy_desc
            })

        # Save to datasets/empire_chronicles.csv
        out_path = os.path.join("datasets", "empire_chronicles.csv")
        header = [
            "empire_id", "empire_name", "origin_story", "expansion_era", 
            "golden_age", "major_wars", "peak_influence", "decline", "legacy"
        ]
        write_csv(out_path, chronicles, header)
        logger.info(f"Saved {len(chronicles)} empire chronicles to {out_path}")

        return chronicles
