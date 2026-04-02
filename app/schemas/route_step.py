from pydantic import BaseModel, Field


# ── Request schemas (admin) ──────────────────────────────────────────────────


class RouteProductLinkRequest(BaseModel):
    product_slug: str
    position: int = 0
    context_text: str | None = None


class RouteStepEnrichItem(BaseModel):
    day: int
    products: list[RouteProductLinkRequest] = []
    detailed_description_es: str | None = None
    detailed_description_en: str | None = None


class EnrichRoutesRequest(BaseModel):
    steps: list[RouteStepEnrichItem]


# ── Response schemas ─────────────────────────────────────────────────────────


class RecommendedProductResponse(BaseModel):
    slug: str
    name: str
    image: str
    price: float
    currency: str
    affiliateUrl: str = Field(alias="affiliate_url")
    contextText: str | None = Field(alias="context_text", default=None)

    model_config = {"populate_by_name": True}


class RouteStepResponse(BaseModel):
    day: int
    title: str
    description: str
    destination: str
    detailedDescription: str | None = Field(
        alias="detailed_description", default=None
    )
    recommendedProducts: list[RecommendedProductResponse] = Field(
        alias="recommended_products", default_factory=list
    )

    model_config = {"populate_by_name": True}
