from collections.abc import AsyncGenerator

from fastapi import Header, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session


def get_locale(
    locale: str | None = Query(None, pattern="^(es|en)$"),
    accept_language: str | None = Header(None, alias="accept-language"),
) -> str:
    if locale:
        return locale
    if accept_language and accept_language.startswith("en"):
        return "en"
    return "es"
