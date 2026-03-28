# Feature: Projects table and product external_id + computed link

**Date:** 2026-03-29

## Description

Added a `projects` table that groups products and provides an affiliate link template. Products now have an `external_id` field and a FK to `projects`. The serializer computes a `link` field per product by substituting `{external_id}` and `{tag_id}` in the project's `link_template`.

## Files created

- `app/domain/models/project.py` — SQLAlchemy model `Project`
- `app/schemas/project.py` — Pydantic schemas `ProjectResponse`, `ProjectCreate`
- `app/services/project_service.py` — `get_projects`, `get_project_by_slug`, `get_project_products`
- `app/api/v1/projects.py` — Endpoints `GET /api/v1/projects`, `GET /api/v1/projects/{slug}`, `GET /api/v1/projects/{slug}/products`
- `alembic/versions/b30399e31d32_add_projects_table_and_product_external_.py` — Migration

## Files modified

- `app/domain/models/product.py` — Added `external_id`, `project_id` FK, `project` relationship
- `app/domain/models/__init__.py` — Exported `Project`
- `app/schemas/product.py` — Added `external_id`, `project_id`, `link` to `ProductResponse`
- `app/services/product_service.py` — `_build_link()` helper, `selectinload(Product.project)` in queries
- `app/api/v1/router.py` — Registered `projects_router` at `/projects`
- `app/admin/views.py` — Added `ProjectAdmin`, updated `ProductAdmin` columns
- `app/main.py` — Added "projects" tag to OpenAPI metadata
- `app/seeds/seed_data.py` — Added `_seed_projects()`, updated `_seed_products(project_id)` with `external_id`

## Key technical decisions

1. `project_id` and `external_id` on `Product` are nullable → backward compatibility with products not belonging to any project.
2. `link_template` is stored on `Project` (not `Product`) → changing the template updates all products in the project automatically.
3. `link` is computed at serialization time (not stored in DB) → no data inconsistency risk.
4. `link_template` is not exposed in `ProjectResponse` (internal field).
5. The project endpoint `/projects/{slug}/products` accepts the same filter/sort/pagination params as `/products`.

## API contract

**GET /api/v1/projects**
```json
[{ "id": "...", "slug": "idea-travel", "name": "Idea Travel", "tag_id": "ideatravel-21" }]
```

**GET /api/v1/projects/idea-travel/products** (same paginated shape as /products)
- Products include `external_id`, `project_id`, `link` fields
- `link` is `null` if product has no project or no external_id

## Verification

- `python -c "from app.main import app; print('OK')"` → OK
- `GET /api/v1/projects` → `[]` (empty list, seed not re-run)
- `GET /api/v1/products?page_size=1` → returns new fields `external_id`, `project_id`, `link`
