# Idea Travel Backend - API REST

## Descripcion del Proyecto
API REST para la plataforma de viajes "Idea Travel". Backend que sirve datos a la aplicacion frontend (Next.js) e incluye:
1. **Packs de viaje** - CRUD completo de packs con destinos, rutas, alojamientos por destino (budget/standard/premium) y experiencias con deep links de afiliados
2. **Productos de Amazon** - CRUD de productos de viaje con links de afiliado
3. **Internacionalizacion** - Soporte multiidioma (es/en) con traducciones por entidad
4. **Extensibilidad** - Modelo de datos preparado para anadir mas destinos, experiencias, packs y rutas sin migraciones destructivas

## Stack Tecnologico
- **Framework**: FastAPI (Python 3.12+)
- **Base de datos**: PostgreSQL 16
- **ORM**: SQLAlchemy 2.0+ (async)
- **Migraciones**: Alembic
- **Contenedores**: Docker + Docker Compose
- **Validacion**: Pydantic v2
- **Testing**: pytest + httpx (async)

## Arquitectura
- Arquitectura hexagonal (puertos y adaptadores)
- Principios SOLID
- Patrones: Repository, Service Layer, Unit of Work
- Separacion clara: domain (modelos) / application (servicios) / infrastructure (repos, DB) / api (endpoints)

## Modelo de Datos (resumen)
- **Pack**: Paquete de viaje con multiples destinos
- **Destination**: Destino dentro de un pack (Bangkok, Tokio, etc.)
- **RouteStep**: Paso del itinerario dia a dia, vinculado a un destino
- **Accommodation**: Alojamiento POR DESTINO con tier (budget/standard/premium)
- **Experience**: Actividad/tour con proveedor (GetYourGuide/Civitatis) y link de afiliado
- **Product**: Producto de Amazon con categoria y link de afiliado
- Todas las entidades tienen traducciones en tabla separada (_translations) para i18n

## Comandos del Proyecto

### Workflow de Desarrollo
Ejecutar en este orden:
1. `/research` - Investigacion tecnica sobre la mejor forma de implementar el backend
2. `/plan` - Genera un plan tecnico paso a paso basado en la investigacion
3. `/implement` - Implementa el plan siguiendo SOLID, patrones de diseno y arquitectura hexagonal
4. `/code-review` - Revision de codigo y calidad

### Trabajo del dia a dia
- `/feature <descripcion>` - Nueva funcionalidad (flujo completo: research > plan > implement > verify)
- `/bug <descripcion>` - Diagnosticar y corregir bugs
- `/improve <descripcion>` - Mejoras de codigo, rendimiento, seguridad o funcionalidad
- `/cost` - Estimar coste en dolares de la sesion actual
- `/migrate <descripcion>` - Crear y ejecutar migraciones de base de datos
- `/seed` - Poblar la base de datos con datos iniciales realistas

### Comandos Docker
```bash
docker-compose up --build    # Levantar proyecto (API + PostgreSQL)
docker-compose down          # Parar proyecto
docker-compose exec api bash # Entrar al contenedor de la API
```

### Comandos de Migraciones
```bash
docker-compose exec api alembic revision --autogenerate -m "descripcion"  # Crear migracion
docker-compose exec api alembic upgrade head                               # Aplicar migraciones
docker-compose exec api alembic downgrade -1                               # Revertir ultima migracion
```

### Comandos de Testing
```bash
docker-compose exec api pytest                    # Ejecutar tests
docker-compose exec api pytest -v                 # Tests con detalle
docker-compose exec api pytest --cov=app          # Tests con coverage
```

### Comandos de Seed
```bash
docker-compose exec api python -m app.seeds.seed_data  # Poblar BD con datos iniciales
```

## Convenciones
- Nombres de clases en PascalCase
- Funciones y variables en snake_case
- Archivos de modelos en singular (pack.py, product.py)
- Schemas Pydantic con sufijo: PackCreate, PackResponse, PackUpdate
- Servicios en carpeta `services/`
- No usar `Any` en Python (tipado estricto con mypy)
- Commits en ingles, codigo y comentarios en espanol donde sea necesario
- Endpoints versionados bajo `/api/v1/`
- Respuestas siempre en JSON con estructura consistente
- Filtros por query params, locale por header Accept-Language o query param `?locale=es`

## Estructura de Carpetas
```
idea-travel-backend/
  CLAUDE.md
  docker-compose.yml
  Dockerfile
  .dockerignore
  .gitignore
  .env.example
  requirements.txt
  alembic.ini
  alembic/
    env.py
    versions/
  app/
    __init__.py
    main.py                 # FastAPI app factory
    config.py               # Settings con Pydantic
    database.py             # Engine, SessionLocal, Base
    domain/
      __init__.py
      models/               # SQLAlchemy models
        __init__.py
        base.py             # Base model con timestamps
        pack.py             # Pack, PackTranslation
        destination.py      # Destination, DestinationTranslation
        route_step.py       # RouteStep, RouteStepTranslation
        accommodation.py    # Accommodation, AccommodationTranslation
        experience.py       # Experience, ExperienceTranslation
        product.py          # Product, ProductTranslation
    schemas/                # Pydantic schemas (request/response)
      __init__.py
      pack.py
      destination.py
      accommodation.py
      experience.py
      product.py
      common.py
    services/               # Business logic
      __init__.py
      pack_service.py
      product_service.py
    api/
      __init__.py
      deps.py               # Dependencies (get_db, etc.)
      v1/
        __init__.py
        router.py           # Router principal v1
        packs.py            # Endpoints de packs
        products.py         # Endpoints de productos
        health.py           # Health check
    seeds/
      __init__.py
      seed_data.py          # Datos iniciales realistas
  tests/
    __init__.py
    conftest.py
    test_packs.py
    test_products.py
    test_health.py
  docs/
    research.md
    plan.md
    code-review.md
```

## Relacion con el Frontend
Este backend sirve datos a `idea-travel` (Next.js). Los endpoints deben devolver datos en el formato que el frontend espera:
- Packs con destinos, rutas, alojamientos y experiencias anidados
- Productos con traducciones segun locale
- Cache headers para ISR/SSG del frontend (Cache-Control: public, s-maxage=3600)
