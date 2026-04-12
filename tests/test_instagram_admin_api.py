import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.admin import routes as admin_routes
from app.main import app


def _payload() -> dict:
    return {
        "topic": "Islandia",
        "language": "es",
        "format": "single_image",
        "slideCount": 1,
        "hashtags": [f"tag{i}" for i in range(15)],
        "mentions": [],
        "translations": [{"locale": "es", "hook": "h", "caption": "c"}],
        "slides": [{"order": 0, "imageUrl": "https://e.com/a.jpg", "imageSource": "stock"}],
    }


async def _login(client):
    # SQLAdmin login sets a session cookie. The backend uses ADMIN_USERNAME/PASSWORD from env.
    resp = await client.post(
        "/admin/login",
        data={"username": "admin", "password": "admin"},
        follow_redirects=False,
    )
    assert resp.status_code in (302, 303)


@pytest_asyncio.fixture(autouse=True)
async def override_admin_db(db_engine):
    """Override _get_db in admin routes to use the test database engine.

    A new session is created per request so that identity-map state from a
    previous request (e.g. a committed create) does not bleed into subsequent
    requests and trigger lazy-load MissingGreenlet errors.
    """
    test_session_factory = async_sessionmaker(
        db_engine, class_=AsyncSession, expire_on_commit=False
    )

    async def _override():
        async with test_session_factory() as session:
            yield session

    app.dependency_overrides[admin_routes._get_db] = _override
    yield
    app.dependency_overrides.pop(admin_routes._get_db, None)


@pytest.mark.asyncio
async def test_endpoints_require_auth(client):
    resp = await client.get("/admin/api/instagram-posts")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_create_get_patch_list_delete_cycle(client):
    await _login(client)

    # Create
    create = await client.post("/admin/api/instagram-posts", json=_payload())
    assert create.status_code == 201, create.text
    created_id = create.json()["id"]

    # Get
    got = await client.get(f"/admin/api/instagram-posts/{created_id}")
    assert got.status_code == 200
    assert got.json()["topic"] == "Islandia"

    # Patch
    patched = await client.patch(
        f"/admin/api/instagram-posts/{created_id}",
        json={"topic": "Groenlandia"},
    )
    assert patched.status_code == 200
    assert patched.json()["topic"] == "Groenlandia"

    # List
    listed = await client.get("/admin/api/instagram-posts")
    assert listed.status_code == 200
    body = listed.json()
    assert body["total"] >= 1
    assert any(item["id"] == created_id for item in body["items"])

    # Delete (still in draft)
    deleted = await client.delete(f"/admin/api/instagram-posts/{created_id}")
    assert deleted.status_code == 204


@pytest.mark.asyncio
async def test_status_and_publish_endpoints(client):
    await _login(client)

    created_id = (await client.post("/admin/api/instagram-posts", json=_payload())).json()["id"]

    # Transition to approved: happy path
    transitioned = await client.post(
        f"/admin/api/instagram-posts/{created_id}/status",
        json={"status": "approved"},
    )
    assert transitioned.status_code == 200
    assert transitioned.json()["status"] == "approved"

    # Publish
    published = await client.post(f"/admin/api/instagram-posts/{created_id}/publish")
    assert published.status_code == 200
    body = published.json()
    assert body["status"] in ("approved", "scheduled")
    assert len(body["publishAttempts"]) == 1

    # Delete now blocked (approved/scheduled)
    blocked = await client.delete(f"/admin/api/instagram-posts/{created_id}")
    assert blocked.status_code == 409
