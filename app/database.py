"""
Supabase client setup.
Reads credentials from environment variables (see .env.example).
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_URL_KEY", "")
SUPABASE_SECRET_KEY = os.getenv("SUPABASE_SECRET_KEY") or os.getenv("SUPABASE_KEY") or os.getenv("PUBLISHABLE_KEY", "")
SUPABASE_PUBLISHABLE_KEY = os.getenv("SUPABASE_PUBLISHABLE_KEY") or os.getenv("PUBLISHABLE_KEY") or os.getenv("SUPABASE_KEY", "")

_client: Client | None = None


def get_supabase() -> Client:
    """Return a singleton Supabase client instance."""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_SECRET_KEY:
            raise RuntimeError("Supabase URL and backend key must be set in .env")
        _client = create_client(SUPABASE_URL, SUPABASE_SECRET_KEY)
    return _client


def get_supabase_auth() -> Client:
    """Return a client intended for user signup/login with the publishable key."""
    if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
        raise RuntimeError("SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY must be set in .env")
    return create_client(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY)


def get_supabase_for_token(access_token: str) -> Client:
    """Create a request-scoped client whose PostgREST calls carry a user JWT."""
    if not SUPABASE_URL or not SUPABASE_PUBLISHABLE_KEY:
        raise RuntimeError("Supabase credentials are not configured")
    client = create_client(SUPABASE_URL, SUPABASE_PUBLISHABLE_KEY)
    client.postgrest.auth(access_token)
    return client
