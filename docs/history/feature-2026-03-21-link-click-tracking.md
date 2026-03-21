# Feature: Tracking de clicks en links de afiliados y reservas

- **Fecha**: 2026-03-21
- **Solicitado como**: Modelo para guardar la interaccion con los links de accommodations y experiences, registrando fecha/hora de acceso y mostrando contador de clicks en las ultimas 24h

## Descripcion
Sistema de tracking de clicks en los links de reserva (accommodations) y afiliado (experiences). Cuando un usuario hace click para redirigirse a un enlace externo, el frontend llama al endpoint POST correspondiente para registrar la interaccion. En cada response de pack detail, cada accommodation y experience incluye un campo `clicks_last_24h` con el numero de clicks registrados en las ultimas 24 horas.

## Archivos creados
- `app/domain/models/link_click.py` - Modelo SQLAlchemy LinkClick (entity_type, entity_id, clicked_at)
- `app/schemas/click.py` - Schema Pydantic ClickResponse
- `app/services/click_service.py` - Logica de negocio: register_click y get_clicks_last_24h (batch query)
- `app/api/v1/clicks.py` - Endpoints POST para registrar clicks
- `alembic/versions/c0808c8ff02a_add_link_clicks_table.py` - Migracion para crear tabla link_clicks

## Archivos modificados
- `app/domain/models/__init__.py` - Export de LinkClick
- `app/schemas/accommodation.py` - Campo clicksLast24h (alias clicks_last_24h)
- `app/schemas/experience.py` - Campo clicksLast24h (alias clicks_last_24h)
- `app/services/pack_service.py` - Batch query de clicks al construir pack detail response
- `app/api/v1/router.py` - Registro del router de clicks
- `app/main.py` - CORS ampliado a POST, tag de clicks en OpenAPI metadata

## Migraciones
- `c0808c8ff02a_add_link_clicks_table` - Crea tabla `link_clicks` con indice compuesto en (entity_type, entity_id, clicked_at)

## Endpoints nuevos
- `POST /api/v1/clicks/accommodations/{accommodation_id}` - Registra click en accommodation (valida que exista, 404 si no)
- `POST /api/v1/clicks/experiences/{experience_id}` - Registra click en experience (valida que exista, 404 si no)

## Decisiones tecnicas
- **Tabla unica polimorfica** (LinkClick) en vez de dos tablas separadas: reduce complejidad, el indice compuesto mantiene performance
- **Sin FK a accommodations/experiences**: evita dependencias ciclicas y permite flexibilidad futura (tracking de otros entity types)
- **Batch query con IN clause**: evita N+1 al contar clicks de multiples entidades en un solo pack
- **Indice compuesto (entity_type, entity_id, clicked_at)**: optimizado para la query de "clicks en las ultimas 24h por entidad"
- **_pack_to_full_response ahora es async**: necesario para hacer la query de clicks dentro del builder

## Verificacion
- POST click accommodation: 200 OK, click registrado
- POST click experience: 200 OK, click registrado
- POST con ID inexistente: 404 Not found
- GET pack detail: accommodation muestra clicks_last_24h=1 despues de registrar un click
