"""
system_generator.py — Procedural star-system generator for the Galactic Dream Engine.

Reads the raw star catalogue (``datasets/stars.csv``), enriches every entry
with astrophysically-motivated properties (age, metallicity, radiation,
planet count, habitable-zone boundaries), and produces a list of
:class:`StarSystem` instances ready for downstream simulation.

All stochastic draws use a seeded ``numpy.random.RandomState`` for full
reproducibility across runs.
"""

from __future__ import annotations

import math
import os
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd

from simulation.systems.star_system import StarSystem


class SystemGenerator:
    """Generate enriched :class:`StarSystem` objects from the star catalogue.

    Parameters
    ----------
    csv_path : str
        Path to the star catalogue CSV file.  Defaults to
        ``datasets/stars.csv`` relative to the project root.
    seed : int
        Random seed for reproducibility.  Defaults to ``42``.

    Attributes
    ----------
    csv_path : str
        Resolved absolute path to the input CSV.
    rng : numpy.random.RandomState
        Seeded pseudo-random number generator.

    Examples
    --------
    >>> gen = SystemGenerator()
    >>> systems = gen.generate_all_systems()
    >>> len(systems)
    1001
    >>> gen.save_to_csv(systems, "datasets/star_systems.csv")
    """

    # Age ranges per spectral type (Gyr).
    AGE_RANGES: Dict[str, Tuple[float, float]] = {
        "O": (0.001, 0.01),
        "B": (0.01, 0.1),
        "A": (0.1, 2.0),
        "F": (1.0, 7.0),
        "G": (2.0, 10.0),
        "K": (3.0, 12.0),
        "M": (1.0, 13.0),
    }

    # Planet-count ranges per spectral type (inclusive).
    PLANET_RANGES: Dict[str, Tuple[int, int]] = {
        "O": (1, 4),
        "B": (1, 5),
        "A": (2, 6),
        "F": (3, 8),
        "G": (4, 10),
        "K": (3, 9),
        "M": (1, 7),
    }

    # Habitable-zone scaling factors (AU per sqrt(L_sun)).
    HZ_INNER_FACTOR: float = 0.75
    HZ_OUTER_FACTOR: float = 1.77

    def __init__(
        self,
        csv_path: str = os.path.join("datasets", "stars.csv"),
        seed: int = 42,
    ) -> None:
        self.csv_path: str = csv_path
        self.rng: np.random.RandomState = np.random.RandomState(seed)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_all_systems(self) -> List[StarSystem]:
        """Read the catalogue and return enriched :class:`StarSystem` objects.

        Returns
        -------
        List[StarSystem]
            One ``StarSystem`` per row in the input CSV, with all derived
            properties populated.

        Raises
        ------
        FileNotFoundError
            If ``self.csv_path`` does not exist.
        """
        df: pd.DataFrame = pd.read_csv(self.csv_path)
        systems: List[StarSystem] = []

        for _, row in df.iterrows():
            system = self._build_system(row)
            systems.append(system)

        return systems

    def save_to_csv(self, systems: List[StarSystem], filepath: str) -> None:
        """Persist a list of star systems to a CSV file.

        Parameters
        ----------
        systems : List[StarSystem]
            The systems to write.
        filepath : str
            Destination file path (will be created or overwritten).
        """
        records = [s.to_dict() for s in systems]
        df = pd.DataFrame(records)
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        df.to_csv(filepath, index=False)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _build_system(self, row: pd.Series) -> StarSystem:
        """Create a single ``StarSystem`` from a catalogue row.

        Parameters
        ----------
        row : pd.Series
            A single row from the stars DataFrame with columns:
            ``id, name, star_type, mass, temperature, luminosity, x, y, z, region``.

        Returns
        -------
        StarSystem
        """
        star_type: str = str(row["star_type"]).strip().upper()
        luminosity: float = float(row["luminosity"])
        temperature: float = float(row["temperature"])

        age = self._generate_age(star_type)
        metallicity = self._generate_metallicity(age)
        radiation = self._compute_radiation_level(luminosity, temperature)
        planet_count = self._generate_planet_count(star_type)
        hz_inner, hz_outer = self._compute_habitable_zone(luminosity)

        return StarSystem(
            star_id=str(row["id"]),
            star_name=str(row["name"]),
            star_type=star_type,
            star_mass=float(row["mass"]),
            star_temperature=temperature,
            star_luminosity=luminosity,
            x=float(row["x"]),
            y=float(row["y"]),
            z=float(row["z"]),
            region=str(row["region"]),
            age_billion_years=round(age, 4),
            metallicity=round(metallicity, 4),
            radiation_level=round(radiation, 4),
            planet_count=planet_count,
            habitable_zone_inner_au=round(hz_inner, 4),
            habitable_zone_outer_au=round(hz_outer, 4),
        )

    def _generate_age(self, star_type: str) -> float:
        """Sample a system age in Gyr from the type-dependent range.

        Parameters
        ----------
        star_type : str
            Spectral class letter (O–M).

        Returns
        -------
        float
            Age in billions of years.
        """
        lo, hi = self.AGE_RANGES.get(star_type, (1.0, 10.0))
        return float(self.rng.uniform(lo, hi))

    def _generate_metallicity(self, age_gyr: float) -> float:
        """Derive metallicity [Fe/H] correlated with system age.

        Younger systems tend to be more metal-rich because they formed from
        gas already enriched by previous stellar generations.  The baseline
        relation is a simple linear ramp from +0.5 (age → 0) to −2.0
        (age → 13 Gyr) with Gaussian scatter (σ = 0.15 dex).

        Parameters
        ----------
        age_gyr : float
            System age in Gyr.

        Returns
        -------
        float
            Metallicity value clamped to [−2.0, +0.5].
        """
        # Linear baseline: young → high, old → low.
        baseline: float = 0.5 - (age_gyr / 13.0) * 2.5
        scatter: float = float(self.rng.normal(0.0, 0.15))
        metallicity: float = baseline + scatter
        return float(np.clip(metallicity, -2.0, 0.5))

    def _compute_radiation_level(
        self, luminosity: float, temperature: float
    ) -> float:
        """Map luminosity and temperature to a 0–100 radiation scale.

        The score combines a logarithmic luminosity term (dominant) with a
        linear temperature contribution, then rescales into [0, 100].

        * ``log10(L) ∈ [−4, +6]`` → mapped to [0, 80]
        * ``T ∈ [2000, 50000]`` → mapped to [0, 20]

        Parameters
        ----------
        luminosity : float
            Bolometric luminosity in L_sun.
        temperature : float
            Effective temperature in Kelvin.

        Returns
        -------
        float
            Radiation level on a 0–100 scale.
        """
        log_lum: float = math.log10(max(luminosity, 1e-10))
        # Normalise log_lum from [-4, 6] → [0, 1]
        lum_norm: float = (log_lum - (-4.0)) / (6.0 - (-4.0))
        lum_norm = float(np.clip(lum_norm, 0.0, 1.0))

        # Normalise temperature from [2000, 50000] → [0, 1]
        temp_norm: float = (temperature - 2000.0) / (50000.0 - 2000.0)
        temp_norm = float(np.clip(temp_norm, 0.0, 1.0))

        return lum_norm * 80.0 + temp_norm * 20.0

    def _generate_planet_count(self, star_type: str) -> int:
        """Sample a planet count from the type-dependent range.

        Parameters
        ----------
        star_type : str
            Spectral class letter.

        Returns
        -------
        int
            Number of planets (≥ 1).
        """
        lo, hi = self.PLANET_RANGES.get(star_type, (1, 7))
        # randint upper bound is exclusive → hi + 1
        return int(self.rng.randint(lo, hi + 1))

    def _compute_habitable_zone(
        self, luminosity: float
    ) -> Tuple[float, float]:
        """Calculate habitable-zone boundaries from stellar luminosity.

        Uses the standard approximation:

        * inner edge = √L × 0.75  AU
        * outer edge = √L × 1.77  AU

        Parameters
        ----------
        luminosity : float
            Bolometric luminosity in L_sun.

        Returns
        -------
        Tuple[float, float]
            ``(inner_au, outer_au)`` boundaries of the habitable zone.
        """
        sqrt_lum: float = math.sqrt(max(luminosity, 0.0))
        inner: float = sqrt_lum * self.HZ_INNER_FACTOR
        outer: float = sqrt_lum * self.HZ_OUTER_FACTOR
        return inner, outer
