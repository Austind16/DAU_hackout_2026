"""
Matching engine — Supabase-backed adapter around pricing_matching_core.py.

Flow:
  1. Load open listings + buyer deficits from Supabase for the relevant
     block(s), converting each into the core's Listing / BuyRequest
     dataclasses.
  2. Run the pure in-memory algorithm (match_block or run_matching_round)
     from pricing_matching_core — this does zero I/O and is where all the
     actual pricing/matching logic lives.
  3. Persist the resulting Trade objects to the `trades` table and write
     back each listing's final available_kWh.

house_id on a Listing is the listing's own row id (not the seller's user
id) so it stays unique even if a seller has multiple open listings;
`_seller_by_listing` maps back to the actual seller user id when persisting.
"""
from app.database import get_supabase
from app.services.pricing_matching_core import (
    Listing,
    BuyRequest,
    Trade,
    match_block as _core_match_block,
    run_matching_round as _core_run_matching_round,
)
from app.services.pricing_engine import GRID_STATE_CONGESTION, _latest_reading_date


def _load_listings(sb, block: str | None = None) -> tuple[list[Listing], dict[str, str]]:
    """Returns (core Listing objects, {listing_id: seller_user_id})."""
    query = sb.table("listings").select("*").eq("status", "open")
    if block:
        query = query.eq("seller_block", block)
    rows = query.execute().data or []

    listings = [
        Listing(house_id=r["id"], block=r["seller_block"], available_kWh=r["available_kwh"])
        for r in rows
    ]
    seller_by_listing = {r["id"]: r["seller_id"] for r in rows}
    return listings, seller_by_listing


def _load_buyers(sb, block: str | None = None) -> list[BuyRequest]:
    """
    Buyers = households with grid_import_kwh > 0 on the latest reading date.
    family_size comes from users; is_outage is derived from that user's
    block's current grid_status.
    """
    date = _latest_reading_date(sb)
    if date is None:
        return []

    users_query = sb.table("users").select("id, block, family_size")
    if block:
        users_query = users_query.eq("block", block)
    users = users_query.execute().data or []
    users_by_id = {u["id"]: u for u in users}
    if not users_by_id:
        return []

    grid_res = sb.table("grid_status").select("block, state").execute()
    outage_blocks = {g["block"] for g in (grid_res.data or []) if g["state"] == "outage"}

    readings = (
        sb.table("meter_readings")
        .select("user_id, grid_import_kwh")
        .eq("date", date)
        .in_("user_id", list(users_by_id.keys()))
        .gt("grid_import_kwh", 0)
        .execute()
        .data or []
    )

    buyers = []
    for r in readings:
        u = users_by_id[r["user_id"]]
        buyers.append(BuyRequest(
            house_id=r["user_id"],
            block=u["block"],
            deficit_kWh=r["grid_import_kwh"],
            family_size=u.get("family_size", 1),
            is_outage=u["block"] in outage_blocks,
        ))
    return buyers


def _congestion_by_block(sb) -> dict[str, float]:
    res = sb.table("grid_status").select("block, state").execute()
    return {
        g["block"]: GRID_STATE_CONGESTION.get(g["state"], 0.0)
        for g in (res.data or [])
    }


def _persist_trades(sb, trades: list[Trade], seller_by_listing: dict[str, str]) -> list[dict]:
    """
    Insert each Trade as a row in `trades`. seller_id on the Trade is the
    listing_id (see _load_listings), so we look up the real seller
    user id via seller_by_listing.
    """
    inserted = []
    for t in trades:
        listing_id = t.seller_id
        seller_user_id = seller_by_listing.get(listing_id)
        payload = {
            "listing_id": listing_id,
            "buyer_id": t.buyer_id,
            "seller_id": seller_user_id,
            "energy_kwh": t.kWh,
            "price_per_kwh": t.price_per_kWh,
            "total_price": t.total_price,
            "status": "completed",  # mocked instant settlement, per hackathon scope
        }
        res = sb.table("trades").insert(payload).execute()
        inserted.append(res.data[0])
    return inserted


def _persist_listing_levels(sb, listings: list[Listing]):
    """Write back each listing's final available_kWh after matching."""
    for l in listings:
        new_status = "fulfilled" if l.available_kWh <= 0 else "open"
        sb.table("listings").update({
            "available_kwh": round(l.available_kWh, 2),
            "status": new_status,
        }).eq("id", l.house_id).execute()


def match_trades(block: str) -> dict:
    """Run one matching pass scoped to a single block (no cross-block fallback)."""
    sb = get_supabase()
    listings, seller_by_listing = _load_listings(sb, block=block)
    buyers = _load_buyers(sb, block=block)
    congestion = _congestion_by_block(sb).get(block, 0.0)

    trades = _core_match_block(listings, buyers, block=block, congestion_level=congestion)

    _persist_trades(sb, trades, seller_by_listing)
    _persist_listing_levels(sb, listings)

    unfulfilled = [
        {"user_id": b.house_id, "block": b.block, "unfulfilled_kWh": round(b.deficit_kWh, 2)}
        for b in buyers if b.deficit_kWh > 0
    ]

    return {
        "block": block,
        "trades_created": len(trades),
        "trades": [t.__dict__ for t in trades],
        "unfulfilled_buyers": unfulfilled,
    }


def match_full_round() -> dict:
    """
    Run a full network-wide matching round: in-block matching for every
    block first, then cross-block fallback for anyone still short.
    """
    sb = get_supabase()
    listings, seller_by_listing = _load_listings(sb)  # all blocks
    buyers = _load_buyers(sb)  # all blocks
    congestion_by_block = _congestion_by_block(sb)

    trades = _core_run_matching_round(listings, buyers, congestion_by_block=congestion_by_block)

    _persist_trades(sb, trades, seller_by_listing)
    _persist_listing_levels(sb, listings)

    unfulfilled = [
        {"user_id": b.house_id, "block": b.block, "unfulfilled_kWh": round(b.deficit_kWh, 2)}
        for b in buyers if b.deficit_kWh > 0
    ]

    return {
        "trades_created": len(trades),
        "cross_block_trades": sum(1 for t in trades if t.cross_block),
        "trades": [t.__dict__ for t in trades],
        "unfulfilled_buyers": unfulfilled,
    }
