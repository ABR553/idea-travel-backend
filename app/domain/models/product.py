import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Index, Integer, Numeric, String, UniqueConstraint, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel


class Product(BaseModel):
    __tablename__ = "products"
    __table_args__ = (
        Index(
            "uq_product_project_external_id",
            "project_id",
            "external_id",
            unique=True,
            postgresql_where=text("project_id IS NOT NULL AND external_id IS NOT NULL"),
        ),
    )

    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(20), index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    affiliate_url: Mapped[str] = mapped_column(String(500))
    image: Mapped[str] = mapped_column(String(500))
    rating: Mapped[float] = mapped_column(Numeric(2, 1))
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, default=None)
    project_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True, default=None
    )

    translations: Mapped[list["ProductTranslation"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    images: Mapped[list["ProductImage"]] = relationship(
        back_populates="product", cascade="all, delete-orphan", order_by="ProductImage.position"
    )
    project: Mapped[Optional["Project"]] = relationship(  # type: ignore[name-defined]
        back_populates="products"
    )


class ProductTranslation(BaseModel):
    __tablename__ = "product_translations"
    __table_args__ = (
        UniqueConstraint(
            "product_id", "locale", name="uq_product_translation_locale"
        ),
    )

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE")
    )
    locale: Mapped[str] = mapped_column(String(5))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(2000))

    product: Mapped["Product"] = relationship(back_populates="translations")


class ProductImage(BaseModel):
    __tablename__ = "product_images"

    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE")
    )
    url: Mapped[str] = mapped_column(String(500))
    position: Mapped[int] = mapped_column(Integer, default=0)

    product: Mapped["Product"] = relationship(back_populates="images")
