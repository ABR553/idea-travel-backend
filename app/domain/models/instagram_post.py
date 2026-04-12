from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    Numeric,
    SmallInteger,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel
from app.domain.models.enums import (
    InstagramImageSource,
    InstagramPostAngle,
    InstagramPostFormat,
    InstagramPostLanguage,
    InstagramPostStatus,
)


class InstagramPost(BaseModel):
    __tablename__ = "instagram_posts"
    __table_args__ = (
        CheckConstraint("slide_count BETWEEN 1 AND 10", name="ck_instagram_post_slide_count"),
    )

    topic: Mapped[str] = mapped_column(String(255), nullable=False)
    source_mcp_refs: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    language: Mapped[InstagramPostLanguage] = mapped_column(
        SAEnum(InstagramPostLanguage, name="instagram_post_language"), nullable=False
    )
    status: Mapped[InstagramPostStatus] = mapped_column(
        SAEnum(InstagramPostStatus, name="instagram_post_status"),
        nullable=False,
        default=InstagramPostStatus.DRAFT,
        index=True,
    )
    format: Mapped[InstagramPostFormat] = mapped_column(
        SAEnum(InstagramPostFormat, name="instagram_post_format"), nullable=False
    )
    slide_count: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    hashtags: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    mentions: Mapped[list[str]] = mapped_column(ARRAY(String), nullable=False, default=list)
    location_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    location_lat: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    location_lng: Mapped[Decimal | None] = mapped_column(Numeric(9, 6), nullable=True)
    target_audience: Mapped[str | None] = mapped_column(Text, nullable=True)
    post_angle: Mapped[InstagramPostAngle | None] = mapped_column(
        SAEnum(InstagramPostAngle, name="instagram_post_angle"), nullable=True
    )
    best_publish_time: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    rationale: Mapped[str | None] = mapped_column(Text, nullable=True)
    instagram_post_id: Mapped[str | None] = mapped_column(String(64), nullable=True)
    publish_attempts: Mapped[list] = mapped_column(JSONB, nullable=False, default=list)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    translations: Mapped[list[InstagramPostTranslation]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
    slides: Mapped[list[InstagramPostSlide]] = relationship(
        back_populates="post",
        cascade="all, delete-orphan",
        order_by="InstagramPostSlide.order",
    )


class InstagramPostTranslation(BaseModel):
    __tablename__ = "instagram_post_translations"
    __table_args__ = (
        UniqueConstraint(
            "instagram_post_id", "locale", name="uq_instagram_post_translation_locale"
        ),
    )

    instagram_post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("instagram_posts.id", ondelete="CASCADE"),
        nullable=False,
    )
    locale: Mapped[str] = mapped_column(String(2), nullable=False)
    hook: Mapped[str] = mapped_column(Text, nullable=False)
    caption: Mapped[str] = mapped_column(Text, nullable=False)
    cta: Mapped[str | None] = mapped_column(Text, nullable=True)
    first_comment: Mapped[str | None] = mapped_column(Text, nullable=True)
    engagement_hook: Mapped[str | None] = mapped_column(Text, nullable=True)

    post: Mapped[InstagramPost] = relationship(back_populates="translations")


class InstagramPostSlide(BaseModel):
    __tablename__ = "instagram_post_slides"
    __table_args__ = (
        UniqueConstraint(
            "instagram_post_id", "order", name="uq_instagram_post_slide_order"
        ),
    )

    instagram_post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("instagram_posts.id", ondelete="CASCADE"),
        nullable=False,
    )
    order: Mapped[int] = mapped_column(SmallInteger, nullable=False)
    image_url: Mapped[str] = mapped_column(String(1024), nullable=False)
    image_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_source: Mapped[InstagramImageSource] = mapped_column(
        SAEnum(InstagramImageSource, name="instagram_image_source"), nullable=False
    )
    alt_text: Mapped[str | None] = mapped_column(String(255), nullable=True)
    overlay_text: Mapped[str | None] = mapped_column(String(255), nullable=True)

    post: Mapped[InstagramPost] = relationship(back_populates="slides")
