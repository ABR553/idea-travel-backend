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


class InstagramPostStatus(str, Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    REJECTED = "rejected"


class InstagramPostFormat(str, Enum):
    SINGLE_IMAGE = "single_image"
    CAROUSEL = "carousel"


class InstagramPostLanguage(str, Enum):
    ES = "es"
    EN = "en"
    BILINGUAL = "bilingual"


class InstagramImageSource(str, Enum):
    AI_GENERATED = "ai_generated"
    STOCK = "stock"
    MCP_ASSET = "mcp_asset"
    USER_UPLOAD = "user_upload"


class InstagramPostAngle(str, Enum):
    INSPIRATIONAL = "inspirational"
    PRACTICAL_TIP = "practical_tip"
    LIST = "list"
    STORYTELLING = "storytelling"
