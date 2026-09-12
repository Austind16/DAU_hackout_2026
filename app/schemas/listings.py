from pydantic import BaseModel, Field


class ListingCreate(BaseModel):
    kwh_available: float = Field(..., gt=0)
    price_per_kwh: float = Field(..., gt=0)


class ListingResponse(BaseModel):
    id: str
    house_id: str
    kwh_available: float
    price_per_kwh: float
    status: str