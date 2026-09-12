from fastapi import APIRouter, Depends, HTTPException

from app.auth import require_user
from app.database import get_supabase
from app.schemas.listings import ListingCreate, ListingResponse

router = APIRouter()


@router.post("", response_model=ListingResponse)
def create_listing(payload: ListingCreate, user_id: str = Depends(require_user)):
    sb = get_supabase()

    # find the caller's own house
    house = sb.table("houses").select("id, has_solar").eq("user_id", user_id).single().execute()
    if not house.data:
        raise HTTPException(404, "No house profile found for this user")
    if not house.data.get("has_solar"):
        raise HTTPException(400, "This house has no solar panels on record")

    house_id = house.data["id"]

    # ADJUST: table/column names for daily_readings — assumed (house_id, production, consumption)
    # and that .order + .limit(1) gets the latest reading. Skips the check if no readings exist yet,
    # so this won't block your demo if daily_readings isn't seeded for this house.
    reading = (
        sb.table("daily_readings")
        .select("production, consumption")
        .eq("house_id", house_id)
        .order("reading_date", desc=True)  # ADJUST: your actual date/timestamp column
        .limit(1)
        .execute()
    )
    if reading.data:
        surplus = reading.data[0]["production"] - reading.data[0]["consumption"]
        if payload.kwh_available > surplus:
            raise HTTPException(
                400,
                f"Cannot list {payload.kwh_available} kWh — today's surplus is only {surplus} kWh",
            )

    # one active listing per house: replace any existing active listing for this house
    existing = (
        sb.table("listings")
        .select("id")
        .eq("house_id", house_id)
        .eq("status", "active")
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
                "kwh_available": payload.kwh_available,
                "price_per_kwh": payload.price_per_kwh,
                "status": "active",
            }
        )
        .execute()
    )
    return result.data[0]


@router.patch("/{listing_id}/cancel")
def cancel_listing(listing_id: str, user_id: str = Depends(require_user)):
    sb = get_supabase()

    house = sb.table("houses").select("id").eq("user_id", user_id).single().execute()
    if not house.data:
        raise HTTPException(404, "No house profile found for this user")

    listing = sb.table("listings").select("house_id").eq("id", listing_id).single().execute()
    if not listing.data or listing.data["house_id"] != house.data["id"]:
        raise HTTPException(404, "Listing not found")

    sb.table("listings").update({"status": "cancelled"}).eq("id", listing_id).execute()
    return {"status": "ok"}