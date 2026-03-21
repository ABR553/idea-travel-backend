import uuid

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel


class Experience(BaseModel):
    __tablename__ = "experiences"

    destination_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("destinations.id", ondelete="CASCADE")
    )
    provider: Mapped[str] = mapped_column(String(20))  # getyourguide, civitatis
    affiliate_url: Mapped[str] = mapped_column(String(500))
    price: Mapped[float] = mapped_column(Numeric(10, 2))
    currency: Mapped[str] = mapped_column(String(3), default="EUR")
    image: Mapped[str] = mapped_column(String(500))
    rating: Mapped[float] = mapped_column(Numeric(2, 1))

    destination: Mapped["Destination"] = relationship(  # noqa: F821
        back_populates="experiences"
    )
    translations: Mapped[list["ExperienceTranslation"]] = relationship(
        back_populates="experience", cascade="all, delete-orphan"
    )


class ExperienceTranslation(BaseModel):
    __tablename__ = "experience_translations"
    __table_args__ = (
        UniqueConstraint(
            "experience_id", "locale", name="uq_experience_translation_locale"
        ),
    )

    experience_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("experiences.id", ondelete="CASCADE")
    )
    locale: Mapped[str] = mapped_column(String(5))
    title: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(String(1000))
    duration: Mapped[str] = mapped_column(String(50))

    experience: Mapped["Experience"] = relationship(back_populates="translations")
