from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.models.base import BaseModel


class Project(BaseModel):
    __tablename__ = "projects"

    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(255))
    tag_id: Mapped[str] = mapped_column(String(255))
    link_template: Mapped[str] = mapped_column(String(500))

    products: Mapped[list["Product"]] = relationship(  # type: ignore[name-defined]
        back_populates="project"
    )
