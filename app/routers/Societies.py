from fastapi import APIRouter, Depends

from app.auth import require_user
from app.database import get_supabase
from app.schemas.Societies import SocietyResponse

router = APIRouter()


@router.get("", response_model=list[SocietyResponse])
def list_societies(user_id: str = Depends(require_user)):
    """There is no `societies` table in the real schema — houses are
    grouped by `houses.block` (a plain text column like 'A'/'B'/'C'/'D')
    instead. This groups by block and shapes the response the same way
    the frontend's society picker already expects.
    """
    sb = get_supabase()
    houses = (
        sb.table("houses")
        .select("house_id, block, area, city, has_solar_panels, has_solar")
        .execute()
        .data
        or []
    )
    open_listings = (
        sb.table("listings")
        .select("house_id, available_kwh")
        .eq("status", "open")
        .execute()
        .data
        or []
    )
    available_by_house = {}
    for listing in open_listings:
        available_by_house[listing["house_id"]] = (
            available_by_house.get(listing["house_id"], 0) + (listing["available_kwh"] or 0)
        )

    blocks: dict[str, dict] = {}
    for house in houses:
        block = house.get("block")
        if not block:
            continue
        entry = blocks.setdefault(
            block,
            {"houses": [], "area": house.get("area"), "city": house.get("city")},
        )
        entry["houses"].append(house)
        # backfill area/city from any house that has them set
        entry["area"] = entry["area"] or house.get("area")
        entry["city"] = entry["city"] or house.get("city")

    results = []
    for block, info in sorted(blocks.items()):
        block_houses = info["houses"]
        # has_solar_panels is the dataset-generated field; has_solar is
        # the (often null) self-reported field from the inquiry flow —
        # prefer whichever is set.
        solar_count = sum(
            1 for h in block_houses if h.get("has_solar_panels") or h.get("has_solar")
        )
        total_available = sum(
            available_by_house.get(h["house_id"], 0) for h in block_houses
        )
        results.append(
            {
                "id": block,
                "name": f"Block {block}",
                "area": info["area"],
                "city": info["city"],
                "solar_home_count": solar_count,
                "kwh_available_total": round(total_available, 1),
            }
        )
    return results