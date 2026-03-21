from pydantic import BaseModel, Field


class ProductResponse(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    category: str
    price: float
    currency: str
    affiliateUrl: str = Field(alias="affiliate_url")
    image: str
    rating: float

    model_config = {"populate_by_name": True}
