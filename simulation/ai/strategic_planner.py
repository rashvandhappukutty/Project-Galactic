"""
strategic_planner.py — Strategic planning and personality assignment for Civilization Agents.

Defines the CivilizationAgent data structure and the decision-making logic
which uses personality, traits, threat, and opportunity scores to select actions.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Tuple
import numpy as np


@dataclass
class CivilizationAgent:
    """Represents an autonomous AI agent for a civilization.

    Attributes
    ----------
    civilization_id : str
        Unique identifier of the civilization.
    name : str
        Name of the civilization.
    technology_level : float
        Current tech level of the civilization (1.0 to 10.0+).
    population : float
        Current population count.
    resources : float
        Accumulated resource reserves.
    government : str
        Type of government structure.
    energy_system : str
        Active primary energy source.
    kardashev_rating : float
        Kardashev scale index.
    aggression : float
        Propensity for hostile actions (1.0 to 100.0).
    curiosity : float
        Propensity for research and exploration (1.0 to 100.0).
    cooperation : float
        Propensity for trade and alliances (1.0 to 100.0).
    risk_tolerance : float
        Propensity for high-risk expansion or combat (1.0 to 100.0).
    personality : str
        Assigned strategic personality.
    megastructure_type : str
        Type of megastructure currently under construction or complete.
    megastructure_progress : float
        Progress of megastructure construction (0.0 to 100.0).
    megastructure_energy : float
        Energy output of completed megastructures (in Watts).
    is_extinct : bool
        Flag indicating if the civilization has collapsed or been destroyed.
    home_planet_id : str
        ID of the home planet.
    home_star_id : str
        ID of the home star system.
    coordinates : Tuple[float, float, float]
        Galactic coordinates in light-years (x, y, z).
    allies : List[str] = field(default_factory=list)
        List of civilization IDs this agent is allied with.
    trading_partners : List[str] = field(default_factory=list)
        List of civilization IDs this agent has trade agreements with.
    wars : List[str] = field(default_factory=list)
        List of civilization IDs this agent is currently at war with.
    colonies : List[str] = field(default_factory=list)
        List of planet IDs colonized by this agent.
    stability : float = 80.0
        Internal stability score (0.0 to 100.0).
    """

    civilization_id: str
    name: str
    technology_level: float
    population: float
    resources: float
    government: str
    energy_system: str
    kardashev_rating: float
    aggression: float
    curiosity: float
    cooperation: float
    risk_tolerance: float
    personality: str = ""
    megastructure_type: str = ""
    megastructure_progress: float = 0.0
    megastructure_energy: float = 0.0
    is_extinct: bool = False
    home_planet_id: str = ""
    home_star_id: str = ""
    coordinates: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    allies: List[str] = field(default_factory=list)
    trading_partners: List[str] = field(default_factory=list)
    wars: List[str] = field(default_factory=list)
    colonies: List[str] = field(default_factory=list)
    stability: float = 80.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert agent state into a serializable dictionary."""
        return {
            "civilization_id": self.civilization_id,
            "name": self.name,
            "technology_level": round(self.technology_level, 3),
            "population": float(self.population),
            "resources": round(self.resources, 2),
            "government": self.government,
            "energy_system": self.energy_system,
            "kardashev_rating": round(self.kardashev_rating, 3),
            "aggression": round(self.aggression, 2),
            "curiosity": round(self.curiosity, 2),
            "cooperation": round(self.cooperation, 2),
            "risk_tolerance": round(self.risk_tolerance, 2),
            "personality": self.personality,
            "megastructure_type": self.megastructure_type,
            "megastructure_progress": round(self.megastructure_progress, 2),
            "megastructure_energy": self.megastructure_energy,
            "is_extinct": self.is_extinct,
            "home_planet_id": self.home_planet_id,
            "home_star_id": self.home_star_id,
            "x": self.coordinates[0],
            "y": self.coordinates[1],
            "z": self.coordinates[2],
            "stability": round(self.stability, 2),
            "allies_count": len(self.allies),
            "partners_count": len(self.trading_partners),
            "wars_count": len(self.wars),
            "colonies_count": len(self.colonies),
        }


