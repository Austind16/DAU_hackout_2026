from fastapi import APIRouter
from app.database import get_supabase
from app.models.schemas import MeterReadingCreate, MeterReading

router = APIRouter()

TABLE = "meter_readings"


@router.get("/", response_model=list[MeterReading])
def list_readings(user_id: str | None = None, date: str | None = None):
    sb = get_supabase()
    query = sb.table(TABLE).select("*")
    if user_id:
        query = query.eq("user_id", user_id)
    if date:
        query = query.eq("date", date)
    res = query.execute()
    return res.data


@router.post("/", response_model=MeterReading, status_code=201)
def create_reading(reading: MeterReadingCreate):
    """
    Ingest a single meter reading (one row per user per day).
    In the demo this is how the 140-house CSV gets loaded in, and later
    could be replaced by a real smart-meter feed.
    """
    sb = get_supabase()
    res = sb.table(TABLE).insert(reading.model_dump()).execute()
    return res.data[0]


@router.post("/bulk", status_code=201)
def bulk_create_readings(readings: list[MeterReadingCreate]):
    """Bulk-insert meter readings — used for seeding the CSV dataset."""
    sb = get_supabase()
    payload = [r.model_dump() for r in readings]
    res = sb.table(TABLE).insert(payload).execute()
    return {"inserted": len(res.data)}
