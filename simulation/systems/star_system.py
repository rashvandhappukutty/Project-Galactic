"""
star_system.py — StarSystem dataclass for the Galactic Dream Engine.

Wraps a star record (from datasets/stars.csv) with system-level astrophysical
properties such as age, metallicity, radiation environment, planet count, and
habitable-zone boundaries.

Columns carried over from stars.csv:
    id, name, star_type, mass, temperature, luminosity, x, y, z, region

Additional derived / generated fields:
    age_billion_years, metallicity, radiation_level, planet_count,
    habitable_zone_inner_au, habitable_zone_outer_au
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict


@dataclass
class StarSystem:
    """A single star system in the Galactic Dream Engine simulation.

    This dataclass enriches the raw star catalogue entry with physical
    properties that govern planet generation and civilisation modelling.

    Attributes
    ----------
    star_id : str
        Unique identifier matching the ``id`` column of ``stars.csv``.
    star_name : str
        Human-readable name of the star.
    star_type : str
        Harvard spectral class letter (one of O, B, A, F, G, K, M).
    star_mass : float
        Stellar mass in solar masses (Msun).
    star_temperature : float
        Effective surface temperature in Kelvin.
    star_luminosity : float
        Bolometric luminosity in solar luminosities (Lsun).
    x : float
        Galactic X coordinate in light-years.
    y : float
        Galactic Y coordinate in light-years.
    z : float
        Galactic Z coordinate in light-years.
    region : str
        Named galactic region (e.g. "Core", "Orion Arm").
    age_billion_years : float
        Estimated system age in billions of years (Gyr).
    metallicity : float
        Iron-to-hydrogen ratio [Fe/H] on the standard logarithmic scale.
        Typical range is −2.0 (metal-poor) to +0.5 (metal-rich).
    radiation_level : float
        Ambient radiation intensity on a 0–100 normalised scale.
    planet_count : int
        Number of planets orbiting this star.
    habitable_zone_inner_au : float
        Inner edge of the circumstellar habitable zone in AU.
    habitable_zone_outer_au : float
        Outer edge of the circumstellar habitable zone in AU.
    """

    # --- Fields carried from stars.csv ---
    star_id: str
    star_name: str
    star_type: str
    star_mass: float
    star_temperature: float
    star_luminosity: float
    x: float
    y: float
    z: float
    region: str

    # --- Derived / generated fields ---
    age_billion_years: float = 0.0
    metallicity: float = 0.0
    radiation_level: float = 0.0
    planet_count: int = 0
    habitable_zone_inner_au: float = 0.0
    habitable_zone_outer_au: float = 0.0

    # --- Property aliases for compatibility ---
    @property
    def hz_inner(self) -> float:
        """Alias for habitable_zone_inner_au."""
        return self.habitable_zone_inner_au

    @property
    def hz_outer(self) -> float:
        """Alias for habitable_zone_outer_au."""
        return self.habitable_zone_outer_au

    # ------------------------------------------------------------------
    # Serialisation helpers
    # ------------------------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """Return a plain-dict representation of the star system.

        All field values are preserved with their native Python types so that
        the result can be directly fed to ``json.dumps`` or a Pandas
        ``DataFrame`` constructor.

        Returns
        -------
        Dict[str, Any]
            Dictionary keyed by field name.
        """
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StarSystem":
        """Construct a ``StarSystem`` from a dictionary.

        The dictionary keys must match the dataclass field names.  Extra keys
        are silently ignored so that the method works safely with super-sets
        of the expected schema (e.g. rows from an enriched CSV).

        Parameters
        ----------
        data : Dict[str, Any]
            Mapping of field names to values.

        Returns
        -------
        StarSystem
            A fully initialised instance.
        """
        field_names = {f.name for f in cls.__dataclass_fields__.values()}
        filtered = {k: v for k, v in data.items() if k in field_names}
        return cls(**filtered)

    # ------------------------------------------------------------------
    # Human-readable representation
    # ------------------------------------------------------------------

    def __str__(self) -> str:
        """Return a concise, human-readable summary string.

        Example output::

            StarSystem(HIP 280040 | Type=M | Mass=0.13 Msun | Temp=2569 K |
            Age=7.42 Gyr | Planets=3 | HZ=0.01-0.03 AU | Region=Core)
        """
        return (
            f"StarSystem({self.star_name} | "
            f"Type={self.star_type} | "
            f"Mass={self.star_mass:.2f} Msun | "
            f"Temp={self.star_temperature:.0f} K | "
            f"Age={self.age_billion_years:.2f} Gyr | "
            f"Planets={self.planet_count} | "
            f"HZ={self.habitable_zone_inner_au:.2f}-{self.habitable_zone_outer_au:.2f} AU | "
            f"Region={self.region})"
        )
