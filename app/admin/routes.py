"""JSON API routes for custom admin pages (Blog Editor & AI Generator).

Called via fetch() from admin templates. Auth checked via SQLAdmin session cookie.
"""

import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.database import async_session_factory
from app.schemas.ai_generate import AIGenerateResponse
from app.schemas.blog_post import BlogPostCreate, BlogPostTranslationCreate, BlogPostUpdate
from app.seeds.seed_data import seed_blog
from app.services import blog_service, pack_service

logger = logging.getLogger("ideatravel.admin")

router = APIRouter(prefix="/admin/api", tags=["admin-api"])

GENERATED_DIR = Path(__file__).resolve().parent.parent.parent / "generated"
PENDING_DIR = GENERATED_DIR / "pending"
APPROVED_DIR = GENERATED_DIR / "approved"


def _require_auth(request: Request) -> None:
    if not request.session.get("authenticated", False):
        raise HTTPException(status_code=401, detail="Not authenticated")


def _require_dev(request: Request) -> None:
    _require_auth(request)
    if settings.environment != "development":
        raise HTTPException(status_code=403, detail="Only available in development environment")


async def _get_db():
    async with async_session_factory() as session:
        yield session


async def _get_prod_db():
    """Crea una sesion contra la BD de produccion."""
    if not settings.database_url_prod:
        raise HTTPException(status_code=400, detail="DATABASE_URL_PROD not configured")
    prod_url = settings.database_url_prod
    if prod_url.startswith("postgresql://"):
        prod_url = prod_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    prod_engine = create_async_engine(prod_url, echo=False)
    prod_session_factory = async_sessionmaker(
        prod_engine, class_=AsyncSession, expire_on_commit=False
    )
    async with prod_session_factory() as session:
        yield session
    await prod_engine.dispose()


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


# -- AI Content: Pending JSON files ----------------------------------------


@router.get("/ai/pending")
async def ai_list_pending(request: Request):
    """Lista los archivos JSON pendientes de aprobacion."""
    _require_dev(request)
    PENDING_DIR.mkdir(parents=True, exist_ok=True)
    files = sorted(PENDING_DIR.glob("*.json"), reverse=True)
    items = []
    for f in files:
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            items.append({
                "filename": f.name,
                "pack_title": data.get("pack", {}).get("title_es", "Sin titulo"),
                "blog_title": data.get("blog", {}).get("title_es", "Sin titulo"),
                "pack_slug": data.get("pack", {}).get("slug", ""),
                "created": f.stem.split("-")[0] if "-" in f.stem else "",
            })
        except (json.JSONDecodeError, KeyError):
            items.append({"filename": f.name, "pack_title": "Error leyendo JSON", "blog_title": "", "pack_slug": "", "created": ""})
    return {"data": items, "total": len(items)}


@router.get("/ai/pending/{filename}")
async def ai_get_pending(filename: str, request: Request):
    """Lee un archivo JSON pendiente para previsualizacion."""
    _require_dev(request)
    filepath = PENDING_DIR / filename
    if not filepath.exists() or not filepath.suffix == ".json":
        raise HTTPException(status_code=404, detail="File not found")
    # Prevenir path traversal
    if filepath.resolve().parent != PENDING_DIR.resolve():
        raise HTTPException(status_code=400, detail="Invalid filename")
    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON file")
    return data


