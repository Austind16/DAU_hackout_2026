from datetime import date

from pydantic import BaseModel, Field


class ListingCreate(BaseModel):
    available_kwh: float = Field(..., gt=0)
    asking_price: float = Field(..., gt=0)


class ListingResponse(BaseModel):
    id: str
    house_id: str
    date: date
    available_kwh: float
    asking_price: float
    status: str