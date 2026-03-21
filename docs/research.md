# Investigacion Tecnica - Idea Travel Backend

**Fecha**: 2026-03-21
**Objetivo**: Investigar las mejores practicas para implementar el backend de Idea Travel

---

## 1. Resumen Ejecutivo

### Decisiones Clave

| Decision | Eleccion | Justificacion |
|----------|----------|---------------|
| Framework | FastAPI 0.115+ | Async nativo, auto-documentacion OpenAPI, rendimiento superior |
| ORM | SQLAlchemy 2.0+ async | ORM mas maduro de Python, soporte async first-class, ecosystem Alembic |
| DB | PostgreSQL 16 | Indices avanzados, JSONB para amenities, fiabilidad probada |
| Validacion | Pydantic v2 | Integrado con FastAPI, serialization de modelos anidados, rendimiento 5-50x vs v1 |
| i18n | Tablas _translations separadas | Integridad relacional, indices optimizables, queries eficientes |
| Migraciones | Alembic + autogenerate | Estandar de facto para SQLAlchemy, soporte async |
| Contenedor | Docker + Docker Compose | Hot reload en dev, multi-stage en produccion |
| Testing | pytest + httpx AsyncClient | Testing async nativo, fixtures con scope function para aislamiento |

### Analisis del Frontend

El frontend Next.js define las siguientes interfaces que el backend debe satisfacer:
- **Pack**: id, slug, title, description, shortDescription, destinations[], route[], accommodations[3], experiences[], coverImage, duration, durationDays, price{from,to,currency}, featured
- **Destination**: name, country, description, image
- **RouteStep**: day, title, description, destination (nombre del destino)
- **Accommodation**: id, name, tier(budget|standard|premium), description, pricePerNight, currency, image, amenities[], rating
- **Experience**: id, title, description, provider(getyourguide|civitatis), affiliateUrl, price, currency, duration, image, rating
- **Product**: id, slug, name, description, category(luggage|electronics|accessories|comfort|photography), price, currency, affiliateUrl, image, rating

**NOTA CRITICA**: En el frontend actual, accommodations y experiences estan a nivel de Pack (no de Destination). Sin embargo, el requerimiento es que en el backend sean POR DESTINO. La API debe transformar los datos para mantener compatibilidad con el frontend actual mientras la base de datos modela la relacion correcta (Destination -> Accommodations/Experiences).

---

## 2. Stack Recomendado

### Versiones Especificas

| Tecnologia | Version | Motivo |
|------------|---------|--------|
| Python | 3.12+ | Performance improvements, TaskGroups, mejor tipado |
| FastAPI | >=0.115.0 | Lifespan events, mejoras en dependency injection |
| SQLAlchemy | >=2.0.36 | Async estable, AsyncAttrs mixin, selectinload optimizado |
| Pydantic | >=2.10 | model_dump/model_validate, TypeAdapter, computed fields |
| Alembic | >=1.14 | Template async, autogenerate mejorado |
| PostgreSQL | 16 | Logical replication mejorada, performance improvements |
| asyncpg | >=0.30 | Driver async mas rapido para PostgreSQL |
| uvicorn | >=0.34 | ASGI server con hot reload, HTTP/2 |
| httpx | >=0.28 | AsyncClient para testing |
| pytest | >=8.0 | Mejoras en async fixtures |
| pytest-asyncio | >=0.24 | asyncio_mode="auto", scope management |

### Dependencias Secundarias
- `python-dotenv`: Carga de variables de entorno
- `gunicorn`: Process manager en produccion (con uvicorn workers)

---

## 3. Arquitectura Propuesta

### Arquitectura Hexagonal (Ports & Adapters)

```
                    ┌─────────────────────────────────┐
                    │           API Layer              │
                    │  (FastAPI routers, middleware)    │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │        Application Layer         │
                    │   (Services / Use Cases)         │
                    │   PackService, ProductService    │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │         Domain Layer             │
                    │   (SQLAlchemy Models / Entities) │
                    │   Pack, Destination, Product...  │
                    └──────────────┬──────────────────┘
                                   │
                    ┌──────────────▼──────────────────┐
                    │      Infrastructure Layer        │
                    │   (Database, External APIs)      │
                    │   AsyncSession, Engine           │
                    └─────────────────────────────────┘
```

