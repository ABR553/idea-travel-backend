from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.domain.models.accommodation import Accommodation
from app.domain.models.experience import Experience
from app.schemas.click import ClickResponse
from app.services import click_service

router = APIRouter()


@router.post(
    "/accommodations/{accommodation_id}",
    response_model=ClickResponse,
    summary="Registrar click en accommodation",
    description="Registra que un usuario ha clicado en el link de reserva de un alojamiento.",
)
async def click_accommodation(
    accommodation_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ClickResponse:
    result = await db.execute(
        select(Accommodation.id).where(Accommodation.id == accommodation_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Accommodation not found")

    await click_service.register_click(db, "accommodation", accommodation_id)
    return ClickResponse(
        message="Click registered",
        entity_type="accommodation",
        entity_id=str(accommodation_id),
    )


@router.post(
    "/experiences/{experience_id}",
    response_model=ClickResponse,
    summary="Registrar click en experience",
    description="Registra que un usuario ha clicado en el link de afiliado de una experiencia.",
)
async def click_experience(
    experience_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ClickResponse:
    result = await db.execute(
        select(Experience.id).where(Experience.id == experience_id)
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Experience not found")

    await click_service.register_click(db, "experience", experience_id)
    return ClickResponse(
        message="Click registered",
        entity_type="experience",
        entity_id=str(experience_id),
    )
