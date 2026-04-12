import json
from typing import Annotated

from pydantic import Field

from app.mcp.db import get_mcp_session
from app.mcp.instance import mcp
from app.schemas.blog_post import BlogPostCreate, BlogPostUpdate
from app.services import blog_service


def _post_summary(post) -> dict:  # noqa: ANN001
    return {
        "id": str(post.id),
        "slug": post.slug,
        "category": post.category,
        "cover_image": post.cover_image,
        "published": post.published,
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "related_pack_id": str(post.related_pack_id) if post.related_pack_id else None,
        "translations": [
            {
                "locale": t.locale,
                "title": t.title,
                "excerpt": t.excerpt,
            }
            for t in post.translations
        ],
    }


@mcp.tool()
async def list_blog_posts(
    category: Annotated[str | None, Field(description="Filter by category slug")] = None,
    search: Annotated[str | None, Field(description="Search text in post title/excerpt")] = None,
    page: Annotated[int, Field(description="Page number, 1-indexed")] = 1,
    page_size: Annotated[int, Field(description="Items per page, max 50")] = 10,
    locale: Annotated[str, Field(description="Language: es or en")] = "es",
    include_unpublished: Annotated[
        bool,
        Field(description="If true, include drafts (admin view). Ignores category/search filters."),
    ] = False,
) -> str:
    """Search and list blog posts with optional filters and pagination.

    By default lists only published posts. Set include_unpublished=True to list all
    posts including drafts (admin view)."""
    async with get_mcp_session() as db:
        if include_unpublished:
            items, total = await blog_service.get_all_posts_admin(
                db, locale, page=page, page_size=page_size
            )
        else:
            items, total = await blog_service.get_posts(
                db, locale, category=category, search=search,
                page=page, page_size=page_size,
            )
        return json.dumps({
            "data": [item.model_dump(by_alias=True) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }, default=str)


@mcp.tool()
async def get_blog_post(
    slug: Annotated[str, Field(description="Blog post URL slug")],
    locale: Annotated[str, Field(description="Language: es or en")] = "es",
    include_unpublished: Annotated[
        bool,
        Field(description="If true, allow fetching drafts (admin view)."),
    ] = False,
) -> str:
    """Get a single blog post by its slug with full content."""
    async with get_mcp_session() as db:
        if include_unpublished:
            post = await blog_service.get_post_by_slug_admin(db, slug, locale)
        else:
            post = await blog_service.get_post_by_slug(db, slug, locale)
        if not post:
            return json.dumps({"error": f"Blog post '{slug}' not found"})
        return json.dumps(post.model_dump(by_alias=True), default=str)


@mcp.tool()
async def list_blog_categories() -> str:
    """Return distinct categories that have at least one published post."""
    async with get_mcp_session() as db:
        categories = await blog_service.get_distinct_categories(db)
        return json.dumps({"data": categories})


@mcp.tool()
async def create_blog_post(
    slug: Annotated[str, Field(description="URL-friendly post identifier (e.g., top-10-tips-thailand)")],
    cover_image: Annotated[str, Field(description="Cover image URL")],
    category: Annotated[str, Field(description="Category slug (e.g., destinos, consejos, gastronomia)")],
    translations: Annotated[list[dict], Field(description=(
        "Array of translations. Provide both es and en: ["
        "{locale: 'es', title: string, excerpt: string (max 500 chars), content: string (markdown)}, "
        "{locale: 'en', title: string, excerpt: string (max 500 chars), content: string (markdown)}"
        "]"
    ))],
    published: Annotated[bool, Field(description="Whether the post is published immediately")] = False,
    published_at: Annotated[
        str | None,
        Field(description="Publish date ISO format YYYY-MM-DD. If omitted and published=true, uses now."),
    ] = None,
    related_pack_slug: Annotated[
        str | None,
        Field(description="Optional slug of a related travel pack"),
    ] = None,
) -> str:
    """Create a new blog post with bilingual translations (es/en).

    The slug must be unique. Returns the created post summary including id and translations."""
    async with get_mcp_session() as db:
        payload = BlogPostCreate(
            slug=slug,
            coverImage=cover_image,
            category=category,
            published=published,
            publishedAt=published_at,
            relatedPackSlug=related_pack_slug,
            translations=translations,  # type: ignore[arg-type]
        )
        post = await blog_service.create_post(db, payload)
        return json.dumps(_post_summary(post), default=str)


@mcp.tool()
async def update_blog_post(
    slug: Annotated[str, Field(description="Current slug of the post to update")],
    new_slug: Annotated[str | None, Field(description="Optional new slug to rename the post")] = None,
    cover_image: Annotated[str | None, Field(description="New cover image URL")] = None,
    category: Annotated[str | None, Field(description="New category slug")] = None,
    translations: Annotated[
        list[dict] | None,
        Field(description=(
            "If provided, REPLACES all existing translations. "
            "Each: {locale: 'es'|'en', title, excerpt, content}"
        )),
    ] = None,
    published: Annotated[bool | None, Field(description="Publish/unpublish the post")] = None,
    published_at: Annotated[
        str | None,
        Field(description="New publish date ISO format YYYY-MM-DD"),
    ] = None,
    related_pack_slug: Annotated[
        str | None,
        Field(description="New related pack slug (pass empty string to keep unchanged is not supported; omit instead)"),
    ] = None,
) -> str:
    """Update an existing blog post by slug. All fields are optional.

    If translations is provided, it replaces the existing set completely — pass both
    es and en entries if you want to keep both locales."""
    async with get_mcp_session() as db:
        payload = BlogPostUpdate(
            slug=new_slug,
            coverImage=cover_image,
            category=category,
            published=published,
            publishedAt=published_at,
            relatedPackSlug=related_pack_slug,
            translations=translations,  # type: ignore[arg-type]
        )
        post = await blog_service.update_post(db, slug, payload)
        if not post:
            return json.dumps({"error": f"Blog post '{slug}' not found"})
        return json.dumps(_post_summary(post), default=str)


@mcp.tool()
async def delete_blog_post(
    slug: Annotated[str, Field(description="Slug of the post to delete")],
) -> str:
    """Delete a blog post by slug. Returns {deleted: true} on success."""
    async with get_mcp_session() as db:
        deleted = await blog_service.delete_post(db, slug)
        if not deleted:
            return json.dumps({"error": f"Blog post '{slug}' not found"})
        return json.dumps({"deleted": True, "slug": slug})
