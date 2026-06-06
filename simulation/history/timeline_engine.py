# simulation/history/timeline_engine.py
"""Grand Timeline Simulator Orchestrator.
Loads, normalizes, extends, and exports the master galactic history.
"""

from __future__ import annotations
import os
import pandas as pd
from typing import List, Dict, Any

from .event_processor import EventProcessor
from .significance_engine import SignificanceEngine
from .civilization_lifecycle import CivilizationLifecycleEngine
from .era_classifier import EraClassifier
from .history_generator import HistoryGenerator
from ..utils import write_csv, logger

class TimelineEngine:
    """Main orchestrator for the Phase 10 Grand Timeline Simulator."""

    def __init__(self, datasets_dir: str = "datasets", seed: int = 42):
        self.datasets_dir = datasets_dir
        self.seed = seed
        self.processor = EventProcessor(datasets_dir)
        self.significance = SignificanceEngine()
        self.lifecycle = CivilizationLifecycleEngine(datasets_dir)
        self.era_classifier = EraClassifier(datasets_dir)
        self.generator = HistoryGenerator(seed)

    def run_pipeline(self, target_years: int = 10000, acceleration: int = 100) -> List[Dict[str, Any]]:
        """Orchestrates the ingestion, simulation extension, analysis, and dataset generation."""
        logger.info(f"Starting Phase 10 grand timeline simulation pipeline for target {target_years} years...")

        # 1. Ingest base events from existing CSVs
        ingested_events = self.processor.load_all_events()
        
        # Load empires catalog
        empires_path = os.path.join(self.datasets_dir, "empires.csv")
        if os.path.exists(empires_path):
            empires = pd.read_csv(empires_path).to_dict(orient="records")
        else:
            logger.warning("No empires.csv found, using fallback placeholder list.")
            empires = [{"founding_civilization_id": "emp_orion", "empire_name": "Orion Confederacy", "gdp": 5e11, "population": 8e10, "capital_world": "Orion Prime"}]

        # 2. Check if timeline needs to be extended procedurally
        max_ingested_year = ingested_events[-1]["year"] if ingested_events else 0
        if max_ingested_year < target_years:
            procedural_events = self.generator.simulate_procedural_history(
                start_year=max_ingested_year,
                end_year=target_years,
                empires=empires,
                acceleration=acceleration
            )
            all_events = ingested_events + procedural_events
        else:
            all_events = ingested_events

        # 3. Calculate impact scores and historical significance
        logger.info("Computing significance and impact scores for all events...")
        for event in all_events:
            self.significance.compute_significance(event)

        # Sort again to ensure strictly chronological order
        all_events.sort(key=lambda x: x["year"])

        # 4. Generate master history dataset
        master_path = os.path.join(self.datasets_dir, "galactic_history_master.csv")
        header = [
            "event_id", "year", "timestamp", "event_type", "event_category", 
            "empire", "participants", "location", "impact_score", "historical_significance", "description"
        ]
        write_csv(master_path, all_events, header)
        logger.info(f"Saved master history timeline to {master_path}")

        # 5. Analyze and output civilization lifecycles
        logger.info("Analyzing empire lifecycles...")
        self.lifecycle.run_lifecycle_analysis(all_events, empires)

        # 6. Classify and output eras
        logger.info("Classifying historical eras...")
        self.era_classifier.classify_eras(all_events)

        logger.info("Timeline Engine pipeline complete.")
        return all_events
