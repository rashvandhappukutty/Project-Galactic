"""
Procedural Milky Way galaxy generator.
Generates stars in a spiral configuration and calculates realistic physical properties.
"""

import math
import random
import hashlib
from typing import List, Dict, Any, Tuple
import pandas as pd
import numpy as np

from simulation.galaxy.constants import (
    STELLAR_CLASSES,
    GALAXY_RADIUS,
    CORE_RADIUS,
    DISK_SCALE_HEIGHT,
    CORE_SCALE_HEIGHT,
    PITCH_ANGLE,
    ARM_DISPERSION,
    REGION_ALLOCATIONS,
    REGION_CONFIGS
)
from simulation.galaxy.star import Star, SpectralType

class GalaxyGenerator:
    """
    Generates a procedurally populated Milky Way galaxy containing stars distributed
    according to spiral arms and galactic core structures, with realistic Morgan-Keenan
    classifications.
    """

    def __init__(self, seed: int = 42):
        self.seed = seed
        self.random_state = np.random.RandomState(seed)
        random.seed(seed)

    def _generate_star_name(self, spectral_type: SpectralType, region: str) -> str:
        """
        Generates a realistic star name based on different naming schemes.
        """
        # Constellation/arm names for Bayer-like designations
        region_genitives = {
            "Core": "Bulge",
            "Perseus Arm": "Persei",
            "Cygnus Arm": "Cygni",
            "Sagittarius Arm": "Sagittarii",
            "Orion Arm": "Orionis",
            "Disk Background": "Galacticis"
        }

        greek_letters = [
            "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
            "Iota", "Kappa", "Lambda", "Mu", "Nu", "Xi", "Omicron", "Pi", "Rho",
            "Sigma", "Tau", "Upsilon", "Phi", "Chi", "Psi", "Omega"
        ]

        legendary_names = [
            "Aethelgard", "Vespera", "Hyperion", "Elysium", "Chronos", "Aurelia",
            "Zephyrus", "Xylar", "Novis", "Astraea", "Caelum", "Tenebris", "Ignis",
            "Solaria", "Nirvana", "Helios", "Selene", "Eos", "Nyx", "Orpheus",
            "Prometheus", "Atlas", "Gaea", "Uranus", "Cronus", "Rhea", "Iapetus",
            "Oceanus", "Tethys", "Hyperion", "Theia", "Coeus", "Phoebe", "Crius"
        ]

        roll = self.random_state.rand()

        if roll < 0.05:
            # 5% chance: Legendary names
            base = self.random_state.choice(legendary_names)
            # Add an optional numeral
            if self.random_state.rand() < 0.3:
                numeral = self.random_state.choice(["I", "II", "III", "IV", "V", "Prime"])
                return f"{base} {numeral}"
            return base

        elif roll < 0.35:
            # 30% chance: Bayer-like designation (e.g., Alpha Orionis)
            greek = self.random_state.choice(greek_letters)
            const = region_genitives.get(region, "Galacticis")
            return f"{greek} {const}"

        elif roll < 0.65:
            # 30% chance: Space telescope survey name (e.g., Kepler-186)
            survey = self.random_state.choice(["Kepler", "TESS", "Gaia", "GDE", "Webb"])
            number = self.random_state.randint(100, 9999)
            letter = self.random_state.choice(["a", "b", "c", "d", "e"]) if self.random_state.rand() < 0.2 else ""
            return f"{survey}-{number}{letter}"

        else:
            # 35% chance: Catalog designation (e.g., HD 189733 or HIP 89322)
            catalog = self.random_state.choice(["HD", "HIP", "Gliese", "PSR", "HR"])
            if catalog == "Gliese":
                number = f"{self.random_state.randint(1, 999):.1f}"
            else:
                number = str(self.random_state.randint(10000, 299999))
            return f"{catalog} {number}"

    def _sample_stellar_properties(self, spectral_type: SpectralType) -> Tuple[float, float, float]:
        """
        Samples mass, temperature, and luminosity for a given spectral type,
        ensuring they remain physically correlated.
        """
        props = STELLAR_CLASSES[spectral_type.value]
        m_min, m_max = props["mass_range"]
        t_min, t_max = props["temp_range"]
        l_min, l_max = props["lum_range"]

        # Sample mass uniformly within the range
        # Using a slightly skewed distribution (log-uniform) makes lower mass stars
        # more common even within a class, which is more realistic
        mass = math.exp(self.random_state.uniform(math.log(m_min), math.log(m_max)))

        # Find interpolation factor based on mass
        t = (mass - m_min) / (m_max - m_min) if m_max > m_min else 0.5
        t = np.clip(t, 0.0, 1.0)

        # Interpolate temperature linearly
        temperature = t_min + t * (t_max - t_min)

        # Interpolate luminosity log-linearly, as luminosity spans orders of magnitude
        log_l_min = math.log10(l_min)
        log_l_max = math.log10(l_max)
        log_lum = log_l_min + t * (log_l_max - log_l_min)
        luminosity = 10 ** log_lum

        return mass, temperature, luminosity

    def _generate_core_coordinates(self) -> Tuple[float, float, float]:
        """
        Generates coordinates in the dense galactic bulge.
        Models the core as a 3D triaxial ellipsoid ( central bar) tilted relative to the disk.
        """
        # Standard deviation for bulge dimensions
        # Elongated bar shape: longer in X, shorter in Y, flat in Z
        sigma_x = CORE_RADIUS * 0.7
        sigma_y = CORE_RADIUS * 0.4
        sigma_z = CORE_SCALE_HEIGHT

        # Sample coordinates along bar principal axes
        x_bar = self.random_state.normal(0, sigma_x)
        y_bar = self.random_state.normal(0, sigma_y)
        z = self.random_state.normal(0, sigma_z)

        # Rotate the bar by 45 degrees (~0.785 rad) to match Milky Way's bar angle
        bar_angle = 0.785398
        x = x_bar * math.cos(bar_angle) - y_bar * math.sin(bar_angle)
        y = x_bar * math.sin(bar_angle) + y_bar * math.cos(bar_angle)

        return x, y, z

    def _generate_arm_coordinates(self, theta_start: float, r_min: float, r_max: float) -> Tuple[float, float, float]:
        """
        Generates coordinates for a star in a spiral arm.
        Uses a logarithmic spiral formula with Gaussian dispersion.
        """
        # Sample radius - concentrate slightly closer to the core using Beta distribution
        # Beta(1.2, 2.0) is skewed towards 0, scaling it to [r_min, r_max]
        t = self.random_state.beta(1.2, 2.0)
        r = r_min + t * (r_max - r_min)

        # Central angle of the arm at radius r according to the logarithmic spiral:
        # theta = theta_start + 1/tan(pitch) * ln(r / r_min)
        b = math.tan(PITCH_ANGLE)
        theta_center = theta_start + (1.0 / b) * math.log(r / r_min)

        # Perpendicular dispersion in the plane of the disk (arm width)
        # Keeps physical width of the arm roughly constant
        disp_perp = self.random_state.normal(0, ARM_DISPERSION)
        
        # Convert perpendicular dispersion to an angular offset: d_theta = d_perp / r
        delta_theta = disp_perp / r
        
        # Radial dispersion
        delta_r = self.random_state.normal(0, ARM_DISPERSION * 0.5)
        
        # Add dispersion to coordinates
        final_r = r + delta_r
        final_theta = theta_center + delta_theta

        # Compute X and Y coordinates
        x = final_r * math.cos(final_theta)
        y = final_r * math.sin(final_theta)

        # Vertical height (Z axis) follows a thin disk Gaussian distribution
        z = self.random_state.normal(0, DISK_SCALE_HEIGHT)

        return x, y, z

    def _generate_disk_background_coordinates(self) -> Tuple[float, float, float]:
        """
        Generates coordinates for stars scattered across the disk, not belonging to any arm.
        Uses an exponential disk distribution.
        """
        # Exponential disk scale length (Milky Way is ~15,000 ly)
        scale_length = 15000.0
        
        # Sample radius using exponential distribution: P(r) ~ r * exp(-r/L)
        # We can sample r by sampling from a Gamma distribution Gamma(shape=2, scale=scale_length)
        r = self.random_state.gamma(2.0, scale_length)
        
        # Clip radius to galaxy boundary
        if r > GALAXY_RADIUS:
            r = self.random_state.uniform(0, GALAXY_RADIUS)

        # Angle is uniform
        theta = self.random_state.uniform(0, 2 * math.pi)

        x = r * math.cos(theta)
        y = r * math.sin(theta)
        z = self.random_state.normal(0, DISK_SCALE_HEIGHT * 1.5)  # Slightly thicker disk dispersion

        return x, y, z

    def generate_galaxy(self, num_stars: int = 1000) -> List[Star]:
        """
        Generates a list of Star objects following the spiral galaxy structure.
        """
        stars = []
        
        # 1. Determine spectral types based on probabilities
        classes = list(STELLAR_CLASSES.keys())
        probs = [STELLAR_CLASSES[c]["probability"] for c in classes]
        # Normalize probabilities to ensure they sum to exactly 1.0
        probs = np.array(probs) / np.sum(probs)
        
        sampled_classes = self.random_state.choice(classes, size=num_stars, p=probs)

        # 2. Determine region for each star
        regions = list(REGION_ALLOCATIONS.keys())
        region_probs = [REGION_ALLOCATIONS[r] for r in regions]
        region_probs = np.array(region_probs) / np.sum(region_probs)
        
        sampled_regions = self.random_state.choice(regions, size=num_stars, p=region_probs)

        # 3. Generate stars
        for i in range(num_stars):
            star_id = hashlib.sha256(f"{self.seed}-{i}".encode()).hexdigest()[:8]
            region = sampled_regions[i]
            spectral_type = SpectralType(sampled_classes[i])
            
            # Generate coordinates based on region
            if region == "Core":
                x, y, z = self._generate_core_coordinates()
            elif region == "Disk Background":
                x, y, z = self._generate_disk_background_coordinates()
            else:
                config = REGION_CONFIGS[region]
                x, y, z = self._generate_arm_coordinates(
                    theta_start=config["theta_start"],
                    r_min=config["r_min"],
                    r_max=config["r_max"]
                )

            # Sample physical properties
            mass, temp, lum = self._sample_stellar_properties(spectral_type)
            
            # Generate name
            name = self._generate_star_name(spectral_type, region)

            # Create Star object
            star = Star(
                id=star_id,
                name=name,
                star_type=spectral_type,
                mass=mass,
                temperature=temp,
                luminosity=lum,
                x=x,
                y=y,
                z=z,
                region=region
            )
            stars.append(star)

        return stars

    def save_stars_to_csv(self, stars: List[Star], file_path: str) -> None:
        """
        Saves the list of stars to a CSV file.
        """
        data = [star.to_dict() for star in stars]
        df = pd.DataFrame(data)
        # Order columns logically
        columns = ["id", "name", "star_type", "mass", "temperature", "luminosity", "x", "y", "z", "region"]
        df = df[columns]
        df.to_csv(file_path, index=False)
        print(f"Successfully generated and saved {len(stars)} stars to {file_path}")

if __name__ == "__main__":
    # Test execution
    generator = GalaxyGenerator(seed=42)
    stars = generator.generate_galaxy(1000)
    generator.save_stars_to_csv(stars, "stars_test.csv")
    for s in stars[:5]:
        print(s)
