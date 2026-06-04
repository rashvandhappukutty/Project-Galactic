"""
Astrophysical and geometrical constants for the Galactic Dream Engine.
Includes stellar classification properties, spiral arm parameters, and coordinate scaling.
"""

from typing import Dict, Any, List

# --- Stellar Classifications (Morgan-Keenan System) ---
# Values are based on standard astrophysical models for main sequence stars.
STELLAR_CLASSES: Dict[str, Dict[str, Any]] = {
    "O": {
        "probability": 0.0003,      # 0.03%
        "temp_range": (30000.0, 50000.0),  # Kelvin
        "mass_range": (16.0, 100.0),       # Solar masses (M_sun)
        "lum_range": (30000.0, 1000000.0), # Solar luminosities (L_sun)
        "color": "#9bb0ff",         # Deep blue-white
    },
    "B": {
        "probability": 0.0013,      # 0.13%
        "temp_range": (10000.0, 30000.0),
        "mass_range": (2.1, 16.0),
        "lum_range": (25.0, 30000.0),
        "color": "#aabfff",         # Blue-white
    },
    "A": {
        "probability": 0.0060,      # 0.6%
        "temp_range": (7500.0, 10000.0),
        "mass_range": (1.4, 2.1),
        "lum_range": (5.0, 25.0),
        "color": "#cad7ff",         # White
    },
    "F": {
        "probability": 0.0300,      # 3.0%
        "temp_range": (6000.0, 7500.0),
        "mass_range": (1.04, 1.4),
        "lum_range": (1.5, 5.0),
        "color": "#f8f7ff",         # Yellow-white
    },
    "G": {
        "probability": 0.0760,      # 7.6%
        "temp_range": (5200.0, 6000.0),
        "mass_range": (0.8, 1.04),
        "lum_range": (0.6, 1.5),
        "color": "#fff4ea",         # Yellow (Sun-like)
    },
    "K": {
        "probability": 0.1210,      # 12.1%
        "temp_range": (3700.0, 5200.0),
        "mass_range": (0.45, 0.8),
        "lum_range": (0.08, 0.6),
        "color": "#ffd2a1",         # Orange
    },
    "M": {
        "probability": 0.7664,      # 76.64% (Red Dwarfs)
        "temp_range": (2400.0, 3700.0),
        "mass_range": (0.08, 0.45),
        "lum_range": (0.0001, 0.08),
        "color": "#ff9e9e",         # Red
    }
}

# --- Galaxy Geometry Constants ---
# Coordinates are in light-years (ly) relative to the Galactic Center (0, 0, 0)
GALAXY_RADIUS = 50000.0       # Radius of the stellar disk
CORE_RADIUS = 8000.0         # Radius of the dense galactic bulge
DISK_SCALE_HEIGHT = 500.0     # Z-axis height standard deviation (thin disk)
CORE_SCALE_HEIGHT = 3000.0    # Z-axis height standard deviation for bulge (spheroidal)

# Pitch angle of the spiral arms in radians (approx. 12 degrees)
# Larger pitch angle = looser spiral, smaller = tighter spiral
PITCH_ANGLE = 0.21  # ~12 degrees

# Arm Dispersion: width of the arms in light-years
ARM_DISPERSION = 1500.0

# --- Structure Components & Allocations ---
# Proportion of total stars allocated to each region
REGION_ALLOCATIONS = {
    "Core": 0.25,
    "Perseus Arm": 0.20,
    "Cygnus Arm": 0.20,
    "Sagittarius Arm": 0.15,
    "Orion Arm": 0.10,
    "Disk Background": 0.10
}

# Parameters for individual components
REGION_CONFIGS = {
    "Core": {
        "r_min": 0.0,
        "r_max": CORE_RADIUS,
    },
    "Perseus Arm": {
        "theta_start": 0.0,            # Radian starting offset
        "r_min": CORE_RADIUS,
        "r_max": GALAXY_RADIUS,
    },
    "Cygnus Arm": {
        "theta_start": 3.14159,        # Opposite side (~pi)
        "r_min": CORE_RADIUS,
        "r_max": GALAXY_RADIUS,
    },
    "Sagittarius Arm": {
        "theta_start": 1.5708,         # Perpendicular (~pi/2)
        "r_min": CORE_RADIUS,
        "r_max": GALAXY_RADIUS * 0.9,
    },
    "Orion Arm": {
        "theta_start": 2.35619,        # Local spur (~3pi/4)
        "r_min": 18000.0,
        "r_max": 32000.0,
    },
    "Disk Background": {
        "r_min": 0.0,
        "r_max": GALAXY_RADIUS,
    }
}
