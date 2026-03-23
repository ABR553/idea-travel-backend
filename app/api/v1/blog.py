from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_locale
from app.schemas.blog_post import BlogPostListResponse, BlogPostResponse
from app.schemas.common import PaginatedResponse
from app.services import blog_service

router = APIRouter()

CACHE_HEADER = "public, s-maxage=3600, stale-while-revalidate=86400"


@router.get(
    "",
    response_model=PaginatedResponse[BlogPostListResponse],
    summary="Listar articulos del blog",
    description=(
        "Devuelve articulos publicados con paginacion. "
        "Filtrable por categoria. Buscador por titulo y extracto."
    ),
)
async def list_posts(
    response: Response,
    locale: str = Depends(get_locale),
    category: str | None = None,
    search: str | None = Query(
        None, min_length=2, max_length=100, description="Buscar en titulo y extracto"
    ),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> dict:
    items, total = await blog_service.get_posts(
        db, locale, category=category, search=search, page=page, page_size=page_size
    )
    response.headers["Cache-Control"] = CACHE_HEADER
    return {
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get(
    "/categories",
    summary="Categorias del blog",
    description="Devuelve las categorias con articulos publicados.",
)
async def list_categories(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    response.headers["Cache-Control"] = CACHE_HEADER
    return await blog_service.get_distinct_categories(db)


@router.get(
    "/{slug}",
    response_model=BlogPostResponse,
    summary="Detalle de articulo",
    description="Devuelve un articulo completo con contenido y traducciones segun locale.",
)
async def get_post(
    slug: str,
    response: Response,
    locale: str = Depends(get_locale),
    db: AsyncSession = Depends(get_db),
) -> BlogPostResponse:
    post = await blog_service.get_post_by_slug(db, slug, locale)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    response.headers["Cache-Control"] = CACHE_HEADER
    return post
