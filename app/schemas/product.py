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
    images: list[str] = []
    rating: float
    external_id: Optional[str] = None
    project_id: Optional[str] = None
    link: Optional[str] = None

    model_config = {"populate_by_name": True}


class ProductTranslationInput(BaseModel):
    locale: str
    name: str
    description: str


class ProductUpsertItem(BaseModel):
    external_id: str
    slug: str
    category: str
    price: float
    currency: str = "EUR"
    affiliate_url: str
    image: str
    rating: float
    images: list[str] = []
    translations: list[ProductTranslationInput] = []


class ProductBulkUpsertRequest(BaseModel):
    items: list[ProductUpsertItem]


class ProductBulkUpsertResponse(BaseModel):
    created: int
    updated: int
    items: list[ProductResponse]
