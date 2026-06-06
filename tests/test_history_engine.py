# tests/test_history_engine.py
"""Unit tests for Phase 10: Grand Timeline Simulator.
"""

from __future__ import annotations
import pytest
from simulation.history.significance_engine import SignificanceEngine
from simulation.history.era_classifier import EraClassifier
from simulation.history.civilization_lifecycle import CivilizationLifecycleEngine
from simulation.history.history_generator import HistoryGenerator

def test_significance_engine():
    engine = SignificanceEngine()
    
    # Test base score mappings
    event_trade = {"event_type": "Trade Agreement", "description": "Trade signed."}
    engine.compute_significance(event_trade)
    assert event_trade["impact_score"] == 5.0
    assert event_trade["historical_significance"] == "Minor"

    event_extinction = {"event_type": "Civilization Extinction", "description": "Wiped out."}
    engine.compute_significance(event_extinction)
    assert event_extinction["impact_score"] == 100.0
    assert event_extinction["historical_significance"] == "Legendary"

    # Test battle casualty adjustment
    event_battle = {
        "event_type": "Deep Space Engagement",
        "event_category": "Military",
        "description": "Raged battle, casualties: 1,500,000 soldiers."
    }
    engine.compute_significance(event_battle)
    assert event_battle["impact_score"] > 15.0  # Casualty scaling increases score
    assert event_battle["impact_score"] <= 100.0

def test_era_classifier():
    classifier = EraClassifier(window_size=100)
    events = [
        {"year": 100, "event_type": "Colonization", "event_category": "Colonization", "empire": "Alpha", "participants": "", "impact_score": 10.0, "description": "Colonized prime planet."},
        {"year": 200, "event_type": "Colonization", "event_category": "Colonization", "empire": "Alpha", "participants": "", "impact_score": 10.0, "description": "Colonized prime planet."},
        {"year": 300, "event_type": "Deep Space Engagement", "event_category": "Military", "empire": "Alpha", "participants": "Beta", "impact_score": 25.0, "description": "Raged battle, casualties: 1,000 soldiers."},
        {"year": 400, "event_type": "Deep Space Engagement", "event_category": "Military", "empire": "Beta", "participants": "Alpha", "impact_score": 25.0, "description": "Raged battle, casualties: 10,000 soldiers."},
    ]
    
    eras = classifier.classify_eras(events)
    assert len(eras) > 0
    # Checks sequence of years
    for era in eras:
        assert era["start_year"] < era["end_year"]
        assert era["era_name"] in [
            "Age of Exploration", "Age of Colonization", "Age of Conflict", 
            "Age of Trade", "Age of Federations", "Age of Expansion", 
            "Age of Megastructures", "Age of Transcendence", "Age of Collapse"
        ]

def test_history_generator():
    generator = HistoryGenerator(seed=42)
    empires = [
        {"founding_civilization_id": "emp_1", "empire_name": "Empire A", "gdp": 1000.0},
        {"founding_civilization_id": "emp_2", "empire_name": "Empire B", "gdp": 2000.0}
    ]
    
    events = generator.simulate_procedural_history(start_year=100, end_year=1000, empires=empires, acceleration=100)
    assert len(events) > 0
    for e in events:
        assert e["year"] >= 100
        assert e["year"] <= 1000
        assert e["empire"] in ["Empire A", "Empire B"]
        assert e["event_category"] in ["Military", "Diplomacy", "Economy", "Science", "Crisis", "Colonization"]
        assert e["description"] != ""
