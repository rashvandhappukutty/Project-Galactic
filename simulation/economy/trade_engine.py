"""
trade_engine.py — Bilateral trade treaties, embargoes, and economic bloc operations.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Tuple


@dataclass
class TradeAgreement:
    """Represents a bilateral trade agreement or economic alliance between two empires."""
    agreement_id: str
    party_a_id: str
    party_b_id: str
    agreement_type: str  # "Trade Deal", "Economic Alliance", "Resource Alliance", "Economic Union", "Industrial Coalition"
    tariff_rate: float
    volume_limit: float
    active_ticks: int = 0
    trade_volume: float = 0.0
    trade_profit: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert agreement state into a serializable dictionary."""
        return {
            "agreement_id": self.agreement_id,
            "party_a_id": self.party_a_id,
            "party_b_id": self.party_b_id,
            "agreement_type": self.agreement_type,
            "tariff_rate": round(self.tariff_rate, 3),
            "volume_limit": round(self.volume_limit, 2),
            "active_ticks": self.active_ticks,
            "trade_volume": round(self.trade_volume, 2),
            "trade_profit": round(self.trade_profit, 2),
        }


@dataclass
class EconomicBloc:
    """Represents a multilateral economic union or trade federation."""
    bloc_id: str
    bloc_name: str
    bloc_type: str  # "Trade Federation", "Resource Alliance", "Economic Union", "Industrial Coalition"
    member_empires: List[str] = field(default_factory=list)
    combined_gdp: float = 0.0
    market_share: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert bloc state into a serializable dictionary."""
        return {
            "bloc_id": self.bloc_id,
            "bloc_name": self.bloc_name,
            "bloc_type": self.bloc_type,
            "member_count": len(self.member_empires),
            "members": ",".join(self.member_empires),
            "combined_gdp": round(self.combined_gdp, 2),
            "market_share": round(self.market_share, 4),
        }


class TradeEngine:
    """Manages economic alliances, tariff structures, trade agreements, and commodity flow arbitrage."""

    def __init__(self) -> None:
        self.agreements: Dict[str, TradeAgreement] = {}
        self.blocs: Dict[str, EconomicBloc] = {}
        self.embargoes: Dict[Tuple[str, str], bool] = {}  # (party_a, party_b) -> True/False
        self.trade_dependency: Dict[str, Dict[str, float]] = {}  # empire_id -> partner_id -> dependency score

    def toggle_embargo(self, empire_a: str, empire_b: str, state: bool) -> None:
        """Impose or lift an embargo between two empires.

        Parameters
        ----------
        empire_a : str
        empire_b : str
        state : bool
            True to impose, False to lift.
        """
        pair1 = (empire_a, empire_b)
        pair2 = (empire_b, empire_a)
        self.embargoes[pair1] = state
        self.embargoes[pair2] = state

    def check_embargo(self, empire_a: str, empire_b: str) -> bool:
        """Check if an active embargo exists between two empires.

        Parameters
        ----------
        empire_a : str
        empire_b : str

        Returns
        -------
        bool
            True if embargo is active, False otherwise.
        """
        return self.embargoes.get((empire_a, empire_b), False) or self.embargoes.get((empire_b, empire_a), False)

    def calculate_tariffs(self, seller_id: str, buyer_id: str) -> float:
        """Calculate the tariff rate applicable between seller and buyer.

        Parameters
        ----------
        seller_id : str
        buyer_id : str

        Returns
        -------
        float
            Tariff rate (decimal multiplier).
        """
        if self.check_embargo(seller_id, buyer_id):
            return 1.0  # Prohibitive tariff / blocked trade

        # Check for Economic Bloc (zero tariffs inside same union)
        for bloc in self.blocs.values():
            if seller_id in bloc.member_empires and buyer_id in bloc.member_empires:
                return 0.0

        # Check for bilateral agreement
        agreement_id = f"AGR-{min(seller_id, buyer_id)}-{max(seller_id, buyer_id)}"
        agreement = self.agreements.get(agreement_id)
        if agreement:
            return agreement.tariff_rate

        # Standard default tariff rate (15%)
        return 0.15

    def resolve_arbitrage(
        self,
        route_length: float,
        seller_prices: Dict[str, float],
        buyer_prices: Dict[str, float],
        commodity: str,
        seller_inventory: float,
        tariff_rate: float
    ) -> Tuple[float, float]:
        """Compute the trade cargo volume and transaction profit based on price differential and transport cost.

        Parameters
        ----------
        route_length : float
            Distance in light-years.
        seller_prices : Dict[str, float]
        buyer_prices : Dict[str, float]
        commodity : str
        seller_inventory : float
        tariff_rate : float

        Returns
        -------
        Tuple[float, float]
            Trade Volume (units to ship), Arbitrage Profit (net credits gained).
        """
        price_diff = buyer_prices.get(commodity, 0.0) - seller_prices.get(commodity, 0.0)
        if price_diff <= 0 or seller_inventory <= 5.0:
            return 0.0, 0.0

        # Transport friction cost: 0.02 credits per light-year per unit
        transport_cost = 0.02 * route_length
        tariff_cost = seller_prices.get(commodity, 0.0) * tariff_rate

        net_margin = price_diff - (transport_cost + tariff_cost)
        if net_margin <= 0:
            return 0.0, 0.0

        # Trade volume scales with the profitability margin and available seller supply
        # Clamp volume to prevent draining entire inventory (leave reserve of 5 units)
        max_ship_volume = max(0.0, seller_inventory - 5.0)
        
        # Market absorbs less volume if prices are high or margin is thin
        market_capacity = 50.0 * (net_margin / (buyer_prices.get(commodity, 1.0) + 1.0))
        volume = min(max_ship_volume, market_capacity)
        volume = max(0.0, round(volume, 2))

        profit = volume * net_margin
        return volume, round(profit, 2)

    def update_dependencies(self, empire_id: str, partner_id: str, import_value: float, total_consumption_value: float) -> None:
        """Track economic import dependencies of an empire on its trade partners.

        Parameters
        ----------
        empire_id : str
            The importing empire.
        partner_id : str
            The exporting trade partner.
        import_value : float
            Value of goods imported in credits.
        total_consumption_value : float
            Total economic consumption value of the importing empire.
        """
        if empire_id not in self.trade_dependency:
            self.trade_dependency[empire_id] = {}
        
        ratio = import_value / (total_consumption_value + 1.0)
        self.trade_dependency[empire_id][partner_id] = round(ratio, 4)

    def formulate_agreements(self, empires: List[Dict[str, Any]], random_state) -> None:
        """Procedurally generate bilateral trade agreements based on cooperation and traits.

        Parameters
        ----------
        empires : List[Dict[str, Any]]
        random_state : np.random.RandomState
        """
        # Form partnerships between empires with high power levels or proximity
        # For simplicity, we randomly seed agreements to represent organic expansion
        agr_counter = 1
        num_empires = len(empires)
        
        for i in range(num_empires):
            emp_a = empires[i]
            cid_a = emp_a["founding_civilization_id"]
            
            # Limit the number of trade treaties to prevent quadratic growth
            num_deals = random_state.randint(1, 4)
            for _ in range(num_deals):
                j = random_state.randint(0, num_empires)
                if i == j:
                    continue
                emp_b = empires[j]
                cid_b = emp_b["founding_civilization_id"]

                # Ensure unique key
                agr_id = f"AGR-{min(cid_a, cid_b)}-{max(cid_a, cid_b)}"
                if agr_id in self.agreements:
                    continue

                # Cooperation rating determines agreement terms
                a_coop = random_state.randint(20, 100)
                b_coop = random_state.randint(20, 100)
                
                # Check for compatibility
                if a_coop >= 40 and b_coop >= 40:
                    # Agreement type
                    avg_coop = (a_coop + b_coop) / 2.0
                    if avg_coop >= 80:
                        agr_type = "Economic Alliance"
                        tariff = 0.03
                    elif avg_coop >= 65:
                        agr_type = "Resource Alliance"
                        tariff = 0.06
                    else:
                        agr_type = "Trade Deal"
                        tariff = 0.09

                    self.agreements[agr_id] = TradeAgreement(
                        agreement_id=f"TR-AGR-{agr_counter:04d}",
                        party_a_id=cid_a,
                        party_b_id=cid_b,
                        agreement_type=agr_type,
                        tariff_rate=tariff,
                        volume_limit=round(float(random_state.uniform(100.0, 500.0)), 2),
                    )
                    agr_counter += 1

    def establish_economic_blocs(self, empires: List[Dict[str, Any]], random_state) -> None:
        """Group empires into Economic Blocs (unions, federations) dynamically.

        Parameters
        ----------
        empires : List[Dict[str, Any]]
        random_state : np.random.RandomState
        """
        self.blocs.clear()
        
        bloc_types = [
            ("Trade Federation", "Cooperative Union"),
            ("Resource Alliance", "Mining Coalition"),
            ("Economic Union", "Galactic Market Union"),
            ("Industrial Coalition", "Heavy Alloy Pact")
        ]

        # Form 4-6 regional economic blocs
        num_blocs = random_state.randint(4, 8)
        
        for k in range(1, num_blocs + 1):
            bloc_idx = random_state.randint(0, len(bloc_types))
            b_type, b_desc = bloc_types[bloc_idx]
            name_suffix = b_desc if random_state.random() < 0.5 else b_type
            bloc_name = f"Centauri {name_suffix} #{k}"
            
            bloc_id = f"BLOC-{k:02d}"
            
            # Choose a core member
            core_idx = random_state.randint(0, len(empires))
            core_cid = empires[core_idx]["founding_civilization_id"]
            
            bloc = EconomicBloc(
                bloc_id=bloc_id,
                bloc_name=bloc_name,
                bloc_type=b_type,
                member_empires=[core_cid]
            )

            # Draw nearby partners to join the bloc
            num_members = random_state.randint(3, 10)
            potential_members = random_state.choice(
                [e["founding_civilization_id"] for e in empires],
                size=num_members,
                replace=False
            )
            for cid in potential_members:
                if cid not in bloc.member_empires:
                    # Ensure they are not already in a bloc
                    in_bloc = False
                    for existing_bloc in self.blocs.values():
                        if cid in existing_bloc.member_empires:
                            in_bloc = True
                            break
                    if not in_bloc:
                        bloc.member_empires.append(str(cid))

            self.blocs[bloc_id] = bloc
