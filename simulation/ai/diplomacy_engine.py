"""
diplomacy_engine.py — Tracks relationship states and resolves battles in Phase 5.
"""

from typing import List, Dict, Any, Tuple
import numpy as np
from simulation.ai.strategic_planner import CivilizationAgent


class DiplomacyEngine:
    """Manages relationships, treaties, war declarations, and battle resolutions."""

    def __init__(self, seed: int = 42) -> None:
        self.random = np.random.RandomState(seed)
        # Nested dictionary mapping: [civ1_id][civ2_id] -> relation_score (-100 to 100)
        self.relations: Dict[str, Dict[str, float]] = {}

    def get_relationship(self, civ1: CivilizationAgent, civ2: CivilizationAgent) -> float:
        """Get or initialize the relationship score between two agents.

        Parameters
        ----------
        civ1 : CivilizationAgent
        civ2 : CivilizationAgent

        Returns
        -------
        float
            Relationship score (-100.0 to 100.0).
        """
        id1, id2 = civ1.civilization_id, civ2.civilization_id
        if id1 not in self.relations:
            self.relations[id1] = {}
        if id2 not in self.relations[id1]:
            # Initial relation depends on cooperation, aggression, and a random scatter
            base = 10.0 + (civ1.cooperation + civ2.cooperation) / 5.0 - (civ1.aggression + civ2.aggression) / 5.0
            scatter = self.random.uniform(-20.0, 20.0)
            score = max(-50.0, min(80.0, base + scatter))
            self.relations[id1][id2] = score
            
            # Reciprocal relation
            if id2 not in self.relations:
                self.relations[id2] = {}
            self.relations[id2][id1] = score

        return self.relations[id1][id2]

    def set_relationship(self, id1: str, id2: str, score: float) -> None:
        """Directly set a relationship score between two agents.

        Parameters
        ----------
        id1 : str
        id2 : str
        score : float
        """
        score = max(-100.0, min(100.0, score))
        if id1 not in self.relations:
            self.relations[id1] = {}
        self.relations[id1][id2] = score

        if id2 not in self.relations:
            self.relations[id2] = {}
        self.relations[id2][id1] = score

    def update_relationships(self, all_agents: Dict[str, CivilizationAgent]) -> None:
        """Decay relationship scores toward baseline values and prune broken treaties.

        Parameters
        ----------
        all_agents : Dict[str, CivilizationAgent]
        """
        for id1, agent1 in all_agents.items():
            if agent1.is_extinct:
                continue
            for id2, agent2 in all_agents.items():
                if id2 == id1 or agent2.is_extinct:
                    continue

                current = self.get_relationship(agent1, agent2)
                
                # Check for war condition
                if id2 in agent1.wars or id1 in agent2.wars:
                    self.set_relationship(id1, id2, -100.0)
                    continue

                # Normal decay toward baseline
                baseline = (agent1.cooperation + agent2.cooperation) / 5.0 - (agent1.aggression + agent2.aggression) / 5.0
                decay_rate = 0.05
                new_score = current + (baseline - current) * decay_rate
                self.set_relationship(id1, id2, new_score)

                # Prune treaties if relationship deteriorates
                if new_score < 0.0:
                    if id2 in agent1.allies:
                        agent1.allies.remove(id2)
                    if id1 in agent2.allies:
                        agent2.allies.remove(id1)
                if new_score < -30.0:
                    if id2 in agent1.trading_partners:
                        agent1.trading_partners.remove(id2)
                    if id1 in agent2.trading_partners:
                        agent2.trading_partners.remove(id1)

    def propose_trade(self, proposer: CivilizationAgent, receiver: CivilizationAgent) -> Tuple[bool, str]:
        """Propose a trade treaty between two agents.

        Parameters
        ----------
        proposer : CivilizationAgent
        receiver : CivilizationAgent

        Returns
        -------
        Tuple[bool, str]
            True if accepted, along with a text explanation.
        """
        rel = self.get_relationship(proposer, receiver)
        
        # Proposer accepts if they chose this action. Receiver decides:
        # Base probability = 20% + relationship * 0.5% + receiver cooperation * 0.5% - receiver aggression * 0.2%
        prob = 0.20 + (rel / 200.0) + (receiver.cooperation / 200.0) - (receiver.aggression / 500.0)
        prob = max(0.05, min(0.95, prob))

        if self.random.random() < prob:
            # Accepted
            if receiver.civilization_id not in proposer.trading_partners:
                proposer.trading_partners.append(receiver.civilization_id)
            if proposer.civilization_id not in receiver.trading_partners:
                receiver.trading_partners.append(proposer.civilization_id)

            # Boost relationship score
            new_rel = rel + 15.0
            self.set_relationship(proposer.civilization_id, receiver.civilization_id, new_rel)

            # Economic benefits (instant resources boost)
            proposer.resources += 200.0
            receiver.resources += 200.0

            return True, f"Trade treaty established between {proposer.name} and {receiver.name}."
        else:
            # Declined
            new_rel = rel - 5.0
            self.set_relationship(proposer.civilization_id, receiver.civilization_id, new_rel)
            return False, f"{receiver.name} declined trade proposal from {proposer.name}."

    def propose_alliance(self, proposer: CivilizationAgent, receiver: CivilizationAgent) -> Tuple[bool, str]:
        """Propose an alliance agreement between two agents.

        Parameters
        ----------
        proposer : CivilizationAgent
        receiver : CivilizationAgent

        Returns
        -------
        Tuple[bool, str]
            True if accepted, along with a text explanation.
        """
        rel = self.get_relationship(proposer, receiver)
        
        # Requires positive relationship and cooperation
        if rel < 30.0:
            return False, f"{receiver.name} immediately rejected alliance from {proposer.name} due to low relations ({rel:.1f})."

        prob = 0.10 + (rel / 150.0) + (receiver.cooperation / 250.0) - (receiver.aggression / 400.0)
        prob = max(0.01, min(0.90, prob))

        if self.random.random() < prob:
            # Accepted
            if receiver.civilization_id not in proposer.allies:
                proposer.allies.append(receiver.civilization_id)
            if proposer.civilization_id not in receiver.allies:
                receiver.allies.append(proposer.civilization_id)

            # Also force trade treaty
            if receiver.civilization_id not in proposer.trading_partners:
                proposer.trading_partners.append(receiver.civilization_id)
            if proposer.civilization_id not in receiver.trading_partners:
                receiver.trading_partners.append(proposer.civilization_id)

            # Boost relationship score
            new_rel = rel + 30.0
            self.set_relationship(proposer.civilization_id, receiver.civilization_id, new_rel)

            # Stability boost
            proposer.stability = min(100.0, proposer.stability + 10.0)
            receiver.stability = min(100.0, receiver.stability + 10.0)

            return True, f"Alliance formed between {proposer.name} and {receiver.name}."
        else:
            # Declined
            new_rel = rel - 10.0
            self.set_relationship(proposer.civilization_id, receiver.civilization_id, new_rel)
            return False, f"{receiver.name} declined alliance proposal from {proposer.name}."

    def resolve_war(
        self,
        attacker: CivilizationAgent,
        defender: CivilizationAgent,
        all_agents: Dict[str, CivilizationAgent],
    ) -> str:
        """Resolve military conflict between an attacker and defender, incorporating allies.

        Parameters
        ----------
        attacker : CivilizationAgent
        defender : CivilizationAgent
        all_agents : Dict[str, CivilizationAgent]

        Returns
        -------
        str
            A detailed log of the war result.
        """
        att_id = attacker.civilization_id
        def_id = defender.civilization_id

        # Declare war formally (relationship score collapses)
        self.set_relationship(att_id, def_id, -100.0)
        if def_id not in attacker.wars:
            attacker.wars.append(def_id)
        if att_id not in defender.wars:
            defender.wars.append(att_id)

        # Break active treaties
        if def_id in attacker.allies:
            attacker.allies.remove(def_id)
        if att_id in defender.allies:
            defender.allies.remove(att_id)
        if def_id in attacker.trading_partners:
            attacker.trading_partners.remove(def_id)
        if att_id in defender.trading_partners:
            defender.trading_partners.remove(att_id)

        # Gather Allies
        attacker_coalition = [attacker]
        defender_coalition = [defender]

        # Defender's allies join the defense
        for ally_id in defender.allies:
            ally_agent = all_agents.get(ally_id)
            if ally_agent and not ally_agent.is_extinct:
                defender_coalition.append(ally_agent)
                if att_id not in ally_agent.wars:
                    ally_agent.wars.append(att_id)
                if ally_id not in attacker.wars:
                    attacker.wars.append(ally_id)

        # Attacker's allies join if they have high relations and risk tolerance
        for ally_id in attacker.allies:
            ally_agent = all_agents.get(ally_id)
            if ally_agent and not ally_agent.is_extinct and ally_id not in defender_coalition:
                # Joining check
                ally_rel_def = self.get_relationship(ally_agent, defender)
                if ally_rel_def < -10.0 and ally_agent.risk_tolerance > 30.0:
                    attacker_coalition.append(ally_agent)
                    if def_id not in ally_agent.wars:
                        ally_agent.wars.append(def_id)
                    if ally_id not in defender.wars:
                        defender.wars.append(ally_id)

        # Calculate combat power
        # base_power = population * (tech_level ** 1.5) * (1 + aggression/100) * random_factor
        att_powers = []
        for att in attacker_coalition:
            rand_factor = self.random.uniform(0.7, 1.3)
            p = att.population * (att.technology_level ** 1.5) * (1.0 + att.aggression / 100.0) * rand_factor
            att_powers.append(p)

        def_powers = []
        for defe in defender_coalition:
            rand_factor = self.random.uniform(0.7, 1.3)
            p = defe.population * (defe.technology_level ** 1.5) * (1.0 + defe.aggression / 100.0) * rand_factor
            def_powers.append(p)

        total_att_power = sum(att_powers)
        total_def_power = sum(def_powers)

        coalition_att_names = ", ".join([a.name for a in attacker_coalition])
        coalition_def_names = ", ".join([d.name for d in defender_coalition])

        # Resolve battle outcome
        if total_att_power > total_def_power:
            # Attacker Coalition wins!
            power_ratio = total_att_power / max(1.0, total_def_power)
            
            # Defender suffers heavy losses
            pop_loss_pct = min(0.40, 0.15 * power_ratio)
            stability_loss = min(60.0, 20.0 * power_ratio)
            resource_loss_pct = min(0.50, 0.20 * power_ratio)

            # Apply consequences to defender
            lost_pop = defender.population * pop_loss_pct
            defender.population = max(0.0, defender.population - lost_pop)
            defender.stability = max(0.0, defender.stability - stability_loss)
            
            lost_res = defender.resources * resource_loss_pct
            defender.resources = max(0.0, defender.resources - lost_res)

            # Attacker gains resources
            loot_per_attacker = lost_res / len(attacker_coalition)
            for att in attacker_coalition:
                att.resources += loot_per_attacker
                att.stability = min(100.0, att.stability + 5.0)

            # Check if defender is annihilated
            extinct_msg = ""
            if defender.population < 1e6:
                defender.is_extinct = True
                defender.population = 0.0
                defender.stability = 0.0
                # Transfer remaining colonies and home planet to the primary attacker
                for col in list(defender.colonies):
                    attacker.colonies.append(col)
                attacker.colonies.append(defender.home_planet_id)
                extinct_msg = f" {defender.name} has been completely conquered and is now extinct."

            # Clear wars if defender is extinct
            if defender.is_extinct:
                for agent in all_agents.values():
                    if def_id in agent.wars:
                        agent.wars.remove(def_id)
                    if def_id in agent.allies:
                        agent.allies.remove(def_id)
                    if def_id in agent.trading_partners:
                        agent.trading_partners.remove(def_id)

            return (
                f"WAR OUTCOME: Coalition [{coalition_att_names}] defeated Coalition [{coalition_def_names}]. "
                f"{defender.name} lost {lost_pop:,.0f} population ({pop_loss_pct*100:.1f}%) and "
                f"reparated {lost_res:,.1f} resources.{extinct_msg}"
            )
        else:
            # Defender Coalition wins!
            power_ratio = total_def_power / max(1.0, total_att_power)
            
            # Attacker suffers losses
            pop_loss_pct = min(0.30, 0.10 * power_ratio)
            stability_loss = min(40.0, 15.0 * power_ratio)
            
            lost_pop = attacker.population * pop_loss_pct
            attacker.population = max(0.0, attacker.population - lost_pop)
            attacker.stability = max(0.0, attacker.stability - stability_loss)

            # Attacker pays reparations to defender
            reparations = min(attacker.resources, attacker.resources * 0.20 * power_ratio)
            attacker.resources = max(0.0, attacker.resources - reparations)
            defender.resources += reparations

            # Check if attacker is annihilated
            extinct_msg = ""
            if attacker.population < 1e6:
                attacker.is_extinct = True
                attacker.population = 0.0
                attacker.stability = 0.0
                extinct_msg = f" {attacker.name}'s military collapsed and the society dissolved into extinction."

            # Clear wars if attacker is extinct
            if attacker.is_extinct:
                for agent in all_agents.values():
                    if att_id in agent.wars:
                        agent.wars.remove(att_id)
                    if att_id in agent.allies:
                        agent.allies.remove(att_id)
                    if att_id in agent.trading_partners:
                        agent.trading_partners.remove(att_id)

            return (
                f"WAR OUTCOME: Coalition [{coalition_def_names}] successfully defended against Coalition [{coalition_att_names}]. "
                f"Attacker {attacker.name} suffered military defeat, losing {lost_pop:,.0f} population and "
                f"paying {reparations:,.1f} resources in reparations.{extinct_msg}"
            )
