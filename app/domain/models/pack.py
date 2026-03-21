import uuid

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel


class Pack(BaseModel):
    __tablename__ = "packs"

    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    cover_image: Mapped[str] = mapped_column(String(500))
    duration_days: Mapped[int] = mapped_column(Integer)
    price_from: Mapped[float] = mapped_column(Numeric(10, 2))
    price_to: Mapped[float] = mapped_column(Numeric(10, 2))
    price_currency: Mapped[str] = mapped_column(String(3), default="EUR")
    featured: Mapped[bool] = mapped_column(Boolean, default=False)

    translations: Mapped[list["PackTranslation"]] = relationship(
        back_populates="pack", cascade="all, delete-orphan"
    )
    destinations: Mapped[list["Destination"]] = relationship(  # noqa: F821
        back_populates="pack",
        cascade="all, delete-orphan",
        order_by="Destination.display_order",
    )
    route_steps: Mapped[list["RouteStep"]] = relationship(  # noqa: F821
        back_populates="pack",
        cascade="all, delete-orphan",
        order_by="RouteStep.day",
    )


class PackTranslation(BaseModel):
    __tablename__ = "pack_translations"
    __table_args__ = (
        UniqueConstraint("pack_id", "locale", name="uq_pack_translation_locale"),
    )

    pack_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("packs.id", ondelete="CASCADE")
    )
    locale: Mapped[str] = mapped_column(String(5))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(2000))
    short_description: Mapped[str] = mapped_column(String(500))
    duration: Mapped[str] = mapped_column(String(50))

    pack: Mapped["Pack"] = relationship(back_populates="translations")
