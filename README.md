# Hackout26 — P2P Energy Trading Marketplace (Backend Skeleton)

FastAPI backend for the society-based P2P renewable energy trading marketplace.

## Structure

```
app/
  main.py              # FastAPI app, router registration
  database.py          # Supabase client
  models/
    schemas.py         # Pydantic models: User, MeterReading, Listing, Trade, GridStatus
  routers/
    users.py           # /api/users
    meters.py          # /api/meters
    listings.py        # /api/listings
    trades.py          # /api/trades
    grid_status.py     # /api/grid-status
  services/
    pricing_engine.py     # suggests price/kWh based on grid state
    matching_engine.py     # greedy buyer<->seller matcher
    trade_execution.py    # validates + settles a trade (mocked instant settlement)
    forecasting.py        # Groq LLM call for next-day forecast / anomaly flag
supabase_schema.sql   # SQL to create the 5 core tables in Supabase
scripts/
  seed_from_csv.py    # loads house_info.csv + society_140_full_dataset.csv into Supabase
```

## Setup

1. Create a Supabase project, then run `supabase_schema.sql` in the SQL editor.
2. Copy `.env.example` to `.env` and fill in `SUPABASE_URL`, `SUPABASE_KEY`, `GROQ_API_KEY`.
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Seed the database with the 140-house demo dataset:
   ```
   python scripts/seed_from_csv.py --house-info house_info.csv --daily society_140_full_dataset.csv
   ```
5. Run the API:
   ```
   uvicorn app.main:app --reload --port 8000
   ```
6. Docs at `http://localhost:8000/docs` (FastAPI auto-generates Swagger UI).

## What's mocked for the hackathon

- **Blockchain / smart meters**: trades settle instantly in the DB (`trade_execution.py`)
  instead of waiting on a real settlement layer.
- **Forecasting**: uses a Groq-hosted LLM prompted to output a next-day estimate,
  rather than a trained numeric model — fast to build, good enough for a demo.

## Not yet wired up

- Supabase Auth / Row Level Security policies (currently open access via anon/service key).
- Supabase Realtime subscriptions for live listing/trade updates on the frontend.
- Any push notification for the "get on net metering" nudge or outage alerts.

## Next steps

- Point `society-energy-map.html` at these endpoints (start with `GET /api/users` and
  `GET /api/grid-status`).
- Add Supabase Auth so `/api/*` calls are scoped to the logged-in user.
- Wire `forecasting.py` into a scheduled or on-demand endpoint (e.g. `GET /api/users/{id}/forecast`).
