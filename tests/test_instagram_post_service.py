from datetime import datetime, timezone
from decimal import Decimal

import pytest

from app.domain.models.enums import (
    InstagramImageSource,
    InstagramPostFormat,
    InstagramPostLanguage,
    InstagramPostStatus,
)
from app.schemas.instagram_post import (
    InstagramPostCreate,
    InstagramPostSlideIn,
    InstagramPostTranslationIn,
)
from app.services import instagram_post_service as svc


def _minimal_payload(**overrides) -> InstagramPostCreate:
    data = dict(
        topic="Islandia en invierno",
        language=InstagramPostLanguage.ES,
        format=InstagramPostFormat.SINGLE_IMAGE,
        slide_count=1,
        hashtags=[f"tag{i}" for i in range(15)],
        mentions=[],
        translations=[
            InstagramPostTranslationIn(
                locale="es",
                hook="Un destino salvaje",
                caption="Texto completo del caption en español",
            )
        ],
        slides=[
            InstagramPostSlideIn(
                order=0,
                image_url="https://example.com/a.jpg",
                image_source=InstagramImageSource.STOCK,
            )
        ],
    )
    data.update(overrides)
    return InstagramPostCreate(**data)


@pytest.mark.asyncio
async def test_create_post_minimal_draft(db_session):
    payload = _minimal_payload()
    post = await svc.create_post(db_session, payload)

    assert post.id is not None
    assert post.status == InstagramPostStatus.DRAFT
    assert post.topic == "Islandia en invierno"
    assert len(post.translations) == 1
    assert post.translations[0].locale == "es"
    assert len(post.slides) == 1
    assert post.slides[0].order == 0


@pytest.mark.asyncio
async def test_get_post_returns_full_post(db_session):
    payload = _minimal_payload()
    created = await svc.create_post(db_session, payload)

    fetched = await svc.get_post(db_session, created.id)

    assert fetched is not None
    assert fetched.id == created.id
    assert len(fetched.translations) == 1
    assert len(fetched.slides) == 1


@pytest.mark.asyncio
async def test_get_post_missing_returns_none(db_session):
    from uuid import uuid4
    result = await svc.get_post(db_session, uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_list_posts_paginates_and_filters_by_status(db_session):
    for i in range(3):
        await svc.create_post(db_session, _minimal_payload(topic=f"Topic {i}"))

    items, total = await svc.list_posts(db_session, limit=2, offset=0)
    assert total == 3
    assert len(items) == 2

    items_filtered, total_filtered = await svc.list_posts(
        db_session, status=InstagramPostStatus.PUBLISHED
    )
    assert total_filtered == 0
    assert items_filtered == []
