# Feature: Product Multiple Images

**Fecha:** 2026-03-31
**Proyecto:** idea-travel-backend

## Descripción

Soporte para múltiples imágenes por producto. Antes cada producto tenía un único campo `image: str`. Ahora existe una relación one-to-many con `ProductImage`, permitiendo galerías ordenadas por `position`.

## Archivos modificados

- `app/domain/models/product.py` — nuevo modelo `ProductImage`, relación `images` en `Product`
- `app/schemas/product.py` — campo `images: list[str]` en `ProductResponse`
- `app/services/product_service.py` — eager load de `Product.images`, mapeo en `_product_to_response`
- `app/seeds/seed_data.py` — productos seed con imágenes extra de ejemplo

## Archivos creados

- `alembic/versions/d1a2b3c4e5f6_add_product_images_table.py` — crea tabla `product_images` con FK a `products` + índice

## Decisiones técnicas

- Se mantiene `image` como imagen principal (campo directo en `products`) por retro-compatibilidad. Las imágenes extra se almacenan en `product_images`.
- `images` en el response incluye sólo las imágenes extra (no la principal), para que el frontend decida cómo combinarlas.
- Ordenación por `position` (integer) permite reordenar sin cambiar el schema.
- `ondelete="CASCADE"` en FK garantiza que al borrar un producto se borran sus imágenes.

## Cómo aplicar

```bash
docker-compose exec api alembic upgrade head
docker-compose exec api python -m app.seeds.seed_data
```
