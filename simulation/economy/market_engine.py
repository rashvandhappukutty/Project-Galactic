"""
market_engine.py — Dynamic pricing, price volatility, and value index logic.
"""

from typing import Dict, List, Any
from simulation.economy.resource_exchange import COMMODITIES

# Base prices in standard Galactic Credits (GC)
BASE_PRICES = {
    "Iron": 10.0,
    "Titanium": 15.0,
    "Rare Minerals": 25.0,
    "Water": 5.0,
    "Helium-3": 20.0,
    "Energy": 8.0,
    "Food": 6.0,
    "Advanced Components": 50.0,
    "Quantum Materials": 120.0,
    "Dark Matter Extracts": 300.0
}


class LocalMarket:
    """Manages inventories, prices, historical prices, and volatility for a single colony market."""

    def __init__(self, colony_id: str) -> None:
        self.colony_id = colony_id
        
        # Initialize inventories with small start stockpile
        self.inventory: Dict[str, float] = {c: 50.0 for c in COMMODITIES}
        
        # Initialize prices at base price
        self.prices: Dict[str, float] = {c: BASE_PRICES[c] for c in COMMODITIES}
        
        # Track histories
        self.price_history: Dict[str, List[float]] = {c: [BASE_PRICES[c]] for c in COMMODITIES}
        self.volatility: Dict[str, float] = {c: 0.05 for c in COMMODITIES}
        self.resource_value_index: Dict[str, float] = {c: 1.0 for c in COMMODITIES}

    def update_prices(
        self,
        production_rates: Dict[str, float],
        consumption_rates: Dict[str, float],
        is_war: bool,
        tech_level: float
    ) -> None:
        """Update market commodity prices based on supply, demand, war, and technology.

        Parameters
        ----------
        production_rates : Dict[str, float]
            Commodity production rates in the local market.
        consumption_rates : Dict[str, float]
            Commodity consumption rates in the local market.
        is_war : bool
            War state modifier.
        tech_level : float
            Technology level modifier.
        """
        for commodity in COMMODITIES:
            base_price = BASE_PRICES[commodity]
            
            # War shocks: militarized demand boosts base prices of strategic goods
            if is_war:
                if commodity in ["Iron", "Titanium", "Advanced Components"]:
                    base_price *= 1.6
                elif commodity == "Food" or commodity == "Water":
                    base_price *= 1.2

            # Technology adjustments: high tech lowers manufacturing costs of high-tech goods
            if tech_level > 5.0:
                if commodity == "Advanced Components":
                    base_price *= max(0.6, 1.0 - (tech_level - 5.0) * 0.05)
                elif commodity == "Quantum Materials":
                    base_price *= max(0.6, 1.0 - (tech_level - 5.0) * 0.05)
                elif commodity == "Dark Matter Extracts":
                    base_price *= max(0.7, 1.0 - (tech_level - 7.0) * 0.06) if tech_level >= 7.0 else 1.0

            supply = production_rates.get(commodity, 0.0)
            demand = consumption_rates.get(commodity, 0.0)
            stockpile = self.inventory.get(commodity, 0.0)

            # Price pressure formula:
            # - Excess demand drives price up.
            # - Excess supply or large stockpiles drive price down.
            # Stockpile is represented as a buffer, where a stockpile equal to 10 ticks of demand is considered healthy.
            demand_buffer = max(1.0, demand * 5.0)
            stockpile_ratio = stockpile / demand_buffer

            # Price adjustment factor: scales dynamically based on short-term gap and long-term stockpile
            short_term_gap = (demand - supply) / (demand + supply + 1.0)
            
            # Stockpile factor pulls prices down if stockpile is high, or up if stockpile is depleted
            if stockpile_ratio > 2.0:
                stockpile_factor = -0.15 * min(3.0, stockpile_ratio - 2.0)
            elif stockpile_ratio < 0.5:
                stockpile_factor = 0.25 * (1.0 - stockpile_ratio)
            else:
                stockpile_factor = 0.0

            adjustment = 0.2 * short_term_gap + stockpile_factor
            
            # Clamp the maximum change in one tick to prevent hyper-spikes
            adjustment = max(-0.35, min(0.50, adjustment))

            old_price = self.prices[commodity]
            new_price = old_price * (1.0 + adjustment)

            # Hard bounds: clamp prices between 10% of base price and 800% of base price
            min_price = base_price * 0.1
            max_price = base_price * 8.0
            new_price = max(min_price, min(max_price, new_price))

            self.prices[commodity] = round(new_price, 2)
            self.price_history[commodity].append(self.prices[commodity])

            # Update volatility: standard exponential moving average of percentage changes
            pct_change = abs(new_price - old_price) / old_price
            self.volatility[commodity] = round(0.85 * self.volatility[commodity] + 0.15 * pct_change, 3)

            # Value Index: relative value indicator of resource scarcity (1.0 = baseline equilibrium)
            self.resource_value_index[commodity] = round(new_price / BASE_PRICES[commodity], 2)

    def to_dict(self) -> Dict[str, Any]:
        """Convert market state into serializable dictionary."""
        state = {"colony_id": self.colony_id}
        for commodity in COMMODITIES:
            state[f"{commodity}_inventory"] = round(self.inventory[commodity], 1)
            state[f"{commodity}_price"] = self.prices[commodity]
            state[f"{commodity}_volatility"] = self.volatility[commodity]
            state[f"{commodity}_value_index"] = self.resource_value_index[commodity]
        return state
