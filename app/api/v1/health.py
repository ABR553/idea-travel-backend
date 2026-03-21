import logging

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db

logger = logging.getLogger("ideatravel")
router = APIRouter()


@router.get("/health", summary="Health check", description="Verifica que la API y la base de datos estan operativas.")
async def health_check(db: AsyncSession = Depends(get_db)) -> dict[str, str]:
    try:
        await db.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        logger.warning("Health check: database not ready: %s", e)
        return {"status": "healthy", "database": "unavailable"}
