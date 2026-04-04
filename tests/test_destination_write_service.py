import pytest
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.domain.models.accommodation import Accommodation
from app.domain.models.experience import Experience
from app.services import pack_write_service, destination_write_service


async def _create_pack_with_destination(db_session) -> str:
    """Helper: creates a pack + destination, returns destination_id."""
    await pack_write_service.create_pack(
        db_session,
        slug="dw-test-pack",
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
        pack_slug="dw-test-pack",
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
    return dests[0]["id"]


@pytest.mark.asyncio
async def test_create_accommodations(db_session):
    dest_id = await _create_pack_with_destination(db_session)

    result = await destination_write_service.create_accommodations(
        db_session,
        destination_id=dest_id,
        accommodations=[
            {
                "tier": "budget",
                "price_per_night": 25.0,
                "currency": "EUR",
                "image": "https://example.com/hostel.jpg",
                "amenities": ["WiFi", "Kitchen"],
                "rating": 4.2,
                "booking_url": "https://booking.com/hostel",
                "nights": 3,
                "translations": [
                    {"locale": "es", "name": "Hostel Barato", "description": "Hostel economico"},
                    {"locale": "en", "name": "Budget Hostel", "description": "Budget hostel"},
                ],
            },
            {
                "tier": "premium",
                "price_per_night": 150.0,
                "image": "https://example.com/hotel.jpg",
                "amenities": ["WiFi", "Pool", "Gym", "Spa"],
                "rating": 4.8,
                "nights": 3,
                "translations": [
                    {"locale": "es", "name": "Hotel Lujo", "description": "Hotel de lujo"},
                    {"locale": "en", "name": "Luxury Hotel", "description": "Luxury hotel"},
                ],
            },
        ],
    )
    assert len(result) == 2
    assert result[0]["tier"] == "budget"
    assert result[0]["name"] == "Hostel Barato"
    assert result[1]["tier"] == "premium"

    # Verify in DB
    query = select(Accommodation).options(selectinload(Accommodation.translations))
    accs = (await db_session.execute(query)).scalars().all()
    assert len(accs) == 2


@pytest.mark.asyncio
async def test_create_experiences(db_session):
    dest_id = await _create_pack_with_destination(db_session)

    result = await destination_write_service.create_experiences(
        db_session,
        destination_id=dest_id,
        experiences=[
            {
                "provider": "getyourguide",
                "affiliate_url": "https://getyourguide.com/tour-123",
                "price": 45.0,
                "currency": "EUR",
                "image": "https://example.com/tour.jpg",
                "rating": 4.6,
                "translations": [
                    {"locale": "es", "title": "Tour Templo", "description": "Visita al templo", "duration": "3 horas"},
                    {"locale": "en", "title": "Temple Tour", "description": "Temple visit", "duration": "3 hours"},
                ],
            },
        ],
    )
    assert len(result) == 1
    assert result[0]["title"] == "Tour Templo"
    assert result[0]["provider"] == "getyourguide"

    # Verify in DB
    query = select(Experience).options(selectinload(Experience.translations))
    exps = (await db_session.execute(query)).scalars().all()
    assert len(exps) == 1
    assert exps[0].provider == "getyourguide"
