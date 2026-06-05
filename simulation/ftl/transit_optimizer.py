"""
transit_optimizer.py — Betweenness centrality chokepoints and economic connectivity multipliers.
"""

from typing import Dict, List, Any
import networkx as nx


class TransitOptimizer:
    """Calculates strategic chokepoints and updates macroeconomic indices based on network effects."""

    @staticmethod
    def identify_chokepoints(graph: nx.Graph, stars: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify strategic chokepoint systems using Betweenness Centrality.

        Parameters
        ----------
        graph : nx.Graph
            The FTL transit graph network.
        stars : Dict[str, Dict[str, Any]]

        Returns
        -------
        List[Dict[str, Any]]
            List of systems with their strategic scores.
        """
        # Run betweenness centrality
        # Weight by FTL travel time to find chokepoints along optimal routes
        centrality = nx.betweenness_centrality(graph, weight="weight")

        chokepoints = []
        max_c = max(centrality.values()) if centrality else 1.0

        for star_id, score in centrality.items():
            star_info = stars.get(star_id)
            if not star_info:
                continue

            # Normalize to 0-100 range
            norm_score = (score / (max_c + 1e-6)) * 100.0
            
            # Check neighbors count to determine bottleneck status
            neighbors_count = len(list(graph.neighbors(star_id)))

            chokepoints.append({
                "star_id": star_id,
                "star_name": star_info["name"],
                "region": star_info.get("region", "Void"),
                "betweenness_centrality": round(score, 6),
                "strategic_value_score": round(norm_score, 2),
                "neighbors_count": neighbors_count
            })

        # Sort by strategic score descending
        chokepoints.sort(key=lambda x: x["strategic_value_score"], reverse=True)
        return chokepoints

    @staticmethod
    def calculate_empire_connectivity(
        graph: nx.Graph,
        empires: List[Dict[str, Any]],
        capital_stars: Dict[str, str]
    ) -> Dict[str, float]:
        """Compute the average travel time connectivity index for each empire.

        Connectivity Index = 100 / (Average FTL Travel Time to other empire capitals + 1)

        Parameters
        ----------
        graph : nx.Graph
        empires : List[Dict[str, Any]]
        capital_stars : Dict[str, str]
            Map of civilization_id -> star_id.

        Returns
        -------
        Dict[str, float]
            Map of civilization_id -> connectivity score (0-100).
        """
        connectivity: Dict[str, float] = {}
        cids = [str(e["founding_civilization_id"]) for e in empires]
        num_empires = len(cids)

        # Precompute all-pairs shortest paths travel times
        # We only compute lengths between capitals to keep execution fast
        cap_stars = {cid: capital_stars[cid] for cid in cids if cid in capital_stars and capital_stars[cid] in graph}

        for cid_a, star_a in cap_stars.items():
            total_time = 0.0
            reachable_count = 0

            # Single-source shortest path lengths
            try:
                lengths = nx.single_source_dijkstra_path_length(graph, source=star_a, weight="weight")
                for cid_b, star_b in cap_stars.items():
                    if cid_a == cid_b:
                        continue
                    if star_b in lengths:
                        total_time += lengths[star_b]
                        # Cap extreme values to prevent skewed averages
                        total_time = min(500.0, total_time)
                        reachable_count += 1
            except Exception:
                pass

            if reachable_count > 0:
                avg_time = total_time / reachable_count
                score = 100.0 / (avg_time + 1.0)
            else:
                score = 0.5  # Completely isolated

            connectivity[cid_a] = round(score, 2)

        return connectivity
