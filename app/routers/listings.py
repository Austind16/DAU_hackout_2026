from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_user
from app.database import get_supabase
from app.schemas.listings import ListingCreate, ListingResponse

router = APIRouter()


@router.post("", response_model=ListingResponse)
def create_listing(payload: ListingCreate, user_id: str = Depends(require_user)):
    sb = get_supabase()

    # find the caller's own house
    house = (
        sb.table("houses")
        .select("house_id, has_solar_panels, has_solar")
        .eq("user_id", user_id)
        .single()
        .execute()
    )
    if not house.data:
        raise HTTPException(404, "No house profile found for this user")
    if not (house.data.get("has_solar_panels") or house.data.get("has_solar")):
        raise HTTPException(400, "This house has no solar panels on record")

    house_id = house.data["house_id"]

    reading = (
        sb.table("daily_readings")
        .select("energy_produced_kwh, energy_consumed_kwh")
        .eq("house_id", house_id)
        .order("date", desc=True)
        .limit(1)
        .execute()
    )
    if reading.data:
        surplus = reading.data[0]["energy_produced_kwh"] - reading.data[0]["energy_consumed_kwh"]
        if payload.available_kwh > surplus:
            raise HTTPException(
                400,
                f"Cannot list {payload.available_kwh} kWh — today's surplus is only {surplus} kWh",
            )

    # one open listing per house: close any existing open listing for this house
    existing = (
        sb.table("listings")
        .select("id")
        .eq("house_id", house_id)
        .eq("status", "open")
        .execute()
    )
    if existing.data:
        sb.table("listings").update({"status": "cancelled"}).eq(
            "id", existing.data[0]["id"]
        ).execute()

    result = (
        sb.table("listings")
        .insert(
            {
                "house_id": house_id,
                "date": date.today().isoformat(),
                "available_kwh": payload.available_kwh,
                "asking_price": payload.asking_price,
                "status": "open",
            }
        )
        .execute()
    )
    return result.data[0]


@router.patch("/{listing_id}/cancel")
def cancel_listing(listing_id: str, user_id: str = Depends(require_user)):
    sb = get_supabase()

    house = sb.table("houses").select("house_id").eq("user_id", user_id).single().execute()
    if not house.data:
        raise HTTPException(404, "No house profile found for this user")

    listing = sb.table("listings").select("house_id").eq("id", listing_id).single().execute()
    if not listing.data or listing.data["house_id"] != house.data["house_id"]:
        raise HTTPException(404, "Listing not found")

    sb.table("listings").update({"status": "cancelled"}).eq("id", listing_id).execute()
    return {"status": "ok"}