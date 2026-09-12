from fastapi import APIRouter, HTTPException
from app.database import get_supabase
from app.models.schemas import UserCreate, User

router = APIRouter()

TABLE = "users"


@router.get("/", response_model=list[User])
def list_users(block: str | None = None, has_solar: bool | None = None):
    sb = get_supabase()
    query = sb.table(TABLE).select("*")
    if block:
        query = query.eq("block", block)
    if has_solar is not None:
        query = query.eq("has_solar_panels", has_solar)
    res = query.execute()
    return res.data


@router.get("/{user_id}", response_model=User)
def get_user(user_id: str):
    sb = get_supabase()
    res = sb.table(TABLE).select("*").eq("id", user_id).single().execute()
    if not res.data:
        raise HTTPException(status_code=404, detail="User not found")
    return res.data


@router.post("/", response_model=User, status_code=201)
def create_user(user: UserCreate):
    sb = get_supabase()
    res = sb.table(TABLE).insert(user.model_dump()).execute()
    return res.data[0]


@router.get("/{user_id}/summary")
def user_energy_summary(user_id: str):
    """
    Aggregate a user's production/consumption/excess totals from meter_readings.
    Useful for the dashboard and for the pricing/matching engines.
    """
    sb = get_supabase()
    res = sb.table("meter_readings").select("*").eq("user_id", user_id).execute()
    readings = res.data or []
    return {
        "user_id": user_id,
        "days_recorded": len(readings),
        "total_produced_kwh": sum(r["energy_produced_kwh"] for r in readings),
        "total_consumed_kwh": sum(r["energy_consumed_kwh"] for r in readings),
        "total_excess_kwh": sum(r["excess_power_kwh"] for r in readings),
        "total_grid_import_kwh": sum(r["grid_import_kwh"] for r in readings),
    }
