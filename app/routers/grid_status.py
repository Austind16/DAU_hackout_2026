from fastapi import APIRouter
from app.database import get_supabase
from app.models.schemas import GridStatusUpdate, GridStatus

router = APIRouter()

TABLE = "grid_status"


@router.get("/", response_model=list[GridStatus])
def list_grid_status():
    """Current grid state per block — powers the map's outage indicators."""
    sb = get_supabase()
    res = sb.table(TABLE).select("*").execute()
    return res.data


@router.post("/", response_model=GridStatus, status_code=201)
def update_grid_status(update: GridStatusUpdate):
    """
    Set/update the grid state for a block (normal / outage / degraded).
    In the demo this can be triggered manually to simulate an outage
    and show the marketplace kicking in.
    """
    sb = get_supabase()
    res = (
        sb.table(TABLE)
        .upsert({**update.model_dump()}, on_conflict="block")
        .execute()
    )
    return res.data[0]
