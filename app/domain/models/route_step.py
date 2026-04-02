import uuid
from typing import Optional

from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel


class RouteStep(BaseModel):
    __tablename__ = "route_steps"

    pack_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("packs.id", ondelete="CASCADE")
    )
    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE")
    )
    day: Mapped[int] = mapped_column(Integer)

    pack: Mapped["Pack"] = relationship(back_populates="route_steps")  # noqa: F821
    destination: Mapped["Destination"] = relationship()  # noqa: F821
    translations: Mapped[list["RouteStepTranslation"]] = relationship(
        back_populates="route_step", cascade="all, delete-orphan"
    )
    recommended_products: Mapped[list["RouteStepProduct"]] = relationship(
        back_populates="route_step", cascade="all, delete-orphan",
        order_by="RouteStepProduct.position",
    )


class RouteStepTranslation(BaseModel):
    __tablename__ = "route_step_translations"
    __table_args__ = (
        UniqueConstraint(
            "route_step_id", "locale", name="uq_route_step_translation_locale"
        ),
    )

    route_step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("route_steps.id", ondelete="CASCADE")
    )
    locale: Mapped[str] = mapped_column(String(5))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1000))
    detailed_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    route_step: Mapped["RouteStep"] = relationship(back_populates="translations")


class RouteStepProduct(BaseModel):
    __tablename__ = "route_step_products"
    __table_args__ = (
        UniqueConstraint(
            "route_step_id", "product_id", name="uq_route_step_product"
        ),
    )

    route_step_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("route_steps.id", ondelete="CASCADE")
    )
    product_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("products.id", ondelete="CASCADE")
    )
    position: Mapped[int] = mapped_column(Integer, default=0)
    context_text: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    route_step: Mapped["RouteStep"] = relationship(back_populates="recommended_products")
    product: Mapped["Product"] = relationship()  # noqa: F821
