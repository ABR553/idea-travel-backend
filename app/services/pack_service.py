import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.accommodation import Accommodation
from app.domain.models.destination import Destination
from app.domain.models.experience import Experience
from app.domain.models.pack import Pack, PackTranslation
from app.domain.models.route_step import RouteStep
from app.schemas.accommodation import AccommodationResponse
from app.schemas.common import PriceRange
from app.schemas.destination import DestinationDetailResponse, DestinationResponse
from app.schemas.experience import ExperienceResponse
from app.schemas.pack import PackListResponse, PackResponse
from app.schemas.route_step import RouteStepResponse
from app.services import click_service
from app.services.utils import resolve_translation, to_float


def _build_pack_options() -> list:
    return [
        selectinload(Pack.translations),
        selectinload(Pack.destinations).selectinload(Destination.translations),
        selectinload(Pack.destinations)
        .selectinload(Destination.accommodations)
        .selectinload(Accommodation.translations),
        selectinload(Pack.destinations)
        .selectinload(Destination.experiences)
        .selectinload(Experience.translations),
        selectinload(Pack.route_steps).selectinload(RouteStep.translations),
        selectinload(Pack.route_steps)
        .selectinload(RouteStep.destination)
        .selectinload(Destination.translations),
    ]


def _build_destination_response(
    dest: Destination, locale: str
) -> DestinationResponse:
    dt = resolve_translation(dest.translations, locale)
    return DestinationResponse(
        name=dt.name if dt else "",
        country=dt.country if dt else "",
        description=dt.description if dt else "",
        image=dest.image,
        days=dest.days,
    )


def _build_destination_detail_response(
    dest: Destination,
    locale: str,
    acc_clicks: dict[uuid.UUID, int],
    exp_clicks: dict[uuid.UUID, int],
) -> DestinationDetailResponse:
    dt = resolve_translation(dest.translations, locale)
    return DestinationDetailResponse(
        name=dt.name if dt else "",
        country=dt.country if dt else "",
        description=dt.description if dt else "",
        image=dest.image,
        days=dest.days,
        accommodations=[
            _build_accommodation_response(a, locale, acc_clicks.get(a.id, 0))
            for a in dest.accommodations
        ],
        experiences=[
            _build_experience_response(e, locale, exp_clicks.get(e.id, 0))
            for e in dest.experiences
        ],
    )


def _build_accommodation_response(
    acc: Accommodation, locale: str, clicks_last_24h: int = 0
) -> AccommodationResponse:
    at = resolve_translation(acc.translations, locale)
    return AccommodationResponse(
        id=str(acc.id),
        name=at.name if at else "",
        tier=acc.tier,
        description=at.description if at else "",
        price_per_night=to_float(acc.price_per_night),
        currency=acc.currency,
        image=acc.image,
        amenities=acc.amenities or [],
        rating=to_float(acc.rating),
        booking_url=acc.booking_url,
        nights=acc.nights,
        clicks_last_24h=clicks_last_24h,
    )


def _build_experience_response(
    exp: Experience, locale: str, clicks_last_24h: int = 0
) -> ExperienceResponse:
    et = resolve_translation(exp.translations, locale)
    return ExperienceResponse(
        id=str(exp.id),
        title=et.title if et else "",
        description=et.description if et else "",
        provider=exp.provider,
        affiliate_url=exp.affiliate_url,
        price=to_float(exp.price),
        currency=exp.currency,
        duration=et.duration if et else "",
        image=exp.image,
        rating=to_float(exp.rating),
        clicks_last_24h=clicks_last_24h,
    )


def _build_route_step_response(
    step: RouteStep, locale: str
) -> RouteStepResponse:
    st = resolve_translation(step.translations, locale)
    dest_t = resolve_translation(step.destination.translations, locale)
    return RouteStepResponse(
        day=step.day,
        title=st.title if st else "",
        description=st.description if st else "",
        destination=dest_t.name if dest_t else "",
    )


def _build_price_range(pack: Pack) -> PriceRange:
    return PriceRange(
        from_price=to_float(pack.price_from),
        to=to_float(pack.price_to),
        currency=pack.price_currency,
    )


