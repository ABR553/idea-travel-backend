# Bug: Missing selectinload for Product.images in get_project_products

**Date:** 2026-04-02
**Affected endpoint:** `GET /api/v1/projects/{slug}/products`
**Example:** `/api/v1/projects/tengounviaje-21/products`

## Causa raiz

En `app/services/project_service.py`, la funcion `get_project_products()` no incluia
`selectinload(Product.images)` en las opciones de la query SQLAlchemy.

Al serializar cada producto, `_product_to_response()` accede a `product.images`
(para construir la lista de URLs). Sin eager loading, SQLAlchemy intentaba hacer
lazy-load de esa relacion despues de que la sesion habia avanzado, lo cual lanza
un `MissingGreenlet` o similar error en contextos async.

## Archivos modificados

- `app/services/project_service.py` — linea 102: añadido `selectinload(Product.images)`

## Fix

```python
# ANTES
ordered.options(selectinload(Product.translations), selectinload(Product.project))

# DESPUES
ordered.options(selectinload(Product.translations), selectinload(Product.images), selectinload(Product.project))
```

## Contexto

El mismo patron correcto ya existia en `product_service.get_products()` y en
`product_service.bulk_upsert_products()`, pero no se habia replicado al escribir
`get_project_products()` en `project_service.py`.
