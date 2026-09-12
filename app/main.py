"""
Hackout26 - P2P Renewable Energy Trading Marketplace
Backend API entrypoint (FastAPI)
"""
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.routers import users, meters, listings, trades, grid_status, demo, auth, societies
from app.auth import require_user

app = FastAPI(
    title="Hackout26 - P2P Energy Trading API",
    description="Society-based platform for households to trade rooftop solar surplus with neighbors.",
    version="0.1.0",
)

DEMO_DIR = Path(__file__).resolve().parent.parent / "demo"
app.mount("/demo", StaticFiles(directory=DEMO_DIR, html=True), name="demo")

# CORS - open for hackathon demo purposes; tighten before any real deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers - one per core entity from the data model
auth_dependencies = [Depends(require_user)]
app.include_router(users.router, prefix="/api/users", tags=["users"], dependencies=auth_dependencies)
app.include_router(meters.router, prefix="/api/meters", tags=["meters"], dependencies=auth_dependencies)
app.include_router(listings.router, prefix="/api/listings", tags=["listings"], dependencies=auth_dependencies)
app.include_router(trades.router, prefix="/api/trades", tags=["trades"], dependencies=auth_dependencies)
app.include_router(grid_status.router, prefix="/api/grid-status", tags=["grid_status"], dependencies=auth_dependencies)
app.include_router(societies.router, prefix="/api/societies", tags=["societies"], dependencies=auth_dependencies)
app.include_router(demo.router, prefix="/api/demo", tags=["demo"])
app.include_router(auth.router, prefix="/api")


@app.get("/")
def root():
    return {"status": "ok", "service": "hackout26-p2p-energy-api"}


@app.get("/health")
def health():
    return {"status": "healthy"}