#!/usr/bin/env python
"""
Main pipeline runner for Phase 8: Galactic Transportation Layer of The Galactic Dream Engine.
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

from simulation.ftl.wormhole_generator import Wormhole, WormholeGenerator
from simulation.ftl.hyperlane_network import Hyperlane, HyperlaneNetwork
from simulation.ftl.jump_gate_engine import JumpGate, JumpGateEngine
from simulation.ftl.route_calculator import RouteCalculator
from simulation.ftl.transit_optimizer import TransitOptimizer
from simulation.analytics.ftl_analytics import FtlAnalytics
from simulation.visualization.galactic_network_visualizer import GalacticNetworkVisualizer


def main():
    parser = argparse.ArgumentParser(description="Run Phase 8: Galactic Transportation Simulation")
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
        help="Random seed for deterministic FTL operations."
    )
    args = parser.parse_args()

    print("=" * 80)
    print("        THE GALACTIC DREAM ENGINE - PHASE 8 PIPELINE")
    print("               Galactic Transportation Layer")
    print("=" * 80)

    output_dir = "datasets"
    os.makedirs(output_dir, exist_ok=True)

    # Validate required Phase 7 inputs
    required_inputs = [
        "stars.csv",
        "planets.csv",
        "colonies.csv",
        "empires.csv",
        "interstellar_routes.csv",
        "civilization_evolution.csv",
        "economy.csv",
        "trade_agreements.csv"
    ]
    for filename in required_inputs:
        path = os.path.join(output_dir, filename)
        if not os.path.exists(path):
            print(f"Error: Required Phase 7 input dataset '{path}' not found.", file=sys.stderr)
            print("Please execute the earlier simulation phases first.", file=sys.stderr)
            sys.exit(1)

    random_state = np.random.RandomState(args.seed)

    # 1. Load datasets
    print(f"\n[Step 1/4] Loading Phase 7 Space Catalogs (Seed: {args.seed})...")
    stars_df = pd.read_csv(os.path.join(output_dir, "stars.csv"))
    planets_df = pd.read_csv(os.path.join(output_dir, "planets.csv"))
    colonies_df = pd.read_csv(os.path.join(output_dir, "colonies.csv"))
    empires_df = pd.read_csv(os.path.join(output_dir, "empires.csv"))
    civ_df = pd.read_csv(os.path.join(output_dir, "civilization_evolution.csv"))
    econ_df = pd.read_csv(os.path.join(output_dir, "economy.csv"))

    stars = stars_df.set_index("id").to_dict(orient="index")
    planets_dict = planets_df.set_index("planet_id").to_dict(orient="index")
    colonies = colonies_df.to_dict(orient="records")
    empires = empires_df.to_dict(orient="records")

    # Cache traits
    civ_techs = civ_df.set_index("civilization_id")["tech_level"].to_dict()
    civ_personalities = {}
    for _, row in civ_df.iterrows():
        cid = str(row["civilization_id"])
        traits = {
            "Militaristic": float(row.get("aggression", 50.0)),
            "Diplomatic": float(row.get("cooperation", 50.0)),
            "Scientific": float(row.get("intelligence", 50.0)),
            "Isolationist": 100.0 - float(row.get("cooperation", 50.0)),
            "Expansionist": (float(row.get("adaptability", 50.0)) + float(row.get("aggression", 50.0))) / 2.0,
            "Explorer": (float(row.get("intelligence", 50.0)) + float(row.get("adaptability", 50.0))) / 2.0,
            "Industrialist": (100.0 - float(row.get("adaptability", 50.0)) + float(row.get("intelligence", 50.0))) / 2.0,
        }
        civ_personalities[cid] = max(traits, key=traits.get)

    # Initialize FTL Generators
    w_gen = WormholeGenerator(seed=args.seed)
    l_gen = HyperlaneNetwork(seed=args.seed)
    g_eng = JumpGateEngine(seed=args.seed)
    
    # 2. Run simulation ticks
    timescale_years = args.ticks * 100
    print(f"\n[Step 2/4] Simulating {args.ticks} Ticks of FTL Infrastructure Evolution ({timescale_years} Years)...")
    
    # Pre-generate static natural and ancient wormholes
    wormholes = w_gen.generate_natural_wormholes(stars, num_wormholes=180)
    wormholes.extend(w_gen.generate_ancient_wormholes(stars, num_wormholes=60))
    
    # Generate hyperlane network grid
    hyperlanes = l_gen.generate_hyperlanes(stars, empires, colonies, k_neighbors=3, max_distance=2000.0)

    # Map capitals and colony systems
    capital_stars = {}
    colony_stars = {}
    
    for e in empires:
        cid = str(e["founding_civilization_id"])
        cap_world = str(e["capital_world"])
        
        # Resolve star id for capital
        star_id = None
        for col in colonies:
            if str(col["colony_name"]) == cap_world:
                star_id = str(col["home_star_id"])
                break
        if not star_id:
            for sid, star in stars.items():
                if str(star["name"]) in cap_world:
                    star_id = sid
                    break
        if not star_id:
            star_id = list(stars.keys())[0]
            
        capital_stars[cid] = star_id

    for col in colonies:
        colony_stars[str(col["target_planet_id"])] = str(col["home_star_id"])

    # Load latest treasury levels from Phase 7 economy
    final_tick_econ = econ_df[econ_df["tick"] == econ_df["tick"].max()].set_index("civilization_id")
    treasury_registry = final_tick_econ["treasury"].to_dict()
    # Add a flat Galactic Transit Infrastructure subsidy to all empires
    for cid in civ_techs:
        treasury_registry[cid] = treasury_registry.get(cid, 0.0) + 15000.0

    events_db = []
    event_counter = 1
    gate_counter = 1
    art_w_counter = 1

    # Map colony planet_ids to colony types for construction evaluations
    colony_types = {col["target_planet_id"]: col["colony_type"] for col in colonies}

    for tick in range(1, args.ticks + 1):
        year_timestamp = tick * 100

        # A. FTL Tech upgrades based on research investments
        for cid in civ_techs:
            # Tech grows slowly per tick
            civ_techs[cid] = round(civ_techs[cid] + random_state.uniform(0.05, 0.15), 3)

        # B. Attempt Jump Gate Construction (Level 4+ FTL required, cost deducted from treasury)
        for e in empires:
            cid = str(e["founding_civilization_id"])
            tech = civ_techs[cid]
            treasury = treasury_registry.get(cid, 1000.0)

            # Check capital star gateway construction
            cap_star = capital_stars.get(cid)
            if cap_star and cap_star not in g_eng.gates:
                success, cost, gate = g_eng.attempt_construction(
                    gate_counter=gate_counter,
                    star_id=cap_star,
                    tech_level=tech,
                    treasury=treasury,
                    empire_id=cid,
                    colony_type="Capital Colony"
                )
                if success and gate:
                    gate_counter += 1
                    treasury_registry[cid] -= cost
                    e_desc = f"{e['empire_name']} constructed capital Jump Gate '{gate.gate_id}' ({gate.gate_type}) in star system {stars[cap_star]['name']}."
                    events_db.append({
                        "event_id": f"TRN-EVT-{event_counter:05d}",
                        "tick": tick,
                        "year": year_timestamp,
                        "civilization_id": cid,
                        "event_type": "Quantum Network Upgrade" if "Quantum" in gate.gate_type else "Transit Revolution",
                        "description": e_desc,
                    })
                    event_counter += 1

            # Check colony stars gateways construction (random selection)
            for col in colonies:
                if str(col["parent_civilization_id"]) == cid:
                    col_star = str(col["home_star_id"])
                    if col_star not in g_eng.gates and random_state.random() < 0.15:
                        c_type = colony_types.get(col["target_planet_id"], "Mining Colony")
                        success, cost, gate = g_eng.attempt_construction(
                            gate_counter=gate_counter,
                            star_id=col_star,
                            tech_level=tech,
                            treasury=treasury_registry.get(cid, 0.0),
                            empire_id=cid,
                            colony_type=c_type
                        )
                        if success and gate:
                            gate_counter += 1
                            treasury_registry[cid] -= cost
                            e_desc = f"{e['empire_name']} constructed gateway '{gate.gate_id}' ({gate.gate_type}) at colony {col['colony_name']}."
                            events_db.append({
                                "event_id": f"TRN-EVT-{event_counter:05d}",
                                "tick": tick,
                                "year": year_timestamp,
                                "civilization_id": cid,
                                "event_type": "Transit Revolution",
                                "description": e_desc,
                            })
                            event_counter += 1

        # C. Construct Artificial Wormholes (Level 5+ FTL required)
        for e in empires:
            cid = str(e["founding_civilization_id"])
            tech = civ_techs[cid]
            if tech >= 7.5 and random_state.random() < 0.08:
                # Link capital to a random colony or trade partner
                cap_star = capital_stars.get(cid)
                my_colonies = [col for col in colonies if col["parent_civilization_id"] == cid]
                if my_colonies:
                    tgt_star = str(random_state.choice(my_colonies)["home_star_id"])
                    if cap_star and tgt_star and cap_star != tgt_star:
                        # Ensure no duplicate artificial link
                        dup = False
                        for w in wormholes:
                            if w.wormhole_type == "Artificial" and \
                               ((w.entry_system == cap_star and w.exit_system == tgt_star) or \
                                (w.entry_system == tgt_star and w.exit_system == cap_star)):
                                dup = True
                                break
                        if not dup:
                            w = w_gen.build_artificial_wormhole(
                                wormhole_counter=art_w_counter,
                                entry_star_id=cap_star,
                                exit_star_id=tgt_star,
                                stars=stars,
                                owner_empire_id=cid
                            )
                            wormholes.append(w)
                            art_w_counter += 1
                            
                            e_desc = f"{e['empire_name']} constructed FTL Artificial Wormhole portal {w.wormhole_id} linking capital to colony system {stars[tgt_star]['name']}."
                            events_db.append({
                                "event_id": f"TRN-EVT-{event_counter:05d}",
                                "tick": tick,
                                "year": year_timestamp,
                                "civilization_id": cid,
                                "event_type": "Hyperlane Expansion",
                                "description": e_desc,
                            })
                            event_counter += 1

        # D. Update Wormhole stability decay & check for collapses
        for w in list(wormholes):
            if w.stability_type == "Unstable":
                # Decay stability by 5%
                w.stability = max(0.0, w.stability - 0.05)
                
                # Collapse check if stability falls below 10%
                if w.stability < 0.10 and random_state.random() < 0.30:
                    wormholes.remove(w)
                    e_desc = f"Unstable Natural Wormhole shortcut {w.wormhole_id} collapsed and closed permanently."
                    events_db.append({
                        "event_id": f"TRN-EVT-{event_counter:05d}",
                        "tick": tick,
                        "year": year_timestamp,
                        "civilization_id": "None",
                        "event_type": "Wormhole Collapse",
                        "description": e_desc,
                    })
                    event_counter += 1

        # E. Random Gate failures
        if g_eng.gates and random_state.random() < 0.05:
            fail_star = random_state.choice(list(g_eng.gates.keys()))
            gate = g_eng.gates[fail_star]
            
            # Temporary throughput reduction
            gate.throughput *= 0.5
            e_desc = f"Gateway {gate.gate_id} in star system {stars[fail_star]['name']} suffered a containment failure, reducing throughput by 50%."
            events_db.append({
                "event_id": f"TRN-EVT-{event_counter:05d}",
                "tick": tick,
                "year": year_timestamp,
                "civilization_id": gate.owner_empire,
                "event_type": "Gate Failure",
                "description": e_desc,
            })
            event_counter += 1

    # Connect gateway relays after all construction ticks
    g_eng.connect_gateways(stars)

    # 3. Network Pathfinding & Calculations
    print("\n[Step 3/4] Solving network pathfinder travel times & strategic chokepoints...")
    
    # Calculate global average tech level
    global_avg_tech = float(np.mean(list(civ_techs.values())))

    router = RouteCalculator()
    router.build_network_graph(stars, hyperlanes, wormholes, g_eng.gates, global_avg_tech)

    # Identify Strategic Chokepoints
    chokepoints = TransitOptimizer.identify_chokepoints(router.graph, stars)

    # Compute capital routing connectivity indices
    connectivity = TransitOptimizer.calculate_empire_connectivity(router.graph, empires, capital_stars)

    # Solve FTL routes between all trading partners to populate ftl_routes.csv
    ftl_routes_db = []
    route_counter = 1
    
    # Connect every empire to every other empire (all-pairs travel time records)
    for i, emp_a in enumerate(empires[:50]):  # Limit subset of pairs to prevent file bloat
        cid_a = emp_a["founding_civilization_id"]
        star_a = capital_stars.get(cid_a)
        if not star_a:
            continue

        for j, emp_b in enumerate(empires):
            if i == j:
                continue
            cid_b = emp_b["founding_civilization_id"]
            star_b = capital_stars.get(cid_b)
            if not star_b:
                continue

            path, travel_time = router.calculate_transit(star_a, star_b)
            if path:
                # Check route type
                r_type = "Trade Route" if cid_b in str(emp_a.get("trading_partners", "")) else "Warp Flight"
                ftl_routes_db.append({
                    "route_id": f"FTL-RTE-{route_counter:06d}",
                    "empire_id": cid_a,
                    "empire_name": emp_a["empire_name"],
                    "source_star_id": star_a,
                    "source_star_name": stars[star_a]["name"],
                    "target_star_id": star_b,
                    "target_star_name": stars[star_b]["name"],
                    "travel_time_years": round(travel_time, 3),
                    "stops_count": len(path) - 1,
                    "route_type": r_type
                })
                route_counter += 1

    # 4. Feedback loops: Boost GDP in datasets/economy.csv and gdp_rankings.csv
    print("\nApplying FTL network feedback boost to empire wealth & GDP...")
    # Update GDPs based on connectivity index
    for idx, row in econ_df.iterrows():
        cid = str(row["civilization_id"])
        conn_score = connectivity.get(cid, 1.0)
        # GDP boost is up to 3% for highly connected empires
        boost = 1.0 + (conn_score / 100.0) * 0.03
        econ_df.at[idx, "gdp"] = round(row["gdp"] * boost, 2)
        econ_df.at[idx, "trade_volume"] = round(row["trade_volume"] * (1.0 + conn_score * 0.005), 2)

    # Write back boosted economy databases
    econ_df.to_csv(os.path.join(output_dir, "economy.csv"), index=False)

    rankings_df = pd.read_csv(os.path.join(output_dir, "gdp_rankings.csv"))
    for idx, row in rankings_df.iterrows():
        cid = str(row["civilization_id"])
        conn_score = connectivity.get(cid, 1.0)
        boost = 1.0 + (conn_score / 100.0) * 0.03
        rankings_df.at[idx, "gdp"] = round(row["gdp"] * boost, 2)
    rankings_df = rankings_df.sort_values(by="gdp", ascending=False).reset_index(drop=True)
    rankings_df.index += 1
    rankings_df.index.name = "gdp_rank"
    rankings_df.to_csv(os.path.join(output_dir, "gdp_rankings.csv"))

    # Export Phase 8 Catalogs
    # A. Wormholes
    w_records = [w.to_dict() for w in wormholes]
    w_out_df = pd.DataFrame(w_records)
    if w_out_df.empty:
        w_out_df = pd.DataFrame(columns=["wormhole_id", "wormhole_type", "stability_type", "entry_system", "exit_system", "distance_reduction", "stability", "capacity", "owner_empire"])
    w_csv = os.path.join(output_dir, "wormholes.csv")
    w_out_df.to_csv(w_csv, index=False)
    print(f"  - Saved wormholes: {w_csv} ({len(w_out_df)} records)")

    # B. Hyperlanes
    l_records = [l.to_dict() for l in hyperlanes]
    l_out_df = pd.DataFrame(l_records)
    if l_out_df.empty:
        l_out_df = pd.DataFrame(columns=["lane_id", "lane_type", "source_star_id", "target_star_id", "route_length_ly", "traffic_index", "economic_value", "security_level"])
    l_csv = os.path.join(output_dir, "hyperlane_network.csv")
    l_out_df.to_csv(l_csv, index=False)
    print(f"  - Saved hyperlanes: {l_csv} ({len(l_out_df)} records)")

    # C. Jump Gates
    g_records = [g.to_dict() for g in g_eng.gates.values()]
    g_out_df = pd.DataFrame(g_records)
    if g_out_df.empty:
        g_out_df = pd.DataFrame(columns=["gate_id", "gate_type", "star_id", "construction_cost", "energy_usage", "throughput", "connected_count", "owner_empire"])
    g_csv = os.path.join(output_dir, "jump_gates.csv")
    g_out_df.to_csv(g_csv, index=False)
    print(f"  - Saved jump gates: {g_csv} ({len(g_out_df)} records)")

    # D. FTL Routes
    r_out_df = pd.DataFrame(ftl_routes_db)
    if r_out_df.empty:
        r_out_df = pd.DataFrame(columns=["route_id", "empire_id", "empire_name", "source_star_id", "source_star_name", "target_star_id", "target_star_name", "travel_time_years", "stops_count", "route_type"])
    r_csv = os.path.join(output_dir, "ftl_routes.csv")
    r_out_df.to_csv(r_csv, index=False)
    print(f"  - Saved FTL routes: {r_csv} ({len(r_out_df)} records)")

    # E. Strategic Systems
    s_out_df = pd.DataFrame(chokepoints)
    if s_out_df.empty:
        s_out_df = pd.DataFrame(columns=["star_id", "star_name", "region", "betweenness_centrality", "strategic_value_score", "neighbors_count"])
    s_csv = os.path.join(output_dir, "strategic_systems.csv")
    s_out_df.to_csv(s_csv, index=False)
    print(f"  - Saved strategic systems: {s_csv} ({len(s_out_df)} records)")

    # F. Transport Events
    evt_out_df = pd.DataFrame(events_db)
    if evt_out_df.empty:
        evt_out_df = pd.DataFrame(columns=["event_id", "tick", "year", "civilization_id", "event_type", "description"])
    evt_csv = os.path.join(output_dir, "transport_events.csv")
    evt_out_df.to_csv(evt_csv, index=False)
    print(f"  - Saved transport events: {evt_csv} ({len(evt_out_df)} records)")

    # 5. Render Visualizations
    print("\n[Step 4/4] Rendering transportation network visualizations...")
    try:
        viz = GalacticNetworkVisualizer(datasets_dir=output_dir)
        viz.plot_wormhole_network(output_dir)
        viz.plot_hyperlane_grid(output_dir)
        viz.plot_jump_gate_map(output_dir)
        viz.plot_strategic_chokepoints(output_dir)
        viz.plot_galactic_connectivity(output_dir)
        viz.generate_ftl_timeline(output_dir)
    except Exception as e:
        print(f"Error during network rendering: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()

    # 6. Generate Reports & Summary
    try:
        anal = FtlAnalytics(datasets_dir=output_dir)
        anal.print_summary()
    except Exception as e:
        print(f"Error during analytics reporting: {e}", file=sys.stderr)

    print("=" * 80)
    print("  PHASE 8 EXECUTION COMPLETE: GALACTIC TRANSPORTATION LAYER")
    print("=" * 80)


if __name__ == "__main__":
    main()
