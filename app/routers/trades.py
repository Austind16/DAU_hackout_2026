from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from app.auth import require_user
from app.database import get_supabase

router = APIRouter()


class TradeRequest(BaseModel):
    seller_house_id: str
    kwh: float


@router.post("")
def create_trade(payload: TradeRequest, user_id: str = Depends(require_user)):
    sb = get_supabase()  # service-role client, bypasses RLS for the write

    # ADJUST: column names below assume houses.id / houses.user_id as in the SQL patch
    buyer_house = (
        sb.table("houses").select("id").eq("user_id", user_id).single().execute()
    )
    if not buyer_house.data:
        raise HTTPException(404, "No house profile found for this user")
    buyer_house_id = buyer_house.data["id"]

    if buyer_house_id == payload.seller_house_id:
        raise HTTPException(400, "Cannot buy from your own house")

    # ADJUST: listings column names (house_id, status, kwh_available, price_per_kwh)
    listing = (
        sb.table("listings")
        .select("*")
        .eq("house_id", payload.seller_house_id)
        .eq("status", "active")
        .single()
        .execute()
    )
    if not listing.data:
        raise HTTPException(404, "No active listing for this house")

    available = listing.data["kwh_available"]
    price = listing.data["price_per_kwh"]

    if payload.kwh <= 0 or payload.kwh > available:
        raise HTTPException(400, "Requested amount exceeds available surplus")

    total = round(payload.kwh * price, 2)

    trade = (
        sb.table("trades")
        .insert(
            {
                "buyer_house_id": buyer_house_id,
                "seller_house_id": payload.seller_house_id,
                "kwh": payload.kwh,
                "price_per_kwh": price,
                "total_price": total,  # ADJUST: match your trades table's total column name
            }
        )
        .execute()
    )

    sb.table("listings").update({"kwh_available": available - payload.kwh}).eq(
        "id", listing.data["id"]
    ).execute()

    return {"status": "ok", "trade": trade.data[0] if trade.data else None}