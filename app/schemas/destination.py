from pydantic import BaseModel

from app.schemas.accommodation import AccommodationResponse
from app.schemas.experience import ExperienceResponse


class DestinationResponse(BaseModel):
    name: str
    country: str
    description: str
    image: str
    days: int


class DestinationDetailResponse(DestinationResponse):
    accommodations: list[AccommodationResponse]
    experiences: list[ExperienceResponse]
