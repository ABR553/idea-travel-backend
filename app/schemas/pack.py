from pydantic import BaseModel, Field

from app.schemas.common import PriceRange
from app.schemas.destination import DestinationDetailResponse, DestinationResponse
from app.schemas.route_step import RouteStepResponse


class PackResponse(BaseModel):
    id: str
    slug: str
    title: str
    description: str
    shortDescription: str = Field(alias="short_description")
    destinations: list[DestinationDetailResponse]
    route: list[RouteStepResponse]
    coverImage: str = Field(alias="cover_image")
    duration: str
    durationDays: int = Field(alias="duration_days")
    price: PriceRange
    featured: bool

    model_config = {"populate_by_name": True}


class PackListResponse(BaseModel):
    id: str
    slug: str
    title: str
    shortDescription: str = Field(alias="short_description")
    destinations: list[DestinationResponse]
    coverImage: str = Field(alias="cover_image")
    duration: str
    durationDays: int = Field(alias="duration_days")
    price: PriceRange
    featured: bool

    model_config = {"populate_by_name": True}
