"""
Pricing and Matching Engine — Renewable Energy P2P Trading Marketplace
Hackout26

Core idea:
- Price always sits between the feed-in tariff (seller floor) and grid retail rate (buyer ceiling)
- Price shifts with local (block-level) supply/demand
- Matching is greedy: cheapest sellers first, neediest/outage buyers first
- Same-block trades preferred; cross-block trades cost a small penalty

This module is intentionally free of any DB/network dependency so it can
be unit-tested and reasoned about in isolation. See matching_engine.py
for the Supabase-backed adapter that loads real listings/buyers, runs
this logic, and persists the resulting trades.
"""

from dataclasses import dataclass, field
from typing import List, Optional
import itertools

# ---------------------------------------------------------------------------
# Config — tune these for your demo
# ---------------------------------------------------------------------------

FEED_IN_TARIFF = 2.5          # ₹/kWh — what the grid pays a seller (low)
GRID_RETAIL_RATE = 9.5        # ₹/kWh — what the grid charges a buyer (high)
SENSITIVITY_FACTOR = 1.5      # how much demand/supply imbalance moves price
CONGESTION_WEIGHT = 0.5       # how much grid congestion moves price
CROSS_BLOCK_PENALTY = 0.3     # ₹/kWh extra for trades that cross blocks


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class Listing:
    house_id: str
    block: str
    available_kWh: float
    is_outage_priority: bool = False   # seller side rarely relevant, kept for symmetry


@dataclass
class BuyRequest:
    house_id: str
    block: str
    deficit_kWh: float
    family_size: int = 1
    is_outage: bool = False            # currently experiencing an outage


@dataclass
class Trade:
    seller_id: str
    buyer_id: str
    kWh: float
    price_per_kWh: float
    total_price: float
    cross_block: bool
    block: str


# ---------------------------------------------------------------------------
# Pricing
# ---------------------------------------------------------------------------

def compute_base_price() -> float:
    """Fair midpoint between feed-in tariff and grid retail rate."""
    return (FEED_IN_TARIFF + GRID_RETAIL_RATE) / 2


def compute_price(block_supply_kWh: float, block_demand_kWh: float,
                   congestion_level: float = 0.0) -> float:
    """
    Compute the current price per kWh for a block, given its total
    available supply and total buyer demand right now.

    congestion_level: 0.0 (no congestion) to 1.0 (fully congested)
    """
    base_price = compute_base_price()

    if block_supply_kWh <= 0:
        demand_ratio = 2.0  # no supply at all -> treat as high scarcity
    else:
        demand_ratio = block_demand_kWh / block_supply_kWh

    demand_supply_adjustment = (demand_ratio - 1) * SENSITIVITY_FACTOR
    congestion_adjustment = congestion_level * CONGESTION_WEIGHT

    price = base_price + demand_supply_adjustment + congestion_adjustment

    # Guarantee: always cheaper than grid retail, always better than feed-in tariff
    price = max(FEED_IN_TARIFF, min(price, GRID_RETAIL_RATE))
    return round(price, 2)


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------

def _buyer_priority_key(buyer: BuyRequest):
    """
    Sort key for buyers: outage first, then larger family size,
    then larger deficit (more urgent need).
    Python sorts ascending, so we negate booleans/numbers we want first/highest.
    """
    return (not buyer.is_outage, -buyer.family_size, -buyer.deficit_kWh)


