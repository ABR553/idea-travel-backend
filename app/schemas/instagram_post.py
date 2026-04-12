from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.domain.models.enums import (
    InstagramImageSource,
    InstagramPostAngle,
    InstagramPostFormat,
    InstagramPostLanguage,
    InstagramPostStatus,
)


class InstagramPostTranslationIn(BaseModel):
    locale: str
    hook: str
    caption: str
    cta: str | None = None
    first_comment: str | None = Field(default=None, alias="firstComment")
    engagement_hook: str | None = Field(default=None, alias="engagementHook")

    model_config = {"populate_by_name": True}


class InstagramPostTranslationOut(InstagramPostTranslationIn):
    pass


class InstagramPostSlideIn(BaseModel):
    order: int
    image_url: str = Field(alias="imageUrl")
    image_prompt: str | None = Field(default=None, alias="imagePrompt")
    image_source: InstagramImageSource = Field(alias="imageSource")
    alt_text: str | None = Field(default=None, alias="altText")
    overlay_text: str | None = Field(default=None, alias="overlayText")

    model_config = {"populate_by_name": True}


class InstagramPostSlideOut(InstagramPostSlideIn):
    pass


class InstagramPostBase(BaseModel):
    topic: str
    language: InstagramPostLanguage
    format: InstagramPostFormat
    slide_count: int = Field(alias="slideCount")
    hashtags: list[str] = Field(default_factory=list)
    mentions: list[str] = Field(default_factory=list)
    location_name: str | None = Field(default=None, alias="locationName")
    location_lat: Decimal | None = Field(default=None, alias="locationLat")
    location_lng: Decimal | None = Field(default=None, alias="locationLng")
    target_audience: str | None = Field(default=None, alias="targetAudience")
    post_angle: InstagramPostAngle | None = Field(default=None, alias="postAngle")
    best_publish_time: datetime | None = Field(default=None, alias="bestPublishTime")
    rationale: str | None = None
    source_mcp_refs: list[dict] = Field(default_factory=list, alias="sourceMcpRefs")

    model_config = {"populate_by_name": True}


class InstagramPostCreate(InstagramPostBase):
    translations: list[InstagramPostTranslationIn]
    slides: list[InstagramPostSlideIn]


class InstagramPostUpdate(BaseModel):
    topic: str | None = None
    language: InstagramPostLanguage | None = None
    format: InstagramPostFormat | None = None
    slide_count: int | None = Field(default=None, alias="slideCount")
    hashtags: list[str] | None = None
    mentions: list[str] | None = None
    location_name: str | None = Field(default=None, alias="locationName")
    location_lat: Decimal | None = Field(default=None, alias="locationLat")
    location_lng: Decimal | None = Field(default=None, alias="locationLng")
    target_audience: str | None = Field(default=None, alias="targetAudience")
    post_angle: InstagramPostAngle | None = Field(default=None, alias="postAngle")
    best_publish_time: datetime | None = Field(default=None, alias="bestPublishTime")
    rationale: str | None = None
    source_mcp_refs: list[dict] | None = Field(default=None, alias="sourceMcpRefs")
    translations: list[InstagramPostTranslationIn] | None = None
    slides: list[InstagramPostSlideIn] | None = None

    model_config = {"populate_by_name": True}


class InstagramPostResponse(InstagramPostBase):
    id: str
    status: InstagramPostStatus
    instagram_post_id: str | None = Field(default=None, alias="instagramPostId")
    publish_attempts: list[dict] = Field(default_factory=list, alias="publishAttempts")
    approved_at: datetime | None = Field(default=None, alias="approvedAt")
    published_at: datetime | None = Field(default=None, alias="publishedAt")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")
    translations: list[InstagramPostTranslationOut]
    slides: list[InstagramPostSlideOut]


class InstagramPostListItem(BaseModel):
    id: str
    topic: str
    status: InstagramPostStatus
    language: InstagramPostLanguage
    format: InstagramPostFormat
    slide_count: int = Field(alias="slideCount")
    first_slide_url: str | None = Field(default=None, alias="firstSlideUrl")
    created_at: datetime = Field(alias="createdAt")
    updated_at: datetime = Field(alias="updatedAt")

    model_config = {"populate_by_name": True}


class InstagramPostListResponse(BaseModel):
    items: list[InstagramPostListItem]
    total: int
    limit: int
    offset: int


class InstagramPostStatusChange(BaseModel):
    status: InstagramPostStatus


class InstagramPostPublishResponse(BaseModel):
    id: str
    status: InstagramPostStatus
    publish_attempts: list[dict] = Field(alias="publishAttempts")

    model_config = {"populate_by_name": True}
