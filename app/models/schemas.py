"""
Pydantic models mirroring the Supabase data model:
users, meters, listings, trades, grid_status
"""
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


# ---------- Enums ----------

class NetMeteringStatus(str, Enum):
    active = "Active"
    pending = "Pending"
    not_applied = "Not Applied"
    not_applicable = "Not Applicable"


class ListingStatus(str, Enum):
    open = "open"
    matched = "matched"
    fulfilled = "fulfilled"
    cancelled = "cancelled"


class TradeStatus(str, Enum):
    pending = "pending"
    confirmed = "confirmed"
    completed = "completed"
    failed = "failed"


class GridState(str, Enum):
    normal = "normal"
    outage = "outage"
    degraded = "degraded"


# ---------- Users ----------

class UserBase(BaseModel):
    owner_name: str
    block: str
    flat_no: str
    family_size: int
    has_solar_panels: bool = False
    panel_capacity_kw: float = 0.0
    panel_brand: Optional[str] = None
    net_metering_status: NetMeteringStatus = NetMeteringStatus.not_applicable


class UserCreate(UserBase):
    pass


class User(UserBase):
    id: str
    created_at: Optional[datetime] = None


# ---------- Meters ----------

class MeterReadingCreate(BaseModel):
    user_id: str
    date: str  # YYYY-MM-DD
    sunlight_hours: float = 0.0
    energy_produced_kwh: float = 0.0
    energy_consumed_kwh: float = 0.0
    excess_power_kwh: float = 0.0
    grid_import_kwh: float = 0.0


class MeterReading(MeterReadingCreate):
    id: str
    created_at: Optional[datetime] = None


# ---------- Listings (a seller offering surplus power) ----------

class ListingCreate(BaseModel):
    seller_id: str
    available_kwh: float = Field(..., gt=0)
    price_per_kwh: float = Field(..., gt=0)
    valid_until: Optional[datetime] = None


class Listing(ListingCreate):
    id: str
    seller_block: str
    status: ListingStatus = ListingStatus.open
    created_at: Optional[datetime] = None


# ---------- Trades ----------

class TradeCreate(BaseModel):
    listing_id: str
    buyer_id: str
    seller_id: str
    energy_kwh: float = Field(..., gt=0)
    price_per_kwh: float
    total_price: float


class Trade(TradeCreate):
    id: str
    status: TradeStatus = TradeStatus.pending
    created_at: Optional[datetime] = None


# ---------- Grid status ----------

class GridStatusUpdate(BaseModel):
    block: str
    state: GridState
    note: Optional[str] = None


class GridStatus(GridStatusUpdate):
    id: str
    updated_at: Optional[datetime] = None
