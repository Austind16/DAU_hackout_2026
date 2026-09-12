"""
Hackout26 - P2P Renewable Energy Trading Marketplace
Backend API entrypoint (FastAPI)
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import users, meters, listings, trades, grid_status

app = FastAPI(
    title="Hackout26 - P2P Energy Trading API",
    description="Society-based platform for households to trade rooftop solar surplus with neighbors.",
    version="0.1.0",
)

# CORS - open for hackathon demo purposes; tighten before any real deployment
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers - one per core entity from the data model
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(meters.router, prefix="/api/meters", tags=["meters"])
app.include_router(listings.router, prefix="/api/listings", tags=["listings"])
app.include_router(trades.router, prefix="/api/trades", tags=["trades"])
app.include_router(grid_status.router, prefix="/api/grid-status", tags=["grid_status"])


@app.get("/")
def root():
    return {"status": "ok", "service": "hackout26-p2p-energy-api"}


@app.get("/health")
def health():
    return {"status": "healthy"}
