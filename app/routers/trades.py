from fastapi import APIRouter
from app.models.schemas import Trade
from app.services import matching_engine, trade_execution

router = APIRouter()


@router.post("/match-block/{block}")
def match_block(block: str):
    """
    Run one matching pass within `block` only: sellers ordered smallest-
    listing-first (fairness — every trade in this round shares one
    block-uniform price, so size order rather than price order is what
    matters), buyers ordered outage-first > larger-family-first > larger-
    deficit-first. No cross-block fallback — use /match-round for that.
    """
    return matching_engine.match_trades(block=block)


@router.post("/match-round")
def match_round():
    """
    Run a full network-wide matching round: in-block matching for every
    block first, then any leftover buyer deficit gets matched against
    sellers in other blocks (at a small cross-block price penalty).
    """
    return matching_engine.match_full_round()


@router.post("/execute", response_model=Trade, status_code=201)
def execute_trade(listing_id: str, buyer_id: str, energy_kwh: float):
    """Confirm and execute a trade against a specific listing."""
    trade = trade_execution.execute(listing_id=listing_id, buyer_id=buyer_id, energy_kwh=energy_kwh)
    return trade


@router.get("/", response_model=list[Trade])
def list_trades(user_id: str | None = None):
    from app.database import get_supabase
    sb = get_supabase()
    query = sb.table("trades").select("*")
    if user_id:
        # trades where the user is either buyer or seller
        query = query.or_(f"buyer_id.eq.{user_id},seller_id.eq.{user_id}")
    res = query.execute()
    return res.data
