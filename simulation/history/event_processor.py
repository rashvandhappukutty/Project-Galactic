# simulation/history/event_processor.py
"""Ingestion and normalization of event datasets.
Converts various raw CSVs into a standardized HistoricalEvent schema.
"""

from __future__ import annotations
import os
import pandas as pd
from typing import List, Dict, Any
from ..utils import read_csv, logger

class EventProcessor:
    """Ingests raw event CSVs and normalizes them into a unified schema."""

    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = datasets_dir

    def load_all_events(self) -> List[Dict[str, Any]]:
        """Loads and normalizes events from all standard sources."""
        normalized_events: List[Dict[str, Any]] = []

        # 1. Civilization Events
        civ_events_path = os.path.join(self.datasets_dir, "civilization_events.csv")
        if os.path.exists(civ_events_path):
            try:
                df = pd.read_csv(civ_events_path)
                for _, row in df.iterrows():
                    normalized_events.append({
                        "event_id": str(row.get("event_id", f"civ_evt_{row.name}")),
                        "year": int(row.get("year", 0)),
                        "timestamp": f"Year {row.get('year', 0)}",
                        "event_type": str(row.get("event_type", "Civilization Event")),
                        "event_category": "Civilization",
                        "empire": str(row.get("civilization_name", row.get("civilization_id", "Unknown"))),
                        "participants": "",
                        "location": str(row.get("civilization_name", "Unknown")),
                        "description": str(row.get("description", "")),
                        "impact_score": 0.0,  # calculated later
                        "historical_significance": "Minor",  # calculated later
                    })
            except Exception as e:
                logger.error(f"Error loading civilization events: {e}")

        # 2. Colonization Events
        col_events_path = os.path.join(self.datasets_dir, "colonization_events.csv")
        if os.path.exists(col_events_path):
            try:
                df = pd.read_csv(col_events_path)
                for _, row in df.iterrows():
                    normalized_events.append({
                        "event_id": str(row.get("event_id", f"col_evt_{row.name}")),
                        "year": int(row.get("year", row.get("tick", 0) * 100)),
                        "timestamp": f"Year {row.get('year', row.get('tick', 0) * 100)}",
                        "event_type": str(row.get("event_type", "Colonization")),
                        "event_category": "Colonization",
                        "empire": str(row.get("civilization_name", row.get("civilization_id", "Unknown"))),
                        "participants": "",
                        "location": str(row.get("description", "")).split("colonized")[-1].strip() if "colonized" in str(row.get("description", "")) else "New Colony",
                        "description": str(row.get("description", "")),
                        "impact_score": 0.0,
                        "historical_significance": "Minor",
                    })
            except Exception as e:
                logger.error(f"Error loading colonization events: {e}")

        # 3. Economic Events
        econ_events_path = os.path.join(self.datasets_dir, "economic_events.csv")
        if os.path.exists(econ_events_path):
            try:
                df = pd.read_csv(econ_events_path)
                for _, row in df.iterrows():
                    normalized_events.append({
                        "event_id": str(row.get("event_id", f"eco_evt_{row.name}")),
                        "year": int(row.get("year", row.get("tick", 0) * 100)),
                        "timestamp": f"Year {row.get('year', row.get('tick', 0) * 100)}",
                        "event_type": str(row.get("event_type", "Economic Event")),
                        "event_category": "Economy",
                        "empire": str(row.get("civilization_id", "Unknown")),
                        "participants": "",
                        "location": str(row.get("civilization_id", "Unknown")),
                        "description": str(row.get("description", "Economic shift detected.")),
                        "impact_score": 0.0,
                        "historical_significance": "Minor",
                    })
            except Exception as e:
                logger.error(f"Error loading economic events: {e}")

        # 4. Transport Events
        trans_events_path = os.path.join(self.datasets_dir, "transport_events.csv")
        if os.path.exists(trans_events_path):
            try:
                df = pd.read_csv(trans_events_path)
                for _, row in df.iterrows():
                    normalized_events.append({
                        "event_id": str(row.get("event_id", f"tra_evt_{row.name}")),
                        "year": int(row.get("year", row.get("tick", 0) * 100)),
                        "timestamp": f"Year {row.get('year', row.get('tick', 0) * 100)}",
                        "event_type": str(row.get("event_type", "Transport Event")),
                        "event_category": "Logistics",
                        "empire": str(row.get("civilization_id", "Unknown")),
                        "participants": "",
                        "location": "Trade Route",
                        "description": str(row.get("description", "FTL transit event.")),
                        "impact_score": 0.0,
                        "historical_significance": "Minor",
                    })
            except Exception as e:
                logger.error(f"Error loading transport events: {e}")

        # 5. Wars
        wars_path = os.path.join(self.datasets_dir, "wars.csv")
        if os.path.exists(wars_path):
            try:
                df = pd.read_csv(wars_path)
                for _, row in df.iterrows():
                    # War start
                    normalized_events.append({
                        "event_id": str(row.get("war_id", f"war_{row.name}")),
                        "year": int(row.get("start_year", 0)),
                        "timestamp": f"Year {row.get('start_year', 0)}",
                        "event_type": "War Declaration",
                        "event_category": "Military",
                        "empire": str(row.get("attacker", "Attacker")),
                        "participants": str(row.get("defender", "Defender")),
                        "location": "Border Regions",
                        "description": f"The {row.get('attacker')} declared war on the {row.get('defender')} due to {row.get('cause', 'geopolitical tension')} (Scale: {row.get('war_scale', 'Regional')}).",
                        "impact_score": 0.0,
                        "historical_significance": "Minor",
                    })
                    # If war ended
                    end_year = row.get("end_year")
                    if pd.notna(end_year) and row.get("status") == "Ended":
                        normalized_events.append({
                            "event_id": f"{row.get('war_id')}_end",
                            "year": int(end_year),
                            "timestamp": f"Year {int(end_year)}",
                            "event_type": "War End",
                            "event_category": "Military",
                            "empire": str(row.get("attacker", "Attacker")),
                            "participants": str(row.get("defender", "Defender")),
                            "location": "Diplomatic Summit",
                            "description": f"The war between {row.get('attacker')} and {row.get('defender')} has officially ended after {int(end_year) - int(row.get('start_year', 0))} years.",
                            "impact_score": 0.0,
                            "historical_significance": "Minor",
                        })
            except Exception as e:
                logger.error(f"Error loading wars: {e}")

        # 6. Battles
        battles_path = os.path.join(self.datasets_dir, "battles.csv")
        if os.path.exists(battles_path):
            try:
                df = pd.read_csv(battles_path)
                for _, row in df.iterrows():
                    normalized_events.append({
                        "event_id": str(row.get("battle_id", f"bat_{row.name}")),
                        "year": int(row.get("year", 0)),
                        "timestamp": f"Year {row.get('year', 0)}",
                        "event_type": str(row.get("battle_type", "Deep Space Engagement")),
                        "event_category": "Military",
                        "empire": str(row.get("attacker_id", "Attacker")),
                        "participants": str(row.get("defender_id", "Defender")),
                        "location": str(row.get("location_star_id", "Deep Space")),
                        "description": f"A violent {row.get('battle_type', 'battle')} raged in system {row.get('location_star_id', 'Unknown')} between {row.get('attacker_id')} and {row.get('defender_id')}. Winner: {row.get('winner_id')}. Casualties: {int(row.get('casualties', 0)):,}.",
                        "impact_score": 0.0,
                        "historical_significance": "Minor",
                    })
            except Exception as e:
                logger.error(f"Error loading battles: {e}")

        # 7. Alliances
        alliances_path = os.path.join(self.datasets_dir, "alliances.csv")
        if os.path.exists(alliances_path):
            try:
                df = pd.read_csv(alliances_path)
                for _, row in df.iterrows():
                    normalized_events.append({
                        "event_id": str(row.get("alliance_id", f"all_{row.name}")),
                        "year": 0,  # Assume inception at Year 0 or first tick if unknown
                        "timestamp": "Year 0",
                        "event_type": "Alliance Formation",
                        "event_category": "Diplomacy",
                        "empire": str(row.get("alliance_name", "Alliance")),
                        "participants": str(row.get("member_empires", "")),
                        "location": "Galactic Assembly",
                        "description": f"The {row.get('alliance_name')} was established as a {row.get('alliance_type', 'Defense Pact')} including members: {row.get('member_empires', '')}.",
                        "impact_score": 0.0,
                        "historical_significance": "Minor",
                    })
            except Exception as e:
                logger.error(f"Error loading alliances: {e}")

        # 8. Peace Treaties
        treaties_path = os.path.join(self.datasets_dir, "peace_treaties.csv")
        if os.path.exists(treaties_path):
            try:
                df = pd.read_csv(treaties_path)
                for _, row in df.iterrows():
                    normalized_events.append({
                        "event_id": str(row.get("treaty_id", f"tre_{row.name}")),
                        "year": int(row.get("year", 0)),
                        "timestamp": f"Year {row.get('year', 0)}",
                        "event_type": "Peace Treaty Signing",
                        "event_category": "Diplomacy",
                        "empire": str(row.get("signer_a", "Party A")),
                        "participants": str(row.get("signer_b", "Party B")),
                        "location": "Neutral Zone",
                        "description": f"The treaty {row.get('treaty_id')} was signed between {row.get('signer_a')} and {row.get('signer_b')} to settle war {row.get('war_id')}. Terms: {row.get('terms', 'Status Quo')}. Reparations: {row.get('reparations_credits', 0)} credits.",
                        "impact_score": 0.0,
                        "historical_significance": "Minor",
                    })
            except Exception as e:
                logger.error(f"Error loading peace treaties: {e}")

        # 9. Espionage Operations
        esp_path = os.path.join(self.datasets_dir, "espionage_operations.csv")
        if os.path.exists(esp_path):
            try:
                df = pd.read_csv(esp_path)
                for _, row in df.iterrows():
                    success_str = "succeeded" if str(row.get("success")).lower() in ["true", "1", "success"] else "failed"
                    normalized_events.append({
                        "event_id": str(row.get("operation_id", f"esp_{row.name}")),
                        "year": int(row.get("tick", 0) * 100),
                        "timestamp": f"Year {int(row.get('tick', 0) * 100)}",
                        "event_type": str(row.get("operation_type", "Espionage Operation")),
                        "event_category": "Espionage",
                        "empire": str(row.get("attacker_id", "Attacker")),
                        "participants": str(row.get("target_id", "Target")),
                        "location": str(row.get("target_id", "Target")),
                        "description": f"A covert {row.get('operation_type', 'operation')} by {row.get('attacker_id')} targeting {row.get('target_id')} {success_str}. Damage caused: {row.get('damage', 0)}. Intel gained: {row.get('intelligence_gain', 0)}.",
                        "impact_score": 0.0,
                        "historical_significance": "Minor",
                    })
            except Exception as e:
                logger.error(f"Error loading espionage: {e}")

        # Sort events by year
        normalized_events.sort(key=lambda x: x["year"])
        logger.info(f"Successfully loaded and normalized {len(normalized_events)} base historical records.")
        return normalized_events
