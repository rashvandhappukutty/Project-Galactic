"""
Unit tests for the Galaxy Generation system.
Verifies structure, physical properties, and reproducibility.
"""

import os
import unittest
import numpy as np
from simulation.galaxy.constants import STELLAR_CLASSES, GALAXY_RADIUS
from simulation.galaxy.star import Star, SpectralType
from simulation.galaxy.galaxy_generator import GalaxyGenerator

class TestGalaxyGeneration(unittest.TestCase):
    
    def setUp(self):
        # Set up generator with fixed seed for reproducibility
        self.generator = GalaxyGenerator(seed=42)
        self.stars = self.generator.generate_galaxy(num_stars=500)

    def test_star_count(self):
        """Verify that the exact requested number of stars are generated."""
        self.assertEqual(len(self.stars), 500)

    def test_serialization(self):
        """Verify that Star objects serialize and deserialize correctly without data loss."""
        star = self.stars[0]
        star_dict = star.to_dict()
        
        # Verify keys
        expected_keys = {"id", "name", "star_type", "mass", "temperature", "luminosity", "x", "y", "z", "region"}
        self.assertEqual(set(star_dict.keys()), expected_keys)
        
        # Reconstruct
        reconstructed_star = Star.from_dict(star_dict)
        self.assertEqual(star.id, reconstructed_star.id)
        self.assertEqual(star.name, reconstructed_star.name)
        self.assertEqual(star.star_type, reconstructed_star.star_type)
        self.assertEqual(star.mass, reconstructed_star.mass)
        self.assertEqual(star.temperature, reconstructed_star.temperature)
        self.assertEqual(star.luminosity, reconstructed_star.luminosity)
        self.assertEqual(star.x, reconstructed_star.x)
        self.assertEqual(star.y, reconstructed_star.y)
        self.assertEqual(star.z, reconstructed_star.z)
        self.assertEqual(star.region, reconstructed_star.region)

    def test_stellar_physics_boundaries(self):
        """Verify that the physical properties of generated stars correspond to their MK spectral types."""
        for star in self.stars:
            class_limits = STELLAR_CLASSES[star.star_type.value]
            
            # Mass bounds
            self.assertTrue(
                class_limits["mass_range"][0] <= star.mass <= class_limits["mass_range"][1],
                f"Star {star.name} of type {star.star_type} has mass {star.mass} out of bounds {class_limits['mass_range']}"
            )
            
            # Temperature bounds
            self.assertTrue(
                class_limits["temp_range"][0] <= star.temperature <= class_limits["temp_range"][1],
                f"Star {star.name} of type {star.star_type} has temperature {star.temperature} out of bounds {class_limits['temp_range']}"
            )
            
            # Luminosity bounds
            self.assertTrue(
                class_limits["lum_range"][0] <= star.luminosity <= class_limits["lum_range"][1],
                f"Star {star.name} of type {star.star_type} has luminosity {star.luminosity} out of bounds {class_limits['lum_range']}"
            )

    def test_geometric_limits(self):
        """Verify that coordinates are valid and stars fall within the galaxy boundary."""
        for star in self.stars:
            self.assertFalse(np.isnan(star.x))
            self.assertFalse(np.isnan(star.y))
            self.assertFalse(np.isnan(star.z))
            
            # Distance from center
            distance_from_center = np.sqrt(star.x**2 + star.y**2 + star.z**2)
            
            # Allow some margin (e.g., 20%) for arm dispersion beyond nominal radius
            max_allowed_distance = GALAXY_RADIUS * 1.3
            self.assertLess(
                distance_from_center, 
                max_allowed_distance,
                f"Star {star.name} is too far from center: {distance_from_center:.1f} ly (max allowed: {max_allowed_distance:.1f} ly)"
            )

    def test_reproducibility(self):
        """Verify that the same seed produces the identical galaxy structure."""
        gen1 = GalaxyGenerator(seed=100)
        stars1 = gen1.generate_galaxy(100)
        
        gen2 = GalaxyGenerator(seed=100)
        stars2 = gen2.generate_galaxy(100)
        
        for s1, s2 in zip(stars1, stars2):
            self.assertEqual(s1.id, s2.id)
            self.assertEqual(s1.name, s2.name)
            self.assertEqual(s1.x, s2.x)
            self.assertEqual(s1.y, s2.y)
            self.assertEqual(s1.z, s2.z)

if __name__ == "__main__":
    unittest.main()
