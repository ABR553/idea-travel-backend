import json
from typing import Annotated

from pydantic import Field

from app.mcp.db import get_mcp_session
from app.mcp.instance import mcp
from app.services import product_service


@mcp.tool()
async def list_products(
    category: Annotated[str | None, Field(description="Filter by category: luggage, electronics, accessories, comfort, photography")] = None,
    search: Annotated[str | None, Field(description="Search text in product name/description")] = None,
    min_price: Annotated[float | None, Field(description="Minimum price filter")] = None,
    max_price: Annotated[float | None, Field(description="Maximum price filter")] = None,
    min_rating: Annotated[float | None, Field(description="Minimum rating 0-5")] = None,
    sort_by: Annotated[str | None, Field(description="Sort: price_asc, price_desc, rating_desc")] = None,
    page: Annotated[int, Field(description="Page number, 1-indexed")] = 1,
    page_size: Annotated[int, Field(description="Items per page, max 50")] = 10,
    locale: Annotated[str, Field(description="Language: es or en")] = "es",
) -> str:
    """Search and list travel products with optional filters and pagination."""
    async with get_mcp_session() as db:
        items, total = await product_service.get_products(
            db, locale, category=category, search=search,
            min_price=min_price, max_price=max_price,
            min_rating=min_rating, sort_by=sort_by,
            page=page, page_size=page_size,
        )
        return json.dumps({
            "data": [item.model_dump(by_alias=True) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
        }, default=str)


@mcp.tool()
async def get_product(
    slug: Annotated[str, Field(description="Product URL slug")],
    locale: Annotated[str, Field(description="Language: es or en")] = "es",
) -> str:
    """Get a single product by its slug."""
    async with get_mcp_session() as db:
        product = await product_service.get_product_by_slug(db, slug, locale)
        if not product:
            return json.dumps({"error": f"Product '{slug}' not found"})
        return json.dumps(product.model_dump(by_alias=True), default=str)


from app.services import project_service
from app.schemas.product import ProductBulkUpsertRequest


@mcp.tool()
async def upsert_products(
    project_slug: Annotated[str, Field(description="Project slug to add products to. Use list_projects to find it.")],
    items: Annotated[list[dict], Field(description=(
        "Array of product objects. Each item: {"
        "external_id: string (Amazon ASIN), "
        "slug: string (URL-friendly id), "
        "category: string (luggage|electronics|accessories|comfort|photography), "
        "price: number, "
        "currency: string (default EUR), "
        "affiliate_url: string (Amazon product URL), "
        "image: string (primary image URL), "
        "rating: number (0-5), "
        "images: string[] (additional image URLs, optional), "
        "translations: [{locale: 'es'|'en', name: string, description: string}]"
        "}"
    ))],
    locale: Annotated[str, Field(description="Language for response: es or en")] = "es",
) -> str:
    """Create or update products in a project. Uses (project_id, external_id) as unique key.
    Existing products are updated (slug never changes). Translations are upserted per locale."""
    async with get_mcp_session() as db:
        project = await project_service.get_project_model_by_slug(db, project_slug)
        if not project:
            return json.dumps({"error": f"Project '{project_slug}' not found"})

        payload = ProductBulkUpsertRequest(items=items)
        result = await product_service.bulk_upsert_products(db, project, payload, locale)
        return json.dumps(result.model_dump(by_alias=True), default=str)


@mcp.tool()
async def delete_products(
    project_slug: Annotated[str, Field(description="Project slug")],
    external_ids: Annotated[list[str] | None, Field(description="List of ASINs to delete. If omitted, deletes ALL products in the project.")] = None,
) -> str:
    """Delete products from a project by their external IDs (ASINs)."""
    async with get_mcp_session() as db:
        project = await project_service.get_project_model_by_slug(db, project_slug)
        if not project:
            return json.dumps({"error": f"Project '{project_slug}' not found"})

        deleted = await product_service.bulk_delete_products(db, project, external_ids)
        return json.dumps({"deleted": deleted})
