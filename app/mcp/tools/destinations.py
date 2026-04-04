import json
from typing import Annotated

from pydantic import Field

from app.mcp.db import get_mcp_session
from app.mcp.instance import mcp
from app.services import destination_write_service, enrich_service


@mcp.tool()
async def create_accommodations(
    destination_id: Annotated[str, Field(description="UUID of the destination (from create_destinations response)")],
    accommodations: Annotated[list[dict], Field(description=(
        "Array of accommodation objects. Each: {"
        "tier: 'budget'|'standard'|'premium', "
        "price_per_night: number, "
        "currency: string (default EUR), "
        "image: string (hotel image URL), "
        "amenities: string[] (e.g. ['WiFi', 'Pool', 'Gym']), "
        "rating: number (0-5), "
        "booking_url: string (optional, Booking.com URL), "
        "nights: int (number of nights), "
        "translations: [{locale: 'es'|'en', name: string, description: string}]"
        "}"
    ))],
) -> str:
    """Create accommodations for a destination. Provide budget, standard, and/or premium tiers."""
    async with get_mcp_session() as db:
        result = await destination_write_service.create_accommodations(
            db, destination_id=destination_id, accommodations=accommodations,
        )
        return json.dumps(result, default=str)


@mcp.tool()
async def create_experiences(
    destination_id: Annotated[str, Field(description="UUID of the destination (from create_destinations response)")],
    experiences: Annotated[list[dict], Field(description=(
        "Array of experience objects. Each: {"
        "provider: 'getyourguide'|'civitatis', "
        "affiliate_url: string (affiliate link), "
        "price: number, "
        "currency: string (default EUR), "
        "image: string (experience image URL), "
        "rating: number (0-5), "
        "translations: [{locale: 'es'|'en', title: string, description: string, duration: string (e.g. '3 horas'/'3 hours')}]"
        "}"
    ))],
) -> str:
    """Create experiences/activities for a destination."""
    async with get_mcp_session() as db:
        result = await destination_write_service.create_experiences(
            db, destination_id=destination_id, experiences=experiences,
        )
        return json.dumps(result, default=str)


@mcp.tool()
async def enrich_route_steps(
    pack_slug: Annotated[str, Field(description="Pack slug to add route steps to")],
    steps: Annotated[list[dict], Field(description=(
        "Array of route step objects. Each: {"
        "day: int (day number), "
        "destination_id: string (UUID from create_destinations), "
        "title_es: string (e.g. 'Día 1: Llegada a Bangkok'), "
        "title_en: string (e.g. 'Day 1: Arrival in Bangkok'), "
        "description_es: string (short day description), "
        "description_en: string, "
        "detailed_description_es: string (optional, full day description with HTML), "
        "detailed_description_en: string (optional), "
        "products: [{product_slug: string, position: int (optional), context_text: string (optional)}] (optional)"
        "}"
    ))],
) -> str:
    """Create route steps for a pack and optionally associate products.
    Use list_products first to find available product slugs to associate.
    If route steps already exist for a day, updates descriptions and re-links products."""
    async with get_mcp_session() as db:
        result = await enrich_service.enrich_route_steps(
            db, pack_slug=pack_slug, steps=steps,
        )
        return json.dumps(result, default=str)
