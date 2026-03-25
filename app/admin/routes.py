"""JSON API routes for custom admin pages (Blog Editor & AI Generator).

Called via fetch() from admin templates. Auth checked via SQLAdmin session cookie.
"""

import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.schemas.ai_generate import AIGenerateResponse
from app.schemas.blog_post import BlogPostCreate, BlogPostTranslationCreate, BlogPostUpdate
from app.seeds.seed_data import seed_blog
from app.services import ai_agent_service, blog_service, pack_service

logger = logging.getLogger("ideatravel.admin")

router = APIRouter(prefix="/admin/api", tags=["admin-api"])


def _require_auth(request: Request) -> None:
    if not request.session.get("authenticated", False):
        raise HTTPException(status_code=401, detail="Not authenticated")


async def _get_db():
    async with async_session_factory() as session:
        yield session


# -- Blog ------------------------------------------------------------------


@router.get("/blog/list")
async def blog_list(request: Request, db: AsyncSession = Depends(_get_db)):
    _require_auth(request)
    items, total = await blog_service.get_all_posts_admin(db, "es")
    return {"data": [i.model_dump(by_alias=True) for i in items], "total": total}


@router.post("/blog/seed")
async def blog_seed(request: Request):
    _require_auth(request)
    await seed_blog()
    return {"status": "ok"}


@router.post("/blog")
async def blog_create(request: Request, db: AsyncSession = Depends(_get_db)):
    _require_auth(request)
    body = await request.json()
    data = BlogPostCreate.model_validate(body)
    post = await blog_service.create_post(db, data)
    return {"status": "ok", "slug": post.slug}


@router.get("/blog/{slug}")
async def blog_get(slug: str, request: Request, db: AsyncSession = Depends(_get_db)):
    _require_auth(request)
    locale = request.query_params.get("locale", "es")
    post = await blog_service.get_post_by_slug_admin(db, slug, locale)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post.model_dump(by_alias=True)


@router.put("/blog/{slug}")
async def blog_update(slug: str, request: Request, db: AsyncSession = Depends(_get_db)):
    _require_auth(request)
    body = await request.json()
    data = BlogPostUpdate.model_validate(body)
    post = await blog_service.update_post(db, slug, data)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"status": "ok", "slug": post.slug}


@router.delete("/blog/{slug}")
async def blog_delete(slug: str, request: Request, db: AsyncSession = Depends(_get_db)):
    _require_auth(request)
    deleted = await blog_service.delete_post(db, slug)
    if not deleted:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"status": "ok"}


# -- AI Content Generator --------------------------------------------------


@router.post("/ai/generate")
async def ai_generate(request: Request):
    _require_auth(request)
    body = await request.json()
    description = body.get("description", "").strip()
    if len(description) < 10:
        raise HTTPException(
            status_code=400,
            detail="La descripcion debe tener al menos 10 caracteres",
        )
    result = await ai_agent_service.generate_content(description)
    return result.model_dump()


@router.post("/ai/approve")
async def ai_approve(request: Request, db: AsyncSession = Depends(_get_db)):
    _require_auth(request)
    body = await request.json()
    data = AIGenerateResponse.model_validate(body)

    await pack_service.create_pack(db, data.pack)

    blog_data = BlogPostCreate(
        slug=data.blog.slug,
        coverImage=data.blog.cover_image,
        category=data.blog.category,
        published=True,
        relatedPackSlug=data.pack.slug,
        translations=[
            BlogPostTranslationCreate(
                locale="es",
                title=data.blog.title_es,
                excerpt=data.blog.excerpt_es,
                content=data.blog.content_es,
            ),
            BlogPostTranslationCreate(
                locale="en",
                title=data.blog.title_en,
                excerpt=data.blog.excerpt_en,
                content=data.blog.content_en,
            ),
        ],
    )
    await blog_service.create_post(db, blog_data)

    return {"status": "ok", "pack_slug": data.pack.slug, "blog_slug": data.blog.slug}
