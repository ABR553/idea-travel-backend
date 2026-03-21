from pydantic import BaseModel, Field


class AccommodationResponse(BaseModel):
    id: str
    name: str
    tier: str
    description: str
    pricePerNight: float = Field(alias="price_per_night")
    currency: str
    image: str
    amenities: list[str]
    rating: float
    bookingUrl: str | None = Field(None, alias="booking_url")
    nights: int
    clicksLast24h: int = Field(0, alias="clicks_last_24h")

    model_config = {"populate_by_name": True}
