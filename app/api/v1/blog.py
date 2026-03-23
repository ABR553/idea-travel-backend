from fastapi import APIRouter, Depends, Header, HTTPException, Query, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db, get_locale
from app.config import settings
from app.schemas.blog_post import (
    BlogPostCreate,
    BlogPostListResponse,
    BlogPostResponse,
    BlogPostUpdate,
)
from app.schemas.common import PaginatedResponse
from app.seeds.seed_data import seed_blog
from app.services import blog_service

router = APIRouter()

CACHE_HEADER = "public, s-maxage=3600, stale-while-revalidate=86400"


def _verify_admin(secret: str) -> None:
    if secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="Forbidden")


# ── Public endpoints (sin path params) ───────────────────────────


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


# ── Admin endpoints (ANTES de /{slug} para evitar conflicto) ─────


@router.post(
    "/seed",
    summary="Seed de blog posts",
    description="Ejecuta seed de articulos del blog. Protegido con ADMIN_SECRET.",
)
async def run_seed_blog(x_admin_secret: str = Header()) -> dict[str, str]:
    _verify_admin(x_admin_secret)
    await seed_blog()
    return {"status": "ok", "message": "Blog seed ejecutado correctamente"}


@router.get(
    "/admin/list",
    response_model=PaginatedResponse[BlogPostListResponse],
    summary="Listar todos los posts (admin)",
    description="Lista todos los posts incluyendo borradores. Protegido con ADMIN_SECRET.",
)
async def list_posts_admin(
    locale: str = Depends(get_locale),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    x_admin_secret: str = Header(),
) -> dict:
    _verify_admin(x_admin_secret)
    items, total = await blog_service.get_all_posts_admin(db, locale, page, page_size)
    return {
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get(
    "/admin/{slug}",
    response_model=BlogPostResponse,
    summary="Detalle de post (admin)",
    description="Obtiene un post por slug sin filtrar por published.",
)
async def get_post_admin(
    slug: str,
    locale: str = Depends(get_locale),
    db: AsyncSession = Depends(get_db),
    x_admin_secret: str = Header(),
) -> BlogPostResponse:
    _verify_admin(x_admin_secret)
    post = await blog_service.get_post_by_slug_admin(db, slug, locale)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return post


@router.post(
    "/admin",
    response_model=BlogPostResponse,
    status_code=201,
    summary="Crear articulo",
    description="Crea un nuevo articulo del blog. Protegido con ADMIN_SECRET.",
)
async def create_post(
    data: BlogPostCreate,
    locale: str = Depends(get_locale),
    db: AsyncSession = Depends(get_db),
    x_admin_secret: str = Header(),
) -> BlogPostResponse:
    _verify_admin(x_admin_secret)
    post = await blog_service.create_post(db, data)
    bt = None
    for t in post.translations:
        if t.locale == locale:
            bt = t
            break
    if not bt and post.translations:
        bt = post.translations[0]
    pack_slug = post.related_pack.slug if post.related_pack else None
    return BlogPostResponse(
        id=str(post.id),
        slug=post.slug,
        title=bt.title if bt else "",
        excerpt=bt.excerpt if bt else "",
        content=bt.content if bt else "",
        coverImage=post.cover_image,
        category=post.category,
        publishedAt=post.published_at.strftime("%Y-%m-%d") if post.published_at else None,
        relatedPackSlug=pack_slug,
    )


@router.put(
    "/admin/{slug}",
    response_model=BlogPostResponse,
    summary="Actualizar articulo",
    description="Actualiza un articulo existente. Protegido con ADMIN_SECRET.",
)
async def update_post(
    slug: str,
    data: BlogPostUpdate,
    locale: str = Depends(get_locale),
    db: AsyncSession = Depends(get_db),
    x_admin_secret: str = Header(),
) -> BlogPostResponse:
    _verify_admin(x_admin_secret)
    post = await blog_service.update_post(db, slug, data)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")
    bt = None
    for t in post.translations:
        if t.locale == locale:
            bt = t
            break
    if not bt and post.translations:
        bt = post.translations[0]
    pack_slug = post.related_pack.slug if post.related_pack else None
    return BlogPostResponse(
        id=str(post.id),
        slug=post.slug,
        title=bt.title if bt else "",
        excerpt=bt.excerpt if bt else "",
        content=bt.content if bt else "",
        coverImage=post.cover_image,
        category=post.category,
        publishedAt=post.published_at.strftime("%Y-%m-%d") if post.published_at else None,
        relatedPackSlug=pack_slug,
    )


@router.delete(
    "/admin/{slug}",
    summary="Eliminar articulo",
    description="Elimina un articulo del blog. Protegido con ADMIN_SECRET.",
)
async def delete_post(
    slug: str,
    db: AsyncSession = Depends(get_db),
    x_admin_secret: str = Header(),
) -> dict[str, str]:
    _verify_admin(x_admin_secret)
    deleted = await blog_service.delete_post(db, slug)
    if not deleted:
        raise HTTPException(status_code=404, detail="Blog post not found")
    return {"status": "ok", "message": f"Post '{slug}' eliminado"}


# ── Public detail (con path param, AL FINAL) ─────────────────────


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
