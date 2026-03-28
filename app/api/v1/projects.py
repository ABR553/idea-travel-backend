from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_locale
from app.schemas.common import PaginatedResponse
from app.schemas.product import ProductResponse
from app.schemas.project import ProjectResponse
from app.services import project_service

router = APIRouter()

CACHE_HEADER = "public, s-maxage=3600, stale-while-revalidate=86400"


@router.get(
    "",
    response_model=list[ProjectResponse],
    summary="Listar proyectos",
    description="Devuelve todos los proyectos disponibles.",
)
async def list_projects(
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> list[ProjectResponse]:
    response.headers["Cache-Control"] = CACHE_HEADER
    return await project_service.get_projects(db)


@router.get(
    "/{slug}",
    response_model=ProjectResponse,
    summary="Detalle de proyecto",
    description="Devuelve un proyecto por su slug.",
)
async def get_project(
    slug: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    project = await project_service.get_project_by_slug(db, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    response.headers["Cache-Control"] = CACHE_HEADER
    return project


@router.get(
    "/{slug}/products",
    response_model=PaginatedResponse[ProductResponse],
    summary="Productos de un proyecto",
    description=(
        "Devuelve los productos asociados a un proyecto con paginacion. "
        "Filtrable por categoria, precio y rating."
    ),
)
async def list_project_products(
    slug: str,
    response: Response,
    locale: str = Depends(get_locale),
    category: str | None = None,
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    min_rating: float | None = Query(None, ge=0, le=5),
    search: str | None = Query(None, min_length=2, max_length=100),
    sort_by: str | None = Query(None, pattern="^(price_asc|price_desc|rating_desc)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
) -> dict:
    result = await project_service.get_project_products(
        db,
        project_slug=slug,
        locale=locale,
        category=category,
        min_price=min_price,
        max_price=max_price,
        min_rating=min_rating,
        search=search,
        sort_by=sort_by,
        page=page,
        page_size=page_size,
    )
    if result is None:
        raise HTTPException(status_code=404, detail="Project not found")
    items, total = result
    response.headers["Cache-Control"] = CACHE_HEADER
    return {
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }
