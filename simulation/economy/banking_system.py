"""
banking_system.py — Credit accounts, investments, and national tax registers.
"""

from typing import Dict, Any, List

# Investment category identifiers
INVESTMENT_CATEGORIES = ["infrastructure", "research", "military"]


class EmpireBank:
    """Manages credit reserves, capital reserves, taxation, and investments for an empire."""

    def __init__(
        self,
        empire_id: str,
        initial_treasury: float,
        initial_reserves: float,
        tax_rate: float = 0.15
    ) -> None:
        self.empire_id = empire_id
        
        # Credit stockpiles
        self.treasury = initial_treasury
        self.capital_reserves = initial_reserves
        
        # Macro indicators
        self.gdp = 0.0
        self.gdp_growth = 0.0
        self.wealth_index = 1.0  # GDP per capita indicator
        self.tax_rate = tax_rate  # Tax rate (decimal multiplier)
        self.private_sector_growth = 0.02  # Base private growth rate (2%)
        
        # Investment budgets
        self.investments: Dict[str, float] = {cat: 0.0 for cat in INVESTMENT_CATEGORIES}

    def collect_taxes(self) -> float:
        """Collect taxes based on GDP and tax rate. Add to treasury.

        Returns
        -------
        float
            Taxes collected in Credits (GC).
        """
        tax_collected = self.gdp * self.tax_rate
        self.treasury += tax_collected
        return round(tax_collected, 2)

    def distribute_investments(self, personality: str) -> Dict[str, float]:
        """Disburse treasury credits into infrastructure, research, and military investments.

        Parameters
        ----------
        personality : str
            Civilization personality (Explorer, Scientific, Militaristic, etc.)

        Returns
        -------
        Dict[str, float]
            Investments distributed this tick.
        """
        disbursed = {cat: 0.0 for cat in INVESTMENT_CATEGORIES}
        
        # Reserve buffer check: always keep a reserve buffer of 20% of GDP
        reserve_threshold = 0.20 * self.gdp
        available_credits = max(0.0, self.treasury - reserve_threshold)
        
        if available_credits <= 0:
            return disbursed

        # Allocate spending based on civilization personality
        allocations = {cat: 0.20 for cat in INVESTMENT_CATEGORIES}  # Default symmetric spending

        if personality == "Militaristic":
            allocations["military"] = 0.60
            allocations["infrastructure"] = 0.20
            allocations["research"] = 0.20
        elif personality == "Scientific":
            allocations["research"] = 0.60
            allocations["infrastructure"] = 0.20
            allocations["military"] = 0.20
        elif personality == "Expansionist":
            allocations["infrastructure"] = 0.50
            allocations["research"] = 0.30
            allocations["military"] = 0.20
        elif personality == "Industrialist":
            allocations["infrastructure"] = 0.60
            allocations["research"] = 0.25
            allocations["military"] = 0.15
        elif personality == "Explorer":
            allocations["research"] = 0.45
            allocations["infrastructure"] = 0.35
            allocations["military"] = 0.20
        elif personality == "Isolationist":
            allocations["infrastructure"] = 0.40
            allocations["military"] = 0.40
            allocations["research"] = 0.20
        elif personality == "Diplomatic":
            allocations["infrastructure"] = 0.40
            allocations["research"] = 0.40
            allocations["military"] = 0.20

        # Disburse credits
        for cat in INVESTMENT_CATEGORIES:
            spend = available_credits * allocations[cat]
            self.investments[cat] += spend
            self.treasury -= spend
            disbursed[cat] = round(spend, 2)

        return disbursed

    def update_private_growth(self) -> None:
        """Update the private sector growth rate based on infrastructure investments."""
        # Infrastructure investments boost private sector GDP growth
        infra_ratio = self.investments["infrastructure"] / (self.gdp + 1.0)
        growth_boost = min(0.08, infra_ratio * 0.1)
        self.private_sector_growth = round(0.02 + growth_boost, 4)

    def pay_upkeep(self, upkeep_costs: float) -> bool:
        """Deduct upkeep costs (e.g. military/colony operational maintenance) from treasury.

        Parameters
        ----------
        upkeep_costs : float

        Returns
        -------
        bool
            True if treasury had sufficient funds, False if bankrupt.
        """
        self.treasury -= upkeep_costs
        if self.treasury < 0:
            # Transfer from capital reserves if available
            transfer = min(self.capital_reserves, abs(self.treasury))
            self.capital_reserves -= transfer
            self.treasury += transfer
            
        if self.treasury < 0:
            self.treasury = 0.0  # Bankrupt state
            return False
        return True

    def to_dict(self) -> Dict[str, Any]:
        """Convert bank state into a serializable dictionary."""
        return {
            "empire_id": self.empire_id,
            "treasury": round(self.treasury, 2),
            "capital_reserves": round(self.capital_reserves, 2),
            "gdp": round(self.gdp, 2),
            "gdp_growth": round(self.gdp_growth, 4),
            "wealth_index": round(self.wealth_index, 2),
            "private_sector_growth": round(self.private_sector_growth, 4),
            "infra_investment": round(self.investments["infrastructure"], 2),
            "research_investment": round(self.investments["research"], 2),
            "military_investment": round(self.investments["military"], 2),
        }
