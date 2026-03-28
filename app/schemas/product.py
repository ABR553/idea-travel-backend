from typing import Optional

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
    external_id: Optional[str] = None
    project_id: Optional[str] = None
    link: Optional[str] = None

    model_config = {"populate_by_name": True}
