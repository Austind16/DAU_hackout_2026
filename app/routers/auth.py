from fastapi import APIRouter

router = APIRouter()


@router.get("/auth/status")
def auth_status() -> dict[str, str]:
    return {"status": "configured"}
