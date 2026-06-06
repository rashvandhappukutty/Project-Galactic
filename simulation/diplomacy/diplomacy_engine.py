# simulation/diplomacy/diplomacy_engine.py
"""Core diplomacy engine handling relationship updates and diplomatic events.
All relationships are stored in a symmetric matrix (CSV) where each row
represents a unique pair of empires.
"""

from __future__ import annotations
import random
from typing import List, Tuple, Dict, Any
from ..utils import write_csv, read_csv, logger, ensure_dir, clamp

import random
from typing import List

from ..models import Empire, Relation
from ..utils import write_csv, read_csv, clamp, logger

DATASET_PATH = "datasets/diplomatic_relations.csv"


def _init_relations(empires: List[Empire]) -> List[Relation]:
    """Internal helper to initialize relations (original function renamed)."""
    relations: List[Relation] = []
    for i, emp_a in enumerate(empires):
        for emp_b in empires[i + 1 :]:
            rel = Relation(
                empire_a=emp_a.empire_id,
                empire_b=emp_b.empire_id,
                relation_score=random.uniform(-10, 10),
                trust=random.uniform(0, 50),
                influence=random.uniform(0, 30),
                cultural_similarity=random.uniform(0, 40),
                economic_dependency=random.uniform(0, 30),
                military_parity=random.uniform(0, 30),
            )
            relations.append(rel)
    logger.info("Initialized %d diplomatic relations.", len(relations))
    return relations
    """Create an initial set of relations for every unordered empire pair.
    Scores are centered around 0 with a small random variance.
    """
    relations: List[Relation] = []
    for i, emp_a in enumerate(empires):
        for emp_b in empires[i + 1 :]:
            rel = Relation(
                empire_a=emp_a.empire_id,
                empire_b=emp_b.empire_id,
                relation_score=random.uniform(-10, 10),
                trust=random.uniform(0, 50),
                influence=random.uniform(0, 30),
                cultural_similarity=random.uniform(0, 40),
                economic_dependency=random.uniform(0, 30),
                military_parity=random.uniform(0, 30),
            )
            relations.append(rel)
    logger.info("Initialized %d diplomatic relations.", len(relations))
    return relations


def _load_relations() -> List[Relation]:
    rows = read_csv(DATASET_PATH)
    return [Relation(**r) for r in rows]
    rows = read_csv(DATASET_PATH)
    return [Relation(**r) for r in rows]


def _save_relations(relations: List[Relation]) -> None:
    if not relations:
        logger.warning("No relations to save.")
        return
    header = list(relations[0].to_dict().keys())
    rows = [rel.to_dict() for rel in relations]
    write_csv(DATASET_PATH, rows, header)
    if not relations:
        logger.warning("No relations to save.")
        return
    header = list(relations[0].to_dict().keys())
    rows = [rel.to_dict() for rel in relations]
    write_csv(DATASET_PATH, rows, header)


def _update_relations(relations: List[Relation], tick: int) -> None:
    """Apply simple diplomatic drift each tick."""
    for rel in relations:
        drift = random.uniform(-2, 2)
        rel.relation_score = clamp(rel.relation_score + drift, -100, 100)
        trust_drift = drift * 0.5
        rel.trust = clamp(rel.trust + trust_drift, 0, 100)
        rel.influence = clamp(rel.influence + trust_drift * 0.3, 0, 100)
    logger.debug("Updated diplomatic relations for tick %d.", tick)
    """Apply simple diplomatic drift each tick.
    Positive economic interactions increase trust; conflicts decrease scores.
    """
    for rel in relations:
        drift = random.uniform(-2, 2)
        rel.relation_score = clamp(rel.relation_score + drift, -100, 100)
        trust_drift = drift * 0.5
        rel.trust = clamp(rel.trust + trust_drift, 0, 100)
        rel.influence = clamp(rel.influence + trust_drift * 0.3, 0, 100)
    logger.debug("Updated diplomatic relations for tick %d.", tick)


class DiplomacyEngine:
    """High‑level wrapper used by the Phase 9 pipeline.
    Provides initialization, tick‑wise updates, and CSV export.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.random = random.Random(seed)
        self.relations: List[Relation] = []
        self.relations_dict: Dict[Tuple[str, str], Relation] = {}

    def initialize_relations(
        self,
        empires: List[Dict[str, Any]],
        stars: Dict[str, Any] = None,
        trade_agreements: List[Dict[str, Any]] = None,
        capital_stars: Dict[str, str] = None,
    ) -> None:
        """Create initial symmetric relations for all empire pairs.
        The extra parameters are accepted for compatibility with the existing
        pipeline but are not used in the simple implementation.
        """
        empire_objs = [Empire(**e) for e in empires]
        self.relations = _init_relations(empire_objs)
        self._build_lookup()

    def _build_lookup(self) -> None:
        self.relations_dict = {}
        for rel in self.relations:
            self.relations_dict[(rel.empire_a, rel.empire_b)] = rel
            self.relations_dict[(rel.empire_b, rel.empire_a)] = rel

    def update_relations(self, empire_ids: List[str]) -> None:
        """Update relations each tick using deterministic random state."""
        _update_relations(self.relations, tick=0)
        self._build_lookup()

    def export_relations(self, file_path: str) -> None:
        ensure_dir(file_path)
        header = list(self.relations[0].to_dict().keys()) if self.relations else []
        rows = [rel.to_dict() for rel in self.relations]
        write_csv(file_path, rows, header)


        relations = initialize_relations(empires)
    else:
        relations = load_relations()
    update_relations(relations, tick)
    save_relations(relations)
    return relations
