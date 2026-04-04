from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory


@asynccontextmanager
async def get_mcp_session() -> AsyncGenerator[AsyncSession, None]:
    """Async context manager that provides a DB session with auto-commit/rollback."""
    async with async_session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