### Patron de Capas

1. **API (app/api/)**: Routers FastAPI, request/response handling, dependency injection
2. **Schemas (app/schemas/)**: Pydantic models para validacion y serialization
3. **Services (app/services/)**: Logica de negocio, orquestacion de queries
4. **Domain (app/domain/models/)**: SQLAlchemy models, relaciones, constraints
5. **Infrastructure (app/database.py)**: Engine, session factory, connection pooling

### Flujo de una Request

```
HTTP Request
  → FastAPI Router (api/v1/packs.py)
    → Dependency Injection (get_db session)
      → Service Layer (pack_service.py)
        → SQLAlchemy Query (eager loading con selectinload)
          → PostgreSQL
        ← SQLAlchemy Models
      ← Pydantic Schema (serialization)
    ← JSON Response + Cache Headers
```

### Patrones Aplicados

- **Repository implicicto**: SQLAlchemy async session como repositorio (no se abstrae innecesariamente)
- **Service Layer**: Logica de negocio en services, no en routers
- **Dependency Injection**: FastAPI Depends() para session y locale
- **DTOs**: Pydantic schemas como objetos de transferencia

**Justificacion de no usar Repository Pattern explicicto**: Para un proyecto de este tamano, abstraer SQLAlchemy detras de un repositorio anade complejidad sin beneficio claro. Los services usan directamente AsyncSession, que ya proporciona una API limpia de queries. Si en el futuro se necesita cambiar de ORM (improbable), se puede refactorizar.

---

## 4. Modelo de Datos

### Estrategia de Internacionalizacion

**Patron elegido: Tabla de traduccion separada por entidad**

```
packs                          pack_translations
┌──────────────────┐           ┌──────────────────────┐
│ id (PK)          │──────────<│ id (PK)              │
│ slug (UNIQUE)    │           │ pack_id (FK)          │
│ cover_image      │           │ locale (es|en)        │
│ duration_days    │           │ title                 │
│ price_from       │           │ description           │
│ price_to         │           │ short_description     │
│ price_currency   │           │ UNIQUE(pack_id,locale)│
│ featured         │           └──────────────────────┘
│ created_at       │
│ updated_at       │
└──────────────────┘
```

**Ventajas**:
- Integridad referencial fuerte (FK, UNIQUE constraints)
- Queries optimizables con indices
- JOIN eficiente con filtro por locale
- Sin parsing JSON en queries
- Facilmente extensible a mas idiomas

### Diagrama de Relaciones Completo

```
Pack (1) ──────< (N) PackTranslation
  │
  ├──< (N) Destination (1) ──────< (N) DestinationTranslation
  │           │
  │           ├──< (N) Accommodation (1) ──< (N) AccommodationTranslation
  │           │
  │           └──< (N) Experience (1) ──< (N) ExperienceTranslation
  │
  └──< (N) RouteStep (1) ──────< (N) RouteStepTranslation
                │
                └──> (1) Destination (FK)
```

### Tablas Principales

**packs**
- id: UUID PK
- slug: VARCHAR(255) UNIQUE INDEX
- cover_image: TEXT
- duration: VARCHAR(50) -- "10 dias" (campo traducible movido a translations)
- duration_days: INTEGER
- price_from: DECIMAL(10,2)
- price_to: DECIMAL(10,2)
- price_currency: VARCHAR(3) DEFAULT 'EUR'
- featured: BOOLEAN DEFAULT false
- created_at: TIMESTAMP
- updated_at: TIMESTAMP

**destinations**
- id: UUID PK
- pack_id: UUID FK -> packs.id (ON DELETE CASCADE)
- image: TEXT
- display_order: INTEGER DEFAULT 0
- created_at, updated_at