class StrategicPlanner:
    """Determines personalities and handles action selection for CivilizationAgents."""

    DECISION_TYPES = [
        "EXPAND",
        "COLONIZE",
        "RESEARCH",
        "TRADE",
        "ALLY",
        "DEFEND",
        "ATTACK",
        "BUILD_MEGASTRUCTURE",
        "EXPLORE",
        "ISOLATE",
    ]

    PERSONALITIES = [
        "Expansionist",
        "Scientific",
        "Diplomatic",
        "Isolationist",
        "Militaristic",
        "Industrialist",
        "Explorer",
    ]

    def assign_personality(self, agent: CivilizationAgent) -> str:
        """Deterministically assign a personality based on the agent's traits.

        Parameters
        ----------
        agent : CivilizationAgent

        Returns
        -------
        str
            The assigned personality name.
        """
        # We classify personalities based on high scores relative to others
        traits = {
            "Militaristic": agent.aggression,
            "Diplomatic": agent.cooperation,
            "Scientific": agent.curiosity,
            "Isolationist": 100.0 - agent.cooperation,  # Low cooperation indicates isolationism
            "Expansionist": (agent.risk_tolerance + agent.aggression) / 2.0,
            "Explorer": (agent.curiosity + agent.risk_tolerance) / 2.0,
            "Industrialist": (100.0 - agent.risk_tolerance + agent.curiosity) / 2.0, # Methodical
        }

        # Select the highest scoring personality
        best_personality = max(traits, key=traits.get)
        agent.personality = best_personality
        return best_personality

    def evaluate_action_probabilities(
        self, agent: CivilizationAgent, threat_score: float, opportunity_score: float, nearby_habitable: int
    ) -> Dict[str, float]:
        """Compute relative probabilities for each strategic action.

        Parameters
        ----------
        agent : CivilizationAgent
        threat_score : float
            Threat score (0.0 to 100.0).
        opportunity_score : float
            Opportunity score (0.0 to 100.0).
        nearby_habitable : int
            Number of nearby habitable planets available.

        Returns
        -------
        Dict[str, float]
            Map of action names to normalized probabilities.
        """
        # Base probabilities
        probs = {a: 1.0 for a in self.DECISION_TYPES}

        # 1. Adjust based on Personality
        p = agent.personality
        if p == "Militaristic":
            probs["ATTACK"] *= 3.5
            probs["DEFEND"] *= 2.0
            probs["ALLY"] *= 0.3
            probs["TRADE"] *= 0.5
            probs["ISOLATE"] *= 0.4
        elif p == "Scientific":
            probs["RESEARCH"] *= 4.0
            probs["BUILD_MEGASTRUCTURE"] *= 2.5
            probs["EXPLORE"] *= 1.8
            probs["ATTACK"] *= 0.2
        elif p == "Expansionist":
            probs["COLONIZE"] *= 3.5
            probs["EXPAND"] *= 3.0
            probs["ISOLATE"] *= 0.2
            if nearby_habitable == 0:
                probs["EXPLORE"] *= 2.0
        elif p == "Diplomatic":
            probs["ALLY"] *= 3.5
            probs["TRADE"] *= 3.0
            probs["ATTACK"] *= 0.1
            probs["ISOLATE"] *= 0.2
        elif p == "Isolationist":
            probs["ISOLATE"] *= 4.0
            probs["DEFEND"] *= 2.5
            probs["ALLY"] *= 0.1
            probs["TRADE"] *= 0.3
            probs["COLONIZE"] *= 0.5
        elif p == "Industrialist":
            probs["BUILD_MEGASTRUCTURE"] *= 3.5
            probs["TRADE"] *= 2.0
            probs["EXPAND"] *= 1.8
            probs["EXPLORE"] *= 0.5
        elif p == "Explorer":
            probs["EXPLORE"] *= 4.0
            probs["COLONIZE"] *= 2.0
            probs["ISOLATE"] *= 0.3
            probs["ATTACK"] *= 0.4

        # 2. Adjust based on Threat Score
        if threat_score > 60.0:
            probs["DEFEND"] *= (threat_score / 30.0)
            probs["ISOLATE"] *= (threat_score / 50.0)
            probs["ALLY"] *= (threat_score / 40.0) if agent.cooperation > 40.0 else 0.5
            if agent.aggression > 60.0:
                probs["ATTACK"] *= (threat_score / 40.0)  # Preemptive strike
            probs["BUILD_MEGASTRUCTURE"] *= 0.3  # Focus on survival
            probs["EXPLORE"] *= 0.5
            probs["COLONIZE"] *= 0.4
        elif threat_score < 20.0:
            probs["DEFEND"] *= 0.5
            probs["ATTACK"] *= 0.8  # No immediate target of opportunity/threat

        # 3. Adjust based on Opportunity Score
        if opportunity_score > 60.0:
            if nearby_habitable > 0:
                probs["COLONIZE"] *= (opportunity_score / 25.0)
                probs["EXPAND"] *= (opportunity_score / 35.0)
            else:
                probs["EXPLORE"] *= 2.0
            probs["TRADE"] *= (opportunity_score / 30.0)
            probs["ALLY"] *= (opportunity_score / 40.0)
            if agent.technology_level >= 6.0:
                probs["BUILD_MEGASTRUCTURE"] *= (opportunity_score / 40.0)

        # 4. Adjust based on Government Type
        gov = agent.government.upper()
        if "TECHNOCRACY" in gov or "SCIENTIFIC" in gov or "AI" in gov:
            probs["RESEARCH"] *= 1.8
            probs["BUILD_MEGASTRUCTURE"] *= 1.5
        elif "FEDERATION" in gov or "DEMOCRACY" in gov:
            probs["ALLY"] *= 1.6
            probs["TRADE"] *= 1.5
            probs["ATTACK"] *= 0.4
        elif "MONARCHY" in gov or "EMPIRE" in gov:
            probs["ATTACK"] *= 1.5
            probs["EXPAND"] *= 1.3
            probs["ALLY"] *= 0.6
        elif "COLLECTIVE" in gov or "HIVE" in gov:
            probs["EXPAND"] *= 1.5
            probs["ISOLATE"] *= 1.2

        # 5. Resource / Tech Restrictions
        if agent.resources < 200.0:
            # Low resources: cannot colonize easily, must trade or defend
            probs["COLONIZE"] *= 0.1
            probs["BUILD_MEGASTRUCTURE"] *= 0.05
            probs["TRADE"] *= 2.0
        if agent.technology_level < 5.0:
            # Cannot build megastructures below tech 5.0
            probs["BUILD_MEGASTRUCTURE"] *= 0.0

        # Ensure no negative or zero probabilities
        for k in probs:
            probs[k] = max(0.001, probs[k])

        # Normalize
        total = sum(probs.values())
        return {k: v / total for k, v in probs.items()}

    def select_action(
        self,
        agent: CivilizationAgent,
        threat_score: float,
        opportunity_score: float,
        nearby_habitable: int,
        random_state: np.random.RandomState,
    ) -> str:
        """Select a strategic action using weighted random choice based on computed probabilities.

        Parameters
        ----------
        agent : CivilizationAgent
        threat_score : float
        opportunity_score : float
        nearby_habitable : int
        random_state : np.random.RandomState

        Returns
        -------
        str
            The chosen action.
        """
        action_probs = self.evaluate_action_probabilities(
            agent, threat_score, opportunity_score, nearby_habitable
        )
        actions = list(action_probs.keys())
        probabilities = [action_probs[a] for a in actions]
        return str(random_state.choice(actions, p=probabilities))
