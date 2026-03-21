import uuid
from datetime import datetime

from sqlalchemy import DateTime, Index, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LinkClick(Base):
    __tablename__ = "link_clicks"
    __table_args__ = (
        Index(
            "ix_link_clicks_entity_clicked_at",
            "entity_type",
            "entity_id",
            "clicked_at",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    entity_type: Mapped[str] = mapped_column(String(20))  # accommodation, experience
    entity_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    clicked_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
