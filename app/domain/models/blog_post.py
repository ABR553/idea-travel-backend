from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel


class BlogPost(BaseModel):
    __tablename__ = "blog_posts"

    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    cover_image: Mapped[str] = mapped_column(String(500))
    category: Mapped[str] = mapped_column(String(50), index=True)
    published: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    published_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    related_pack_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("packs.id", ondelete="SET NULL"), nullable=True
    )

    translations: Mapped[list[BlogPostTranslation]] = relationship(
        back_populates="blog_post", cascade="all, delete-orphan"
    )
    related_pack = relationship("Pack", lazy="selectin")


class BlogPostTranslation(BaseModel):
    __tablename__ = "blog_post_translations"
    __table_args__ = (
        UniqueConstraint(
            "blog_post_id", "locale", name="uq_blog_post_translation_locale"
        ),
    )

    blog_post_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("blog_posts.id", ondelete="CASCADE")
    )
    locale: Mapped[str] = mapped_column(String(5))
    title: Mapped[str] = mapped_column(String(255))
    excerpt: Mapped[str] = mapped_column(String(500))
    content: Mapped[str] = mapped_column(Text)

    blog_post: Mapped[BlogPost] = relationship(back_populates="translations")
