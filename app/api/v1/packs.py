from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_locale
from app.schemas.common import PaginatedResponse
from app.schemas.pack import PackListResponse, PackResponse
from app.services import pack_service

router = APIRouter()

CACHE_HEADER = "public, s-maxage=3600, stale-while-revalidate=86400"


@router.get(
    "",
    response_model=PaginatedResponse[PackListResponse],
    summary="Listar packs",
    description=(
        "Devuelve packs de viaje con paginacion. "
        "Filtrable por featured, precio, duracion, numero de destinos. "
        "Buscador por titulo y descripcion. Ordenable por precio o duracion."
    ),
)
async def list_packs(
    response: Response,
    locale: str = Depends(get_locale),
    featured: bool | None = None,
    min_price: float | None = Query(None, ge=0, description="Precio minimo (price_from)"),
    max_price: float | None = Query(None, ge=0, description="Precio maximo (price_to)"),
    min_days: int | None = Query(None, ge=1, description="Duracion minima en dias"),
    max_days: int | None = Query(None, ge=1, description="Duracion maxima en dias"),
    min_destinations: int | None = Query(None, ge=1, description="Minimo de destinos"),
    max_destinations: int | None = Query(None, ge=1, description="Maximo de destinos"),
    search: str | None = Query(None, min_length=2, max_length=100, description="Buscar en titulo y descripcion"),
    sort_by: str | None = Query(None, pattern="^(price_asc|price_desc|duration_asc|duration_desc)$", description="Ordenar: price_asc, price_desc, duration_asc, duration_desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> dict:
    items, total = await pack_service.get_packs(
        db,
        locale,
        featured=featured,
        min_price=min_price,
        max_price=max_price,
        min_days=min_days,
        max_days=max_days,
        min_destinations=min_destinations,
        max_destinations=max_destinations,
        search=search,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    response.headers["Cache-Control"] = CACHE_HEADER
    return {
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/featured", response_model=list[PackListResponse], summary="Packs destacados", description="Devuelve solo los packs con featured=true.")
async def featured_packs(
    response: Response,
    locale: str = Depends(get_locale),
    db: AsyncSession = Depends(get_db),
) -> list[PackListResponse]:
    items = await pack_service.get_featured_packs(db, locale)
    response.headers["Cache-Control"] = CACHE_HEADER
    return items


@router.get("/{slug}", response_model=PackResponse, summary="Detalle de pack", description="Devuelve un pack completo con destinos, alojamientos, experiencias y ruta dia a dia.")
async def get_pack(
    slug: str,
    response: Response,
    locale: str = Depends(get_locale),
    db: AsyncSession = Depends(get_db),
) -> PackResponse:
    pack = await pack_service.get_pack_by_slug(db, slug, locale)
    if not pack:
        raise HTTPException(status_code=404, detail="Pack not found")
    response.headers["Cache-Control"] = CACHE_HEADER
    return pack
