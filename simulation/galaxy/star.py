"""
Representation of a star and its physical characteristics in the simulator.
"""

from dataclasses import dataclass, asdict
from enum import Enum
from typing import Dict, Any

class SpectralType(str, Enum):
    O = "O"
    B = "B"
    A = "A"
    F = "F"
    G = "G"
    K = "K"
    M = "M"

@dataclass
class Star:
    """
    Represents a single stellar system in the Galactic Dream Engine.
    Coordinates are in light-years relative to the Galactic Center.
    """
    id: str
    name: str
    star_type: SpectralType
    mass: float          # In Solar Masses (M_sun)
    temperature: float   # In Kelvin (K)
    luminosity: float    # In Solar Luminosities (L_sun)
    x: float             # X coordinate in light-years (ly)
    y: float             # Y coordinate in light-years (ly)
    z: float             # Z coordinate in light-years (ly)
    region: str          # Component of the galaxy the star belongs to (e.g., Orion Arm, Core)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the star's properties to a dictionary, suitable for serialization."""
        data = asdict(self)
        # Ensure enum is converted to its string value
        data["star_type"] = self.star_type.value
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Star":
        """Reconstruct a Star instance from a dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            star_type=SpectralType(data["star_type"]),
            mass=float(data["mass"]),
            temperature=float(data["temperature"]),
            luminosity=float(data["luminosity"]),
            x=float(data["x"]),
            y=float(data["y"]),
            z=float(data["z"]),
            region=data["region"]
        )

    def __str__(self) -> str:
        return (
            f"Star {self.name} [{self.star_type}] | "
            f"Pos: ({self.x:,.1f}, {self.y:,.1f}, {self.z:,.1f}) ly | "
            f"M: {self.mass:.2f} M☉ | T: {self.temperature:,.0f} K | L: {self.luminosity:,.4f} L☉"
        )