**route_steps**
- id: UUID PK
- pack_id: UUID FK -> packs.id (ON DELETE CASCADE)
- destination_id: UUID FK -> destinations.id
- day: INTEGER
- created_at, updated_at

**accommodations**
- id: UUID PK
- destination_id: UUID FK -> destinations.id (ON DELETE CASCADE)
- tier: VARCHAR(20) CHECK (budget|standard|premium)
- price_per_night: DECIMAL(10,2)
- currency: VARCHAR(3) DEFAULT 'EUR'
- image: TEXT
- amenities: JSONB DEFAULT '[]' -- array simple, JSONB es ideal aqui
- rating: DECIMAL(2,1)
- created_at, updated_at

**experiences**
- id: UUID PK
- destination_id: UUID FK -> destinations.id (ON DELETE CASCADE)
- provider: VARCHAR(20) CHECK (getyourguide|civitatis)
- affiliate_url: TEXT
- price: DECIMAL(10,2)
- currency: VARCHAR(3) DEFAULT 'EUR'
- image: TEXT
- rating: DECIMAL(2,1)
- created_at, updated_at

**products**
- id: UUID PK
- slug: VARCHAR(255) UNIQUE INDEX
- category: VARCHAR(20) CHECK (luggage|electronics|accessories|comfort|photography)
- price: DECIMAL(10,2)
- currency: VARCHAR(3) DEFAULT 'EUR'
- affiliate_url: TEXT
- image: TEXT
- rating: DECIMAL(2,1)
- created_at, updated_at

### Tablas de Traduccion (patron repetido)
Cada tabla `_translations` contiene:
- id: UUID PK
- {entity}_id: UUID FK -> {entity}.id (ON DELETE CASCADE)
- locale: VARCHAR(5)
- campos de texto traducibles
- UNIQUE({entity}_id, locale)

### Indices Recomendados

```sql
-- Busqueda por slug (GET /packs/:slug)
CREATE UNIQUE INDEX idx_packs_slug ON packs(slug);
CREATE UNIQUE INDEX idx_products_slug ON products(slug);

-- Filtro por locale en traducciones
CREATE INDEX idx_pack_translations_locale ON pack_translations(pack_id, locale);
CREATE INDEX idx_destination_translations_locale ON destination_translations(destination_id, locale);
CREATE INDEX idx_accommodation_translations_locale ON accommodation_translations(accommodation_id, locale);
CREATE INDEX idx_experience_translations_locale ON experience_translations(experience_id, locale);
CREATE INDEX idx_route_step_translations_locale ON route_step_translations(route_step_id, locale);
CREATE INDEX idx_product_translations_locale ON product_translations(product_id, locale);

-- Filtro por featured
CREATE INDEX idx_packs_featured ON packs(featured) WHERE featured = true;

-- Filtro por categoria
CREATE INDEX idx_products_category ON products(category);

-- Orden de destinos y ruta
CREATE INDEX idx_destinations_order ON destinations(pack_id, display_order);
CREATE INDEX idx_route_steps_day ON route_steps(pack_id, day);
```

---

## 5. API Design

### Endpoints v1

```
GET  /api/v1/health                    # Health check
GET  /api/v1/packs                     # Lista packs (con filtros)
GET  /api/v1/packs/:slug               # Detalle pack completo
GET  /api/v1/packs/featured            # Packs destacados
GET  /api/v1/products                  # Lista productos (con filtros)
GET  /api/v1/products/:slug            # Detalle producto
GET  /api/v1/products/categories       # Categorias disponibles
```

### Query Parameters

```
?locale=es|en           # Idioma (default: es, tambien via Accept-Language header)
?category=electronics   # Filtro por categoria (productos)
?featured=true          # Filtro featured (packs)
?page=1&page_size=10    # Paginacion
```

### Resolucion de Locale

Prioridad:
1. Query param `?locale=es`
2. Header `Accept-Language: en`
3. Default: `es`

### Formato de Respuesta

