from pydantic import BaseModel, Field


class AIGenerateRequest(BaseModel):
    description: str = Field(
        ..., min_length=10, max_length=2000,
        description="Descripcion libre del viaje que quieres generar",
    )


class AIAccommodation(BaseModel):
    tier: str = Field(..., description="budget, standard o premium")
    name_es: str
    name_en: str
    description_es: str
    description_en: str
    price_per_night: float
    currency: str = "EUR"
    amenities: list[str]
    rating: float = Field(..., ge=1.0, le=5.0)
    image: str
    nights: int = Field(..., ge=1)


class AIExperience(BaseModel):
    title_es: str
    title_en: str
    description_es: str
    description_en: str
    duration_es: str
    duration_en: str
    provider: str = Field(..., description="getyourguide o civitatis")
    price: float
    currency: str = "EUR"
    rating: float = Field(..., ge=1.0, le=5.0)
    image: str


class AIDestination(BaseModel):
    name_es: str
    name_en: str
    country_es: str
    country_en: str
    description_es: str
    description_en: str
    image: str
    days: int = Field(..., ge=1)
    accommodations: list[AIAccommodation]
    experiences: list[AIExperience]


class AIRouteStep(BaseModel):
    day: int = Field(..., ge=1)
    title_es: str
    title_en: str
    description_es: str
    description_en: str
    destination_name: str = Field(
        ..., description="Nombre del destino al que pertenece este paso (en espanol)",
    )


class AIPack(BaseModel):
    slug: str
    cover_image: str
    duration_days: int = Field(..., ge=1)
    price_from: float
    price_to: float
    featured: bool = False
    title_es: str
    title_en: str
    description_es: str
    description_en: str
    short_description_es: str
    short_description_en: str
    duration_es: str
    duration_en: str
    destinations: list[AIDestination]
    route_steps: list[AIRouteStep]


class AIBlogPost(BaseModel):
    slug: str
    cover_image: str
    category: str
    title_es: str
    title_en: str
    excerpt_es: str
    excerpt_en: str
    content_es: str = Field(..., description="Contenido completo en Markdown")
    content_en: str = Field(..., description="Full content in Markdown")


class AIGenerateResponse(BaseModel):
    pack: AIPack
    blog: AIBlogPost
