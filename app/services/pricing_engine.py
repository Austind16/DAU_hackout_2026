"""
Pricing engine — Supabase-backed adapter.

The actual pricing formula lives in pricing_matching_core.py (pure,
no DB dependency). This module's job is just to pull the current
block-level supply (open listings) and demand (buyer deficits) from
Supabase and hand them to that formula.
"""
from app.database import get_supabase
from app.services.pricing_matching_core import compute_price

GRID_STATE_CONGESTION = {
    "normal": 0.0,
    "degraded": 0.5,
    "outage": 1.0,
}


def _latest_reading_date(sb) -> str | None:
    res = (
        sb.table("meter_readings")
        .select("date")
        .order("date", desc=True)
        .limit(1)
        .execute()
    )
    return res.data[0]["date"] if res.data else None


def _block_supply_kwh(sb, block: str) -> float:
    res = sb.table("listings").select("available_kwh").eq("status", "open").eq("seller_block", block).execute()
    return sum(r["available_kwh"] for r in (res.data or []))


def _block_demand_kwh(sb, block: str) -> float:
    date = _latest_reading_date(sb)
    if date is None:
        return 0.0
    users_res = sb.table("users").select("id").eq("block", block).execute()
    user_ids = [u["id"] for u in (users_res.data or [])]
    if not user_ids:
        return 0.0
    readings_res = (
        sb.table("meter_readings")
        .select("grid_import_kwh")
        .eq("date", date)
        .in_("user_id", user_ids)
        .gt("grid_import_kwh", 0)
        .execute()
    )
    return sum(r["grid_import_kwh"] for r in (readings_res.data or []))


def _block_congestion(sb, block: str) -> float:
    res = sb.table("grid_status").select("state").eq("block", block).execute()
    state = res.data[0]["state"] if res.data else "normal"
    return GRID_STATE_CONGESTION.get(state, 0.0)


def suggest_price(block: str) -> float:
    """
    Live price/kWh for `block` right now, based on actual open supply,
    actual buyer deficit, and current grid congestion — via the formula
    in pricing_matching_core.compute_price.
    """
    sb = get_supabase()
    supply = _block_supply_kwh(sb, block)
    demand = _block_demand_kwh(sb, block)
    congestion = _block_congestion(sb, block)
    return compute_price(supply, demand, congestion)
