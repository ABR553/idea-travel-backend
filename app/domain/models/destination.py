import uuid

from sqlalchemy import ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel


class Destination(BaseModel):
    __tablename__ = "destinations"

    pack_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("packs.id", ondelete="CASCADE")
    )
    image: Mapped[str] = mapped_column(String(500))
    display_order: Mapped[int] = mapped_column(Integer, default=0)
    days: Mapped[int] = mapped_column(Integer, default=1)

    pack: Mapped["Pack"] = relationship(back_populates="destinations")  # noqa: F821
    translations: Mapped[list["DestinationTranslation"]] = relationship(
        back_populates="destination", cascade="all, delete-orphan"
    )
    accommodations: Mapped[list["Accommodation"]] = relationship(  # noqa: F821
        back_populates="destination", cascade="all, delete-orphan"
    )
    experiences: Mapped[list["Experience"]] = relationship(  # noqa: F821
        back_populates="destination", cascade="all, delete-orphan"
    )


class DestinationTranslation(BaseModel):
    __tablename__ = "destination_translations"
    __table_args__ = (
        UniqueConstraint(
            "destination_id", "locale", name="uq_destination_translation_locale"
        ),
    )

    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE")
    )
    locale: Mapped[str] = mapped_column(String(5))
    name: Mapped[str] = mapped_column(String(255))
    country: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1000))

    destination: Mapped["Destination"] = relationship(back_populates="translations")