```json
// GET /api/v1/packs
{
  "data": [...],
  "total": 6,
  "page": 1,
  "page_size": 10
}

// GET /api/v1/packs/:slug
{
  "id": "...",
  "slug": "tailandia-aventura-tropical",
  "title": "Tailandia: Aventura Tropical",
  ...
}

// Errores
{
  "detail": "Pack not found"
}
```

### Cache Headers

```
Cache-Control: public, s-maxage=3600, stale-while-revalidate=86400
```

- `s-maxage=3600`: CDN/ISR cachea 1 hora
- `stale-while-revalidate=86400`: Permite servir stale mientras revalida (24h)

### Compatibilidad con Frontend

El frontend actual espera accommodations y experiences a nivel de Pack. La API GET de pack debe:
1. Cargar accommodations y experiences por destino desde la BD
2. Serializar aplanando al nivel de pack si el frontend lo requiere, O devolver por destino si el frontend se adapta
3. **Decision**: Devolver por destino (estructura correcta) y adaptar el frontend. Esto es mas limpio y extensible.

---

## 6. Docker Setup

### Dockerfile (Multi-stage)

```dockerfile
# Stage 1: Base con dependencias
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Stage 2: Development (hot reload)
FROM base AS development
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# Stage 3: Production
FROM base AS production
COPY . .
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Docker Compose

```yaml
services:
  api:
    build: .
    target: development  # En dev
    ports: ["8000:8000"]
    volumes: [".:/app"]  # Hot reload
    environment:
      DATABASE_URL: postgresql+asyncpg://user:pass@db:5432/ideatravel
    depends_on:
      db:
        condition: service_healthy

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: ideatravel
      POSTGRES_USER: ideatravel
      POSTGRES_PASSWORD: ideatravel
    ports: ["5432:5432"]
    volumes: [postgres_data:/var/lib/postgresql/data]
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ideatravel"]
      interval: 5s
      timeout: 5s
      retries: 5
```

### Entrypoint con migraciones automaticas

```bash
#!/bin/bash
alembic upgrade head
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 7. Testing Strategy

### Piramide de Tests

1. **API Tests** (prioritarios): Tests de endpoints con httpx.AsyncClient
2. **Service Tests**: Tests de logica de negocio con session mockeada o real
3. **Model Tests**: Tests de validacion Pydantic schemas

### Setup de Tests

```python
# conftest.py
@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async_session = async_sessionmaker(engine, expire_on_commit=False)
    async with async_session() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest_asyncio.fixture
async def client(async_session):
    app.dependency_overrides[get_db] = lambda: async_session
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```

### Tests Prioritarios
- GET /api/v1/health -> 200
- GET /api/v1/packs -> lista packs con locale es y en
- GET /api/v1/packs/:slug -> pack completo con destinos anidados
- GET /api/v1/products -> lista productos filtrable por categoria
- GET /api/v1/products/:slug -> producto con traduccion
- 404 para slugs inexistentes
- Cache headers presentes en respuestas

---

## 8. Seguridad

### Checklist

- [x] CORS configurado con origenes especificos (frontend URL)
- [x] Validacion de input con Pydantic (inyeccion SQL prevenida por SQLAlchemy parametrizado)
- [x] Headers de seguridad: X-Content-Type-Options, X-Frame-Options, X-XSS-Protection
- [x] Rate limiting con slowapi (futuro, no critico para API de lectura)
- [x] No exposicion de errores internos (custom exception handlers)
- [x] Variables de entorno para secrets (DATABASE_URL, etc.)
- [x] .env en .gitignore
- [x] SQL injection prevenida: SQLAlchemy usa queries parametrizadas
- [x] HTTPS en produccion (reverse proxy/CDN)

