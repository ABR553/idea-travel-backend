import pytest


@pytest.mark.asyncio
async def test_list_packs_empty(client):
    response = await client.get("/api/v1/packs")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_packs_with_data(client, seeded_db):
    response = await client.get("/api/v1/packs")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert len(data["data"]) == 1
    pack = data["data"][0]
    assert pack["slug"] == "test-pack"
    assert pack["title"] == "Pack Test"


@pytest.mark.asyncio
async def test_get_pack_by_slug(client, seeded_db):
    response = await client.get("/api/v1/packs/test-pack")
    assert response.status_code == 200
    pack = response.json()
    assert pack["slug"] == "test-pack"
    assert pack["title"] == "Pack Test"
    assert len(pack["destinations"]) == 1
    assert len(pack["route"]) == 1
    assert len(pack["destinations"][0]["accommodations"]) == 1
    assert len(pack["destinations"][0]["experiences"]) == 1
    assert pack["destinations"][0]["accommodations"][0]["tier"] == "budget"
    assert pack["destinations"][0]["experiences"][0]["provider"] == "getyourguide"


@pytest.mark.asyncio
async def test_get_pack_not_found(client):
    response = await client.get("/api/v1/packs/nonexistent-slug")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_pack_locale_es(client, seeded_db):
    response = await client.get("/api/v1/packs/test-pack?locale=es")
    assert response.status_code == 200
    pack = response.json()
    assert pack["title"] == "Pack Test"
    assert pack["destinations"][0]["name"] == "Destino Test"


@pytest.mark.asyncio
async def test_pack_locale_en(client, seeded_db):
    response = await client.get("/api/v1/packs/test-pack?locale=en")
    assert response.status_code == 200
    pack = response.json()
    assert pack["title"] == "Test Pack"
    assert pack["destinations"][0]["name"] == "Test Destination"


@pytest.mark.asyncio
async def test_featured_packs(client, seeded_db):
    response = await client.get("/api/v1/packs/featured")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["featured"] is True


@pytest.mark.asyncio
async def test_pack_has_cache_headers(client, seeded_db):
    response = await client.get("/api/v1/packs/test-pack")
    assert "cache-control" in response.headers
    assert "s-maxage=3600" in response.headers["cache-control"]
