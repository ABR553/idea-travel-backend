import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.destination import Destination, DestinationTranslation
from app.domain.models.pack import Pack, PackTranslation


async def create_pack(
    db: AsyncSession,
    slug: str,
    cover_image: str,
    duration_days: int,
    price_from: float,
    price_to: float,
    currency: str = "EUR",
    featured: bool = False,
    translations: list[dict] | None = None,
) -> dict:
    """Create a pack with translations. Returns {id, slug}."""
    pack_id = uuid.uuid4()
    pack = Pack(
        id=pack_id,
        slug=slug,
        cover_image=cover_image,
        duration_days=duration_days,
        price_from=price_from,
        price_to=price_to,
        price_currency=currency,
        featured=featured,
    )
    for t in translations or []:
        pack.translations.append(
            PackTranslation(
                id=uuid.uuid4(),
                pack_id=pack_id,
                locale=t["locale"],
                title=t["title"],
                description=t["description"],
                short_description=t["short_description"],
                duration=t["duration"],
            )
        )
    db.add(pack)
    await db.flush()
    return {"id": str(pack.id), "slug": pack.slug}


async def create_destinations(
    db: AsyncSession,
    pack_slug: str,
    destinations: list[dict],
) -> list[dict]:
    """Create destinations for a pack. Returns list of {id, name, display_order}."""
    result = await db.execute(select(Pack).where(Pack.slug == pack_slug))
    pack = result.scalar_one_or_none()
    if not pack:
        raise ValueError(f"Pack '{pack_slug}' not found")

    created = []
    for dest_data in destinations:
        dest_id = uuid.uuid4()
        dest = Destination(
            id=dest_id,
            pack_id=pack.id,
            image=dest_data["image"],
            display_order=dest_data["display_order"],
            days=dest_data["days"],
        )
        for t in dest_data.get("translations", []):
            dest.translations.append(
                DestinationTranslation(
                    id=uuid.uuid4(),
                    destination_id=dest_id,
                    locale=t["locale"],
                    name=t["name"],
                    country=t["country"],
                    description=t["description"],
                )
            )
        db.add(dest)
        es_name = next(
            (t["name"] for t in dest_data.get("translations", []) if t["locale"] == "es"),
            "",
        )
        created.append({"id": str(dest_id), "name": es_name, "display_order": dest_data["display_order"]})
    await db.flush()
    return created
