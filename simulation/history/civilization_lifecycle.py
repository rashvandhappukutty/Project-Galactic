# simulation/history/civilization_lifecycle.py
"""Tracks civilization lifecycle stages: Birth, Expansion, Peak, Decline, Collapse, Extinction, Rebirth.
Outputs to datasets/empire_lifecycles.csv.
"""

from __future__ import annotations
import os
import pandas as pd
from typing import List, Dict, Any
from ..utils import write_csv, logger

class CivilizationLifecycleEngine:
    """Tracks state transitions of empires across simulated history."""

    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = datasets_dir
        self.lifecycle_records: List[Dict[str, Any]] = []

    def run_lifecycle_analysis(self, master_events: List[Dict[str, Any]], empires_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Processes events in chronological order to detect state transitions for each empire."""
        # 1. Initialize trackers for each empire and build a multi-key lookup
        lookup: Dict[str, Dict[str, Any]] = {}
        for emp in empires_list:
            emp_id = str(emp.get("founding_civilization_id", emp.get("civilization_id", "emp_unknown")))
            emp_name = str(emp.get("empire_name", emp.get("name", "Unnamed Empire")))
            
            # Prevent empty trackers
            if not emp_id or not emp_name:
                continue

            tracker = {
                "empire_id": emp_id,
                "empire_name": emp_name,
                "status": "Birth",
                "birth_year": 0,
                "peak_year": 0,
                "peak_gdp": float(emp.get("gdp", 1e9)),
                "current_gdp": float(emp.get("gdp", 1e9)),
                "colonies_count": 1,
                "decline_year": 0,
                "collapse_year": 0,
                "is_active": True,
            }
            
            lookup[emp_name] = tracker
            lookup[emp_id] = tracker
            civ_name = str(emp.get("civilization_name", ""))
            if civ_name:
                lookup[civ_name] = tracker

            # Record initial birth state
            self.lifecycle_records.append({
                "empire_id": emp_id,
                "empire_name": emp_name,
                "status": "Birth",
                "year": 0,
                "gdp": float(emp.get("gdp", 1e9)),
                "population": float(emp.get("population", 1e9)),
                "colonies": 1,
                "description": f"The {emp_name} emerges in the galaxy, establishing its capital at {emp.get('capital_world', 'its homeworld')}.",
            })

        # Sort events by year
        sorted_events = sorted(master_events, key=lambda x: x["year"])

        # 2. Iterate through history and evaluate state transitions
        for event in sorted_events:
            year = event["year"]
            emp_name = str(event.get("empire", ""))
            target = str(event.get("participants", ""))
            evt_type = event["event_type"]
            desc = event["description"]

            # Process primary empire
            if emp_name and emp_name in lookup:
                tracker = lookup[emp_name]
                self._update_empire_state(tracker, evt_type, desc, year, is_primary=True)

            # Process secondary empire/participant if applicable
            if target and target in lookup:
                tracker = lookup[target]
                self._update_empire_state(tracker, evt_type, desc, year, is_primary=False)

        # 3. Write output to datasets/empire_lifecycles.csv
        out_path = os.path.join(self.datasets_dir, "empire_lifecycles.csv")
        if self.lifecycle_records:
            header = ["empire_id", "empire_name", "status", "year", "gdp", "population", "colonies", "description"]
            write_csv(out_path, self.lifecycle_records, header)
        else:
            # Empty fallback
            pd.DataFrame(columns=["empire_id", "empire_name", "status", "year", "gdp", "population", "colonies", "description"]).to_csv(out_path, index=False)

        logger.info(f"Saved empire lifecycles to {out_path}")
        return self.lifecycle_records

    def _update_empire_state(self, tracker: Dict[str, Any], evt_type: str, desc: str, year: int, is_primary: bool):
        """Helper to transition states based on events."""
        emp_name = tracker["empire_name"]
        emp_id = tracker["empire_id"]
        current_status = tracker["status"]

        new_status = None
        transition_desc = ""

        # Logic for transitions
        if evt_type == "Colonization" and current_status in ["Birth", "Collapse", "Decline"]:
            tracker["colonies_count"] += 1
            new_status = "Expansion"
            transition_desc = f"The {emp_name} enters an expansionist phase, establishing new colonies and expanding its territorial footprint."
        
        elif evt_type == "War Declaration" and is_primary and current_status == "Expansion":
            # Expansion can lead to a Peak if they win or declare war to cement hegemony
            new_status = "Peak"
            transition_desc = f"The {emp_name} reaches its peak geopolitical influence, asserting military dominance."

        elif "breakthrough" in desc.lower() or "economic boom" in desc.lower():
            tracker["current_gdp"] *= 1.2
            if tracker["current_gdp"] > tracker["peak_gdp"]:
                tracker["peak_gdp"] = tracker["current_gdp"]
                if current_status not in ["Peak", "Expansion"]:
                    new_status = "Peak"
                    transition_desc = f"The {emp_name} achieves a golden age of scientific and economic peak development."

        elif "defeat" in desc.lower() or "economic sabotage" in desc.lower() or "market crash" in desc.lower():
            tracker["current_gdp"] *= 0.8
            if current_status in ["Peak", "Expansion"]:
                new_status = "Decline"
                transition_desc = f"The {emp_name} enters a period of decline following military setbacks and economic shocks."

        elif evt_type == "War End" and not is_primary and "annexed" in desc.lower():
            new_status = "Extinction"
            tracker["is_active"] = False
            transition_desc = f"The {emp_name} is completely annexed or wiped out from the galactic theater."

        elif "collapse" in desc.lower() or "fragmentation" in desc.lower():
            new_status = "Collapse"
            transition_desc = f"Internal instability and resource depletion cause the collapse of the central authority of {emp_name}."

        elif evt_type == "Civilization Evolution" and "rebirth" in desc.lower() and not tracker["is_active"]:
            tracker["is_active"] = True
            new_status = "Rebirth"
            transition_desc = f"Out of the ashes of the old world, the {emp_name} is reborn as a new galactic power."

        # If a status transition occurred, record it
        if new_status and new_status != current_status:
            tracker["status"] = new_status
            self.lifecycle_records.append({
                "empire_id": emp_id,
                "empire_name": emp_name,
                "status": new_status,
                "year": year,
                "gdp": round(tracker["current_gdp"], 2),
                "population": 0.0,  # placeholder, can be scaled if we track it
                "colonies": tracker["colonies_count"],
                "description": transition_desc,
            })