def _pack_to_list_response(pack: Pack, locale: str) -> PackListResponse:
    pt = resolve_translation(pack.translations, locale)
    destinations = [
        _build_destination_response(d, locale) for d in pack.destinations
    ]
    return PackListResponse(
        id=str(pack.id),
        slug=pack.slug,
        title=pt.title if pt else "",
        short_description=pt.short_description if pt else "",
        destinations=destinations,
        cover_image=pack.cover_image,
        duration=pt.duration if pt else "",
        duration_days=pack.duration_days,
        price=_build_price_range(pack),
        featured=pack.featured,
    )


async def _pack_to_full_response(
    pack: Pack, locale: str, db: AsyncSession
) -> PackResponse:
    pt = resolve_translation(pack.translations, locale)

    # Recoger todos los IDs de accommodations y experiences del pack
    acc_ids: list[uuid.UUID] = []
    exp_ids: list[uuid.UUID] = []
    for d in pack.destinations:
        acc_ids.extend(a.id for a in d.accommodations)
        exp_ids.extend(e.id for e in d.experiences)

    # Batch query para clicks de las ultimas 24h
    acc_clicks = await click_service.get_clicks_last_24h(db, "accommodation", acc_ids)
    exp_clicks = await click_service.get_clicks_last_24h(db, "experience", exp_ids)

    destinations = [
        _build_destination_detail_response(d, locale, acc_clicks, exp_clicks)
        for d in pack.destinations
    ]
    route = [_build_route_step_response(s, locale) for s in pack.route_steps]

    return PackResponse(
        id=str(pack.id),
        slug=pack.slug,
        title=pt.title if pt else "",
        description=pt.description if pt else "",
        short_description=pt.short_description if pt else "",
        destinations=destinations,
        route=route,
        cover_image=pack.cover_image,
        duration=pt.duration if pt else "",
        duration_days=pack.duration_days,
        price=_build_price_range(pack),
        featured=pack.featured,
    )


async def get_packs(
    db: AsyncSession,
    locale: str,
    featured: bool | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_days: int | None = None,
    max_days: int | None = None,
    min_destinations: int | None = None,
    max_destinations: int | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[PackListResponse], int]:
    base = select(Pack)

    if featured is not None:
        base = base.where(Pack.featured == featured)
    if min_price is not None:
        base = base.where(Pack.price_from >= min_price)
    if max_price is not None:
        base = base.where(Pack.price_to <= max_price)
    if min_days is not None:
        base = base.where(Pack.duration_days >= min_days)
    if max_days is not None:
        base = base.where(Pack.duration_days <= max_days)

    if min_destinations is not None or max_destinations is not None:
        dest_count = (
            select(
                Destination.pack_id,
                func.count(Destination.id).label("dest_count"),
            )
            .group_by(Destination.pack_id)
            .subquery()
        )
        base = base.join(dest_count, Pack.id == dest_count.c.pack_id)
        if min_destinations is not None:
            base = base.where(dest_count.c.dest_count >= min_destinations)
        if max_destinations is not None:
            base = base.where(dest_count.c.dest_count <= max_destinations)

    if search:
        search_term = f"%{search}%"
        base = base.where(
            Pack.id.in_(
                select(PackTranslation.pack_id).where(
                    (PackTranslation.title.ilike(search_term))
                    | (PackTranslation.short_description.ilike(search_term))
                    | (PackTranslation.description.ilike(search_term))
                )
            )
        )

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    ordered = base
    if sort_by == "price_asc":
        ordered = ordered.order_by(Pack.price_from.asc())
    elif sort_by == "price_desc":
        ordered = ordered.order_by(Pack.price_from.desc())
    elif sort_by == "duration_asc":
        ordered = ordered.order_by(Pack.duration_days.asc())
    elif sort_by == "duration_desc":
        ordered = ordered.order_by(Pack.duration_days.desc())
    else:
        ordered = ordered.order_by(Pack.created_at.desc())

    query = (
        ordered.options(*_build_pack_options())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    packs = result.scalars().unique().all()
    items = [_pack_to_list_response(p, locale) for p in packs]
    return items, total


async def get_pack_by_slug(
    db: AsyncSession, slug: str, locale: str
) -> PackResponse | None:
    query = (
        select(Pack)
        .where(Pack.slug == slug)
        .options(*_build_pack_options())
    )
    result = await db.execute(query)
    pack = result.scalars().unique().first()
    if not pack:
        return None
    return await _pack_to_full_response(pack, locale, db)


async def get_featured_packs(
    db: AsyncSession, locale: str
) -> list[PackListResponse]:
    items, _ = await get_packs(db, locale, featured=True, page=1, page_size=50)
    return items
