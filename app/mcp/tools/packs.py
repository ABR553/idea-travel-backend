import json
from typing import Annotated

from pydantic import Field

from app.mcp.db import get_mcp_session
from app.mcp.instance import mcp
from app.services import pack_service


@mcp.tool()
async def list_packs(
    featured: Annotated[bool | None, Field(description="Filter by featured status")] = None,
    search: Annotated[str | None, Field(description="Search text in pack title/description")] = None,
    min_price: Annotated[float | None, Field(description="Minimum starting price")] = None,
    max_price: Annotated[float | None, Field(description="Maximum starting price")] = None,
    min_days: Annotated[int | None, Field(description="Minimum trip duration in days")] = None,
    max_days: Annotated[int | None, Field(description="Maximum trip duration in days")] = None,
    sort_by: Annotated[str | None, Field(description="Sort: price_asc, price_desc, duration_asc, duration_desc")] = None,
    page: Annotated[int, Field(description="Page number, 1-indexed")] = 1,
    page_size: Annotated[int, Field(description="Items per page, max 50")] = 10,
    locale: Annotated[str, Field(description="Language: es or en")] = "es",
) -> str:
    """Search and list travel packs with optional filters and pagination."""
    async with get_mcp_session() as db:
        items, total = await pack_service.get_packs(
            db, locale, featured=featured,
            min_price=min_price, max_price=max_price,
            min_days=min_days, max_days=max_days,
            search=search, sort_by=sort_by,
            page=page, page_size=page_size,
        )
        return json.dumps({
            "data": [item.model_dump(by_alias=True) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }, default=str)


@mcp.tool()
async def get_pack(
    slug: Annotated[str, Field(description="Pack URL slug")],
    locale: Annotated[str, Field(description="Language: es or en")] = "es",
) -> str:
    """Get a complete pack with all destinations, accommodations, experiences, and route steps."""
    async with get_mcp_session() as db:
        pack = await pack_service.get_pack_by_slug(db, slug, locale)
        if not pack:
            return json.dumps({"error": f"Pack '{slug}' not found"})
        return json.dumps(pack.model_dump(by_alias=True), default=str)


from app.services import pack_write_service


@mcp.tool()
async def create_pack(
    slug: Annotated[str, Field(description="URL-friendly pack identifier (e.g., thailand-7-days)")],
    cover_image: Annotated[str, Field(description="Cover image URL")],
    duration_days: Annotated[int, Field(description="Total trip duration in days")],
    price_from: Annotated[float, Field(description="Starting price")],
    price_to: Annotated[float, Field(description="Maximum price")],
    translations: Annotated[list[dict], Field(description=(
        "Array of translations. Provide both es and en: ["
        "{locale: 'es', title: string, description: string, short_description: string, duration: string (e.g. '7 días')}, "
        "{locale: 'en', title: string, description: string, short_description: string, duration: string (e.g. '7 days')}"
        "]"
    ))],
    currency: Annotated[str, Field(description="Currency code")] = "EUR",
    featured: Annotated[bool, Field(description="Whether the pack is featured on the homepage")] = False,
) -> str:
    """Create a new travel pack with bilingual translations. Returns the pack id and slug.
    After creating a pack, use create_destinations to add destinations."""
    async with get_mcp_session() as db:
        result = await pack_write_service.create_pack(
            db, slug=slug, cover_image=cover_image,
            duration_days=duration_days, price_from=price_from, price_to=price_to,
            currency=currency, featured=featured, translations=translations,
        )
        return json.dumps(result, default=str)


@mcp.tool()
async def create_destinations(
    pack_slug: Annotated[str, Field(description="Slug of the pack to add destinations to")],
    destinations: Annotated[list[dict], Field(description=(
        "Array of destination objects. Each: {"
        "image: string (destination image URL), "
        "display_order: int (0-indexed order), "
        "days: int (days spent here), "
        "translations: [{locale: 'es'|'en', name: string, country: string, description: string}]"
        "}"
    ))],
) -> str:
    """Create destinations for a pack. Returns list with destination ids (needed for create_accommodations and create_experiences)."""
    async with get_mcp_session() as db:
        result = await pack_write_service.create_destinations(
            db, pack_slug=pack_slug, destinations=destinations,
        )
        return json.dumps(result, default=str)
