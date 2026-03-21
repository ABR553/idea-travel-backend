import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.link_click import LinkClick


async def register_click(
    db: AsyncSession,
    entity_type: str,
    entity_id: uuid.UUID,
) -> LinkClick:
    click = LinkClick(entity_type=entity_type, entity_id=entity_id)
    db.add(click)
    await db.commit()
    return click


async def get_clicks_last_24h(
    db: AsyncSession,
    entity_type: str,
    entity_ids: list[uuid.UUID],
) -> dict[uuid.UUID, int]:
    """Devuelve un dict {entity_id: count} con los clicks de las ultimas 24h."""
    if not entity_ids:
        return {}

    since = datetime.now(timezone.utc) - timedelta(hours=24)
    query = (
        select(
            LinkClick.entity_id,
            func.count(LinkClick.id).label("click_count"),
        )
        .where(
            LinkClick.entity_type == entity_type,
            LinkClick.entity_id.in_(entity_ids),
            LinkClick.clicked_at >= since,
        )
        .group_by(LinkClick.entity_id)
    )
    result = await db.execute(query)
    return {row.entity_id: row.click_count for row in result.all()}
