"""
test_phase7.py — Unit tests and validation suite for Phase 7 Economy Engine.
"""

import unittest
from typing import Dict, Any, List

from simulation.economy.resource_exchange import ResourceExchange
from simulation.economy.market_engine import LocalMarket, BASE_PRICES
from simulation.economy.trade_engine import TradeEngine, TradeAgreement, EconomicBloc
from simulation.economy.banking_system import EmpireBank
from simulation.economy.inflation_engine import InflationEngine


class TestPhase7Economy(unittest.TestCase):
    """Verifies production-consumption math, price adjustments, arbitrage trade flow, and inflation stability."""

    def test_colony_resource_extraction(self) -> None:
        """Verify raw extraction rates scale with planet type coefficients and colony types."""
        # 1. Mining colony on a Lava World should produce high amounts of Iron
        inventories = {c: 100.0 for c in ["Iron", "Titanium", "Rare Minerals", "Energy"]}
        prod = ResourceExchange.calculate_colony_production(
            planet_type="Lava World",
            resource_score=80.0,
            development_level=50.0,
            tech_level=5.0,
            colony_type="Mining Colony",
            population=5e7,
            inventories=inventories
        )

        # Lava world Iron coeff is 2.5. Mining colony modifier is 1.8.
        # Base extraction = (80 / 100) * 0.5 * 1.5 * 1.0 * 100.0 = 60.0
        # Iron output = 60.0 * 2.5 * 1.8 = 270.0
        self.assertAlmostEqual(prod["Iron"], 270.0, places=1)
        self.assertEqual(prod["Food"], 0.0)  # Lava world has no food multiplier

    def test_high_tech_manufacturing_and_consumption(self) -> None:
        """Verify manufacturing processes consume inputs and produce advanced outputs."""
        inventories = {
            "Iron": 200.0,
            "Titanium": 100.0,
            "Rare Minerals": 50.0,
            "Helium-3": 50.0,
            "Energy": 100.0
        }

        # Verify advanced component manufacturing consumes Iron & Titanium
        prod = ResourceExchange.calculate_colony_production(
            planet_type="Rocky",
            resource_score=60.0,
            development_level=100.0,
            tech_level=6.0,
            colony_type="Capital Colony",
            population=2e7,
            inventories=inventories
        )

        self.assertTrue(prod["Advanced Components"] > 0.0)
        self.assertEqual(prod["_consume_Iron"], prod["Advanced Components"])
        self.assertEqual(prod["_consume_Titanium"], prod["Advanced Components"] * 0.5)

    def test_dynamic_pricing_demand_shocks(self) -> None:
        """Verify market price discovery increases price when demand is high and decreases when stockpiles are full."""
        market = LocalMarket(colony_id="test_colony")
        
        # 1. Excess demand price hike
        # Set stockpile to 0 to maximize scarcity pressure
        market.inventory["Iron"] = 0.0
        prod = {"Iron": 1.0}
        cons = {"Iron": 50.0}
        
        old_price = market.prices["Iron"]
        market.update_prices(production_rates=prod, consumption_rates=cons, is_war=False, tech_level=1.0)
        new_price = market.prices["Iron"]
        
        self.assertTrue(new_price > old_price)

        # 2. Excess stockpile price drop
        # Set a massive stockpile (1000 units)
        market.inventory["Iron"] = 1000.0
        prod = {"Iron": 50.0}
        cons = {"Iron": 5.0}
        
        old_price2 = market.prices["Iron"]
        market.update_prices(production_rates=prod, consumption_rates=cons, is_war=False, tech_level=1.0)
        new_price2 = market.prices["Iron"]
        
        self.assertTrue(new_price2 < old_price2)

    def test_trade_arbitrage_and_embargoes(self) -> None:
        """Verify arbitrage flows are calculated correctly and blocked by embargoes."""
        trade_engine = TradeEngine()
        
        # Prices in two markets:
        # A: cheap Iron (10.0 credits)
        # B: expensive Iron (30.0 credits)
        prices_a = {"Iron": 10.0}
        prices_b = {"Iron": 30.0}
        inventory_a = 100.0

        # Case 1: normal trade route (20 LY) with 10% tariff
        vol, profit = trade_engine.resolve_arbitrage(
            route_length=20.0,
            seller_prices=prices_a,
            buyer_prices=prices_b,
            commodity="Iron",
            seller_inventory=inventory_a,
            tariff_rate=0.10
        )
        self.assertTrue(vol > 0.0)
        self.assertTrue(profit > 0.0)

        # Case 2: trade blocked by active embargo
        trade_engine.toggle_embargo("civ_a", "civ_b", True)
        tariff_with_embargo = trade_engine.calculate_tariffs("civ_a", "civ_b")
        self.assertEqual(tariff_with_embargo, 1.0)  # Prohibitive tariff

    def test_banking_taxes_and_investments(self) -> None:
        """Verify taxation, investment distribution, and reserve rules operate correctly."""
        bank = EmpireBank(empire_id="civ_a", initial_treasury=500.0, initial_reserves=250.0, tax_rate=0.20)
        bank.gdp = 10000.0  # GDP set

        # 1. Tax collections
        taxes = bank.collect_taxes()
        self.assertEqual(taxes, 2000.0)
        self.assertEqual(bank.treasury, 2500.0)

        # 2. Investment allocations based on personality
        disbursed = bank.distribute_investments("Scientific")
        # Reserve buffer is 20% of GDP = 2000.0.
        # Available credits to spend = 2500.0 - 2000.0 = 500.0.
        # Scientific spends 60% of available on research = 300.0.
        self.assertEqual(disbursed["research"], 300.0)
        self.assertEqual(disbursed["military"], 100.0)
        self.assertEqual(disbursed["infrastructure"], 100.0)
        # Remaining treasury = 2000.0 (the reserve buffer)
        self.assertAlmostEqual(bank.treasury, 2000.0, places=1)

    def test_monetary_inflation_dynamics(self) -> None:
        """Verify inflation rate calculations behave predictably."""
        inf_engine = InflationEngine(empire_id="civ_a")
        
        # High money supply growth and flat GDP growth should drive inflation up
        inf = inf_engine.calculate_inflation(
            gdp=1000.0,
            prev_gdp=1000.0,
            trade_volume=500.0,
            deficits={"Food": 0.0, "Water": 0.0, "Energy": 0.0},
            consumptions={"Food": 100.0, "Water": 150.0, "Energy": 200.0}
        )
        # Expansion of money supply creates inflation
        self.assertTrue(inf > 0.0)


if __name__ == "__main__":
    unittest.main()
