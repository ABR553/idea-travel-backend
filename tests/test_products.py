import pytest


@pytest.mark.asyncio
async def test_list_products_empty(client):
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert data["data"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_products_with_data(client, seeded_db):
    response = await client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["data"][0]["slug"] == "test-product"


@pytest.mark.asyncio
async def test_filter_products_by_category(client, seeded_db):
    response = await client.get("/api/v1/products?category=electronics")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1

    response = await client.get("/api/v1/products?category=luggage")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_get_product_by_slug(client, seeded_db):
    response = await client.get("/api/v1/products/test-product")
    assert response.status_code == 200
    product = response.json()
    assert product["slug"] == "test-product"
    assert product["name"] == "Producto Test"
    assert product["category"] == "electronics"


@pytest.mark.asyncio
async def test_product_not_found(client):
    response = await client.get("/api/v1/products/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_product_locale_en(client, seeded_db):
    response = await client.get("/api/v1/products/test-product?locale=en")
    assert response.status_code == 200
    product = response.json()
    assert product["name"] == "Test Product"


@pytest.mark.asyncio
async def test_product_categories(client):
    response = await client.get("/api/v1/products/categories")
    assert response.status_code == 200
    categories = response.json()
    assert "luggage" in categories
    assert "electronics" in categories
    assert len(categories) == 5


@pytest.mark.asyncio
async def test_product_response_has_no_link_field(client, seeded_db):
    """The deprecated `link` field (interpolated from Project.link_template) must no longer be returned.
    Product links must come from `affiliate_url` / `affiliateUrl` exclusively."""
    list_response = await client.get("/api/v1/products")
    assert list_response.status_code == 200
    item = list_response.json()["data"][0]
    assert "link" not in item, f"`link` field must be removed, got: {item.get('link')!r}"
    assert item.get("affiliate_url") == "https://example.com/prod"

    detail_response = await client.get("/api/v1/products/test-product")
    assert detail_response.status_code == 200
    detail = detail_response.json()
    assert "link" not in detail
    assert detail.get("affiliate_url") == "https://example.com/prod"
