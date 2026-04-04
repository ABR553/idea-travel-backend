import uuid

import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.models.product import Product, ProductTranslation
from app.domain.models.route_step import RouteStep
from app.services import pack_write_service, enrich_service


@pytest.mark.asyncio
async def test_enrich_creates_route_steps_and_links(db_session):
    # Create pack with destination
    await pack_write_service.create_pack(
        db_session,
        slug="enrich-test-pack",
        cover_image="https://example.com/c.jpg",
        duration_days=3,
        price_from=300.0,
        price_to=600.0,
        translations=[
            {"locale": "es", "title": "P", "description": "D", "short_description": "S", "duration": "3 días"},
            {"locale": "en", "title": "P", "description": "D", "short_description": "S", "duration": "3 days"},
        ],
    )
    dests = await pack_write_service.create_destinations(
        db_session,
        pack_slug="enrich-test-pack",
        destinations=[
            {
                "image": "https://example.com/d.jpg",
                "display_order": 0,
                "days": 3,
                "translations": [
                    {"locale": "es", "name": "Destino", "country": "Pais", "description": "Desc"},
                    {"locale": "en", "name": "Dest", "country": "Country", "description": "Desc"},
                ],
            }
        ],
    )
    dest_id = dests[0]["id"]

    # Create a product to link
    prod_id = uuid.uuid4()
    product = Product(
        id=prod_id, slug="test-travel-bag", category="luggage", price=49.99,
        currency="EUR", affiliate_url="https://amazon.com/bag", image="https://example.com/bag.jpg",
        rating=4.5,
        translations=[
            ProductTranslation(id=uuid.uuid4(), product_id=prod_id, locale="es", name="Bolsa", description="Bolsa viaje"),
            ProductTranslation(id=uuid.uuid4(), product_id=prod_id, locale="en", name="Bag", description="Travel bag"),
        ],
    )
    db_session.add(product)
    await db_session.flush()

    # Enrich route steps
    result = await enrich_service.enrich_route_steps(
        db_session,
        pack_slug="enrich-test-pack",
        steps=[
            {
                "day": 1,
                "destination_id": dest_id,
                "title_es": "Día 1: Llegada",
                "title_en": "Day 1: Arrival",
                "description_es": "Llegada al destino",
                "description_en": "Arrival at destination",
                "detailed_description_es": "<p>Texto detallado día 1</p>",
                "detailed_description_en": "<p>Detailed text day 1</p>",
                "products": [
                    {"product_slug": "test-travel-bag", "position": 0, "context_text": "Essential for this trip"},
                ],
            },
            {
                "day": 2,
                "destination_id": dest_id,
                "title_es": "Día 2: Exploración",
                "title_en": "Day 2: Exploration",
                "description_es": "Explorar la ciudad",
                "description_en": "Explore the city",
                "products": [],
            },
        ],
    )
    assert result["steps_created"] == 2
    assert result["links_created"] == 1

    # Verify route steps in DB
    query = (
        select(RouteStep)
        .options(selectinload(RouteStep.translations), selectinload(RouteStep.recommended_products))
        .order_by(RouteStep.day)
    )
    steps = (await db_session.execute(query)).scalars().all()
    assert len(steps) == 2
    assert steps[0].day == 1
    assert len(steps[0].recommended_products) == 1
    assert len(steps[0].translations) == 2


@pytest.mark.asyncio
async def test_enrich_pack_not_found(db_session):
    with pytest.raises(ValueError, match="not found"):
        await enrich_service.enrich_route_steps(db_session, pack_slug="nonexistent", steps=[])