@router.post("/ai/approve/{filename}")
async def ai_approve(filename: str, request: Request):
    """Aprueba un JSON pendiente y lo guarda en la BD seleccionada (dev o prod)."""
    _require_dev(request)
    body = await request.json()
    target = body.get("target", "dev")

    filepath = PENDING_DIR / filename
    if not filepath.exists() or not filepath.suffix == ".json":
        raise HTTPException(status_code=404, detail="File not found")
    if filepath.resolve().parent != PENDING_DIR.resolve():
        raise HTTPException(status_code=400, detail="Invalid filename")

    try:
        raw = json.loads(filepath.read_text(encoding="utf-8"))
        data = AIGenerateResponse.model_validate(raw)
    except (json.JSONDecodeError, Exception) as exc:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {exc}")

    # Seleccionar sesion de BD segun target
    if target == "prod":
        if not settings.database_url_prod:
            raise HTTPException(status_code=400, detail="DATABASE_URL_PROD not configured")
        prod_url = settings.database_url_prod
        if prod_url.startswith("postgresql://"):
            prod_url = prod_url.replace("postgresql://", "postgresql+asyncpg://", 1)
        prod_engine = create_async_engine(prod_url, echo=False)
        prod_factory = async_sessionmaker(prod_engine, class_=AsyncSession, expire_on_commit=False)
        async with prod_factory() as db:
            await _save_to_db(db, data)
        await prod_engine.dispose()
    else:
        async with async_session_factory() as db:
            await _save_to_db(db, data)

    # Mover a approved
    APPROVED_DIR.mkdir(parents=True, exist_ok=True)
    approved_name = f"{datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')}-{target}-{filename}"
    shutil.move(str(filepath), str(APPROVED_DIR / approved_name))

    return {
        "status": "ok",
        "target": target,
        "pack_slug": data.pack.slug,
        "blog_slug": data.blog.slug,
    }


@router.delete("/ai/pending/{filename}")
async def ai_delete_pending(filename: str, request: Request):
    """Elimina un archivo JSON pendiente."""
    _require_dev(request)
    filepath = PENDING_DIR / filename
    if not filepath.exists() or not filepath.suffix == ".json":
        raise HTTPException(status_code=404, detail="File not found")
    if filepath.resolve().parent != PENDING_DIR.resolve():
        raise HTTPException(status_code=400, detail="Invalid filename")
    filepath.unlink()
    return {"status": "ok"}


@router.get("/ai/config")
async def ai_config(request: Request):
    """Devuelve configuracion relevante para el admin UI."""
    _require_dev(request)
    return {
        "has_prod_db": bool(settings.database_url_prod),
        "environment": settings.environment,
    }


async def _save_to_db(db: AsyncSession, data: AIGenerateResponse) -> None:
    """Guarda pack + blog en la BD proporcionada."""
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


# -- Instagram Posts -----------------------------------------------------------

from uuid import UUID  # noqa: E402

from app.schemas.instagram_post import (  # noqa: E402
    InstagramPostCreate,
    InstagramPostListItem,
    InstagramPostListResponse,
    InstagramPostPublishResponse,
    InstagramPostResponse,
    InstagramPostStatusChange,
    InstagramPostUpdate,
)
from app.services import instagram_post_service  # noqa: E402


def _post_to_response(post) -> InstagramPostResponse:
    return InstagramPostResponse.model_validate(
        {
            "id": str(post.id),
            "topic": post.topic,
            "language": post.language,
            "format": post.format,
            "slideCount": post.slide_count,
            "hashtags": post.hashtags,
            "mentions": post.mentions,
            "locationName": post.location_name,
            "locationLat": post.location_lat,
            "locationLng": post.location_lng,
            "targetAudience": post.target_audience,
            "postAngle": post.post_angle,
            "bestPublishTime": post.best_publish_time,
            "rationale": post.rationale,
            "sourceMcpRefs": post.source_mcp_refs,
            "status": post.status,
            "instagramPostId": post.instagram_post_id,
            "publishAttempts": post.publish_attempts,
            "approvedAt": post.approved_at,
            "publishedAt": post.published_at,
            "createdAt": post.created_at,
            "updatedAt": post.updated_at,
            "translations": [
                {
                    "locale": t.locale,
                    "hook": t.hook,
                    "caption": t.caption,
                    "cta": t.cta,
                    "firstComment": t.first_comment,
                    "engagementHook": t.engagement_hook,
                }
                for t in post.translations
            ],
            "slides": [
                {
                    "order": s.order,
                    "imageUrl": s.image_url,
                    "imagePrompt": s.image_prompt,
                    "imageSource": s.image_source,
                    "altText": s.alt_text,
                    "overlayText": s.overlay_text,
                }
                for s in sorted(post.slides, key=lambda x: x.order)
            ],
        }
    )


