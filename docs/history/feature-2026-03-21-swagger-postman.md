# Feature: Swagger UI + Postman Collection auto-generada

- **Fecha**: 2026-03-21
- **Solicitado como**: "anade el swagger al proyecto y genera un json para poder importarme la collection a postman"

## Descripcion
Se mejoro la documentacion OpenAPI de FastAPI con metadata completa (tags, descriptions por endpoint)
y se creo un script que genera automaticamente una Postman Collection v2.1 al arrancar Docker.

## Archivos creados
- `scripts/__init__.py` - Package init
- `scripts/generate_postman.py` - Script que convierte OpenAPI spec a Postman Collection v2.1
- `docs/postman_collection.json` - Collection generada automaticamente (auto-regenerada en cada arranque)
- `docs/history/feature-2026-03-21-swagger-postman.md` - Este archivo

## Archivos modificados
- `app/main.py` - Anadida metadata OpenAPI: tags con descriptions, description detallada de la API
- `app/api/v1/health.py` - Anadido summary/description al endpoint
- `app/api/v1/packs.py` - Anadido summary/description a los 3 endpoints
- `app/api/v1/products.py` - Anadido summary/description a los 3 endpoints
- `entrypoint.sh` - Anadido paso de generacion de Postman collection antes de arrancar uvicorn

## Endpoints nuevos
Ninguno nuevo. Se mejoraron las descripciones de los existentes.

## Decisiones tecnicas
- La collection se genera **offline** importando la app de FastAPI directamente (sin HTTP), evitando dependencias de timing en el arranque
- Se ejecuta en el entrypoint despues de migraciones y antes de uvicorn
- La collection usa variables de Postman (`{{base_url}}`, `{{locale}}`) para flexibilidad
- El archivo se regenera en cada `docker-compose up`, siempre actualizado

## Verificacion
- Swagger UI accesible en `http://localhost:8100/docs`
- ReDoc accesible en `http://localhost:8100/redoc`
- OpenAPI JSON en `http://localhost:8100/openapi.json`
- Postman collection en `docs/postman_collection.json` - importable directamente en Postman
