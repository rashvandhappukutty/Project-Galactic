"""
inflation_engine.py — Money supply velocity, CPI tracking, and exchange rate models.
"""

from typing import Dict, Any, List


class InflationEngine:
    """Calculates inflation rates, purchasing power index, and exchange rates for empires."""

    def __init__(self, empire_id: str) -> None:
        self.empire_id = empire_id
        
        # Monetary parameters
        self.money_supply = 10000.0  # Initial currency notes in circulation
        self.velocity = 1.2  # Initial money velocity index
        self.cpi = 1.0  # Consumer Price Index (1.0 = equilibrium base)
        self.inflation_rate = 0.02  # Initial inflation rate (2%)
        
        # Currency exchange rates relative to standard Galactic Credit (1.0 local = 1.0 GC initially)
        self.exchange_rate = 1.0
        self.purchasing_power_index = 1.0

    def calculate_inflation(
        self,
        gdp: float,
        prev_gdp: float,
        trade_volume: float,
        deficits: Dict[str, float],
        consumptions: Dict[str, float]
    ) -> float:
        """Calculate the inflation rate based on money growth, velocity, and commodity deficits.

        Parameters
        ----------
        gdp : float
            Current tick GDP.
        prev_gdp : float
            Previous tick GDP.
        trade_volume : float
            Total economic trade transaction value this tick.
        deficits : Dict[str, float]
            Deficit amounts of commodities.
        consumptions : Dict[str, float]
            Total consumption amounts of commodities.

        Returns
        -------
        float
            The calculated inflation rate (decimal fraction, e.g. 0.05 for 5%).
        """
        # 1. Money velocity scales with trade activity
        # High trade volume relative to GDP increases the speed at which currency changes hands
        new_velocity = 1.0 + (trade_volume / (gdp + 1.0)) * 0.5
        velocity_change_rate = (new_velocity - self.velocity) / self.velocity
        self.velocity = round(new_velocity, 2)

        # 2. Money supply expands with GDP growth and treasury loans
        # Money supply expansion rate matches GDP growth but with a small positive bias (seigniorage)
        gdp_growth_rate = (gdp - prev_gdp) / (prev_gdp + 1.0)
        money_expansion = max(0.01, gdp_growth_rate + 0.02)
        
        prev_money_supply = self.money_supply
        self.money_supply *= (1.0 + money_expansion)

        # 3. Supply Shock: Cost-push inflation due to shortages of essentials (Food, Water, Energy)
        deficit_shocks = []
        for essential in ["Food", "Water", "Energy"]:
            def_val = deficits.get(essential, 0.0)
            cons_val = consumptions.get(essential, 1.0)
            ratio = def_val / (cons_val + 1.0)
            deficit_shocks.append(ratio)
        
        supply_shock_index = sum(deficit_shocks)  # Ranges from 0.0 upwards

        # 4. Monetary Equation of Exchange: MV = PY -> P = MV / Y
        # Delta P / P = Delta M / M + Delta V / V - Delta Y / Y
        monetary_inflation = money_expansion + velocity_change_rate - gdp_growth_rate
        
        # Combine monetary inflation with supply shocks
        # If supply shock is high, prices spike rapidly
        total_inflation = 0.6 * monetary_inflation + 0.4 * supply_shock_index
        
        # Enforce realistic bounds (-5% deflation to 150% hyperinflation per tick)
        self.inflation_rate = max(-0.05, min(1.50, total_inflation))
        
        # Update CPI
        self.cpi *= (1.0 + self.inflation_rate)
        self.cpi = max(0.05, round(self.cpi, 3))
        
        # Purchasing Power: Inverse of CPI
        self.purchasing_power_index = round(1.0 / self.cpi, 3)
        self.money_supply = round(self.money_supply, 2)

        return self.inflation_rate

    def update_exchange_rate(self, global_inflation_avg: float, gdp_growth: float) -> float:
        """Update the currency strength (exchange rate) relative to standard Galactic Credit (GC).

        Parameters
        ----------
        global_inflation_avg : float
            Average inflation across the galaxy.
        gdp_growth : float
            GDP growth rate of the local empire.

        Returns
        -------
        float
            New exchange rate (local currency per 1 GC).
            Higher exchange rate = weaker currency.
        """
        # Local currency weakens if local inflation is higher than global average
        # Local currency strengthens if local GDP growth is strong (increases foreign demand)
        inflation_gap = self.inflation_rate - global_inflation_avg
        adjustment = inflation_gap - 0.25 * gdp_growth
        
        # Clamp adjustment per tick
        adjustment = max(-0.25, min(0.35, adjustment))
        
        new_rate = self.exchange_rate * (1.0 + adjustment)
        
        # Hard bounds: clamp exchange rates between 0.1 and 15.0 local per GC
        self.exchange_rate = round(max(0.1, min(15.0, new_rate)), 3)
        return self.exchange_rate

    def to_dict(self) -> Dict[str, Any]:
        """Convert engine state into a serializable dictionary."""
        return {
            "empire_id": self.empire_id,
            "money_supply": self.money_supply,
            "velocity": self.velocity,
            "cpi": self.cpi,
            "inflation_rate": round(self.inflation_rate, 4),
            "exchange_rate": self.exchange_rate,
            "purchasing_power_index": self.purchasing_power_index,
        }
