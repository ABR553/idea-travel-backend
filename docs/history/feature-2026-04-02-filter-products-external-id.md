# Feature: Filter products without external_id

**Date:** 2026-04-02
**Proyecto:** idea-travel-backend

## Descripcion
All product query endpoints now exclude products where `external_id` is NULL or empty string. Products without a valid `external_id` cannot generate a working Amazon affiliate link, so they should not be exposed via the API.

## Archivos modificados
- `app/services/product_service.py` — added `external_id` not-null/not-empty filter to `get_products()`
- `app/services/project_service.py` — same filter in `get_project_products()`

## Decisiones tecnicas
- The filter is applied at the base query level (before count and pagination) so both the total count and the results are consistent.
- Applied to both the general `/products` endpoint and the project-specific `/projects/{slug}/products` endpoint.

## Verificacion
- `GET /api/v1/products` returns only products with a valid `external_id`
- `GET /api/v1/projects/tengounviaje-21/products` same behaviour
