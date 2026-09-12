from fastapi import APIRouter

router = APIRouter()


@router.get("/status")
def demo_status() -> dict[str, str]:
    return {"status": "ready"}
