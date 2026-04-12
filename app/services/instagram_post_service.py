from __future__ import annotations

from datetime import datetime, timezone
import uuid
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.enums import InstagramPostLanguage, InstagramPostStatus
from app.domain.models.instagram_post import (
    InstagramPost,
    InstagramPostSlide,
    InstagramPostTranslation,
)
from app.schemas.instagram_post import InstagramPostCreate, InstagramPostUpdate


class InvalidStatusTransition(Exception):
    """Raised when a state transition is not allowed by the service rules."""


async def _load_with_children(db: AsyncSession, post_id: uuid.UUID) -> InstagramPost | None:
    result = await db.execute(
        select(InstagramPost)
        .where(InstagramPost.id == post_id)
        .options(
            selectinload(InstagramPost.translations),
            selectinload(InstagramPost.slides),
        )
    )
    return result.scalars().unique().first()


async def create_post(db: AsyncSession, data: InstagramPostCreate) -> InstagramPost:
    post = InstagramPost(
        topic=data.topic,
        language=data.language,
        format=data.format,
        slide_count=data.slide_count,
        hashtags=list(data.hashtags),
        mentions=list(data.mentions),
        location_name=data.location_name,
        location_lat=data.location_lat,
        location_lng=data.location_lng,
        target_audience=data.target_audience,
        post_angle=data.post_angle,
        best_publish_time=data.best_publish_time,
        rationale=data.rationale,
        source_mcp_refs=list(data.source_mcp_refs),
        status=InstagramPostStatus.DRAFT,
    )
    for t in data.translations:
        post.translations.append(
            InstagramPostTranslation(
                locale=t.locale,
                hook=t.hook,
                caption=t.caption,
                cta=t.cta,
                first_comment=t.first_comment,
                engagement_hook=t.engagement_hook,
            )
        )
    for s in data.slides:
        post.slides.append(
            InstagramPostSlide(
                order=s.order,
                image_url=s.image_url,
                image_prompt=s.image_prompt,
                image_source=s.image_source,
                alt_text=s.alt_text,
                overlay_text=s.overlay_text,
            )
        )

    db.add(post)
    await db.commit()
    await db.refresh(post, ["translations", "slides"])
    return post


async def get_post(db: AsyncSession, post_id: uuid.UUID) -> InstagramPost | None:
    return await _load_with_children(db, post_id)


async def list_posts(
    db: AsyncSession,
    status=None,
    language=None,
    format=None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[InstagramPost], int]:
    base = select(InstagramPost)
    if status is not None:
        base = base.where(InstagramPost.status == status)
    if language is not None:
        base = base.where(InstagramPost.language == language)
    if format is not None:
        base = base.where(InstagramPost.format == format)

    count_result = await db.execute(
        select(func.count()).select_from(base.subquery())
    )
    total = count_result.scalar() or 0

    query = (
        base.order_by(InstagramPost.created_at.desc())
        .options(
            selectinload(InstagramPost.translations),
            selectinload(InstagramPost.slides),
        )
        .offset(offset)
        .limit(limit)
    )
    result = await db.execute(query)
    items = list(result.scalars().unique().all())
    return items, total


async def update_post(
    db: AsyncSession, post_id: uuid.UUID, data: InstagramPostUpdate
) -> InstagramPost | None:
    post = await _load_with_children(db, post_id)
    if post is None:
        return None

    scalar_fields = {
        "topic",
        "language",
        "format",
        "slide_count",
        "hashtags",
        "mentions",
        "location_name",
        "location_lat",
        "location_lng",
        "target_audience",
        "post_angle",
        "best_publish_time",
        "rationale",
        "source_mcp_refs",
    }
    for field in scalar_fields:
        value = getattr(data, field)
        if value is not None:
            setattr(post, field, value)

    if data.translations is not None:
        for old in list(post.translations):
            await db.delete(old)
        await db.flush()
        for t in data.translations:
            post.translations.append(
                InstagramPostTranslation(
                    locale=t.locale,
                    hook=t.hook,
                    caption=t.caption,
                    cta=t.cta,
                    first_comment=t.first_comment,
                    engagement_hook=t.engagement_hook,
                )
            )

    if data.slides is not None:
        for old in list(post.slides):
            await db.delete(old)
        await db.flush()
        for s in data.slides:
            post.slides.append(
                InstagramPostSlide(
                    order=s.order,
                    image_url=s.image_url,
                    image_prompt=s.image_prompt,
                    image_source=s.image_source,
                    alt_text=s.alt_text,
                    overlay_text=s.overlay_text,
                )
            )

    await db.commit()
    await db.refresh(post, ["translations", "slides"])
    return post


_DELETABLE_STATUSES = {InstagramPostStatus.DRAFT, InstagramPostStatus.REJECTED}


async def delete_post(db: AsyncSession, post_id: uuid.UUID) -> bool:
    post = await _load_with_children(db, post_id)
    if post is None:
        return False
    if post.status not in _DELETABLE_STATUSES:
        raise InvalidStatusTransition(
            f"Cannot delete a post in status {post.status.value}"
        )
    await db.delete(post)
    await db.commit()
    return True


def _required_locales(language: InstagramPostLanguage) -> set[str]:
    if language == InstagramPostLanguage.ES:
        return {"es"}
    if language == InstagramPostLanguage.EN:
        return {"en"}
    return {"es", "en"}


def _validate_for_approval(post: InstagramPost) -> None:
    if not (15 <= len(post.hashtags) <= 30):
        raise InvalidStatusTransition(
            f"Approved posts need 15-30 hashtags, got {len(post.hashtags)}"
        )
    if post.slide_count != len(post.slides):
        raise InvalidStatusTransition(
            f"slide_count={post.slide_count} but {len(post.slides)} slides persisted"
        )
    required = _required_locales(post.language)
    present = {t.locale for t in post.translations}
    missing = required - present
    if missing:
        raise InvalidStatusTransition(
            f"Missing required translations for locales: {sorted(missing)}"
        )


async def transition_status(
    db: AsyncSession,
    post_id: uuid.UUID,
    new_status: InstagramPostStatus,
) -> InstagramPost | None:
    post = await _load_with_children(db, post_id)
    if post is None:
        return None

    if new_status == InstagramPostStatus.APPROVED:
        _validate_for_approval(post)
        if post.approved_at is None:
            post.approved_at = datetime.now(timezone.utc)
    if new_status == InstagramPostStatus.PUBLISHED:
        if post.published_at is None:
            post.published_at = datetime.now(timezone.utc)

    post.status = new_status
    await db.commit()
    await db.refresh(post, ["translations", "slides"])
    return post
