# Feature: Filtros, buscador y ordenacion para packs y productos

- **Fecha**: 2026-03-21
- **Solicitado como**: crea filtros por lo que se pueda filtrar desde el listado de packs y productos, ordenar por precios, buscador por description, filtrar por cantidad de destinos

## Descripcion
Implementacion completa de filtros, busqueda por texto y ordenacion en los endpoints de listado de packs y productos. Los filtros se aplican a nivel SQL para maximo rendimiento.

## Archivos modificados
- `app/services/pack_service.py` - Filtros SQL por precio, duracion, destinos, busqueda ILIKE en traducciones, ordenacion
- `app/services/product_service.py` - Filtros SQL por precio, rating, busqueda ILIKE en traducciones, ordenacion
- `app/api/v1/packs.py` - Nuevos query params con validacion Pydantic
- `app/api/v1/products.py` - Nuevos query params con validacion Pydantic

## Endpoints modificados

### `GET /api/v1/packs`
Nuevos query params:
- `min_price` / `max_price` (float, >=0) - Rango de precio
- `min_days` / `max_days` (int, >=1) - Rango de duracion en dias
- `min_destinations` / `max_destinations` (int, >=1) - Rango de cantidad de destinos
- `search` (str, 2-100 chars) - Busca en title, short_description y description (traducciones, case-insensitive)
- `sort_by` - price_asc, price_desc, duration_asc, duration_desc

### `GET /api/v1/products`
Nuevos query params:
- `min_price` / `max_price` (float, >=0) - Rango de precio
- `min_rating` (float, 0-5) - Rating minimo
- `search` (str, 2-100 chars) - Busca en name y description (traducciones, case-insensitive)
- `sort_by` - price_asc, price_desc, rating_desc

## Decisiones tecnicas
- Busqueda con ILIKE en tablas de traduccion via subquery `IN` para no afectar el eager loading
- Filtro de destinos usa subquery con GROUP BY + COUNT para contar destinos por pack
- COUNT total se ejecuta antes de OFFSET/LIMIT para devolver el total correcto con filtros
- Ordenacion por defecto: created_at DESC (mas recientes primero)
- Validacion de sort_by con pattern regex en Query para evitar valores invalidos

## Verificacion
- Packs filtro precio 500-5000: total=3
- Packs filtro duracion 7-10 dias: total=5
- Packs filtro >=3 destinos: total=5
- Packs busqueda "paris": total=1
- Packs busqueda descripcion "monumentos": total=1
- Products filtro precio 10-50: total=6
- Products filtro rating >=4.5: total=10
- Products busqueda "adaptador": total=1
- Products sort price_desc: 200 OK
