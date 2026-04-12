import json

import pytest

from app.mcp.tools import instagram as ig_tools


def _create_args() -> dict:
    return dict(
        topic="Islandia",
        language="es",
        format="single_image",
        slide_count=1,
        hashtags=[f"tag{i}" for i in range(15)],
        mentions=[],
        translations=[{"locale": "es", "hook": "h", "caption": "c"}],
        slides=[{"order": 0, "image_url": "https://e.com/a.jpg", "image_source": "stock"}],
    )


@pytest.mark.asyncio
async def test_mcp_create_get_update_status_delete_cycle(db_session, monkeypatch):
    # Point the MCP session factory at the test session
    from contextlib import asynccontextmanager

    @asynccontextmanager
    async def _fake_session():
        yield db_session

    monkeypatch.setattr(ig_tools, "get_mcp_session", _fake_session)

    # Create
    created_json = await ig_tools.create_instagram_post(**_create_args())
    created = json.loads(created_json)
    assert created["status"] == "draft"
    post_id = created["id"]

    # Get
    got = json.loads(await ig_tools.get_instagram_post(post_id=post_id))
    assert got["id"] == post_id

    # Update
    upd = json.loads(await ig_tools.update_instagram_post(post_id=post_id, topic="Nuevo"))
    assert upd["topic"] == "Nuevo"

    # Set status (approved)
    approved = json.loads(
        await ig_tools.set_instagram_post_status(post_id=post_id, status="approved")
    )
    assert approved["status"] == "approved"

    # List
    listed = json.loads(await ig_tools.list_instagram_posts())
    assert listed["total"] >= 1

    # Delete blocked in approved
    deleted = json.loads(await ig_tools.delete_instagram_post(post_id=post_id))
    assert "error" in deleted
