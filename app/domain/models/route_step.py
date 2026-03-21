import uuid

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
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

    route_step: Mapped["RouteStep"] = relationship(back_populates="translations")
