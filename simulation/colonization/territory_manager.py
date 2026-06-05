"""
territory_manager.py — Defines Territory data structures and claim evaluations.
"""

import math
from dataclasses import dataclass, field
from typing import Dict, List, Any, Set, Tuple
import numpy as np


@dataclass
class Territory:
    """Represents the galactic territorial borders of a civilization.

    Attributes
    ----------
    civilization_id : str
    controlled_systems : List[str]
        Star IDs currently claimed.
    controlled_planets : List[str]
        Planet IDs currently claimed.
    territory_size : float
        Estimated volume in cubic light-years.
    sphere_of_influence : float
        Claim radius in light-years.
    frontier_regions : List[str]
        Galactic regions representing boundary interfaces.
    """

    civilization_id: str
    controlled_systems: List[str] = field(default_factory=list)
    controlled_planets: List[str] = field(default_factory=list)
    territory_size: float = 0.0
    sphere_of_influence: float = 0.0
    frontier_regions: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert territory fields into a plain dictionary."""
        return {
            "civilization_id": self.civilization_id,
            "controlled_systems_count": len(self.controlled_systems),
            "controlled_planets_count": len(self.controlled_planets),
            "territory_size_ly3": round(self.territory_size, 2),
            "sphere_of_influence_ly": round(self.sphere_of_influence, 2),
            "frontier_regions_count": len(self.frontier_regions),
        }


class TerritoryManager:
    """Computes spheres of influence and resolves overlapping border claims."""

    def __init__(self, proximity_threshold: float = 150.0) -> None:
        self.proximity_threshold = proximity_threshold

    def calculate_distance(self, c1: Tuple[float, float, float], c2: Tuple[float, float, float]) -> float:
        """Calculate Euclidean distance between two coordinates."""
        return float(math.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2 + (c1[2] - c2[2])**2))

    def calculate_influence_radius(self, tech_level: float, population: float) -> float:
        """Compute sphere of influence radius in light-years based on size and tech.

        Formula: R = 25.0 + 10.0 * tech_level + 5.0 * log10(1 + population)
        """
        log_pop = math.log10(max(1.0, population))
        r = 25.0 + 10.0 * tech_level + 5.0 * log_pop
        return max(30.0, min(500.0, r))  # Clamped boundary limits

    def update_territories(
        self,
        agents_dict: Dict[str, Any],
        stars_dict: Dict[str, Dict[str, Any]],
        planets_list: List[Dict[str, Any]],
    ) -> Dict[str, Territory]:
        """Resolve galactic star claims and update each active agent's territory.

        If a system lies within the SOI of multiple agents, it is awarded to
        the agent with the highest Power Index.

        Parameters
        ----------
        agents_dict : Dict[str, CivilizationAgent]
        stars_dict : Dict[str, Dict[str, Any]]
        planets_list : List[Dict[str, Any]]

        Returns
        -------
        Dict[str, Territory]
            Registry of resolved Territory dataclasses.
        """
        territories: Dict[str, Territory] = {}
        active_agents = {aid: agent for aid, agent in agents_dict.items() if not agent.is_extinct}

        # Step 1: Initialize influence radii and base territories
        for aid, agent in active_agents.items():
            r = self.calculate_influence_radius(agent.technology_level, agent.population)
            territories[aid] = Territory(
                civilization_id=aid,
                sphere_of_influence=r,
            )

        # Map stars to their region names
        star_regions = {sid: star.get("region", "Void") for sid, star in stars_dict.items()}

        # Group planets by parent star system
        planets_by_star: Dict[str, List[str]] = {}
        for p in planets_list:
            star_id = str(p["star_id"])
            planet_id = str(p["planet_id"])
            if star_id not in planets_by_star:
                planets_by_star[star_id] = []
            planets_by_star[star_id].append(planet_id)

        # Step 2: For each star system, evaluate which agents' SOIs cover it and select winner
        for star_id, star in stars_dict.items():
            star_coords = (float(star["x"]), float(star["y"]), float(star["z"]))
            
            soi_claimants: List[Tuple[str, float]] = []  # List of (agent_id, distance)

            for aid, agent in active_agents.items():
                # Check distance from agent's home star and colonies
                home_star_info = stars_dict.get(agent.home_star_id)
                if not home_star_info:
                    continue
                home_coords = (float(home_star_info["x"]), float(home_star_info["y"]), float(home_star_info["z"]))
                
                # Check home star distance
                d = self.calculate_distance(home_coords, star_coords)
                if d <= territories[aid].sphere_of_influence:
                    soi_claimants.append((aid, d))
                    continue

                # Check colony stars distance
                colony_claimed = False
                for col_planet_id in agent.colonies:
                    # Resolve planet parent star ID
                    # Since planets list is large, we check parent star from planet ID
                    for p in planets_list:
                        if p["planet_id"] == col_planet_id:
                            col_star_id = str(p["star_id"])
                            col_star_info = stars_dict.get(col_star_id)
                            if col_star_info:
                                col_coords = (float(col_star_info["x"]), float(col_star_info["y"]), float(col_star_info["z"]))
                                d_col = self.calculate_distance(col_coords, star_coords)
                                if d_col <= territories[aid].sphere_of_influence:
                                    soi_claimants.append((aid, d_col))
                                    colony_claimed = True
                                    break
                    if colony_claimed:
                        break

            # If claimed by one or more agents
            if len(soi_claimants) == 1:
                winner_id = soi_claimants[0][0]
                territories[winner_id].controlled_systems.append(star_id)
            elif len(soi_claimants) > 1:
                # Contested claim! Winner is agent with highest Power Index
                # Power Index proxy = tech_level * 10 + log10(pop)
                best_id = ""
                best_power = -1.0
                for claimant_id, dist in soi_claimants:
                    agent = active_agents[claimant_id]
                    power = agent.technology_level * 10.0 + math.log10(max(1.0, agent.population))
                    # Small distance bonus to break ties or favor close proximity
                    power += (1.0 - (dist / territories[claimant_id].sphere_of_influence)) * 5.0
                    if power > best_power:
                        best_power = power
                        best_id = claimant_id
                
                territories[best_id].controlled_systems.append(star_id)

        # Step 3: Populate planets, size, and frontier regions
        for aid, terr in territories.items():
            agent = active_agents[aid]
            # controlled planets are all planets inside controlled systems
            for star_id in terr.controlled_systems:
                p_ids = planets_by_star.get(star_id, [])
                terr.controlled_planets.extend(p_ids)
                
                # Regions check
                r_name = star_regions.get(star_id, "Void")
                if r_name not in terr.frontier_regions:
                    terr.frontier_regions.append(r_name)

            # Territory size approximation
            r = terr.sphere_of_influence
            # Volume = 4/3 * pi * R^3 * (1 + 0.2 * colonies_count)
            base_vol = (4.0 / 3.0) * math.pi * (r ** 3)
            terr.territory_size = base_vol * (1.0 + 0.20 * len(agent.colonies))

        return territories
