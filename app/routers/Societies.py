from fastapi import APIRouter, Depends

from app.auth import require_user
from app.database import get_supabase
from app.schemas.Societies import SocietyResponse

router = APIRouter()


@router.get("", response_model=list[SocietyResponse])
def list_societies(user_id: str = Depends(require_user)):
    sb = get_supabase()
    societies = sb.table("societies").select("*").execute().data or []
    houses = sb.table("houses").select("id, society_id, has_solar").execute().data or []
    active_listings = (
        sb.table("listings")
        .select("house_id, kwh_available")
        .eq("status", "active")
        .execute()
        .data
        or []
    )
    available_by_house = {listing["house_id"]: listing["kwh_available"] for listing in active_listings}

    results = []
    for society in societies:
        society_houses = [house for house in houses if house.get("society_id") == society["id"]]
        solar_count = sum(1 for house in society_houses if house.get("has_solar"))
        total_available = sum(
            available_by_house.get(house["id"], 0) for house in society_houses
        )
        results.append(
            {
                "id": society["id"],
                "name": society["name"],
                "area": society.get("area"),
                "city": society.get("city"),
                "solar_home_count": solar_count,
                "kwh_available_total": round(total_available, 1),
            }
        )
    return results