#!/usr/bin/env python
"""
Main pipeline runner for Phase 9: Political and Military Layer of The Galactic Dream Engine.
"""

import os
import sys
import argparse
import io
import pandas as pd
import numpy as np

# Set console encoding to UTF-8 to handle special symbols safely on Windows
try:
    sys.stdout.reconfigure(encoding='utf-8')
except (AttributeError, io.UnsupportedOperation):
    pass

from simulation.diplomacy.diplomacy_engine import DiplomacyEngine
from simulation.diplomacy.alliance_manager import AllianceManager
from simulation.diplomacy.treaty_engine import TreatyEngine
from simulation.diplomacy.espionage_engine import EspionageEngine
from simulation.warfare.fleet_generator import FleetGenerator
from simulation.warfare.battle_engine import BattleEngine
from simulation.warfare.invasion_engine import InvasionEngine
from simulation.warfare.war_simulator import WarSimulator
from simulation.analytics.warfare_analytics import WarfareAnalytics
from simulation.visualization.galactic_conflict_visualizer import GalacticConflictVisualizer
from simulation.colonization.colony_generator import Colony


def main():
    parser = argparse.ArgumentParser(description="Run Phase 9: Political and Military Simulation")
    parser.add_argument(
        "--ticks",
        type=int,
        default=10,
        help="Number of simulation ticks to run (1 tick = 100 years). Default is 10."
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for deterministic political/military simulation operations."
    )
    args = parser.parse_args()

    print("=" * 80)
    print("        THE GALACTIC DREAM ENGINE - PHASE 9 PIPELINE")
    print("                 Political & Military Layer")
    print("=" * 80)

    output_dir = "datasets"
    os.makedirs(output_dir, exist_ok=True)

    # Validate required Phase 8 inputs
    required_inputs = [
        "stars.csv",
        "planets.csv",
        "colonies.csv",
        "empires.csv",
        "civilization_evolution.csv",
        "economy.csv",
        "gdp_rankings.csv",
        "hyperlane_network.csv",
        "wormholes.csv",
        "jump_gates.csv"
    ]
    for filename in required_inputs:
        path = os.path.join(output_dir, filename)
        if not os.path.exists(path):
            print(f"Error: Required Phase 8 input dataset '{path}' not found.", file=sys.stderr)
            print("Please execute the earlier simulation phases first.", file=sys.stderr)
            sys.exit(1)

    random_state = np.random.RandomState(args.seed)

    # 1. Load datasets
    print(f"\n[Step 1/4] Loading Phase 8 Geopolitical Catalogs (Seed: {args.seed})...")
    stars_df = pd.read_csv(os.path.join(output_dir, "stars.csv"))
    planets_df = pd.read_csv(os.path.join(output_dir, "planets.csv"))
    colonies_df = pd.read_csv(os.path.join(output_dir, "colonies.csv"))
    empires_df = pd.read_csv(os.path.join(output_dir, "empires.csv"))
    civ_df = pd.read_csv(os.path.join(output_dir, "civilization_evolution.csv"))
    econ_df = pd.read_csv(os.path.join(output_dir, "economy.csv"))
    trade_df = pd.read_csv(os.path.join(output_dir, "trade_agreements.csv"))
    species_df = pd.read_csv(os.path.join(output_dir, "species_catalog.csv"))

    stars = stars_df.set_index("id").to_dict(orient="index")
    planets_dict = planets_df.set_index("planet_id").to_dict(orient="index")
    species_lookup = species_df.set_index("species_id").to_dict(orient="index")
    civ_species = civ_df.set_index("civilization_id")["species_id"].to_dict()

    # Load Colonies and reconstruct dataclasses
    colonies: List[Colony] = []
    for _, row in colonies_df.iterrows():
        colonies.append(Colony.from_dict(row.to_dict()))

    # Map capital systems
    capital_stars = {}
    for _, e in empires_df.iterrows():
        cid = str(e["founding_civilization_id"])
        cap_world = str(e["capital_world"])
        
        # Resolve star id for capital
        star_id = None
        for col in colonies:
            if str(col.colony_name) == cap_world:
                star_id = str(col.home_star_id)
                break
        if not star_id:
            for sid, star in stars.items():
                if str(star["name"]) in cap_world:
                    star_id = sid
                    break
        if not star_id:
            star_id = list(stars.keys())[0]
            
        capital_stars[cid] = star_id

    # Cache tech levels, treasuries, and stability
    civ_techs = civ_df.set_index("civilization_id")["tech_level"].to_dict()
    
    final_tick_econ = econ_df[econ_df["tick"] == econ_df["tick"].max()].set_index("civilization_id")
    treasury_registry = final_tick_econ["treasury"].to_dict()
    stability_registry = civ_df.set_index("civilization_id")["stability_score"].to_dict()

    # Map of civilization details for easy lookup
    empire_stats = {}
    for _, row in empires_df.iterrows():
        cid = str(row["founding_civilization_id"])
        # Map personality from species traits
        sp_id = civ_species.get(cid)
        sp_traits = species_lookup.get(sp_id, {}) if sp_id else {}
        
        traits = {
            "Militaristic": float(sp_traits.get("aggression", 50.0)),
            "Diplomatic": float(sp_traits.get("cooperation", 50.0)),
            "Scientific": float(sp_traits.get("intelligence", 50.0)),
            "Isolationist": 100.0 - float(sp_traits.get("cooperation", 50.0)),
            "Expansionist": (float(sp_traits.get("adaptability", 50.0)) + float(sp_traits.get("aggression", 50.0))) / 2.0,
        }
        personality = max(traits, key=traits.get)

        empire_stats[cid] = {
            "founding_civilization_id": cid,
            "empire_name": str(row["empire_name"]),
            "capital_world": str(row["capital_world"]),
            "gdp": float(row.get("gdp", 5000.0)),
            "population": float(row.get("population", 1e9)),
            "personality": personality,
        }

    # Initialize Political/Military Engines
    diplomacy_eng = DiplomacyEngine(seed=args.seed)
    alliance_mgr = AllianceManager(seed=args.seed)
    treaty_eng = TreatyEngine(seed=args.seed)
    espionage_eng = EspionageEngine(seed=args.seed)
    fleet_gen = FleetGenerator(seed=args.seed)
    battle_eng = BattleEngine(seed=args.seed)
    invasion_eng = InvasionEngine(seed=args.seed)
    war_sim = WarSimulator(seed=args.seed)

    # 2. Setup Starting Fleets and Diplomatic Relations
    print("\n[Step 2/4] Generating initial space fleets and establishing NAPs/Relations...")
    fleet_gen.generate_initial_fleets(empires_df.to_dict(orient="records"), capital_stars, civ_techs)
    
    trade_agreements = trade_df.to_dict(orient="records") if not trade_df.empty else []
    diplomacy_eng.initialize_relations(empires_df.to_dict(orient="records"), stars, trade_agreements, capital_stars)

    # Cache initial fleet power maps
    fleet_power_map = {cid: fleet_gen.get_empire_fleet_power(cid) for cid in empire_stats}

    # 3. Run simulation ticks
    timescale_years = args.ticks * 100
    print(f"\n[Step 3/4] Simulating {args.ticks} Ticks of Geopolitical Evolution ({timescale_years} Years)...")
    
    all_logs = []

    for tick in range(1, args.ticks + 1):
        year_timestamp = tick * 100

        # A. Upkeep deductions & economic rebuilds
        fleet_gen.deduct_upkeep(treasury_registry)

        # B. Spy operations
        esp_logs = espionage_eng.run_tick_operations(
            tick,
            empires_df.to_dict(orient="records"),
            diplomacy_eng.relations,
            empire_stats,
            treasury_registry,
            stability_registry,
            civ_techs
        )
        all_logs.extend(esp_logs)

        # C. Relations decay & Alliance updates
        diplomacy_eng.update_relations(list(empire_stats.keys()))
        fleet_power_map = {cid: fleet_gen.get_empire_fleet_power(cid) for cid in empire_stats}
        
        alliance_mgr.update_alliances(diplomacy_eng.relations, empire_stats, fleet_power_map)

        # D. War declarations evaluation
        war_logs = war_sim.trigger_new_wars(
            year_timestamp,
            empires_df.to_dict(orient="records"),
            diplomacy_eng.relations,
            alliance_mgr,
            treaty_eng,
            capital_stars,
            stars
        )
        all_logs.extend(war_logs)

        # E. War campaigns and movements
        camp_logs = war_sim.run_campaign_movements(
            year_timestamp,
            fleet_gen.fleets,
            colonies,
            planets_dict,
            stars,
            capital_stars,
            battle_eng,
            invasion_eng,
            empire_stats,
            treaty_eng,
            treasury_registry
        )
        all_logs.extend(camp_logs)

        # F. Rebuilding destroyed fleets
        for cid in list(empire_stats.keys()):
            # militaristic or active-war empires rebuild faster
            in_war = any(w.status == "Active" and cid in [w.attacker, w.defender] for w in war_sim.wars)
            personality = empire_stats[cid]["personality"]
            rebuild_chance = 0.05
            if in_war:
                rebuild_chance = 0.25
            elif personality == "Militaristic":
                rebuild_chance = 0.15

            if random_state.random() < rebuild_chance:
                treasury = treasury_registry.get(cid, 0.0)
                cap_star = capital_stars.get(cid)
                if cap_star:
                    res = fleet_gen.build_new_fleet(
                        cid,
                        empire_stats[cid]["empire_name"],
                        cap_star,
                        civ_techs.get(cid, 5.0),
                        treasury
                    )
                    if res:
                        new_f, cost = res
                        treasury_registry[cid] -= cost

    print("\nWriting out Phase 9 political and military databases...")
    
    # 4. Save outputs
    # A. Diplomatic Relations
    diplomacy_eng.export_relations(os.path.join(output_dir, "diplomatic_relations.csv"))

    # B. Alliances
    alliance_mgr.export_alliances(os.path.join(output_dir, "alliances.csv"))

    # C. Espionage Operations
    espionage_eng.export_operations(os.path.join(output_dir, "espionage_operations.csv"))

    # D. Fleets
    fleet_gen.export_fleets(os.path.join(output_dir, "fleets.csv"))

    # E. Wars
    war_sim.export_wars(os.path.join(output_dir, "wars.csv"))

    # F. Battles
    battle_eng.export_battles(os.path.join(output_dir, "battles.csv"))

    # G. Conquests
    invasion_eng.export_conquests(os.path.join(output_dir, "conquests.csv"))

    # H. Peace Treaties
    treaty_eng.export_treaties(os.path.join(output_dir, "peace_treaties.csv"))

    # I. Write updated sovereignty to colonies.csv and empires.csv
    updated_col_records = [c.to_dict() for c in colonies]
    pd.DataFrame(updated_col_records).to_csv(os.path.join(output_dir, "colonies.csv"), index=False)
    print(f"  - Saved updated colonies: datasets/colonies.csv")

    # Update empires details
    updated_empires = []
    for _, row in empires_df.iterrows():
        cid = str(row["founding_civilization_id"])
        if cid in empire_stats:
            # Recalculate population from colonies
            pop_sum = sum(float(c.population) for c in colonies if c.parent_civilization_id == cid)
            row["population"] = pop_sum
            
            # Recalculate GDP (boosted/penalized by military upkeeps and war events)
            # GDP is updated partially based on new colony ownership
            row["gdp"] = empire_stats[cid]["gdp"]
            
            updated_empires.append(row)
    
    pd.DataFrame(updated_empires).to_csv(os.path.join(output_dir, "empires.csv"), index=False)
    print(f"  - Saved updated empires: datasets/empires.csv")

    # Update gdp_rankings.csv
    gdp_rankings_df = pd.DataFrame(updated_empires)[["founding_civilization_id", "empire_name", "gdp"]]
    gdp_rankings_df = gdp_rankings_df.rename(columns={"founding_civilization_id": "civilization_id"})
    gdp_rankings_df = gdp_rankings_df.sort_values(by="gdp", ascending=False).reset_index(drop=True)
    gdp_rankings_df.index += 1
    gdp_rankings_df.index.name = "gdp_rank"
    gdp_rankings_df.to_csv(os.path.join(output_dir, "gdp_rankings.csv"))
    print(f"  - Saved updated rankings: datasets/gdp_rankings.csv")

    # 5. Render Visualizations
    print("\n[Step 4/4] Rendering geopolitical network maps & timelines...")
    try:
        viz = GalacticConflictVisualizer(datasets_dir=output_dir)
        viz.plot_alliance_network(output_dir)
        viz.plot_galactic_wars_map(output_dir)
        viz.plot_fleet_power_distribution(output_dir)
        viz.plot_battle_casualties(output_dir)
        viz.plot_territorial_changes(output_dir)
        viz.plot_diplomacy_heatmap(output_dir)
        viz.generate_war_timeline(output_dir)
        print("  - Renders complete: plots saved to datasets/ and HTML timeline generated.")
    except Exception as e:
        print(f"Error during conflict rendering: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

    # 6. Generate Reports & Summary
    try:
        anal = WarfareAnalytics(datasets_dir=output_dir)
        anal.print_summary()
    except Exception as e:
        print(f"Error during analytics reporting: {e}", file=sys.stderr)

    print("=" * 80)
    print("  PHASE 9 EXECUTION COMPLETE: POLITICAL & MILITARY SIMULATION")
    print("=" * 80)


if __name__ == "__main__":
    main()
