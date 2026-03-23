from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.blog_post import BlogPost, BlogPostTranslation
from app.schemas.blog_post import BlogPostListResponse, BlogPostResponse
from app.services.utils import resolve_translation


def _format_date(dt) -> str | None:  # noqa: ANN001
    if dt is None:
        return None
    return dt.strftime("%Y-%m-%d")


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
