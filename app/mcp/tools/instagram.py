import json
from typing import Annotated
from uuid import UUID

from pydantic import Field

from app.domain.models.enums import InstagramPostStatus
from app.mcp.db import get_mcp_session
from app.mcp.instance import mcp
from app.schemas.instagram_post import (
    InstagramPostCreate,
    InstagramPostUpdate,
)
from app.services import instagram_post_service


def _post_full(post) -> dict:
    return {
        "id": str(post.id),
        "topic": post.topic,
        "status": post.status.value if hasattr(post.status, "value") else post.status,
        "language": post.language.value if hasattr(post.language, "value") else post.language,
        "format": post.format.value if hasattr(post.format, "value") else post.format,
        "slide_count": post.slide_count,
        "hashtags": post.hashtags,
        "mentions": post.mentions,
        "location_name": post.location_name,
        "location_lat": str(post.location_lat) if post.location_lat is not None else None,
        "location_lng": str(post.location_lng) if post.location_lng is not None else None,
        "target_audience": post.target_audience,
        "post_angle": post.post_angle.value if post.post_angle else None,
        "best_publish_time": post.best_publish_time.isoformat() if post.best_publish_time else None,
        "rationale": post.rationale,
        "source_mcp_refs": post.source_mcp_refs,
        "instagram_post_id": post.instagram_post_id,
        "publish_attempts": post.publish_attempts,
        "approved_at": post.approved_at.isoformat() if post.approved_at else None,
        "published_at": post.published_at.isoformat() if post.published_at else None,
        "created_at": post.created_at.isoformat() if post.created_at else None,
        "updated_at": post.updated_at.isoformat() if post.updated_at else None,
        "translations": [
            {
                "locale": t.locale,
                "hook": t.hook,
                "caption": t.caption,
                "cta": t.cta,
                "first_comment": t.first_comment,
                "engagement_hook": t.engagement_hook,
            }
            for t in post.translations
        ],
        "slides": [
            {
                "order": s.order,
                "image_url": s.image_url,
                "image_prompt": s.image_prompt,
                "image_source": s.image_source.value if hasattr(s.image_source, "value") else s.image_source,
                "alt_text": s.alt_text,
                "overlay_text": s.overlay_text,
            }
            for s in sorted(post.slides, key=lambda x: x.order)
        ],
    }


@mcp.tool()
async def list_instagram_posts(
    status: Annotated[str | None, Field(description="Filter by status: draft|pending_review|approved|scheduled|published|rejected")] = None,
    language: Annotated[str | None, Field(description="Filter by language: es|en|bilingual")] = None,
    format: Annotated[str | None, Field(description="Filter by format: single_image|carousel")] = None,
    limit: Annotated[int, Field(description="Max items, default 50")] = 50,
    offset: Annotated[int, Field(description="Offset for pagination")] = 0,
) -> str:
    """List Instagram posts with optional filters."""
    async with get_mcp_session() as db:
        items, total = await instagram_post_service.list_posts(
            db, status=status, language=language, format=format, limit=limit, offset=offset
        )
        data = [
            {
                "id": str(p.id),
                "topic": p.topic,
                "status": p.status.value if hasattr(p.status, "value") else p.status,
                "language": p.language.value if hasattr(p.language, "value") else p.language,
                "format": p.format.value if hasattr(p.format, "value") else p.format,
                "slide_count": p.slide_count,
                "first_slide_url": (
                    sorted(p.slides, key=lambda s: s.order)[0].image_url if p.slides else None
                ),
                "created_at": p.created_at.isoformat() if p.created_at else None,
                "updated_at": p.updated_at.isoformat() if p.updated_at else None,
            }
            for p in items
        ]
        return json.dumps({"items": data, "total": total, "limit": limit, "offset": offset})


@mcp.tool()
async def get_instagram_post(
    post_id: Annotated[str, Field(description="UUID of the post")],
) -> str:
    """Fetch the full Instagram post by id."""
    async with get_mcp_session() as db:
        post = await instagram_post_service.get_post(db, UUID(post_id))
        if not post:
            return json.dumps({"error": f"Instagram post '{post_id}' not found"})
        return json.dumps(_post_full(post))


