from fastapi import HTTPException, Request, status

from app.database import get_supabase


def require_user(request: Request) -> str:
    """Verify the bearer token against Supabase Auth and return the user's id."""
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A bearer token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )

    sb = get_supabase()
    try:
        result = sb.auth.get_user(token)
    except Exception:
        result = None

    if not result or not getattr(result, "user", None):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return result.user.id