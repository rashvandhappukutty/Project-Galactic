# simulation/storytelling/story_api.py
"""Lore and Geopolitical Query API.
Prepares narrative data querying for the Phase 12 Digital Twin.
"""

from __future__ import annotations
import os
import pandas as pd
from typing import List, Dict, Any, Optional

class GalacticLoreAPI:
    """Standardized API exposing methods to query story, history, and empire data."""

    def __init__(self, datasets_dir: str = "datasets"):
        self.datasets_dir = datasets_dir

    def _load_csv(self, filename: str) -> List[Dict[str, Any]]:
        path = os.path.join(self.datasets_dir, filename)
        if os.path.exists(path):
            try:
                # Use fillna to avoid float('nan') values in serialization
                return pd.read_csv(path).fillna("").to_dict(orient="records")
            except Exception:
                return []
        return []

    def get_empires(self, name_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch all empires cataloged in the simulation."""
        empires = self._load_csv("empires.csv")
        if name_filter:
            empires = [e for e in empires if name_filter.lower() in str(e.get("empire_name", "")).lower()]
        return empires

    def get_wars(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query wars databases."""
        wars = self._load_csv("wars.csv")
        if status_filter:
            wars = [w for w in wars if str(w.get("status", "")).lower() == status_filter.lower()]
        return wars

    def get_history(self, min_year: int = 0, max_year: int = 10000000) -> List[Dict[str, Any]]:
        """Query the master timeline events within a year span."""
        history = self._load_csv("galactic_history_master.csv")
        return [h for h in history if min_year <= int(h.get("year", 0)) <= max_year]

    def get_stories(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch generated books and chronicles."""
        stories = self._load_csv("legendary_stories.csv")
        if category:
            stories = [s for s in stories if category.lower() in str(s.get("legendary_type", "")).lower()]
        return stories

    def get_figures(self, role_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch historical characters."""
        figures = self._load_csv("historical_figures.csv")
        if role_filter:
            figures = [f for f in figures if str(f.get("role", "")).lower() == role_filter.lower()]
        return figures

    def get_news(self, category_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query news feed articles."""
        news = self._load_csv("galactic_news.csv")
        if category_filter:
            news = [n for n in news if str(n.get("category", "")).lower() == category_filter.lower()]
        return news

    def get_chronicles(self, empire_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """Fetch chronicles for a specific empire."""
        chronicles = self._load_csv("empire_chronicles.csv")
        if empire_name:
            chronicles = [c for c in chronicles if empire_name.lower() in str(c.get("empire_name", "")).lower()]
        return chronicles