def _post_to_list_item(post) -> InstagramPostListItem:
    first_url = None
    if post.slides:
        first_url = sorted(post.slides, key=lambda s: s.order)[0].image_url
    return InstagramPostListItem(
        id=str(post.id),
        topic=post.topic,
        status=post.status,
        language=post.language,
        format=post.format,
        slideCount=post.slide_count,
        firstSlideUrl=first_url,
        createdAt=post.created_at,
        updatedAt=post.updated_at,
    )


@router.get("/instagram-posts", response_model=InstagramPostListResponse)
async def ig_list(
    request: Request,
    status: str | None = None,
    language: str | None = None,
    format: str | None = None,
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(_get_db),
) -> InstagramPostListResponse:
    _require_auth(request)
    items, total = await instagram_post_service.list_posts(
        db,
        status=status,
        language=language,
        format=format,
        limit=limit,
        offset=offset,
    )
    return InstagramPostListResponse(
        items=[_post_to_list_item(p) for p in items],
        total=total,
        limit=limit,
        offset=offset,
    )


@router.get("/instagram-posts/{post_id}", response_model=InstagramPostResponse)
async def ig_get(
    post_id: UUID,
    request: Request,
    db: AsyncSession = Depends(_get_db),
) -> InstagramPostResponse:
    _require_auth(request)
    post = await instagram_post_service.get_post(db, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Instagram post not found")
    return _post_to_response(post)


@router.post(
    "/instagram-posts",
    response_model=InstagramPostResponse,
    status_code=201,
)
async def ig_create(
    payload: InstagramPostCreate,
    request: Request,
    db: AsyncSession = Depends(_get_db),
) -> InstagramPostResponse:
    _require_auth(request)
    post = await instagram_post_service.create_post(db, payload)
    post = await instagram_post_service.get_post(db, post.id)
    return _post_to_response(post)


@router.patch("/instagram-posts/{post_id}", response_model=InstagramPostResponse)
async def ig_update(
    post_id: UUID,
    payload: InstagramPostUpdate,
    request: Request,
    db: AsyncSession = Depends(_get_db),
) -> InstagramPostResponse:
    _require_auth(request)
    post = await instagram_post_service.update_post(db, post_id, payload)
    if not post:
        raise HTTPException(status_code=404, detail="Instagram post not found")
    post = await instagram_post_service.get_post(db, post.id)
    return _post_to_response(post)


@router.delete("/instagram-posts/{post_id}", status_code=204)
async def ig_delete(
    post_id: UUID,
    request: Request,
    db: AsyncSession = Depends(_get_db),
) -> None:
    _require_auth(request)
    try:
        deleted = await instagram_post_service.delete_post(db, post_id)
    except instagram_post_service.InvalidStatusTransition as e:
        raise HTTPException(status_code=409, detail=str(e))
    if not deleted:
        raise HTTPException(status_code=404, detail="Instagram post not found")


@router.post("/instagram-posts/{post_id}/status", response_model=InstagramPostResponse)
async def ig_status(
    post_id: UUID,
    payload: InstagramPostStatusChange,
    request: Request,
    db: AsyncSession = Depends(_get_db),
) -> InstagramPostResponse:
    _require_auth(request)
    try:
        post = await instagram_post_service.transition_status(db, post_id, payload.status)
    except instagram_post_service.InvalidStatusTransition as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not post:
        raise HTTPException(status_code=404, detail="Instagram post not found")
    post = await instagram_post_service.get_post(db, post.id)
    return _post_to_response(post)


@router.post(
    "/instagram-posts/{post_id}/publish",
    response_model=InstagramPostPublishResponse,
)
async def ig_publish(
    post_id: UUID,
    request: Request,
    db: AsyncSession = Depends(_get_db),
) -> InstagramPostPublishResponse:
    _require_auth(request)
    try:
        post = await instagram_post_service.publish_post(
            db, post_id, actor=str(request.session.get("username", "admin"))
        )
    except instagram_post_service.InvalidStatusTransition as e:
        raise HTTPException(status_code=422, detail=str(e))
    if not post:
        raise HTTPException(status_code=404, detail="Instagram post not found")
    post = await instagram_post_service.get_post(db, post.id)
    return InstagramPostPublishResponse(
        id=str(post.id),
        status=post.status,
        publishAttempts=post.publish_attempts,
    )
