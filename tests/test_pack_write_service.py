import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.models.pack import Pack
from app.domain.models.destination import Destination
from app.services import pack_write_service


@pytest.mark.asyncio
async def test_create_pack(db_session):
    result = await pack_write_service.create_pack(
        db_session,
        slug="mcp-test-pack",
        cover_image="https://example.com/cover.jpg",
        duration_days=7,
        price_from=1000.0,
        price_to=2500.0,
        currency="EUR",
        featured=True,
        translations=[
            {
                "locale": "es",
                "title": "Tailandia 7 Días",
                "description": "Viaje completo a Tailandia",
                "short_description": "Una semana en Tailandia",
                "duration": "7 días",
            },
            {
                "locale": "en",
                "title": "Thailand 7 Days",
                "description": "Complete trip to Thailand",
                "short_description": "A week in Thailand",
                "duration": "7 days",
            },
        ],
    )
    assert result["slug"] == "mcp-test-pack"
    assert "id" in result

    # Verify in DB
    query = select(Pack).where(Pack.slug == "mcp-test-pack").options(selectinload(Pack.translations))
    pack = (await db_session.execute(query)).scalar_one()
    assert pack.duration_days == 7
    assert pack.featured is True
    assert len(pack.translations) == 2
    locales = {t.locale for t in pack.translations}
    assert locales == {"es", "en"}


@pytest.mark.asyncio
async def test_create_destinations(db_session):
    # First create a pack
    await pack_write_service.create_pack(
        db_session,
        slug="dest-test-pack",
        cover_image="https://example.com/c.jpg",
        duration_days=5,
        price_from=500.0,
        price_to=1000.0,
        currency="EUR",
        featured=False,
        translations=[
            {"locale": "es", "title": "P", "description": "D", "short_description": "S", "duration": "5 días"},
            {"locale": "en", "title": "P", "description": "D", "short_description": "S", "duration": "5 days"},
        ],
    )

    destinations = await pack_write_service.create_destinations(
        db_session,
        pack_slug="dest-test-pack",
        destinations=[
            {
                "image": "https://example.com/bangkok.jpg",
                "display_order": 0,
                "days": 3,
                "translations": [
                    {"locale": "es", "name": "Bangkok", "country": "Tailandia", "description": "Capital de Tailandia"},
                    {"locale": "en", "name": "Bangkok", "country": "Thailand", "description": "Capital of Thailand"},
                ],
            },
            {
                "image": "https://example.com/chiangmai.jpg",
                "display_order": 1,
                "days": 2,
                "translations": [
                    {"locale": "es", "name": "Chiang Mai", "country": "Tailandia", "description": "Norte de Tailandia"},
                    {"locale": "en", "name": "Chiang Mai", "country": "Thailand", "description": "Northern Thailand"},
                ],
            },
        ],
    )
    assert len(destinations) == 2
    assert destinations[0]["name"] == "Bangkok"
    assert destinations[0]["display_order"] == 0
    assert destinations[1]["name"] == "Chiang Mai"
    assert "id" in destinations[0]

    # Verify in DB
    query = select(Destination).options(selectinload(Destination.translations))
    dests = (await db_session.execute(query)).scalars().all()
    assert len(dests) == 2


@pytest.mark.asyncio
async def test_create_destinations_pack_not_found(db_session):
    with pytest.raises(ValueError, match="not found"):
        await pack_write_service.create_destinations(
            db_session, pack_slug="nonexistent", destinations=[],
        )