def match_block(listings: List[Listing], buyers: List[BuyRequest],
                 block: str, congestion_level: float = 0.0) -> List[Trade]:
    """
    Match buyers to sellers within a single block.
    Returns list of Trade objects. Mutates listings/buyers in place
    (reduces available_kWh / deficit_kWh as trades are made).
    """
    block_listings = sorted(
        [l for l in listings if l.block == block and l.available_kWh > 0],
        key=lambda l: l.available_kWh  # smaller listings cleared first (fairness);
                                        # swap to price-based order if listings carry price
    )
    block_buyers = sorted(
        [b for b in buyers if b.block == block and b.deficit_kWh > 0],
        key=_buyer_priority_key
    )

    total_supply = sum(l.available_kWh for l in block_listings)
    total_demand = sum(b.deficit_kWh for b in block_buyers)
    price = compute_price(total_supply, total_demand, congestion_level)

    trades = []
    for buyer in block_buyers:
        for listing in block_listings:
            if buyer.deficit_kWh <= 0:
                break
            if listing.available_kWh <= 0:
                continue

            trade_kWh = min(listing.available_kWh, buyer.deficit_kWh)
            trades.append(Trade(
                seller_id=listing.house_id,
                buyer_id=buyer.house_id,
                kWh=round(trade_kWh, 2),
                price_per_kWh=price,
                total_price=round(trade_kWh * price, 2),
                cross_block=False,
                block=block,
            ))

            listing.available_kWh -= trade_kWh
            buyer.deficit_kWh -= trade_kWh

    return trades


def match_cross_block(listings: List[Listing], buyers: List[BuyRequest],
                       congestion_level: float = 0.0) -> List[Trade]:
    """
    For any buyers still with unmet deficit after in-block matching,
    match them against sellers in *other* blocks, at a small price penalty.
    """
    trades = []
    remaining_buyers = sorted(
        [b for b in buyers if b.deficit_kWh > 0],
        key=_buyer_priority_key
    )
    remaining_listings = sorted(
        [l for l in listings if l.available_kWh > 0],
        key=lambda l: l.available_kWh
    )

    for buyer in remaining_buyers:
        for listing in remaining_listings:
            if buyer.deficit_kWh <= 0:
                break
            if listing.available_kWh <= 0 or listing.block == buyer.block:
                continue

            total_supply = sum(l.available_kWh for l in remaining_listings)
            total_demand = sum(b.deficit_kWh for b in remaining_buyers)
            base = compute_price(total_supply, total_demand, congestion_level)
            price = round(min(base + CROSS_BLOCK_PENALTY, GRID_RETAIL_RATE), 2)

            trade_kWh = min(listing.available_kWh, buyer.deficit_kWh)
            trades.append(Trade(
                seller_id=listing.house_id,
                buyer_id=buyer.house_id,
                kWh=round(trade_kWh, 2),
                price_per_kWh=price,
                total_price=round(trade_kWh * price, 2),
                cross_block=True,
                block=f"{listing.block}->{buyer.block}",
            ))

            listing.available_kWh -= trade_kWh
            buyer.deficit_kWh -= trade_kWh

    return trades


def run_matching_round(listings: List[Listing], buyers: List[BuyRequest],
                        congestion_by_block: Optional[dict] = None) -> List[Trade]:
    """
    Full matching round across all blocks:
    1. Match within each block first (cheapest, most local trades).
    2. Any leftover buyer deficit gets matched cross-block.
    """
    congestion_by_block = congestion_by_block or {}
    all_trades = []

    blocks = sorted(set(l.block for l in listings) | set(b.block for b in buyers))
    for block in blocks:
        congestion = congestion_by_block.get(block, 0.0)
        all_trades.extend(match_block(listings, buyers, block, congestion))

    all_trades.extend(match_cross_block(listings, buyers))
    return all_trades


# ---------------------------------------------------------------------------
# Example usage / quick manual test
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    listings = [
        Listing(house_id="A1", block="A", available_kWh=3.2),
        Listing(house_id="A3", block="A", available_kWh=1.6),
        Listing(house_id="B1", block="B", available_kWh=4.0),
    ]
    buyers = [
        BuyRequest(house_id="A2", block="A", deficit_kWh=2.0, family_size=4, is_outage=True),
        BuyRequest(house_id="A4", block="A", deficit_kWh=3.5, family_size=2, is_outage=False),
        BuyRequest(house_id="C1", block="C", deficit_kWh=1.0, family_size=3, is_outage=False),
    ]

    trades = run_matching_round(listings, buyers, congestion_by_block={"A": 0.2})

    for t in trades:
        tag = " (cross-block)" if t.cross_block else ""
        print(f"{t.seller_id} -> {t.buyer_id}: {t.kWh} kWh @ ₹{t.price_per_kWh}/kWh "
              f"= ₹{t.total_price}{tag}")