@mcp.tool()
async def create_instagram_post(
    topic: Annotated[str, Field(description="Input topic, e.g. 'Islandia en invierno'")],
    language: Annotated[str, Field(description="es | en | bilingual")],
    format: Annotated[str, Field(description="single_image | carousel")],
    slide_count: Annotated[int, Field(description="Number of slides 1-10")],
    translations: Annotated[list[dict], Field(description="Array of {locale, hook, caption, cta?, first_comment?, engagement_hook?}")],
    slides: Annotated[list[dict], Field(description="Array of {order, image_url, image_source, image_prompt?, alt_text?, overlay_text?}")],
    hashtags: Annotated[list[str] | None, Field(description="15-30 hashtags without the #")] = None,
    mentions: Annotated[list[str] | None, Field(description="@accounts without the @")] = None,
    location_name: Annotated[str | None, Field(description="Location name")] = None,
    location_lat: Annotated[float | None, Field(description="Latitude")] = None,
    location_lng: Annotated[float | None, Field(description="Longitude")] = None,
    target_audience: Annotated[str | None, Field(description="Internal audience note")] = None,
    post_angle: Annotated[str | None, Field(description="inspirational | practical_tip | list | storytelling")] = None,
    best_publish_time: Annotated[str | None, Field(description="ISO datetime")] = None,
    rationale: Annotated[str | None, Field(description="Why this post should perform well")] = None,
    source_mcp_refs: Annotated[list[dict] | None, Field(description="List of {kind, id}")] = None,
) -> str:
    """Create a new Instagram post draft. All content fields must be pre-composed."""
    async with get_mcp_session() as db:
        payload = InstagramPostCreate.model_validate(
            {
                "topic": topic,
                "language": language,
                "format": format,
                "slideCount": slide_count,
                "hashtags": hashtags or [],
                "mentions": mentions or [],
                "locationName": location_name,
                "locationLat": location_lat,
                "locationLng": location_lng,
                "targetAudience": target_audience,
                "postAngle": post_angle,
                "bestPublishTime": best_publish_time,
                "rationale": rationale,
                "sourceMcpRefs": source_mcp_refs or [],
                "translations": translations,
                "slides": slides,
            }
        )
        post = await instagram_post_service.create_post(db, payload)
        # Reload to avoid MissingGreenlet errors when accessing scalar columns
        post = await instagram_post_service.get_post(db, post.id)
        return json.dumps(_post_full(post))


@mcp.tool()
async def update_instagram_post(
    post_id: Annotated[str, Field(description="UUID of the post to update")],
    topic: Annotated[str | None, Field(description="New topic")] = None,
    language: Annotated[str | None, Field(description="es | en | bilingual")] = None,
    format: Annotated[str | None, Field(description="single_image | carousel")] = None,
    slide_count: Annotated[int | None, Field(description="1-10")] = None,
    hashtags: Annotated[list[str] | None, Field(description="Replace all hashtags")] = None,
    mentions: Annotated[list[str] | None, Field(description="Replace all mentions")] = None,
    location_name: Annotated[str | None, Field(description="Location name")] = None,
    location_lat: Annotated[float | None, Field(description="Latitude")] = None,
    location_lng: Annotated[float | None, Field(description="Longitude")] = None,
    target_audience: Annotated[str | None, Field(description="Internal audience note")] = None,
    post_angle: Annotated[str | None, Field(description="inspirational | practical_tip | list | storytelling")] = None,
    best_publish_time: Annotated[str | None, Field(description="ISO datetime")] = None,
    rationale: Annotated[str | None, Field(description="Why this post should perform well")] = None,
    source_mcp_refs: Annotated[list[dict] | None, Field(description="Replace source refs")] = None,
    translations: Annotated[list[dict] | None, Field(description="If provided REPLACES translations")] = None,
    slides: Annotated[list[dict] | None, Field(description="If provided REPLACES slides")] = None,
) -> str:
    """Update any subset of fields on an existing Instagram post."""
    async with get_mcp_session() as db:
        payload = InstagramPostUpdate.model_validate(
            {
                "topic": topic,
                "language": language,
                "format": format,
                "slideCount": slide_count,
                "hashtags": hashtags,
                "mentions": mentions,
                "locationName": location_name,
                "locationLat": location_lat,
                "locationLng": location_lng,
                "targetAudience": target_audience,
                "postAngle": post_angle,
                "bestPublishTime": best_publish_time,
                "rationale": rationale,
                "sourceMcpRefs": source_mcp_refs,
                "translations": translations,
                "slides": slides,
            }
        )
        post = await instagram_post_service.update_post(db, UUID(post_id), payload)
        if not post:
            return json.dumps({"error": f"Instagram post '{post_id}' not found"})
        # Reload to avoid MissingGreenlet errors when accessing scalar columns
        post = await instagram_post_service.get_post(db, post.id)
        return json.dumps(_post_full(post))


@mcp.tool()
async def set_instagram_post_status(
    post_id: Annotated[str, Field(description="UUID of the post")],
    status: Annotated[str, Field(description="draft|pending_review|approved|scheduled|published|rejected")],
) -> str:
    """Change the status of a post. Transition to 'approved' validates hashtags, slides and translations."""
    async with get_mcp_session() as db:
        try:
            post = await instagram_post_service.transition_status(
                db, UUID(post_id), InstagramPostStatus(status)
            )
        except instagram_post_service.InvalidStatusTransition as e:
            return json.dumps({"error": str(e)})
        if not post:
            return json.dumps({"error": f"Instagram post '{post_id}' not found"})
        # Reload to avoid MissingGreenlet errors when accessing scalar columns
        post = await instagram_post_service.get_post(db, post.id)
        return json.dumps(
            {
                "id": str(post.id),
                "status": post.status.value,
                "approved_at": post.approved_at.isoformat() if post.approved_at else None,
                "published_at": post.published_at.isoformat() if post.published_at else None,
            }
        )


@mcp.tool()
async def delete_instagram_post(
    post_id: Annotated[str, Field(description="UUID of the post to delete")],
) -> str:
    """Delete a draft or rejected post. Returns an error for any other status."""
    async with get_mcp_session() as db:
        try:
            deleted = await instagram_post_service.delete_post(db, UUID(post_id))
        except instagram_post_service.InvalidStatusTransition as e:
            return json.dumps({"error": str(e)})
        if not deleted:
            return json.dumps({"error": f"Instagram post '{post_id}' not found"})
        return json.dumps({"deleted": True, "id": post_id})
