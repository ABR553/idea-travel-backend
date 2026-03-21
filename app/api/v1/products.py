from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_locale
from app.schemas.common import PaginatedResponse
from app.schemas.product import ProductResponse
from app.services import product_service

router = APIRouter()

CACHE_HEADER = "public, s-maxage=3600, stale-while-revalidate=86400"

@router.get(
    "",
    response_model=PaginatedResponse[ProductResponse],
    summary="Listar productos",
    description=(
        "Devuelve productos de viaje con paginacion. "
        "Filtrable por categoria, precio y rating. "
        "Buscador por nombre y descripcion. Ordenable por precio o rating."
    ),
)
async def list_products(
    response: Response,
    locale: str = Depends(get_locale),
    category: str | None = None,
    min_price: float | None = Query(None, ge=0, description="Precio minimo"),
    max_price: float | None = Query(None, ge=0, description="Precio maximo"),
    min_rating: float | None = Query(None, ge=0, le=5, description="Rating minimo (0-5)"),
    search: str | None = Query(None, min_length=2, max_length=100, description="Buscar en nombre y descripcion"),
    sort_by: str | None = Query(None, pattern="^(price_asc|price_desc|rating_desc)$", description="Ordenar: price_asc, price_desc, rating_desc"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> dict:
    items, total = await product_service.get_products(
        db,
        locale,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
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


@router.get("/categories", summary="Categorias de productos", description="Devuelve las categorias disponibles de productos existentes en BD.")
async def list_categories(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    response.headers["Cache-Control"] = CACHE_HEADER
    return await product_service.get_distinct_categories(db)


@router.get("/{slug}", response_model=ProductResponse, summary="Detalle de producto", description="Devuelve un producto individual con traducciones segun locale.")
async def get_product(
    slug: str,
    response: Response,
    locale: str = Depends(get_locale),
    db: AsyncSession = Depends(get_db),
) -> ProductResponse:
    product = await product_service.get_product_by_slug(db, slug, locale)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    response.headers["Cache-Control"] = CACHE_HEADER
    return product
