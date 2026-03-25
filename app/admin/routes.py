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
