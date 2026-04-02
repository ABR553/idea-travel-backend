from fastapi import APIRouter, Depends, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_locale
from app.schemas.common import PaginatedResponse
from app.schemas.product import ProductBulkUpsertRequest, ProductBulkUpsertResponse, ProductResponse
from app.schemas.project import ProjectResponse
from app.services import product_service, project_service

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
    "/{slug}/products/categories",
    summary="Categorias de productos de un proyecto",
    description="Devuelve las categorias distintas de los productos asociados a un proyecto.",
)
async def list_project_product_categories(
    slug: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> list[str]:
    categories = await project_service.get_project_categories(db, slug)
    if categories is None:
        raise HTTPException(status_code=404, detail="Project not found")
    response.headers["Cache-Control"] = CACHE_HEADER
    return categories


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


@router.post(
    "/{slug}/products/upsert",
    response_model=ProductBulkUpsertResponse,
    summary="Upsert masivo de productos",
    description=(
        "Crea o actualiza productos en un proyecto usando (project_id, external_id) como clave. "
        "Si el producto ya existe (mismo external_id en el proyecto) se actualiza; si no, se crea. "
        "El slug nunca se modifica en actualizaciones. "
        "Las traducciones se hacen upsert por locale; las no incluidas en el payload se dejan intactas."
    ),
    status_code=200,
)
async def bulk_upsert_project_products(
    slug: str,
    payload: ProductBulkUpsertRequest,
    locale: str = Depends(get_locale),
    db: AsyncSession = Depends(get_db),
) -> ProductBulkUpsertResponse:
    project = await project_service.get_project_model_by_slug(db, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    result = await product_service.bulk_upsert_products(db, project, payload, locale)
    await db.commit()
    return result


@router.delete(
    "/{slug}/products",
    summary="Eliminar productos de un proyecto",
    description=(
        "Elimina productos de un proyecto. "
        "Si se pasan external_ids como query params, solo elimina esos productos. "
        "Si no se pasan external_ids, elimina TODOS los productos del proyecto."
    ),
    status_code=200,
)
async def delete_project_products(
    slug: str,
    external_ids: list[str] | None = Query(None, description="external_ids a eliminar. Si se omite, se eliminan todos los productos del proyecto."),
    db: AsyncSession = Depends(get_db),
) -> dict:
    project = await project_service.get_project_model_by_slug(db, slug)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    deleted = await product_service.bulk_delete_products(db, project, external_ids)
    await db.commit()
    return {"deleted": deleted}
