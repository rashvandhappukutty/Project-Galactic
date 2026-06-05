"""
resource_exchange.py — Resource definitions, production, and consumption calculations.
"""

from typing import Dict, List, Any

# Define the 10 core galactic commodities
COMMODITIES = [
    "Iron",
    "Titanium",
    "Rare Minerals",
    "Water",
    "Helium-3",
    "Energy",
    "Food",
    "Advanced Components",
    "Quantum Materials",
    "Dark Matter Extracts"
]

# Planet type extraction multipliers
# Maps planet_type -> commodity -> production coefficient
EXTRACTION_MULTIPLIERS = {
    "Lava World": {
        "Iron": 2.5,
        "Titanium": 2.0,
        "Rare Minerals": 0.5,
        "Energy": 1.8,
        "Water": 0.0,
        "Food": 0.0,
        "Helium-3": 0.0
    },
    "Rocky": {
        "Iron": 1.2,
        "Titanium": 1.0,
        "Rare Minerals": 0.8,
        "Water": 0.3,
        "Food": 0.4,
        "Energy": 1.0,
        "Helium-3": 0.0
    },
    "Desert": {
        "Iron": 1.0,
        "Titanium": 0.8,
        "Rare Minerals": 1.5,
        "Energy": 1.6,
        "Water": 0.1,
        "Food": 0.2,
        "Helium-3": 0.0
    },
    "Ice": {
        "Water": 2.2,
        "Helium-3": 1.5,
        "Iron": 0.5,
        "Titanium": 0.5,
        "Rare Minerals": 0.4,
        "Energy": 0.6,
        "Food": 0.1
    },
    "Ocean": {
        "Water": 3.0,
        "Food": 2.5,
        "Iron": 0.4,
        "Titanium": 0.4,
        "Rare Minerals": 0.3,
        "Energy": 0.9,
        "Helium-3": 0.0
    },
    "Super Earth": {
        "Iron": 1.5,
        "Titanium": 1.5,
        "Rare Minerals": 1.2,
        "Water": 1.5,
        "Food": 2.0,
        "Energy": 1.2,
        "Helium-3": 0.0
    },
    "Gas Giant": {
        "Helium-3": 3.5,
        "Energy": 2.0,
        "Iron": 0.0,
        "Titanium": 0.0,
        "Rare Minerals": 0.0,
        "Water": 0.0,
        "Food": 0.0
    },
    "Toxic World": {
        "Rare Minerals": 2.2,
        "Titanium": 1.8,
        "Iron": 0.8,
        "Energy": 0.8,
        "Water": 0.0,
        "Food": 0.0,
        "Helium-3": 0.0
    }
}


class ResourceExchange:
    """Calculates production and consumption rates for colonies and empires."""

    @staticmethod
    def calculate_colony_production(
        planet_type: str,
        resource_score: float,
        development_level: float,
        tech_level: float,
        colony_type: str,
        population: float,
        inventories: Dict[str, float]
    ) -> Dict[str, float]:
        """Calculate production rates for a colony based on planetary and technological parameters.

        Parameters
        ----------
        planet_type : str
        resource_score : float
        development_level : float
        tech_level : float
        colony_type : str
        population : float
        inventories : Dict[str, float]

        Returns
        -------
        Dict[str, float]
            Rates of production (units per year/tick equivalent).
        """
        production = {c: 0.0 for c in COMMODITIES}
        dev_mult = development_level / 100.0
        tech_mult = 1.0 + (tech_level * 0.1)

        # 1. Raw extraction based on planet type and resource abundance
        multipliers = EXTRACTION_MULTIPLIERS.get(planet_type, EXTRACTION_MULTIPLIERS["Rocky"])
        
        # Base scale factor: resource abundance + population size modifier
        # Extraction needs population to labor, capping at 1e8 people for full production scale
        pop_labor_factor = min(1.0, population / 1e7) if population > 0 else 0.0
        base_extraction = (resource_score / 100.0) * dev_mult * tech_mult * pop_labor_factor * 100.0

        for commodity, coeff in multipliers.items():
            production[commodity] = base_extraction * coeff

        # 2. Adjust production based on Colony Type
        if colony_type == "Mining Colony":
            production["Iron"] *= 1.8
            production["Titanium"] *= 1.8
            production["Rare Minerals"] *= 1.8
        elif colony_type == "Industrial Colony":
            production["Iron"] *= 1.3
            production["Titanium"] *= 1.3
            production["Rare Minerals"] *= 1.2
        elif colony_type == "Trade Hub":
            # Trade hubs get slightly lower raw extraction but produce more energy
            production["Energy"] *= 1.5
        elif colony_type == "Research Colony":
            # Focus is research, raw output is slightly reduced
            for c in ["Iron", "Titanium", "Rare Minerals", "Water", "Food", "Helium-3"]:
                if c in production:
                    production[c] *= 0.7
        elif colony_type == "Capital Colony":
            # Well rounded production boost
            for c in production:
                production[c] *= 1.2

        # 3. High-Tech Manufacturing (consumes raw materials from stockpiles/inventories)
        # Advanced Components: Tech >= 3.0 required. Consumes Iron and Titanium.
        if tech_level >= 3.0 and population > 1e6:
            component_capacity = 10.0 * tech_mult * dev_mult * pop_labor_factor
            # Check input availability (need 1.0 Iron and 0.5 Titanium per component)
            iron_available = inventories.get("Iron", 0.0)
            titanium_available = inventories.get("Titanium", 0.0)
            
            # Max we can make based on raw inputs
            limit_by_iron = iron_available
            limit_by_titanium = titanium_available / 0.5
            components_to_produce = min(component_capacity, limit_by_iron, limit_by_titanium)
            
            if components_to_produce > 0:
                production["Advanced Components"] = components_to_produce
                # These inputs will be consumed during execution
                # We log the rates here; actual deduction is done in the engine
                production["_consume_Iron"] = components_to_produce
                production["_consume_Titanium"] = components_to_produce * 0.5

        # Quantum Materials: Tech >= 5.0 required. Consumes Rare Minerals and Helium-3.
        if tech_level >= 5.0 and population > 1e6:
            quantum_capacity = 5.0 * (tech_level - 4.0) * dev_mult * pop_labor_factor
            rare_available = inventories.get("Rare Minerals", 0.0)
            he3_available = inventories.get("Helium-3", 0.0)
            
            limit_by_rare = rare_available / 0.5
            limit_by_he3 = he3_available / 0.5
            quantum_to_produce = min(quantum_capacity, limit_by_rare, limit_by_he3)
            
            if quantum_to_produce > 0:
                production["Quantum Materials"] = quantum_to_produce
                production["_consume_Rare Minerals"] = quantum_to_produce * 0.5
                production["_consume_Helium-3"] = quantum_to_produce * 0.5

        # Dark Matter Extracts: Tech >= 7.0 required. Consumes Energy.
        if tech_level >= 7.0 and population > 5e6:
            dark_matter_capacity = 2.0 * (tech_level - 6.0) * dev_mult * pop_labor_factor
            energy_available = inventories.get("Energy", 0.0)
            
            limit_by_energy = energy_available / 2.0
            dark_matter_to_produce = min(dark_matter_capacity, limit_by_energy)
            
            if dark_matter_to_produce > 0:
                production["Dark Matter Extracts"] = dark_matter_to_produce
                production["_consume_Energy"] = dark_matter_to_produce * 2.0

        return production

    @staticmethod
    def calculate_colony_consumption(
        population: float,
        tech_level: float,
        colony_type: str,
        government: str
    ) -> Dict[str, float]:
        """Calculate resource consumption rates for a colony.

        Parameters
        ----------
        population : float
        tech_level : float
        colony_type : str
        government : str

        Returns
        -------
        Dict[str, float]
            Rates of consumption.
        """
        consumption = {c: 0.0 for c in COMMODITIES}
        if population <= 0:
            return consumption

        pop_mil = population / 1e6

        # 1. Demographic necessities (Food, Water, Energy)
        consumption["Food"] = 0.12 * pop_mil
        consumption["Water"] = 0.18 * pop_mil
        consumption["Energy"] = 0.25 * pop_mil * (1.0 + tech_level * 0.08)

        # 2. Technological & industrial upkeep
        if tech_level >= 3.0:
            # Advanced Components consumer demand
            consumption["Advanced Components"] = 0.02 * pop_mil * (tech_level / 3.0)
            
        if tech_level >= 4.0:
            # Fusion reactors consume Helium-3
            consumption["Helium-3"] = 0.04 * (tech_level ** 1.3)
            
        if tech_level >= 5.0:
            # Quantum tech and science labs consume Quantum Materials
            consumption["Quantum Materials"] = 0.015 * (tech_level ** 1.8)
            
        if tech_level >= 7.0:
            # High-tech systems consume Dark Matter
            consumption["Dark Matter Extracts"] = 0.008 * (tech_level ** 2.2)

        # 3. Adjust consumption based on colony type and government
        if colony_type == "Research Colony":
            consumption["Energy"] *= 1.4
            consumption["Quantum Materials"] *= 1.5
            consumption["Dark Matter Extracts"] *= 1.5
        elif colony_type == "Industrial Colony":
            consumption["Iron"] = 5.0 * (tech_level * 0.2)
            consumption["Titanium"] = 3.0 * (tech_level * 0.2)
            consumption["Energy"] *= 1.6
        elif colony_type == "Mining Colony":
            consumption["Energy"] *= 1.2
        elif colony_type == "Military Outpost":
            # Upkeep of bases requires titanium and advanced components
            consumption["Titanium"] = 2.0 * (tech_level * 0.1)
            consumption["Advanced Components"] *= 1.5
            consumption["Energy"] *= 1.3

        gov_upper = government.upper()
        if "TECHNOCRACY" in gov_upper or "AI" in gov_upper:
            consumption["Energy"] *= 1.15
            consumption["Quantum Materials"] *= 1.2
        elif "MONARCHY" in gov_upper or "EMPIRE" in gov_upper:
            # More militarized/heavy spending upkeep
            consumption["Advanced Components"] *= 1.1

        return consumption
