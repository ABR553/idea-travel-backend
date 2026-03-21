from pydantic import BaseModel, Field


class ExperienceResponse(BaseModel):
    id: str
    title: str
    description: str
    provider: str
    affiliateUrl: str = Field(alias="affiliate_url")
    price: float
    currency: str
    duration: str
    image: str
    rating: float
    clicksLast24h: int = Field(0, alias="clicks_last_24h")

    model_config = {"populate_by_name": True}
