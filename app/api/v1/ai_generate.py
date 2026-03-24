from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.config import settings
from app.schemas.ai_generate import AIGenerateRequest, AIGenerateResponse
from app.schemas.blog_post import BlogPostCreate, BlogPostTranslationCreate
from app.services import ai_agent_service, blog_service, pack_service

router = APIRouter()


def _verify_admin(secret: str) -> None:
    if secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post(
    "/generate",
    response_model=AIGenerateResponse,
    summary="Generar pack y blog con IA",
    description="Genera un pack de viaje y un articulo de blog usando IA. Devuelve una previsualizacion.",
)
async def generate(
    data: AIGenerateRequest,
    x_admin_secret: str = Header(),
) -> AIGenerateResponse:
    _verify_admin(x_admin_secret)
    try:
        result = await ai_agent_service.generate_content(data.description)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error generando contenido: {exc}",
        ) from exc
    return result


@router.post(
    "/approve",
    summary="Aprobar y guardar pack y blog generados",
    description="Guarda en base de datos el pack y blog previamente generados por IA.",
    status_code=201,
)
async def approve(
    data: AIGenerateResponse,
    db: AsyncSession = Depends(get_db),
    x_admin_secret: str = Header(),
) -> dict[str, str]:
    _verify_admin(x_admin_secret)

    # Crear pack
    try:
        pack = await pack_service.create_pack(db, data.pack)
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error creando pack: {exc}",
        ) from exc

    # Crear blog post vinculado al pack
    try:
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
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Error creando blog post: {exc}",
        ) from exc

    return {
        "status": "ok",
        "message": "Pack y blog creados correctamente",
        "pack_slug": data.pack.slug,
        "blog_slug": data.blog.slug,
    }
