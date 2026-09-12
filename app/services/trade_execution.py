"""
Trade execution.

v0 logic: given a listing + buyer + amount, this:
1. Validates the listing has enough available_kwh.
2. Creates a trade record (status starts "pending" -> "completed" since
   blockchain/smart-meter settlement is mocked for the hackathon).
3. Decrements the listing's available_kwh (marks it "matched"/"fulfilled"
   if fully consumed).

In a real deployment, "completed" would instead wait on a smart-meter
confirmation or a blockchain settlement callback.
"""
from fastapi import HTTPException
from app.database import get_supabase


def execute(listing_id: str, buyer_id: str, energy_kwh: float) -> dict:
    sb = get_supabase()

    listing_res = sb.table("listings").select("*").eq("id", listing_id).single().execute()
    listing = listing_res.data
    if not listing:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing["status"] != "open":
        raise HTTPException(status_code=400, detail="Listing is not open")
    if energy_kwh > listing["available_kwh"]:
        raise HTTPException(status_code=400, detail="Requested kWh exceeds availability")

    price_per_kwh = listing["price_per_kwh"]
    total_price = round(energy_kwh * price_per_kwh, 2)

    trade_payload = {
        "listing_id": listing_id,
        "buyer_id": buyer_id,
        "seller_id": listing["seller_id"],
        "energy_kwh": energy_kwh,
        "price_per_kwh": price_per_kwh,
        "total_price": total_price,
        "status": "completed",  # mocked instant settlement for the demo
    }
    trade_res = sb.table("trades").insert(trade_payload).execute()

    remaining = round(listing["available_kwh"] - energy_kwh, 2)
    new_status = "fulfilled" if remaining <= 0 else "open"
    sb.table("listings").update({
        "available_kwh": remaining,
        "status": new_status,
    }).eq("id", listing_id).execute()

    return trade_res.data[0]
