from fastapi import HTTPException, Request, status


def require_user(request: Request) -> str:
    """Require a bearer token until Supabase auth is wired into the API."""
    authorization = request.headers.get("Authorization", "")
    scheme, _, token = authorization.partition(" ")
    if scheme.lower() != "bearer" or not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="A bearer token is required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
