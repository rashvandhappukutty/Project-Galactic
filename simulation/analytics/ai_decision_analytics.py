"""
ai_decision_analytics.py — Computes post-simulation statistics for Phase 5.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List


class AIDecisionAnalytics:
    """Calculates and reports strategic insights and rankings from Phase 5 AI simulations."""

    def __init__(
        self,
        decisions_csv: str,
        threat_csv: str,
        opportunity_csv: str,
        megastructures_csv: str,
    ) -> None:
        self.decisions_df = pd.read_csv(decisions_csv)
        self.threat_df = pd.read_csv(threat_csv)
        self.opportunity_df = pd.read_csv(opportunity_csv)
        self.megastructures_df = pd.read_csv(megastructures_csv)

    def calculate_metrics(self, all_agents_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Compute top ranking civilizations across strategic categories.

        Parameters
        ----------
        all_agents_dict : Dict[str, CivilizationAgent]

        Returns
        -------
        Dict[str, Any]
            Calculated ranking dictionaries.
        """
        metrics = {}

        # 1. Most Aggressive (Most ATTACK decisions or highest aggression trait)
        attack_counts = self.decisions_df[self.decisions_df["decision"] == "ATTACK"].groupby("civilization_name").size()
        if not attack_counts.empty:
            most_aggr_name = attack_counts.idxmax()
            most_aggr_val = int(attack_counts.max())
        else:
            # Fallback to traits
            aggr_agent = max(all_agents_dict.values(), key=lambda a: a.aggression, default=None)
            most_aggr_name = aggr_agent.name if aggr_agent else "None"
            most_aggr_val = int(aggr_agent.aggression) if aggr_agent else 0
        metrics["most_aggressive"] = (most_aggr_name, most_aggr_val)

        # 2. Most Scientific (Most RESEARCH decisions or highest curiosity trait)
        research_counts = self.decisions_df[self.decisions_df["decision"] == "RESEARCH"].groupby("civilization_name").size()
        if not research_counts.empty:
            most_sci_name = research_counts.idxmax()
            most_sci_val = int(research_counts.max())
        else:
            sci_agent = max(all_agents_dict.values(), key=lambda a: a.curiosity, default=None)
            most_sci_name = sci_agent.name if sci_agent else "None"
            most_sci_val = int(sci_agent.curiosity) if sci_agent else 0
        metrics["most_scientific"] = (most_sci_name, most_sci_val)

        # 3. Most Expansionist (Most COLONIZE/EXPAND decisions or highest colony count)
        exp_decisions = ["COLONIZE", "EXPAND"]
        expansion_counts = self.decisions_df[self.decisions_df["decision"].isin(exp_decisions)].groupby("civilization_name").size()
        if not expansion_counts.empty:
            most_exp_name = expansion_counts.idxmax()
            most_exp_val = int(expansion_counts.max())
        else:
            exp_agent = max(all_agents_dict.values(), key=lambda a: len(a.colonies), default=None)
            most_exp_name = exp_agent.name if exp_agent else "None"
            most_exp_val = len(exp_agent.colonies) if exp_agent else 0
        metrics["most_expansionist"] = (most_exp_name, most_exp_val)

        # 4. Largest Megastructure Builder (Highest energy output or progress)
        if not self.megastructures_df.empty:
            complete_megs = self.megastructures_df[self.megastructures_df["status"] == "Complete"]
            if not complete_megs.empty:
                max_energy_row = complete_megs.loc[complete_megs["energy_output_watts"].idxmax()]
                metrics["largest_megastructure"] = (max_energy_row["civilization_name"], max_energy_row["megastructure_type"], float(max_energy_row["energy_output_watts"]))
            else:
                max_progress_row = self.megastructures_df.loc[self.megastructures_df["construction_progress"].idxmax()]
                metrics["largest_megastructure"] = (max_progress_row["civilization_name"], max_progress_row["megastructure_type"], float(max_progress_row["construction_progress"]))
        else:
            metrics["largest_megastructure"] = ("None", "N/A", 0.0)

        # 5. Highest Threat Civilization (Highest average threat score posed to neighbors at final state)
        final_tick = self.threat_df["tick"].max()
        final_threats = self.threat_df[self.threat_df["tick"] == final_tick]
        if not final_threats.empty:
            max_threat_row = final_threats.loc[final_threats["threat_score"].idxmax()]
            metrics["highest_threat"] = (max_threat_row["civilization_name"], float(max_threat_row["threat_score"]))
        else:
            metrics["highest_threat"] = ("None", 0.0)

        # 6. Most Influential (Highest allies + trading partners count)
        influential_agent = max(all_agents_dict.values(), key=lambda a: len(a.allies) + len(a.trading_partners), default=None)
        if influential_agent:
            score = len(influential_agent.allies) + len(influential_agent.trading_partners)
            metrics["most_influential"] = (influential_agent.name, score)
        else:
            metrics["most_influential"] = ("None", 0)

        # 7. Top 20 Strategic Powers Index
        # Power Index = (population / 1e9) + tech_level * 3.0 + colonies * 2.0 + allies * 1.5 + megastructure_complete * 10.0
        powers = []
        for agent in all_agents_dict.values():
            if agent.is_extinct:
                continue
            
            meg_bonus = 10.0 if (agent.megastructure_progress >= 100.0) else 0.0
            p_index = (agent.population / 1e9) + (agent.technology_level * 3.0) + (len(agent.colonies) * 2.0) + (len(agent.allies) * 1.5) + meg_bonus
            
            powers.append({
                "civilization_id": agent.civilization_id,
                "name": agent.name,
                "population": agent.population,
                "tech_level": agent.technology_level,
                "colonies_count": len(agent.colonies),
                "allies_count": len(agent.allies),
                "megastructure": agent.megastructure_type if agent.megastructure_type else "None",
                "power_index": round(p_index, 3)
            })

        powers_df = pd.DataFrame(powers)
        if not powers_df.empty:
            top_20 = powers_df.sort_values(by="power_index", ascending=False).head(20).to_dict(orient="records")
        else:
            top_20 = []
        
        metrics["top_20_powers"] = top_20

        return metrics

    def print_summary(self, all_agents_dict: Dict[str, Any]) -> None:
        """Print high-fidelity formatted report of Phase 5 simulation results."""
        metrics = self.calculate_metrics(all_agents_dict)

        print("\n" + "=" * 80)
        print("          THE GALACTIC DREAM ENGINE - PHASE 5 DECISION ANALYTICS REPORT")
        print("=" * 80)

        # Active vs Extinct summary
        total_civs = len(all_agents_dict)
        active_civs = sum(1 for a in all_agents_dict.values() if not a.is_extinct)
        extinct_civs = total_civs - active_civs
        print(f"Total Civilizations: {total_civs:4d} | Active Agents: {active_civs:4d} | Extinct/Conquered: {extinct_civs:3d}")
        print("-" * 80)

        # Strategic Categories
        print("STRATEGIC SUPERLATIVES:")
        ma_name, ma_val = metrics["most_aggressive"]
        print(f"  - Most Aggressive Agent      : {ma_name} ({ma_val} ATTACK actions)")
        
        ms_name, ms_val = metrics["most_scientific"]
        print(f"  - Most Scientific Agent      : {ms_name} ({ms_val} RESEARCH actions)")
        
        me_name, me_val = metrics["most_expansionist"]
        print(f"  - Most Expansionist Agent     : {me_name} ({me_val} expansionist actions)")

        name, m_type, m_val = metrics["largest_megastructure"]
        if m_val >= 100.0 or m_val > 1e10:
            val_str = f"{m_val:.1e} Watts" if m_val > 1e10 else f"{m_val:.1f}% progress"
            print(f"  - Largest Megastructure Project: {name} ({m_type} | {val_str})")
        else:
            print(f"  - Largest Megastructure Project: None")

        mt_name, mt_val = metrics["highest_threat"]
        print(f"  - Highest Threat Agent       : {mt_name} (final threat score: {mt_val:.1f})")

        mi_name, mi_val = metrics["most_influential"]
        print(f"  - Most Influential Diplomat  : {mi_name} ({mi_val} treaties active)")

        print("-" * 80)
        print("TOP 20 GALACTIC POWERS RANKING (BY POWER INDEX):")
        print(f"  {'Rank':4s} | {'Civilization Name':30s} | {'Tech':5s} | {'Colonies':8s} | {'Allies':6s} | {'Power Index':12s}")
        print("  " + "-" * 76)

        for rank, p in enumerate(metrics["top_20_powers"], 1):
            name_truncated = p["name"][:30]
            print(f"  {rank:<4d} | {name_truncated:30s} | {p['tech_level']:<5.2f} | {p['colonies_count']:<8d} | {p['allies_count']:<6d} | {p['power_index']:<12.3f}")

        print("=" * 80 + "\n")
