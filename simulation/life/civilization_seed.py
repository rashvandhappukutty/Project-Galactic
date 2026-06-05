"""
civilization_seed.py — CivilizationSeedGenerator class for the Galactic Dream Engine.

Phase 3 – Life Emergence Engine
"""

import hashlib
import re
from enum import Enum
from typing import Any

import numpy as np

from simulation.life.species import Species, Civilization


class CivilizationSeedGenerator:
    """Generates sentient species and seeds civilizations on advanced planets.

    Uses a seeded NumPy RandomState for reproducible generation.

    Parameters
    ----------
    seed : int, default 42
        Random seed for reproducibility.
    """

    def __init__(self, seed: int = 42) -> None:
        self.random = np.random.RandomState(seed)

    def _generate_species_name(self, planet_name: str) -> str:
        """Procedurally generate a species name derived from the planet name.

        Parameters
        ----------
        planet_name : str
            The name of the planet, e.g. "Eta Galacticis-e".

        Returns
        -------
        str
            A capitalized, pronounceable species name.
        """
        # Strip suffix like -b, -c, -e, etc.
        base_name = re.sub(r"-[b-j]$", "", planet_name).strip()

        # Check if the name consists of numbers/catalog codes
        has_digits = any(c.isdigit() for c in base_name)

        prefixes = [
            "Aurel",
            "Vesper",
            "Zylar",
            "Kaelum",
            "Xen",
            "Orion",
            "Zel",
            "Thran",
            "Sol",
            "Mer",
            "Val",
        ]
        suffixes = ["ian", "ite", "an", "is", "ex", "oid", "ari"]

        if has_digits or len(base_name) < 3:
            # Catalog name, generate purely procedural name
            p = self.random.choice(prefixes)
            s = self.random.choice(suffixes)
            return f"{p}{s}"
        else:
            # Derive from planet name (e.g. "Eta Galacticis")
            words = base_name.split()
            core_word = words[-1] if words else base_name

            # Strip vowel/classic endings
            for end in ["is", "us", "a", "e", "i", "o", "um"]:
                if core_word.lower().endswith(end):
                    core_word = core_word[: -len(end)]
                    break

            roll = self.random.choice([0, 1, 2, 3])
            if roll == 0:
                name = f"{core_word}an"
            elif roll == 1:
                name = f"{core_word}ian"
            elif roll == 2:
                name = f"{core_word}ite"
            else:
                if len(words) >= 2:
                    name = f"{words[0]}-{core_word}is"
                else:
                    name = f"{core_word}is"

            # Clean and ensure it's capitalized
            final_name = name.strip().capitalize()
            if len(final_name) < 3:
                # Fallback to pure procedural
                return f"{self.random.choice(prefixes)}{self.random.choice(suffixes)}"
            return final_name

    def generate_species_for_planet(
        self, planet: Any, star_system: Any
    ) -> Species:
        """Generate a sentient species for a Stage 4 or 5 planet.

        Parameters
        ----------
        planet : Any
            The Planet object.
        star_system : Any
            The StarSystem object containing the planet.

        Returns
        -------
        Species
            The newly created sentient species.
        """
        planet_name = str(getattr(planet, "planet_name", "Unknown-Planet"))
        planet_id = str(getattr(planet, "planet_id", "unknown_id"))
        stage = int(getattr(planet, "life_stage", 4))

        # 1. Procedural Name
        name = self._generate_species_name(planet_name)

        # 2. Intelligence
        # base 50 + habitability * 0.2 + resource_score * 0.1 + normal scatter (sigma=10)
        habitability = float(getattr(planet, "habitability_score", 0.0))
        resource_score = float(getattr(planet, "resource_score", 0.0))
        scatter_intel = self.random.normal(0.0, 10.0)
        intelligence = 50.0 + habitability * 0.2 + resource_score * 0.1 + scatter_intel
        if stage == 5:
            intelligence += 15.0
        intelligence = max(1.0, min(intelligence, 100.0))

        # 3. Cooperation
        # base 40 + age_billion_years * 2 + normal scatter
        system_age = float(getattr(star_system, "age_billion_years", 0.0))
        scatter_coop = self.random.normal(0.0, 10.0)
        cooperation = 40.0 + system_age * 2.0 + scatter_coop
        cooperation = max(1.0, min(cooperation, 100.0))

        # 4. Aggression
        # base 50 - cooperation * 0.2 + normal scatter
        scatter_aggr = self.random.normal(0.0, 10.0)
        aggression = 50.0 - cooperation * 0.2 + scatter_aggr
        aggression = max(1.0, min(aggression, 100.0))

        # 5. Adaptability
        # base 40 + normal scatter
        scatter_adapt = self.random.normal(0.0, 10.0)
        adaptability = 40.0 + scatter_adapt
        adaptability = max(1.0, min(adaptability, 100.0))

        # 6. Lifespan
        # base 30 + gravity * 15 + normal scatter
        gravity = float(getattr(planet, "gravity", 1.0))
        scatter_life = self.random.normal(0.0, 10.0)
        lifespan = 30.0 + gravity * 15.0 + scatter_life
        lifespan = max(10.0, min(lifespan, 1000.0))

        # 7. Population
        # Rocky/Ocean/SuperEarth have populations between 10M and 15B
        radius = float(getattr(planet, "radius", 1.0))
        planet_type = getattr(planet, "planet_type", "")
        if isinstance(planet_type, Enum):
            planet_type_str = planet_type.value
        else:
            planet_type_str = str(planet_type)

        is_primary_habitable = planet_type_str in ["Rocky", "Ocean", "Super Earth"]

        if is_primary_habitable:
            # Scales with planet surface area (radius squared)
            area_factor = radius ** 2
            rand_mult = self.random.uniform(0.5, 2.0)
            population = 5.0e9 * area_factor * rand_mult
            population = max(1.0e7, min(population, 1.5e10))
        else:
            # Other planet types support lower populations
            area_factor = radius ** 2
            rand_mult = self.random.uniform(0.1, 1.0)
            population = 1.0e9 * area_factor * rand_mult
            population = max(1.0e6, min(population, 1.0e9))

        population = float(round(population))

        # 8. Species ID
        species_id = hashlib.sha256(
            f"{planet_id}-species-{self.random.randint(1000000)}".encode()
        ).hexdigest()[:10]

        species = Species(
            species_id=species_id,
            name=name,
            planet_id=planet_id,
            intelligence=round(intelligence, 2),
            cooperation=round(cooperation, 2),
            aggression=round(aggression, 2),
            adaptability=round(adaptability, 2),
            lifespan=round(lifespan, 2),
            population=population,
        )

        # Attach species dynamically to planet
        setattr(planet, "species", species)

        return species

    def seed_civilization(
        self, planet: Any, species: Species, stage: int
    ) -> Civilization:
        """Seed a civilization for a Stage 4 or 5 planet using a species.

        Parameters
        ----------
        planet : Any
            The Planet object.
        species : Species
            The dominant sentient species.
        stage : int
            The current life stage of the planet (4 or 5).

        Returns
        -------
        Civilization
            The newly created civilization.
        """
        planet_id = str(getattr(planet, "planet_id", "unknown_id"))

        # 1. Procedural Civilization Name
        # High cooperation/low aggression -> Democratic/Federation structures
        # Low cooperation/high aggression -> Empire/Hive structures
        # High intelligence -> Technocracy/Scientific Directorate
        if species.cooperation > 70.0 and species.aggression < 30.0:
            templates = [
                "The {species} Federation",
                "Republic of {species}",
                "{species} Commonwealth",
            ]
        elif species.cooperation < 30.0 and species.aggression > 70.0:
            templates = [
                "{species} Hive Collective",
                "Holy {species} Empire",
                "Dominion of {species}",
            ]
        elif species.intelligence > 75.0:
            templates = [
                "{species} Directorate",
                "Unified {species} Council",
                "Scientific {species} Union",
            ]
        else:
            templates = [
                "The {species} Federation",
                "Consolidated {species} Worlds",
                "Allied {species} Systems",
                "{species} Commonwealth",
            ]

        selected_template = self.random.choice(templates)
        civ_name = selected_template.format(species=species.name)

        # 2. Technology level
        # base 50 + species.intelligence * 0.3 + normal scatter. Clamp to [10, 100] (boosted to 80-100 if stage is 5)
        scatter_tech = self.random.normal(0.0, 10.0)
        tech_level = 50.0 + species.intelligence * 0.3 + scatter_tech
        if stage == 5:
            # Shift distribution up and clamp to [80, 100]
            tech_level += 25.0
            tech_level = max(80.0, min(tech_level, 100.0))
        else:
            tech_level = max(10.0, min(tech_level, 100.0))

        # 3. Energy source
        # Tech < 40: Fossil, 40-60: Nuclear, 60-80: Fusion, 80-95: Antimatter, >= 95: Dyson Swarm Prototype
        if tech_level < 40.0:
            energy_source = "Fossil"
        elif tech_level < 60.0:
            energy_source = "Nuclear"
        elif tech_level < 80.0:
            energy_source = "Fusion"
        elif tech_level < 95.0:
            energy_source = "Antimatter"
        else:
            energy_source = "Dyson Swarm Prototype"

        # 4. Government type
        # Democracy, Technocracy, Federation, Monarchy, Collective, AI Governance, Scientific Council
        # Weighted by species cooperation and aggression
        weights = {
            "Democracy": 10.0,
            "Technocracy": 10.0,
            "Federation": 10.0,
            "Monarchy": 10.0,
            "Collective": 10.0,
            "AI Governance": 10.0,
            "Scientific Council": 10.0,
        }

        # Adjust weights dynamically based on species traits
        if species.cooperation > 60.0:
            weights["Democracy"] += (species.cooperation - 60.0) * 0.8
            weights["Federation"] += (species.cooperation - 60.0) * 0.8

        if species.cooperation < 40.0:
            weights["Monarchy"] += (40.0 - species.cooperation) * 1.2

        if species.intelligence > 60.0:
            weights["Technocracy"] += (species.intelligence - 60.0) * 1.0
            weights["Scientific Council"] += (species.intelligence - 60.0) * 1.0

        if species.aggression > 60.0:
            weights["Collective"] += (species.aggression - 60.0) * 1.5

        if species.intelligence > 80.0:
            weights["AI Governance"] += (species.intelligence - 80.0) * 1.2

        gov_list = list(weights.keys())
        weight_values = np.array([weights[g] for g in gov_list], dtype=np.float64)
        weight_values = np.clip(weight_values, 0.1, None)  # Safety floor
        weight_values /= weight_values.sum()

        government_type = str(self.random.choice(gov_list, p=weight_values))

        # 5. Civilization age
        # Random uniform between 1,000 and 100,000 years. If stage 5, age = 50,000 to 500,000 years.
        if stage == 5:
            civ_age = self.random.uniform(50000.0, 500000.0)
        else:
            civ_age = self.random.uniform(1000.0, 100000.0)
        civ_age = float(round(civ_age))

        # 6. Civilization ID
        civilization_id = hashlib.sha256(
            f"{planet_id}-civ-{self.random.randint(1000000)}".encode()
        ).hexdigest()[:10]

        civilization = Civilization(
            civilization_id=civilization_id,
            name=civ_name,
            species=species,
            planet_id=planet_id,
            tech_level=round(tech_level, 2),
            energy_source=energy_source,
            government_type=government_type,
            civilization_age=civ_age,
        )

        # Attach civilization dynamically to planet
        setattr(planet, "civilization", civilization)

        return civilization
