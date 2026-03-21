import uuid

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel


class Product(BaseModel):
    __tablename__ = "products"

    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    category: Mapped[str] = mapped_column(String(20), index=True)
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    affiliate_url: Mapped[str] = mapped_column(String(500))
    image: Mapped[str] = mapped_column(String(500))
    rating: Mapped[float] = mapped_column(Numeric(2, 1))

    translations: Mapped[list["ProductTranslation"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
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
