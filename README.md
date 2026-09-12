# DAU Hackout 2026 API

FastAPI backend for the society-based P2P renewable energy trading marketplace.

## Layout

```text
app/
  main.py              # FastAPI application and router registration
  auth.py              # Request authentication boundary
  database.py          # Supabase client setup
  core/                # Shared configuration
  models/              # Persistence models
  schemas/             # Pydantic request and response schemas
  services/            # Business logic
  routers/             # Versionable API route modules
tests/                 # API tests
demo/                  # Static demo assets
```

## Run locally

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API is available at `http://127.0.0.1:8000`; interactive docs are at `/docs`.
Copy `.env.example` to `.env` and add Supabase credentials before using database-backed routes.