### CORS Config

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://ideatravel.com"],
    allow_credentials=True,
    allow_methods=["GET"],  # Solo lectura por ahora
    allow_headers=["*"],
)
```

---

## 9. Riesgos y Mitigaciones

| Riesgo | Impacto | Mitigacion |
|--------|---------|------------|
| N+1 queries en relaciones anidadas | Performance degradada | Usar selectinload() para eager loading de todas las relaciones |
| Lazy loading falla en async | Errores runtime | AsyncAttrs mixin + selectinload obligatorio |
| Datos seed no coinciden con frontend | Integracion rota | Mapear mocks del frontend directamente a seed_data.py |
| Migraciones autogenerate incompletas | Schema drift | Revisar manualmente cada migracion generada |
| Docker compose lento en Windows | DX pobre | Volumen nombrado para node_modules, .dockerignore agresivo |
| Cambio de estructura frontend | API breaking | Versionar API bajo /api/v1/, documentar contrato |

---

## 10. Referencias

### Documentacion Oficial
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy 2.0 Async I/O](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html)
- [Pydantic v2 Documentation](https://docs.pydantic.dev/latest/)
- [Alembic Documentation](https://alembic.sqlalchemy.org/en/latest/)
- [FastAPI Docker Deployment](https://fastapi.tiangolo.com/deployment/docker/)

### Mejores Practicas
- [FastAPI Best Practices (zhanymkanov)](https://github.com/zhanymkanov/fastapi-best-practices)
- [FastAPI Best Practices for Production 2026](https://fastlaunchapi.dev/blog/fastapi-best-practices-production-2026)
- [How to Structure a Scalable FastAPI Project](https://fastlaunchapi.dev/blog/how-to-structure-fastapi)
- [Building High-Performance Async APIs with FastAPI, SQLAlchemy 2.0](https://leapcell.io/blog/building-high-performance-async-apis-with-fastapi-sqlalchemy-2-0-and-asyncpg)
- [FastAPI + SQLAlchemy 2.0: Modern Async Database Patterns](https://dev-faizan.medium.com/fastapi-sqlalchemy-2-0-modern-async-database-patterns-7879d39b6843)

### Arquitectura
- [Hexagonal Architecture with Python FastAPI](https://github.com/marcosvs98/hexagonal-architecture-with-python)
- [Hexagonal FastAPI](https://moldhouse.de/posts/hexagonal-fastapi/)
- [Python Design Patterns for Clean Architecture](https://www.glukhov.org/app-architecture/code-architecture/python-design-patterns-for-clean-architecture)
- [Building Maintainable Python Applications with Hexagonal Architecture](https://dev.to/hieutran25/building-maintainable-python-applications-with-hexagonal-architecture-and-domain-driven-design-chp)

### Base de Datos e i18n
- [Database i18n/L10n Design Patterns](https://medium.com/walkin/database-internationalization-i18n-localization-l10n-design-patterns-94ff372375c6)
- [Alembic Best Practices](https://www.pingcap.com/article/best-practices-alembic-schema-migration/)
- [PostgreSQL Anti-patterns: Unnecessary JSON columns](https://www.enterprisedb.com/blog/postgresql-anti-patterns-unnecessary-jsonhstore-dynamic-columns)

### Testing
- [FastAPI Async Tests](https://fastapi.tiangolo.com/advanced/async-tests/)
- [Fast and Furious: Async Testing with FastAPI and pytest](https://weirdsheeplabs.com/blog/fast-and-furious-async-testing-with-fastapi-and-pytest)
- [Testing FastAPI with Async Database Session](https://dev.to/whchi/testing-fastapi-with-async-database-session-1b5d)

### Docker y Deployment
- [Dockerize FastAPI with PostgreSQL](https://kitemetric.com/blogs/dockerizing-a-fastapi-project-with-postgresql-a-comprehensive-guide)
- [Dockerizing FastAPI with Postgres, Uvicorn, and Traefik](https://testdriven.io/blog/fastapi-docker-traefik/)
- [FastAPI Production Deployment 2025](https://craftyourstartup.com/cys-docs/fastapi-production-deployment/)

### Seguridad
- [FastAPI Security Best Practices 2025](https://blog.greeden.me/en/2025/07/29/fastapi-security-best-practices-from-authentication-authorization-to-cors/)
- [A Practical Guide to FastAPI Security](https://davidmuraya.com/blog/fastapi-security-guide/)
- [FastAPI Production Deployment Best Practices](https://render.com/articles/fastapi-production-deployment-best-practices)
