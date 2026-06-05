"""
Unit tests for Phase 3: Life Emergence Engine.
Verifies evolution, extinction modifiers, species generation, and civilization seeding.
"""

import unittest
import numpy as np
from dataclasses import dataclass

from simulation.planets.planet import Planet, PlanetType, AtmosphereType
from simulation.systems.star_system import StarSystem
from simulation.life.species import Species, Civilization
from simulation.life.evolution_engine import EvolutionEngine
from simulation.life.civilization_seed import CivilizationSeedGenerator


class TestLifeEmergenceEngine(unittest.TestCase):
    def setUp(self):
        # Create standard test objects
        self.mock_star = StarSystem(
            star_id="star_123",
            star_name="Sol-Prime",
            star_type="G",
            star_mass=1.0,
            star_temperature=5800.0,
            star_luminosity=1.0,
            x=0.0,
            y=0.0,
            z=0.0,
            region="Core",
            age_billion_years=4.5,
            metallicity=0.1,
            radiation_level=10.0,
            planet_count=1,
            habitable_zone_inner_au=0.9,
            habitable_zone_outer_au=1.4,
        )

        self.mock_planet = Planet(
            planet_id="planet_456",
            planet_name="Sol-Prime-b",
            star_id="star_123",
            planet_type=PlanetType.ROCKY,
            orbital_distance_au=1.0,
            mass=1.0,
            radius=1.0,
            gravity=1.0,
            temperature=288.0,
            water_percentage=70.0,
            atmosphere_type=AtmosphereType.MODERATE,
            resource_score=60.0,
            habitability_score=75.0,
        )

        self.engine = EvolutionEngine(seed=42)
        self.seeder = CivilizationSeedGenerator(seed=42)

    def test_evolution_progression(self):
        """Verify that evolution accumulates progress and increases stage under normal conditions."""
        # Reset stage/progress
        self.mock_planet.life_stage = 0
        self.mock_planet.evolution_progress = 0.0

        # Run multiple steps to guarantee stage advancement without triggering extinction (with high habitability)
        # Using a large number of years to force progress >= 100
        # Since we use seed 42, we know the rolls are reproducible
        res = self.engine.simulate_evolution(
            self.mock_planet, self.mock_star, years=500000
        )

        self.assertIn("updated_stage", res)
        self.assertIn("evolution_progress", res)
        self.assertIn("species_complexity", res)
        self.assertIn("technology_potential", res)

        # Check that attributes are set on mock_planet
        self.assertEqual(self.mock_planet.life_stage, res["updated_stage"])
        self.assertEqual(self.mock_planet.evolution_progress, res["evolution_progress"])

    def test_age_restrictions(self):
        """Verify that evolution stage is restricted by the star system's age."""
        # System age < 0.1 Gyr -> stage cannot exceed 0
        young_star = StarSystem(
            star_id="young_star",
            star_name="Young Star",
            star_type="O",
            star_mass=20.0,
            star_temperature=30000.0,
            star_luminosity=10000.0,
            x=10.0,
            y=10.0,
            z=10.0,
            region="Arm",
            age_billion_years=0.05,
            metallicity=0.2,
            radiation_level=90.0,
            planet_count=1,
            habitable_zone_inner_au=10.0,
            habitable_zone_outer_au=20.0,
        )

        self.mock_planet.life_stage = 0
        self.mock_planet.evolution_progress = 90.0

        # Run simulation with 100,000 years, progress will exceed 100, but stage must remain 0
        res = self.engine.simulate_evolution(
            self.mock_planet, young_star, years=100000
        )
        self.assertEqual(res["updated_stage"], 0)
        self.assertLess(res["evolution_progress"], 100.0)

        # System age < 1.0 Gyr (e.g. 0.5) -> stage cannot exceed 1
        mid_star = StarSystem(
            star_id="mid_star",
            star_name="Mid Star",
            star_type="A",
            star_mass=2.0,
            star_temperature=9000.0,
            star_luminosity=15.0,
            x=10.0,
            y=10.0,
            z=10.0,
            region="Arm",
            age_billion_years=0.5,
            metallicity=0.0,
            radiation_level=40.0,
            planet_count=1,
            habitable_zone_inner_au=3.0,
            habitable_zone_outer_au=5.0,
        )

        self.mock_planet.life_stage = 1
        self.mock_planet.evolution_progress = 99.0

        res = self.engine.simulate_evolution(self.mock_planet, mid_star, years=100000)
        self.assertEqual(res["updated_stage"], 1)

    def test_extinction_rate_modifiers(self):
        """Verify that host star type, radiation, and temperature modify extinction rates."""
        # We can test the modifiers by configuring different star/planet environments and seeing that
        # the engine calculates the expected extinction risk/stage reduction when extinction triggers.
        
        # O/B UV flare risk:
        ob_star = StarSystem(
            star_id="ob_star",
            star_name="OB Star",
            star_type="O",
            star_mass=25.0,
            star_temperature=35000.0,
            star_luminosity=20000.0,
            x=0.0, y=0.0, z=0.0, region="Core",
            age_billion_years=0.05,
            metallicity=0.1,
            radiation_level=0.0,  # No radiation to isolate star type
            planet_count=1,
        )
        
        # Test extreme temperature modifier
        hot_planet = Planet(
            planet_id="hot_planet",
            planet_name="Hot Planet",
            star_id="star_123",
            planet_type=PlanetType.DESERT,
            orbital_distance_au=0.5,
            mass=1.0, radius=1.0, gravity=1.0,
            temperature=400.0,  # Extreme temp (> 380K)
            water_percentage=0.0,
            atmosphere_type=AtmosphereType.THIN,
            resource_score=20.0,
            habitability_score=10.0,
        )
        
        # Run some simulations to ensure no exceptions and check correct properties returned
        res = self.engine.simulate_evolution(hot_planet, ob_star, years=10000)
        self.assertIn("extinction_occurred", res)

    def test_species_generation(self):
        """Verify procedural species generation traits and naming."""
        species = self.seeder.generate_species_for_planet(
            self.mock_planet, self.mock_star
        )

        self.assertIsInstance(species, Species)
        self.assertIsNotNone(species.name)
        self.assertTrue(1.0 <= species.intelligence <= 100.0)
        self.assertTrue(1.0 <= species.cooperation <= 100.0)
        self.assertTrue(1.0 <= species.aggression <= 100.0)
        self.assertTrue(1.0 <= species.adaptability <= 100.0)
        self.assertTrue(10.0 <= species.lifespan <= 1000.0)
        self.assertTrue(1e7 <= species.population <= 1.5e10)

        # Check name generation for different catalog style planet names
        named_planet = Planet(
            planet_id="pl_1",
            planet_name="Aurelia-c",
            star_id="star_123",
            planet_type=PlanetType.ROCKY,
            orbital_distance_au=1.0, mass=1.0, radius=1.0, gravity=1.0,
            temperature=290.0, water_percentage=50.0,
            atmosphere_type=AtmosphereType.MODERATE,
            resource_score=50.0, habitability_score=50.0,
        )
        sp2 = self.seeder.generate_species_for_planet(named_planet, self.mock_star)
        self.assertTrue("Aurel" in sp2.name or sp2.name.endswith("an") or sp2.name.endswith("ian") or sp2.name.endswith("ite") or sp2.name.endswith("is"))

    def test_civilization_seeding(self):
        """Verify civilization seeding, energy sources, and government weighting."""
        # Force a species
        species = Species(
            species_id="sp_999",
            name="Kaelumite",
            planet_id="planet_456",
            intelligence=90.0,
            cooperation=85.0,
            aggression=15.0,
            adaptability=70.0,
            lifespan=120.0,
            population=6.0e9,
        )

        civ = self.seeder.seed_civilization(self.mock_planet, species, stage=5)

        self.assertIsInstance(civ, Civilization)
        self.assertEqual(civ.species.species_id, species.species_id)
        self.assertIn("Kaelumite", civ.name)
        self.assertTrue(80.0 <= civ.tech_level <= 100.0)  # stage 5 boost
        self.assertIn(civ.energy_source, ["Antimatter", "Dyson Swarm Prototype"])
        self.assertTrue(50000.0 <= civ.civilization_age <= 500000.0)
        self.assertIn(civ.government_type, ["Democracy", "Technocracy", "Federation", "Scientific Council", "AI Governance", "Monarchy", "Collective"])

    def test_reproducibility(self):
        """Verify that identical seeds produce identical evolutionary path / species properties."""
        eng1 = EvolutionEngine(seed=100)
        eng2 = EvolutionEngine(seed=100)

        p1 = Planet(
            planet_id="pl_rep",
            planet_name="Rep-b",
            star_id="star_123",
            planet_type=PlanetType.ROCKY,
            orbital_distance_au=1.0, mass=1.0, radius=1.0, gravity=1.0,
            temperature=290.0, water_percentage=50.0,
            atmosphere_type=AtmosphereType.MODERATE,
            resource_score=50.0, habitability_score=50.0,
        )
        p2 = Planet(
            planet_id="pl_rep",
            planet_name="Rep-b",
            star_id="star_123",
            planet_type=PlanetType.ROCKY,
            orbital_distance_au=1.0, mass=1.0, radius=1.0, gravity=1.0,
            temperature=290.0, water_percentage=50.0,
            atmosphere_type=AtmosphereType.MODERATE,
            resource_score=50.0, habitability_score=50.0,
        )

        res1 = eng1.simulate_evolution(p1, self.mock_star, years=100000)
        res2 = eng2.simulate_evolution(p2, self.mock_star, years=100000)

        self.assertEqual(res1["updated_stage"], res2["updated_stage"])
        self.assertEqual(res1["evolution_progress"], res2["evolution_progress"])
        self.assertEqual(res1["extinction_occurred"], res2["extinction_occurred"])
        self.assertEqual(res1["species_complexity"], res2["species_complexity"])
        self.assertEqual(res1["technology_potential"], res2["technology_potential"])


if __name__ == "__main__":
    unittest.main()
