from pydantic import BaseModel


class SocietyResponse(BaseModel):
    id: str
    name: str
    area: str | None = None
    city: str | None = None
    solar_home_count: int
    kwh_available_total: float