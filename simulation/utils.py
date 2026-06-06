# simulation/utils.py
"""Utility helpers for Phase 9 of the Galactic Dream Engine.
Provides CSV read/write, logging, probability helpers, and simple ID generation.
All functions are pure Python with no external dependencies beyond the standard library.
"""

import csv
import os
import logging
import random
import math
from typing import List, Dict, Any, Iterable

# Configure a module‑level logger.
logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


def ensure_dir(path: str) -> None:
    """Create parent directories for *path* if they do not exist."""
    os.makedirs(os.path.dirname(path), exist_ok=True)


def write_csv(path: str, rows: Iterable[Dict[str, Any]], header: List[str] = None) -> None:
    """Write *rows* to *path* as a CSV.
    *header* overrides automatic header detection.
    The file is opened with UTF‑8 encoding and will be overwritten.
    """
    ensure_dir(path)
    rows = list(rows)
    if not rows:
        logger.warning("No rows supplied for CSV %s – creating empty file with header only.", path)
    if header is None and rows:
        header = list(rows[0].keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        writer.writerows(rows)
    logger.info("Wrote %d rows to %s", len(rows), path)


def read_csv(path: str) -> List[Dict[str, Any]]:
    """Read a CSV file and return a list of dictionaries.
    If the file does not exist, returns an empty list.
    """
    if not os.path.exists(path):
        logger.warning("CSV file %s not found – returning empty list.", path)
        return []
    with open(path, "r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def random_probability(base: float = 0.5, variance: float = 0.2) -> float:
    """Return a probability value between 0 and 1.
    *base* is the central probability, *variance* defines the maximum deviation.
    """
    prob = random.uniform(max(0.0, base - variance), min(1.0, base + variance))
    logger.debug("Generated random probability %f (base %f, variance %f)", prob, base, variance)
    return prob


def weighted_choice(choices: List[Any], weights: List[float]) -> Any:
    """Select an element from *choices* according to *weights*.
    The length of *choices* and *weights* must match.
    """
    total = sum(weights)
    if total == 0:
        logger.error("All weights are zero – cannot perform weighted choice.")
        raise ValueError("All weights are zero")
    cum_weights = []
    cumsum = 0.0
    for w in weights:
        cumsum += w
        cum_weights.append(cumsum)
    rnd = random.random() * total
    for choice, cum_w in zip(choices, cum_weights):
        if rnd <= cum_w:
            return choice
    return choices[-1]


def clamp(value: float, min_val: float, max_val: float) -> float:
    """Clamp *value* to the inclusive range [*min_val*, *max_val*]."""
    return max(min_val, min(max_val, value))

# Exported symbols for other modules.
__all__ = [
    "logger",
    "ensure_dir",
    "write_csv",
    "read_csv",
    "random_probability",
    "weighted_choice",
    "clamp",
]
