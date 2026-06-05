"""
economy_engine.py — Core orchestrator for the Galactic Economy Engine (Phase 7).
"""

import os
import math
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Tuple

from simulation.economy.resource_exchange import ResourceExchange, COMMODITIES
from simulation.economy.market_engine import LocalMarket, BASE_PRICES
from simulation.economy.trade_engine import TradeEngine, TradeAgreement, EconomicBloc
from simulation.economy.banking_system import EmpireBank
from simulation.economy.inflation_engine import InflationEngine


class EconomyEngine:
    """Orchestrates the macro- and micro-economic simulation of 482 Galactic Empires."""

    def __init__(self, seed: int = 42) -> None:
        self.seed = seed
        self.random = np.random.RandomState(seed)
        
        # Engines
        self.trade_engine = TradeEngine()

        # Registries
        self.empires: List[Dict[str, Any]] = []
        self.planets_dict: Dict[str, Dict[str, Any]] = {}
        self.stars_dict: Dict[str, Dict[str, Any]] = {}
        self.routes: List[Dict[str, Any]] = []
        self.colonies: List[Dict[str, Any]] = []

        # Local economy models (keys: world/planet_id or empire_id)
        self.markets: Dict[str, LocalMarket] = {}  # planet_id -> LocalMarket
        self.banks: Dict[str, EmpireBank] = {}  # empire_id -> EmpireBank
        self.inflation_engines: Dict[str, InflationEngine] = {}  # empire_id -> InflationEngine

        # History log tables
        self.economy_history: List[Dict[str, Any]] = []
        self.market_history: List[Dict[str, Any]] = []
        self.trade_agreements_history: List[Dict[str, Any]] = []
        self.economic_events: List[Dict[str, Any]] = []
        self.blocs_history: List[Dict[str, Any]] = []
        
        # Helper mappings
        self.star_to_owner: Dict[str, str] = {}  # star_id -> empire_id
        self.civ_personalities: Dict[str, str] = {}  # civ_id -> personality
        self.civ_techs: Dict[str, float] = {}  # civ_id -> tech_level
        self.civ_governments: Dict[str, str] = {}  # civ_id -> government
        self.civ_wars: Dict[str, List[str]] = {}  # civ_id -> list of enemy civ_ids

    def load_datasets(self, datasets_dir: str = "datasets") -> None:
        """Load star systems, planets, colonies, empires, and routes from Phase 6.

        Parameters
        ----------
        datasets_dir : str
        """
        # 1. Load stars
        stars_df = pd.read_csv(os.path.join(datasets_dir, "stars.csv"))
        self.stars_dict = stars_df.set_index("id").to_dict(orient="index")

        # 2. Load planets
        planets_df = pd.read_csv(os.path.join(datasets_dir, "planets.csv"))
        self.planets_dict = planets_df.set_index("planet_id").to_dict(orient="index")

        # 3. Load colonies
        col_csv = os.path.join(datasets_dir, "colonies.csv")
        if os.path.exists(col_csv):
            self.colonies = pd.read_csv(col_csv).to_dict(orient="records")
        else:
            self.colonies = []

        # 4. Load empires
        emp_csv = os.path.join(datasets_dir, "empires.csv")
        if os.path.exists(emp_csv):
            self.empires = pd.read_csv(emp_csv).to_dict(orient="records")
        else:
            raise FileNotFoundError(f"Required Phase 6 dataset '{emp_csv}' not found.")

        # 5. Load routes
        rte_csv = os.path.join(datasets_dir, "interstellar_routes.csv")
        if os.path.exists(rte_csv):
            self.routes = pd.read_csv(rte_csv).to_dict(orient="records")
        else:
            self.routes = []

        # 6. Load civilizations evolution (to extract base stats like personalities & home planet coords)
        civ_evo_df = pd.read_csv(os.path.join(datasets_dir, "civilization_evolution.csv"))
        
        # Cache traits for quick lookup
        self.civ_personalities.clear()
        self.civ_techs.clear()
        self.civ_governments.clear()
        self.civ_wars.clear()

        # Parse AI decisions to reconstruct wars list
        dec_csv = os.path.join(datasets_dir, "ai_decisions.csv")
        if os.path.exists(dec_csv):
            dec_df = pd.read_csv(dec_csv)
            for _, row in dec_df.iterrows():
                cid = str(row["civilization_id"])
                decision = str(row.get("decision", ""))
                res_text = str(row.get("result", ""))
                if cid not in self.civ_wars:
                    self.civ_wars[cid] = []
                
                # Check if at war
                if decision == "ATTACK" and "War declared on" in res_text:
                    for other_row in civ_evo_df.itertuples():
                        if other_row.name in res_text and other_row.civilization_id != cid:
                            if other_row.civilization_id not in self.civ_wars[cid]:
                                self.civ_wars[cid].append(other_row.civilization_id)
                            break

        for _, row in civ_evo_df.iterrows():
            cid = str(row["civilization_id"])
            self.civ_techs[cid] = float(row["tech_level"])
            self.civ_governments[cid] = str(row["government_type"])
            
            # Map personality
            traits = {
                "Militaristic": float(row.get("aggression", 50.0)),
                "Diplomatic": float(row.get("cooperation", 50.0)),
                "Scientific": float(row.get("intelligence", 50.0)),
                "Isolationist": 100.0 - float(row.get("cooperation", 50.0)),
                "Expansionist": (float(row.get("adaptability", 50.0)) + float(row.get("aggression", 50.0))) / 2.0,
                "Explorer": (float(row.get("intelligence", 50.0)) + float(row.get("adaptability", 50.0))) / 2.0,
                "Industrialist": (100.0 - float(row.get("adaptability", 50.0)) + float(row.get("intelligence", 50.0))) / 2.0,
            }
            self.civ_personalities[cid] = max(traits, key=traits.get)

        # 7. Map star ownership from homeworld capitals and colonies
        self.star_to_owner.clear()
        
        # Map homeworlds first
        for _, row in civ_evo_df.iterrows():
            cid = str(row["civilization_id"])
            pid = str(row["planet_id"])
            p_info = self.planets_dict.get(pid)
            if p_info:
                star_id = str(p_info["star_id"])
                self.star_to_owner[star_id] = cid
                
        # Map colonies next (overwrites if overlapping, but colonies are distinct)
        for col in self.colonies:
            cid = str(col["parent_civilization_id"])
            star_id = str(col["home_star_id"])
            self.star_to_owner[star_id] = cid

    def initialize_economic_states(self) -> None:
        """Initialize banking, markets, and inflation engines for all empires."""
        self.markets.clear()
        self.banks.clear()
        self.inflation_engines.clear()

        # Step 1: Initialize local markets for homeworlds and colonies
        # Load home planets from civ_evolution
        civ_evo = pd.read_csv(os.path.join("datasets", "civilization_evolution.csv"))
        
        for _, row in civ_evo.iterrows():
            cid = str(row["civilization_id"])
            home_pid = str(row["planet_id"])
            pop = float(row["population"])
            tech = float(row["tech_level"])

            # Homeworld market
            self.markets[home_pid] = LocalMarket(colony_id=home_pid)
            
            # Bootstrap starting stockpile for homeworld (1000 units of raw essentials)
            for raw_goods in ["Food", "Water", "Energy", "Iron", "Titanium", "Rare Minerals"]:
                self.markets[home_pid].inventory[raw_goods] = 200.0

            # Step 2: Initialize banking & treasury
            # Treasury proportional to population size and tech level
            init_treasury = (pop * 1e-9) * 1000.0 + tech * 2000.0
            init_treasury = max(1000.0, round(init_treasury, 2))
            init_reserves = round(init_treasury * 0.5, 2)
            
            self.banks[cid] = EmpireBank(
                empire_id=cid,
                initial_treasury=init_treasury,
                initial_reserves=init_reserves,
            )

            # Step 3: Initialize inflation engines
            self.inflation_engines[cid] = InflationEngine(empire_id=cid)

        # Step 4: Initialize external colony markets
        for col in self.colonies:
            col_pid = str(col["target_planet_id"])
            self.markets[col_pid] = LocalMarket(colony_id=col_pid)
            
            # Bootstrap starting stockpile for colonies (50 units of raw essentials)
            for raw_goods in ["Food", "Water", "Energy", "Iron", "Titanium", "Rare Minerals"]:
                self.markets[col_pid].inventory[raw_goods] = 50.0

        # Step 5: Procedurally formulate trade agreements and economic blocs
        self.trade_engine.formulate_agreements(self.empires, self.random)
        self.trade_engine.establish_economic_blocs(self.empires, self.random)

    def run_ticks(self, num_ticks: int = 10, output_dir: str = "datasets") -> None:
        """Run the temporal galactic economic simulation loop.

        Parameters
        ----------
        num_ticks : int
            Number of ticks to simulate.
        output_dir : str
        """
        os.makedirs(output_dir, exist_ok=True)
        event_counter = 1

        print(f"Starting Phase 7 Galactic Economy simulation over {num_ticks} ticks...")

        # Initialize tracking histories
        self.economy_history.clear()
        self.market_history.clear()
        self.trade_agreements_history.clear()
        self.economic_events.clear()
        self.blocs_history.clear()

        # Re-bootstrap baseline states
        self.initialize_economic_states()

        for tick in range(1, num_ticks + 1):
            year_timestamp = tick * 100  # 1 tick = 100 years
            
            # Store prev GDPs for growth calculations
            prev_gdps = {cid: bank.gdp for cid, bank in self.banks.items()}

            # -------------------------------------------------------------
            # STEP 1: Calculate local production & consumption on each world
            # -------------------------------------------------------------
            world_productions: Dict[str, Dict[str, float]] = {}
            world_consumptions: Dict[str, Dict[str, float]] = {}

            # Process Homeworlds
            civ_evo = pd.read_csv(os.path.join("datasets", "civilization_evolution.csv"))
            for _, row in civ_evo.iterrows():
                cid = str(row["civilization_id"])
                home_pid = str(row["planet_id"])
                pop = float(row["population"])
                tech = self.civ_techs[cid]
                gov = self.civ_governments[cid]

                planet_info = self.planets_dict.get(home_pid, {"planet_type": "Rocky", "resource_score": 50.0})
                p_type = str(planet_info["planet_type"])
                p_res = float(planet_info["resource_score"])

                market = self.markets[home_pid]

                # Production
                prod = ResourceExchange.calculate_colony_production(
                    planet_type=p_type,
                    resource_score=p_res,
                    development_level=100.0,
                    tech_level=tech,
                    colony_type="Capital Colony",
                    population=pop,
                    inventories=market.inventory
                )

                # Consumption
                cons = ResourceExchange.calculate_colony_consumption(
                    population=pop,
                    tech_level=tech,
                    colony_type="Capital Colony",
                    government=gov
                )

                world_productions[home_pid] = prod
                world_consumptions[home_pid] = cons

            # Process External Colonies
            for col in self.colonies:
                col_pid = str(col["target_planet_id"])
                cid = str(col["parent_civilization_id"])
                pop = float(col["population"])
                dev = float(col["development_level"])
                col_type = str(col["colony_type"])
                tech = self.civ_techs[cid]
                gov = self.civ_governments[cid]

                planet_info = self.planets_dict.get(col_pid, {"planet_type": "Rocky", "resource_score": 50.0})
                p_type = str(planet_info["planet_type"])
                p_res = float(planet_info["resource_score"])

                market = self.markets[col_pid]

                # Production
                prod = ResourceExchange.calculate_colony_production(
                    planet_type=p_type,
                    resource_score=p_res,
                    development_level=dev,
                    tech_level=tech,
                    colony_type=col_type,
                    population=pop,
                    inventories=market.inventory
                )

                # Consumption
                cons = ResourceExchange.calculate_colony_consumption(
                    population=pop,
                    tech_level=tech,
                    colony_type=col_type,
                    government=gov
                )

                world_productions[col_pid] = prod
                world_consumptions[col_pid] = cons

            # Apply consumption & manufacturing raw deductions to stockpiles
            for pid, market in self.markets.items():
                prod = world_productions.get(pid, {})
                cons = world_consumptions.get(pid, {})

                # Check if manufacturing consumed raw inputs
                for commodity in COMMODITIES:
                    p_rate = prod.get(commodity, 0.0)
                    c_rate = cons.get(commodity, 0.0)
                    
                    # Deduct raw material input consumption rates
                    consume_input_key = f"_consume_{commodity}"
                    input_cons_rate = prod.get(consume_input_key, 0.0)
                    
                    net_rate = p_rate - (c_rate + input_cons_rate)

                    # Update stockpile
                    market.inventory[commodity] = max(0.0, market.inventory[commodity] + net_rate)

            # -------------------------------------------------------------
            # STEP 2: Internal Resource Distribution (Colony pools to Capitals)
            # -------------------------------------------------------------
            # Empires ship colony surpluses back to their capitals to prevent localized starvation
            for col in self.colonies:
                col_pid = str(col["target_planet_id"])
                cid = str(col["parent_civilization_id"])
                
                # Get parent homeworld planet id
                home_row = civ_evo[civ_evo["civilization_id"] == cid]
                if home_row.empty:
                    continue
                home_pid = str(home_row.iloc[0]["planet_id"])

                col_market = self.markets[col_pid]
                home_market = self.markets[home_pid]

                for commodity in COMMODITIES:
                    # If colony has surplus (stockpile > 50) and capital has deficit (< 100)
                    if col_market.inventory[commodity] > 100.0 and home_market.inventory[commodity] < 50.0:
                        transfer_amount = min(50.0, col_market.inventory[commodity] - 100.0)
                        col_market.inventory[commodity] -= transfer_amount
                        home_market.inventory[commodity] += transfer_amount

            # -------------------------------------------------------------
            # STEP 3: Interstellar Trade Arbitrage (Route transactions)
            # -------------------------------------------------------------
            net_trade_income: Dict[str, float] = {e["founding_civilization_id"]: 0.0 for e in self.empires}
            ticks_trade_volume: Dict[str, float] = {e["founding_civilization_id"]: 0.0 for e in self.empires}

            for route in self.routes:
                source_star = str(route["source_star_id"])
                target_star = str(route["target_star_id"])
                
                owner_source = self.star_to_owner.get(source_star)
                owner_target = self.star_to_owner.get(target_star)

                # Route length/friction
                dist = float(route["route_length_ly"])

                # Interstellar commerce occurs if stars are owned by active civilizations
                if owner_source and owner_target and owner_source != owner_target:
                    # Find home markets
                    home_source_row = civ_evo[civ_evo["civilization_id"] == owner_source]
                    home_target_row = civ_evo[civ_evo["civilization_id"] == owner_target]
                    if home_source_row.empty or home_target_row.empty:
                        continue

                    market_source = self.markets[str(home_source_row.iloc[0]["planet_id"])]
                    market_target = self.markets[str(home_target_row.iloc[0]["planet_id"])]

                    # Calculate bilateral tariff rate
                    tariff = self.trade_engine.calculate_tariffs(owner_source, owner_target)

                    for commodity in COMMODITIES:
                        # Arbitrage pathfinding (Source exports to Target)
                        vol_s_to_t, profit_s_to_t = self.trade_engine.resolve_arbitrage(
                            route_length=dist,
                            seller_prices=market_source.prices,
                            buyer_prices=market_target.prices,
                            commodity=commodity,
                            seller_inventory=market_source.inventory[commodity],
                            tariff_rate=tariff
                        )

                        if vol_s_to_t > 0:
                            # Transfer goods
                            market_source.inventory[commodity] -= vol_s_to_t
                            market_target.inventory[commodity] += vol_s_to_t

                            # Credits transfer
                            unit_price = market_source.prices[commodity]
                            cargo_value = vol_s_to_t * unit_price
                            
                            # Bank transaction
                            bank_source = self.banks[owner_source]
                            bank_target = self.banks[owner_target]
                            
                            # Buyer pays seller
                            bank_target.treasury -= cargo_value
                            bank_source.treasury += cargo_value

                            # Tariffs collected by buyer empire
                            tariffs = cargo_value * tariff
                            bank_target.treasury += tariffs

                            # Track trade balances
                            net_trade_income[owner_source] += cargo_value
                            net_trade_income[owner_target] -= (cargo_value - tariffs)

                            ticks_trade_volume[owner_source] += cargo_value
                            ticks_trade_volume[owner_target] += cargo_value

                        # Arbitrage pathfinding (Target exports to Source)
                        vol_t_to_s, profit_t_to_s = self.trade_engine.resolve_arbitrage(
                            route_length=dist,
                            seller_prices=market_target.prices,
                            buyer_prices=market_source.prices,
                            commodity=commodity,
                            seller_inventory=market_target.inventory[commodity],
                            tariff_rate=tariff
                        )

                        if vol_t_to_s > 0:
                            # Transfer goods
                            market_target.inventory[commodity] -= vol_t_to_s
                            market_source.inventory[commodity] += vol_t_to_s

                            # Credits transfer
                            unit_price = market_target.prices[commodity]
                            cargo_value = vol_t_to_s * unit_price
                            
                            bank_source = self.banks[owner_source]
                            bank_target = self.banks[owner_target]
                            
                            bank_source.treasury -= cargo_value
                            bank_target.treasury += cargo_value

                            # Tariffs collected by buyer empire
                            tariffs = cargo_value * tariff
                            bank_source.treasury += tariffs

                            net_trade_income[owner_target] += cargo_value
                            net_trade_income[owner_source] -= (cargo_value - tariffs)

                            ticks_trade_volume[owner_source] += cargo_value
                            ticks_trade_volume[owner_target] += cargo_value

            # -------------------------------------------------------------
            # STEP 4: Taxes, Investments, and Operational Upkeep
            # -------------------------------------------------------------
            # Calculate GDP for each empire as sum of production value plus net trade
            empire_gdp_contributions: Dict[str, List[float]] = {e["founding_civilization_id"]: [] for e in self.empires}
            
            # Map colony planet_ids to parent civ_ids
            col_to_civ = {col["target_planet_id"]: col["parent_civilization_id"] for col in self.colonies}
            
            for pid, market in self.markets.items():
                civ_id = col_to_civ.get(pid)
                if not civ_id:
                    # Find homeworld owner
                    for _, row in civ_evo.iterrows():
                        if str(row["planet_id"]) == pid:
                            civ_id = str(row["civilization_id"])
                            break
                if not civ_id:
                    continue

                prod = world_productions.get(pid, {})
                world_production_value = 0.0
                for commodity in COMMODITIES:
                    p_val = prod.get(commodity, 0.0) * market.prices[commodity]
                    world_production_value += p_val
                
                empire_gdp_contributions[civ_id].append(world_production_value)

            for cid, bank in self.banks.items():
                total_prod_val = sum(empire_gdp_contributions.get(cid, [0.0]))
                net_trade = net_trade_income.get(cid, 0.0)
                
                # GDP formula: production value + net trade balance
                gdp_val = max(100.0, total_prod_val + net_trade)
                
                # Update bank records
                prev_gdp_val = prev_gdps.get(cid, gdp_val)
                bank.gdp_growth = (gdp_val - prev_gdp_val) / (prev_gdp_val + 1.0)
                bank.gdp = round(gdp_val, 2)
                
                # GDP per capita indicator
                bank.wealth_index = round(gdp_val / (civ_evo[civ_evo["civilization_id"] == cid]["population"].iloc[0] * 1e-9 + 0.1), 2)

                # Collect taxes
                bank.collect_taxes()

                # Distribute public spending
                personality = self.civ_personalities.get(cid, "Industrialist")
                bank.distribute_investments(personality)

                # Pay Upkeep costs: military maintenance and colony operating expenses
                upkeep = (bank.investments["military"] * 0.15) + len(civ_evo[civ_evo["civilization_id"] == cid]["planet_id"]) * 50.0
                bank.pay_upkeep(upkeep)

                # Infrastructure boosts private sector growth rate
                bank.update_private_growth()

            # -------------------------------------------------------------
            # STEP 5: Macroeconomic Inflation & Currency strength
            # -------------------------------------------------------------
            all_inflations = []
            for cid, inf_engine in self.inflation_engines.items():
                bank = self.banks[cid]
                trade_vol = ticks_trade_volume.get(cid, 0.0)
                
                # Check deficits on worlds owned by this empire
                deficits = {c: 0.0 for c in COMMODITIES}
                consumptions = {c: 0.0 for c in COMMODITIES}

                owned_worlds = [pid for pid, col_id in col_to_civ.items() if col_id == cid]
                # Add homeworld
                home_pid = civ_evo[civ_evo["civilization_id"] == cid]["planet_id"].iloc[0]
                owned_worlds.append(home_pid)

                for pid in owned_worlds:
                    cons_rates = world_consumptions.get(pid, {})
                    market = self.markets.get(pid)
                    if not market:
                        continue
                    for commodity in COMMODITIES:
                        consumptions[commodity] += cons_rates.get(commodity, 0.0)
                        if market.inventory[commodity] <= 0:
                            deficits[commodity] += cons_rates.get(commodity, 0.0)

                inf_rate = inf_engine.calculate_inflation(
                    gdp=bank.gdp,
                    prev_gdp=prev_gdps.get(cid, bank.gdp),
                    trade_volume=trade_vol,
                    deficits=deficits,
                    consumptions=consumptions
                )
                all_inflations.append(inf_rate)

            # Global average inflation
            global_inflation_avg = float(np.mean(all_inflations)) if all_inflations else 0.02

            # Update exchange rates
            for cid, inf_engine in self.inflation_engines.items():
                bank = self.banks[cid]
                inf_engine.update_exchange_rate(global_inflation_avg, bank.gdp_growth)

            # -------------------------------------------------------------
            # STEP 6: Update Market Prices per world
            # -------------------------------------------------------------
            for pid, market in self.markets.items():
                # Find parent tech level and war status
                civ_id = col_to_civ.get(pid)
                if not civ_id:
                    for _, row in civ_evo.iterrows():
                        if str(row["planet_id"]) == pid:
                            civ_id = str(row["civilization_id"])
                            break
                
                tech = self.civ_techs.get(civ_id, 1.0)
                is_war = len(self.civ_wars.get(civ_id, [])) > 0

                prod_rates = world_productions.get(pid, {})
                cons_rates = world_consumptions.get(pid, {})

                market.update_prices(
                    production_rates=prod_rates,
                    consumption_rates=cons_rates,
                    is_war=is_war,
                    tech_level=tech
                )

            # -------------------------------------------------------------
            # STEP 7: Macroeconomic Events triggers
            # -------------------------------------------------------------
            for cid, bank in self.banks.items():
                inf_engine = self.inflation_engines[cid]
                gdp_growth = bank.gdp_growth
                inflation = inf_engine.inflation_rate
                
                # Check for major events
                e_type = ""
                e_desc = ""
                
                if gdp_growth >= 0.15 and inflation <= 0.04:
                    e_type = "Golden Age"
                    e_desc = f"{self.banks[cid].empire_id} entered a Golden Age, fueled by high GDP growth ({gdp_growth*100:.1f}%) and low inflation."
                elif inflation >= 0.50:
                    e_type = "Hyperinflation"
                    e_desc = f"Hyperinflation crisis declared in {self.banks[cid].empire_id} as local currency values plummeted by {inflation*100:.1f}%."
                elif gdp_growth <= -0.10 and bank.treasury < 200.0:
                    e_type = "Economic Collapse"
                    e_desc = f"An Economic Collapse occurred in {self.banks[cid].empire_id} due to negative GDP growth and treasury depletion."
                elif self.random.random() < 0.02:
                    # Random resource boom
                    e_type = "Resource Discovery"
                    e_desc = f"Explorers discovered massive quantum mineral veins in the frontier colonies of {self.banks[cid].empire_id}."
                elif self.random.random() < 0.01:
                    e_type = "Industrial Revolution"
                    e_desc = f"New automation paradigms sparked an Industrial Revolution in the manufacturing sectors of {self.banks[cid].empire_id}."

                if e_type:
                    self.economic_events.append({
                        "event_id": f"ECN-EVT-{event_counter:05d}",
                        "tick": tick,
                        "year": year_timestamp,
                        "civilization_id": cid,
                        "event_type": e_type,
                        "description": e_desc,
                    })
                    event_counter += 1

            # -------------------------------------------------------------
            # STEP 8: Update Economic Blocs market share
            # -------------------------------------------------------------
            global_total_gdp = sum(bank.gdp for bank in self.banks.values())
            for bloc_id, bloc in self.trade_engine.blocs.items():
                bloc_gdp = 0.0
                for cid in bloc.member_empires:
                    if cid in self.banks:
                        bloc_gdp += self.banks[cid].gdp
                
                bloc.combined_gdp = bloc_gdp
                bloc.market_share = bloc_gdp / (global_total_gdp + 1.0)
                
                self.blocs_history.append({
                    "tick": tick,
                    "year": year_timestamp,
                    "bloc_id": bloc.bloc_id,
                    "bloc_name": bloc.bloc_name,
                    "bloc_type": bloc.bloc_type,
                    "member_count": len(bloc.member_empires),
                    "combined_gdp": round(bloc_gdp, 2),
                    "market_share": round(bloc.market_share, 4),
                })

            # -------------------------------------------------------------
            # STEP 9: Append histories for logging
            # -------------------------------------------------------------
            for cid, bank in self.banks.items():
                inf = self.inflation_engines[cid]
                trade_vol = ticks_trade_volume.get(cid, 0.0)
                net_trade = net_trade_income.get(cid, 0.0)
                
                self.economy_history.append({
                    "tick": tick,
                    "year": year_timestamp,
                    "civilization_id": cid,
                    "gdp": bank.gdp,
                    "gdp_growth": round(bank.gdp_growth, 4),
                    "treasury": bank.treasury,
                    "capital_reserves": bank.capital_reserves,
                    "money_supply": inf.money_supply,
                    "inflation_rate": inf.inflation_rate,
                    "exchange_rate": inf.exchange_rate,
                    "purchasing_power_index": inf.purchasing_power_index,
                    "trade_volume": round(trade_vol, 2),
                    "trade_balance": round(net_trade, 2),
                })

            for pid, market in self.markets.items():
                for commodity in COMMODITIES:
                    self.market_history.append({
                        "tick": tick,
                        "year": year_timestamp,
                        "planet_id": pid,
                        "commodity": commodity,
                        "price": market.prices[commodity],
                        "volatility": market.volatility[commodity],
                        "inventory": round(market.inventory[commodity], 1),
                        "value_index": market.resource_value_index[commodity]
                    })

        # Save registers to disk
        self._save_output_catalogs(output_dir)

    def _save_output_catalogs(self, output_dir: str) -> None:
        """Export Phase 7 simulation catalogs to CSV.

        Parameters
        ----------
        output_dir : str
        """
        # 1. datasets/economy.csv
        econ_df = pd.DataFrame(self.economy_history)
        econ_csv = os.path.join(output_dir, "economy.csv")
        econ_df.to_csv(econ_csv, index=False)
        print(f"  - Saved economy database: {econ_csv} ({len(econ_df)} records)")

        # 2. datasets/market_prices.csv
        mkt_df = pd.DataFrame(self.market_history)
        mkt_csv = os.path.join(output_dir, "market_prices.csv")
        mkt_df.to_csv(mkt_csv, index=False)
        print(f"  - Saved market prices: {mkt_csv} ({len(mkt_df)} records)")

        # 3. datasets/trade_agreements.csv
        agr_records = [a.to_dict() for a in self.trade_engine.agreements.values()]
        agr_df = pd.DataFrame(agr_records)
        if agr_df.empty:
            agr_df = pd.DataFrame(columns=["agreement_id", "party_a_id", "party_b_id", "agreement_type", "tariff_rate", "volume_limit", "active_ticks", "trade_volume", "trade_profit"])
        agr_csv = os.path.join(output_dir, "trade_agreements.csv")
        agr_df.to_csv(agr_csv, index=False)
        print(f"  - Saved trade agreements: {agr_csv} ({len(agr_df)} records)")

        # 4. datasets/economic_events.csv
        evt_df = pd.DataFrame(self.economic_events)
        if evt_df.empty:
            evt_df = pd.DataFrame(columns=["event_id", "tick", "year", "civilization_id", "event_type", "description"])
        evt_csv = os.path.join(output_dir, "economic_events.csv")
        evt_df.to_csv(evt_csv, index=False)
        print(f"  - Saved economic events: {evt_csv} ({len(evt_df)} records)")

        # 5. datasets/economic_blocs.csv
        blocs_df = pd.DataFrame(self.blocs_history)
        if blocs_df.empty:
            blocs_df = pd.DataFrame(columns=["tick", "year", "bloc_id", "bloc_name", "bloc_type", "member_count", "combined_gdp", "market_share"])
        blocs_csv = os.path.join(output_dir, "economic_blocs.csv")
        blocs_df.to_csv(blocs_csv, index=False)
        print(f"  - Saved economic blocs: {blocs_csv} ({len(blocs_df)} records)")

        # 6. datasets/gdp_rankings.csv
        # Take the final tick economy data to generate the rankings
        final_tick = econ_df["tick"].max() if not econ_df.empty else 1
        final_econ = econ_df[econ_df["tick"] == final_tick]
        
        # Merge names
        civ_names = pd.read_csv(os.path.join(output_dir, "civilization_evolution.csv"))[["civilization_id", "name"]]
        rankings = final_econ.merge(civ_names, on="civilization_id")
        rankings = rankings[["civilization_id", "name", "gdp", "gdp_growth", "treasury", "inflation_rate", "exchange_rate"]]
        rankings = rankings.sort_values(by="gdp", ascending=False).reset_index(drop=True)
        rankings.index += 1  # 1-indexed ranks
        rankings.index.name = "gdp_rank"
        
        rankings_csv = os.path.join(output_dir, "gdp_rankings.csv")
        rankings.to_csv(rankings_csv)
        print(f"  - Saved GDP rankings: {rankings_csv} ({len(rankings)} empires ranked)")
