from fastapi import APIRouter, Depends

from app.auth import require_user
from app.database import get_supabase
from app.schemas.societies import SocietyResponse

router = APIRouter()


@router.get("", response_model=list[SocietyResponse])
def list_societies(user_id: str = Depends(require_user)):
    sb = get_supabase()

    # ADJUST: assumes a `societies` table exists (id, name, area, city) — see the SQL
    # patch note below if it doesn't exist yet.
    societies = sb.table("societies").select("*").execute().data or []

    # ADJUST: assumes houses.society_id and listings.house_id/status/kwh_available
    houses = sb.table("houses").select("id, society_id, has_solar").execute().data or []
    active_listings = (
        sb.table("listings").select("house_id, kwh_available").eq("status", "active").execute().data or []
    )
    available_by_house = {l["house_id"]: l["kwh_available"] for l in active_listings}

    results = []
    for society in societies:
        society_houses = [h for h in houses if h.get("society_id") == society["id"]]
        solar_count = sum(1 for h in society_houses if h.get("has_solar"))
        total_available = sum(
            available_by_house.get(h["id"], 0) for h in society_houses
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