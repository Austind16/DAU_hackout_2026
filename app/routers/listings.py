from fastapi import APIRouter, HTTPException
from app.database import get_supabase
from app.models.schemas import ListingCreate, Listing
from app.services import pricing_engine

router = APIRouter()

TABLE = "listings"


@router.get("/", response_model=list[Listing])
def list_listings(status: str | None = "open", block: str | None = None):
    sb = get_supabase()
    query = sb.table(TABLE).select("*")
    if status:
        query = query.eq("status", status)
    if block:
        query = query.eq("seller_block", block)
    res = query.execute()
    return res.data or []


@router.post("/", response_model=Listing, status_code=201)
def create_listing(listing: ListingCreate):
    """
    A seller (surplus household) posts available kWh.
    If no price_per_kwh override is meaningful, the pricing engine can
    suggest one via GET /api/listings/suggest-price first.
    seller_block is looked up from the seller's user record so the
    matching engine can filter by block without a join.
    """
    sb = get_supabase()
    seller_res = sb.table("users").select("block").eq("id", listing.seller_id).single().execute()
    if not seller_res.data:
        raise HTTPException(status_code=404, detail="Seller not found")
    payload = {
        **listing.model_dump(),
        "seller_block": seller_res.data["block"],
        "status": "open",
    }
    res = sb.table(TABLE).insert(payload).execute()
    return res.data[0]


@router.get("/suggest-price")
def suggest_price(block: str):
    """
    Ask the pricing engine for the current live price/kWh in `block`,
    based on actual open supply, actual buyer deficit, and grid congestion.
    """
    price = pricing_engine.suggest_price(block=block)
    return {"block": block, "suggested_price_per_kwh": price}


@router.delete("/{listing_id}", status_code=204)
def cancel_listing(listing_id: str):
    sb = get_supabase()
    res = sb.table(TABLE).update({"status": "cancelled"}).eq("id", listing_id).execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="Listing not found")
