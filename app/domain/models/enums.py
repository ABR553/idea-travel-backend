from enum import Enum


class AccommodationTier(str, Enum):
    BUDGET = "budget"
    STANDARD = "standard"
    PREMIUM = "premium"


class ExperienceProvider(str, Enum):
    GETYOURGUIDE = "getyourguide"
    CIVITATIS = "civitatis"


class ProductCategory(str, Enum):
    LUGGAGE = "luggage"
    ELECTRONICS = "electronics"
    ACCESSORIES = "accessories"
    COMFORT = "comfort"
    PHOTOGRAPHY = "photography"
