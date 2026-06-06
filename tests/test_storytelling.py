# tests/test_storytelling.py
"""Unit tests for Phase 11: Galactic Story Generator.
"""

from __future__ import annotations
import pytest
from simulation.storytelling.biography_generator import BiographyGenerator
from simulation.storytelling.news_generator import NewsGenerator
from simulation.storytelling.story_api import GalacticLoreAPI

def test_biography_generator():
    generator = BiographyGenerator(seed=42)
    empires = [
        {"empire_name": "Sol Imperium"},
        {"empire_name": "Centauri Dominion"}
    ]
    
    figures = generator.generate_figures(empires, count=100)
    assert len(figures) == 100
    for f in figures:
        assert f["name"] != ""
        assert f["civilization"] in ["Sol Imperium", "Centauri Dominion"]
        assert f["role"] in ["Emperor", "Scientist", "Military Leader", "Explorer", "Diplomat"]
        assert f["achievements"] != ""
        assert 20 <= f["legacy_score"] <= 100

def test_news_generator():
    generator = NewsGenerator(seed=42)
    events = [
        {"year": 100, "event_type": "Colonization", "event_category": "Colonization", "empire": "Alpha", "participants": "", "description": "Colonized Prime Planet."},
        {"year": 200, "event_type": "Deep Space Engagement", "event_category": "Military", "empire": "Beta", "participants": "Alpha", "description": "Fleet skirmish near jump gate."}
    ]
    
    news = generator.generate_news(events, target_count=50)
    assert len(news) == 50
    for n in news:
        assert n["article_id"] != ""
        assert n["year"] > 0
        assert n["category"] in ["Breaking News", "Political Update", "Economic Report", "Scientific Discovery", "Military Bulletin"]
        assert n["headline"] != ""
        assert n["body"] != ""
        assert n["spokesperson"] != ""

def test_story_api():
    # Test API loading behavior with nonexistent path or empty fallback
    api = GalacticLoreAPI(datasets_dir="nonexistent_folder")
    assert api.get_empires() == []
    assert api.get_wars() == []
    assert api.get_history() == []
    assert api.get_stories() == []
    assert api.get_figures() == []
    assert api.get_news() == []
    assert api.get_chronicles() == []
