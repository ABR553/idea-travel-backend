from __future__ import annotations

import uuid
from typing import Iterable

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.enums import InstagramPostStatus
from app.domain.models.instagram_post import (
    InstagramPost,
    InstagramPostSlide,
    InstagramPostTranslation,
)
from app.schemas.instagram_post import InstagramPostCreate


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
