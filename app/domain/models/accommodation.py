import uuid

from sqlalchemy import ForeignKey, Integer, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel


class Accommodation(BaseModel):
    __tablename__ = "accommodations"

    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE")
    )
    tier: Mapped[str] = mapped_column(String(20))  # budget, standard, premium
    price_per_night: Mapped[float] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    image: Mapped[str] = mapped_column(String(500))
    amenities: Mapped[list] = mapped_column(JSONB, default=list)
    rating: Mapped[float] = mapped_column(Numeric(2, 1))
    booking_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    nights: Mapped[int] = mapped_column(Integer, default=1)

    destination: Mapped["Destination"] = relationship(  # noqa: F821
        back_populates="accommodations"
    )
    translations: Mapped[list["AccommodationTranslation"]] = relationship(
        back_populates="accommodation", cascade="all, delete-orphan"
    )


class AccommodationTranslation(BaseModel):
    __tablename__ = "accommodation_translations"
    __table_args__ = (
        UniqueConstraint(
            "accommodation_id", "locale", name="uq_accommodation_translation_locale"
        ),
    )

    accommodation_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("accommodations.id", ondelete="CASCADE")
    )
    locale: Mapped[str] = mapped_column(String(5))
    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1000))

    accommodation: Mapped["Accommodation"] = relationship(
        back_populates="translations"
    )
