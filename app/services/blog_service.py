from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.blog_post import BlogPost, BlogPostTranslation
from app.domain.models.pack import Pack
from app.schemas.blog_post import (
    BlogPostCreate,
    BlogPostListResponse,
    BlogPostResponse,
    BlogPostUpdate,
)
from app.services.utils import resolve_translation


def _format_date(dt) -> str | None:  # noqa: ANN001
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d")


def _available_locales(post: BlogPost) -> list[str]:
    return sorted({t.locale for t in post.translations})


def _post_to_list_response(post: BlogPost, locale: str) -> BlogPostListResponse:
    bt = resolve_translation(post.translations, locale)
    pack_slug = None
    if post.related_pack is not None:
        pack_slug = post.related_pack.slug
    return BlogPostListResponse(
        id=str(post.id),
        slug=post.slug,
        title=bt.title if bt else "",
        excerpt=bt.excerpt if bt else "",
        coverImage=post.cover_image,
        category=post.category,
        publishedAt=_format_date(post.published_at),
        relatedPackSlug=pack_slug,
        availableLocales=_available_locales(post),
    )


def _post_to_response(post: BlogPost, locale: str) -> BlogPostResponse:
    bt = resolve_translation(post.translations, locale)
    pack_slug = None
    if post.related_pack is not None:
        pack_slug = post.related_pack.slug
    return BlogPostResponse(
        id=str(post.id),
        slug=post.slug,
        title=bt.title if bt else "",
        excerpt=bt.excerpt if bt else "",
        content=bt.content if bt else "",
        coverImage=post.cover_image,
        category=post.category,
        publishedAt=_format_date(post.published_at),
        relatedPackSlug=pack_slug,
        availableLocales=_available_locales(post),
    )


async def get_posts(
    db: AsyncSession,
    locale: str,
    category: str | None = None,
    search: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[BlogPostListResponse], int]:
    base = select(BlogPost).where(BlogPost.published.is_(True))

    if category:
        base = base.where(BlogPost.category == category)

    if search:
        search_term = f"%{search}%"
        base = base.where(
            BlogPost.id.in_(
                select(BlogPostTranslation.blog_post_id).where(
                    (BlogPostTranslation.title.ilike(search_term))
                    | (BlogPostTranslation.excerpt.ilike(search_term))
                )
            )
        )

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    query = (
        base.order_by(BlogPost.published_at.desc().nullslast())
        .options(selectinload(BlogPost.translations))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    posts = result.scalars().unique().all()
    items = [_post_to_list_response(p, locale) for p in posts]
    return items, total


async def get_distinct_categories(db: AsyncSession) -> list[str]:
    result = await db.execute(
        select(BlogPost.category)
        .where(BlogPost.published.is_(True))
        .distinct()
        .order_by(BlogPost.category)
    )
    return [row[0] for row in result.all()]


async def get_post_by_slug(
    db: AsyncSession, slug: str, locale: str
) -> BlogPostResponse | None:
    query = (
        select(BlogPost)
        .where(BlogPost.slug == slug, BlogPost.published.is_(True))
        .options(selectinload(BlogPost.translations))
    )
    result = await db.execute(query)
    post = result.scalars().unique().first()
    if not post:
        return None
    return _post_to_response(post, locale)


async def _resolve_pack_id(db: AsyncSession, slug: str | None) -> None | str:
    """Resuelve un pack slug a su UUID."""
    if not slug:
        return None
    result = await db.execute(select(Pack.id).where(Pack.slug == slug))
    row = result.first()
    return row[0] if row else None


async def get_all_posts_admin(
    db: AsyncSession,
    locale: str,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[BlogPostListResponse], int]:
    """Lista todos los posts (publicados o no) para el admin."""
    base = select(BlogPost)
    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    query = (
        base.order_by(BlogPost.created_at.desc())
        .options(selectinload(BlogPost.translations))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    posts = result.scalars().unique().all()
    items = [_post_to_list_response(p, locale) for p in posts]
    return items, total


async def create_post(db: AsyncSession, data: BlogPostCreate) -> BlogPost:
    pack_id = await _resolve_pack_id(db, data.related_pack_slug)
    published_at = None
    if data.published_at:
        published_at = datetime.fromisoformat(data.published_at).replace(tzinfo=timezone.utc)
    elif data.published:
        published_at = datetime.now(timezone.utc)

    post = BlogPost(
        slug=data.slug,
        cover_image=data.cover_image,
        category=data.category,
        published=data.published,
        published_at=published_at,
        related_pack_id=pack_id,
    )
    for t in data.translations:
        post.translations.append(
            BlogPostTranslation(
                locale=t.locale,
                title=t.title,
                excerpt=t.excerpt,
                content=t.content,
            )
        )
    db.add(post)
    await db.commit()
    await db.refresh(post, ["translations"])
    return post


async def update_post(db: AsyncSession, slug: str, data: BlogPostUpdate) -> BlogPost | None:
    query = (
        select(BlogPost)
        .where(BlogPost.slug == slug)
        .options(selectinload(BlogPost.translations))
    )
    result = await db.execute(query)
    post = result.scalars().unique().first()
    if not post:
        return None

    if data.slug is not None:
        post.slug = data.slug
    if data.cover_image is not None:
        post.cover_image = data.cover_image
    if data.category is not None:
        post.category = data.category
    if data.published is not None:
        post.published = data.published
        if data.published and post.published_at is None:
            post.published_at = datetime.now(timezone.utc)
    if data.published_at is not None:
        post.published_at = datetime.fromisoformat(data.published_at).replace(tzinfo=timezone.utc)
    if data.related_pack_slug is not None:
        post.related_pack_id = await _resolve_pack_id(db, data.related_pack_slug)

    if data.translations is not None:
        # Reemplazar traducciones existentes
        for old_t in list(post.translations):
            await db.delete(old_t)
        await db.flush()
        for t in data.translations:
            post.translations.append(
                BlogPostTranslation(
                    locale=t.locale,
                    title=t.title,
                    excerpt=t.excerpt,
                    content=t.content,
                )
            )

    await db.commit()
    await db.refresh(post, ["translations"])
    return post


async def delete_post(db: AsyncSession, slug: str) -> bool:
    query = select(BlogPost).where(BlogPost.slug == slug)
    result = await db.execute(query)
    post = result.scalars().first()
    if not post:
        return False
    await db.delete(post)
    await db.commit()
    return True


async def get_post_by_slug_admin(
    db: AsyncSession, slug: str, locale: str
) -> BlogPostResponse | None:
    """Obtiene un post por slug sin filtrar por published (para admin)."""
    query = (
        select(BlogPost)
        .where(BlogPost.slug == slug)
        .options(selectinload(BlogPost.translations))
    )
    result = await db.execute(query)
    post = result.scalars().unique().first()
    if not post:
        return None
    return _post_to_response(post, locale)
