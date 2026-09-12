from pydantic import BaseModel


class SocietyResponse(BaseModel):
    """A 'society' here is really one block (A/B/C/D) of the dataset —
    there is no separate societies table in the real Supabase schema,
    so we group houses.block into a society-shaped response the
    frontend already expects."""

    id: str  # block letter, e.g. "A"
    name: str  # e.g. "Block A"
    area: str | None = None
    city: str | None = None
    solar_home_count: int
    kwh_available_total: float