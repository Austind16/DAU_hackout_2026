"""
Supabase client setup.
Reads credentials from environment variables (see .env.example).
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL") or os.getenv("SUPABASE_URL_KEY", "")
SUPABASE_KEY = os.getenv("SUPABASE_KEY") or os.getenv("PUBLISHABLE_KEY", "")

_client: Client | None = None


def get_supabase() -> Client:
    """Return a singleton Supabase client instance."""
    global _client
    if _client is None:
        if not SUPABASE_URL or not SUPABASE_KEY:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_KEY must be set in the environment (.env)"
            )
        _client = create_client(SUPABASE_URL, SUPABASE_KEY)
    return _client
