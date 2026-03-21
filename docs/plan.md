# Plan Tecnico - Idea Travel Backend

**Fecha**: 2026-03-21
**Basado en**: docs/research.md
**Objetivo**: Implementar el backend completo, ejecutable con `docker-compose up --build`

---

## Resumen de Fases

| Fase | Descripcion | Complejidad | Archivos |
|------|-------------|-------------|----------|
| 0 | Setup inicial (Docker, deps, estructura) | Baja | 8 |
| 1 | Arquitectura base (FastAPI, DB, config) | Media | 6 |
| 2 | Modelos de dominio (SQLAlchemy + migracion) | Alta | 8 |
| 3 | Schemas Pydantic | Media | 7 |
| 4 | Service Layer | Media | 3 |
| 5 | API Endpoints | Media | 5 |
| 6 | Seed Data | Alta | 2 |
| 7 | Testing | Media | 4 |
| 8 | Polish (cache, CORS, entrypoint) | Baja | 3 |

---

## Fase 0: Setup Inicial
**Complejidad**: Baja
**Objetivo**: Proyecto arrancable con `docker-compose up --build` mostrando "Hello World"

### Tarea 0.1: requirements.txt
**Archivo**: `requirements.txt`
**Que hace**: Define todas las dependencias del proyecto con versiones pinned
**Contenido**:
```
fastapi>=0.115.0
uvicorn[standard]>=0.34.0
sqlalchemy[asyncio]>=2.0.36
asyncpg>=0.30.0
alembic>=1.14.0
pydantic>=2.10.0
pydantic-settings>=2.6.0
python-dotenv>=1.0.0
gunicorn>=23.0.0
httpx>=0.28.0
pytest>=8.0.0
pytest-asyncio>=0.24.0
```
**Criterio**: `pip install -r requirements.txt` sin errores

### Tarea 0.2: .env.example
**Archivo**: `.env.example`
**Que hace**: Documenta variables de entorno necesarias
**Contenido**:
```
DATABASE_URL=postgresql+asyncpg://ideatravel:ideatravel@db:5432/ideatravel
ENVIRONMENT=development
DEBUG=true
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:3001
```
**Criterio**: Todas las variables usadas en config.py estan documentadas

### Tarea 0.3: .gitignore
**Archivo**: `.gitignore`
**Que hace**: Excluye archivos generados y sensibles
**Contenido clave**: `__pycache__/`, `.env`, `*.pyc`, `.pytest_cache/`, `alembic/versions/*.pyc`
**Criterio**: `git status` no muestra archivos no deseados

### Tarea 0.4: .dockerignore
**Archivo**: `.dockerignore`
**Que hace**: Reduce contexto de build de Docker
**Contenido clave**: `__pycache__/`, `.git/`, `.env`, `*.pyc`, `.pytest_cache/`, `docs/`, `tests/`
**Criterio**: Build de Docker no copia archivos innecesarios

### Tarea 0.5: Dockerfile
**Archivo**: `Dockerfile`
**Que hace**: Multi-stage build con target development (hot reload) y production
**Patron**: Separar COPY requirements.txt antes de COPY . para cachear layer de dependencias
**Contenido**:
```dockerfile
FROM python:3.12-slim AS base
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS development
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS production
COPY . .
CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```
**Criterio**: `docker build --target development .` exitoso

### Tarea 0.6: docker-compose.yml
**Archivo**: `docker-compose.yml`
**Que hace**: Orquesta API + PostgreSQL con hot reload, healthcheck y migraciones automaticas
**Detalles clave**:
- Servicio `api`: build con target development, volume `.:/app`, port 8000, entrypoint con migraciones
- Servicio `db`: postgres:16-alpine, healthcheck con pg_isready, volume persistente
- `depends_on.db.condition: service_healthy` para que API espere a que DB este lista
- Entrypoint script que ejecuta `alembic upgrade head` antes de arrancar uvicorn
**Criterio**: `docker-compose up --build` levanta ambos servicios y API responde en localhost:8000

### Tarea 0.7: entrypoint.sh
**Archivo**: `entrypoint.sh`
**Que hace**: Script de arranque que ejecuta migraciones y luego arranca la API
**Contenido**:
```bash
#!/bin/bash
set -e
echo "Running migrations..."
alembic upgrade head
echo "Starting API server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
**Criterio**: Al arrancar el contenedor, migraciones se aplican automaticamente

### Tarea 0.8: Estructura de carpetas vacia
**Archivos**: Todos los `__init__.py` necesarios
```
app/__init__.py
app/domain/__init__.py
app/domain/models/__init__.py
app/schemas/__init__.py
app/services/__init__.py
app/api/__init__.py
app/api/v1/__init__.py
app/seeds/__init__.py
tests/__init__.py
```
**Criterio**: `from app import *` no falla

---

## Fase 1: Arquitectura Base
**Complejidad**: Media
**Dependencias**: Fase 0 completada
**Objetivo**: API funcional con health check, conectada a PostgreSQL

### Tarea 1.1: Configuracion con Pydantic Settings
**Archivo**: `app/config.py`
**Que hace**: Centraliza configuracion cargada desde variables de entorno
**Patron**: Pydantic Settings (single source of truth para config)
```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str
    environment: str = "development"
    debug: bool = True
    allowed_origins: str = "http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
```
**Criterio**: `settings.database_url` devuelve la URL correcta desde env

### Tarea 1.2: Database setup
**Archivo**: `app/database.py`
**Que hace**: Crea engine async, session factory y Base declarativa
**Patron**: Singleton para engine, factory para sessions
```python
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

engine = create_async_engine(settings.database_url, echo=settings.debug)
async_session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass
```
**Clave**: `expire_on_commit=False` para poder acceder a atributos despues de commit en async
**Criterio**: Conexion a PostgreSQL funcional desde el contenedor

### Tarea 1.3: Base model con timestamps
**Archivo**: `app/domain/models/base.py`
**Que hace**: Modelo base que todos los modelos heredan, con id UUID, created_at, updated_at
**Patron**: Template Method (campos comunes en base)
```python
import uuid
from sqlalchemy import Column, DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from app.database import Base

class BaseModel(Base):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
```
**Criterio**: Todos los modelos heredan de BaseModel y tienen id, created_at, updated_at

### Tarea 1.4: Dependencies (get_db, get_locale)
**Archivo**: `app/api/deps.py`
**Que hace**: FastAPI dependencies para inyectar session de BD y locale
**Patron**: Dependency Injection
```python
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_factory() as session:
        yield session

def get_locale(
    locale: str | None = Query(None, regex="^(es|en)$"),
    accept_language: str | None = Header(None, alias="accept-language"),
) -> str:
    if locale:
        return locale
    if accept_language and accept_language.startswith("en"):
        return "en"
    return "es"
```
**Criterio**: Endpoints reciben session y locale automaticamente via Depends()

### Tarea 1.5: FastAPI app factory
**Archivo**: `app/main.py`
**Que hace**: Crea la app FastAPI con lifespan, CORS, routers, exception handlers
**Patron**: App Factory
**Detalles**:
- Lifespan para verificar conexion a BD al arrancar
- CORS middleware con origenes de settings
- Include router v1
- Exception handlers para 404, 500
**Criterio**: `GET /` devuelve 404 o redirect, API docs en `/docs`

### Tarea 1.6: Health check endpoint
**Archivo**: `app/api/v1/health.py`
**Que hace**: Endpoint GET /api/v1/health que verifica conexion a BD
**Contenido**:
```python
@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    await db.execute(text("SELECT 1"))
    return {"status": "healthy", "database": "connected"}
```
**Criterio**: `curl localhost:8000/api/v1/health` devuelve 200 con status healthy

### Tarea 1.7: Router principal v1
**Archivo**: `app/api/v1/router.py`
**Que hace**: Agrupa todos los routers bajo /api/v1
```python
api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, tags=["health"])
```
**Criterio**: Todos los endpoints accesibles bajo /api/v1/

### Tarea 1.8: Alembic setup
**Archivos**: `alembic.ini`, `alembic/env.py`
**Que hace**: Configuracion de Alembic para async con SQLAlchemy
**Detalles clave en env.py**:
- Importar todos los modelos para que autogenerate los detecte
- Usar `run_async()` para migraciones async
- `target_metadata = Base.metadata`
- Cargar DATABASE_URL desde settings (NO hardcoded en alembic.ini)
**Criterio**: `alembic revision --autogenerate -m "init"` genera migracion vacia (aun no hay modelos)

---

## Fase 2: Modelos de Dominio (SQLAlchemy)
**Complejidad**: Alta
**Dependencias**: Fase 1 completada
**Objetivo**: Todos los modelos SQLAlchemy creados con relaciones y migracion aplicada

### Tarea 2.1: Pack + PackTranslation
**Archivo**: `app/domain/models/pack.py`
**Que hace**: Modelo Pack con campos no traducibles + PackTranslation con campos traducibles
**Campos Pack**: slug, cover_image, duration_days, price_from, price_to, price_currency, featured
**Campos PackTranslation**: pack_id(FK), locale, title, description, short_description, duration
**Relaciones**:
- `translations` -> PackTranslation (cascade="all, delete-orphan")
- `destinations` -> Destination (cascade="all, delete-orphan", order_by display_order)
- `route_steps` -> RouteStep (cascade="all, delete-orphan", order_by day)
**Indices**: UNIQUE(slug), UNIQUE(pack_id, locale) en translations
**Criterio**: Pack.translations, Pack.destinations, Pack.route_steps accesibles con selectinload

### Tarea 2.2: Destination + DestinationTranslation
**Archivo**: `app/domain/models/destination.py`
**Que hace**: Destino dentro de un pack, con traducciones
**Campos Destination**: pack_id(FK), image, display_order
**Campos DestinationTranslation**: destination_id(FK), locale, name, country, description
**Relaciones**:
- `translations` -> DestinationTranslation
- `accommodations` -> Accommodation (cascade="all, delete-orphan")
- `experiences` -> Experience (cascade="all, delete-orphan")
- `pack` -> Pack (back_populates)
**Criterio**: Destination.accommodations y Destination.experiences cargan los datos por destino

### Tarea 2.3: RouteStep + RouteStepTranslation
**Archivo**: `app/domain/models/route_step.py`
**Que hace**: Paso dia a dia del itinerario, vinculado a pack y destino
**Campos RouteStep**: pack_id(FK), destination_id(FK), day
**Campos RouteStepTranslation**: route_step_id(FK), locale, title, description
**Relaciones**:
- `translations` -> RouteStepTranslation
- `destination` -> Destination (para resolver nombre del destino en la respuesta)
- `pack` -> Pack (back_populates)
**Criterio**: RouteStep.destination accesible para obtener el nombre del destino

### Tarea 2.4: Accommodation + AccommodationTranslation
**Archivo**: `app/domain/models/accommodation.py`
**Que hace**: Alojamiento por destino con tier (budget/standard/premium)
**Campos Accommodation**: destination_id(FK), tier, price_per_night, currency, image, amenities(JSONB), rating
**Campos AccommodationTranslation**: accommodation_id(FK), locale, name, description
**Tipo tier**: VARCHAR con CHECK constraint o Enum PostgreSQL
**Criterio**: Filtrar accommodations por destination_id y tier funcional

### Tarea 2.5: Experience + ExperienceTranslation
**Archivo**: `app/domain/models/experience.py`
**Que hace**: Experiencia/actividad por destino con link de afiliado
**Campos Experience**: destination_id(FK), provider, affiliate_url, price, currency, image, rating
**Campos ExperienceTranslation**: experience_id(FK), locale, title, description, duration
**Tipo provider**: VARCHAR con CHECK (getyourguide|civitatis)
**Criterio**: Filtrar experiences por destination_id funcional

### Tarea 2.6: Product + ProductTranslation
**Archivo**: `app/domain/models/product.py`
**Que hace**: Producto de Amazon con link de afiliado
**Campos Product**: slug, category, price, currency, affiliate_url, image, rating
**Campos ProductTranslation**: product_id(FK), locale, name, description
**Tipo category**: VARCHAR con CHECK (luggage|electronics|accessories|comfort|photography)
**Indices**: UNIQUE(slug), INDEX(category), UNIQUE(product_id, locale)
**Criterio**: Product.translations accesible, filtro por category funcional

### Tarea 2.7: Registro de modelos en __init__
**Archivo**: `app/domain/models/__init__.py`
**Que hace**: Importa todos los modelos para que Alembic los detecte en autogenerate
```python
from app.domain.models.base import BaseModel
from app.domain.models.pack import Pack, PackTranslation
from app.domain.models.destination import Destination, DestinationTranslation
from app.domain.models.route_step import RouteStep, RouteStepTranslation
from app.domain.models.accommodation import Accommodation, AccommodationTranslation
from app.domain.models.experience import Experience, ExperienceTranslation
from app.domain.models.product import Product, ProductTranslation
```
**Criterio**: `from app.domain.models import *` importa todos los modelos

### Tarea 2.8: Migracion inicial
**Comando**: `docker-compose exec api alembic revision --autogenerate -m "initial schema"`
**Que hace**: Genera la migracion con todas las tablas, relaciones e indices
**Post-paso**: Revisar migracion generada, verificar que incluye:
- 12 tablas (6 entidades + 6 traducciones)
- Todos los FK con ON DELETE CASCADE
- Todos los UNIQUE constraints
- Todos los indices
**Comando aplicar**: `docker-compose exec api alembic upgrade head`
**Criterio**: `\dt` en psql muestra las 12 tablas correctamente

---

## Fase 3: Schemas Pydantic
**Complejidad**: Media
**Dependencias**: Fase 2 completada (modelos definen estructura)
**Objetivo**: Schemas para serializar/deserializar datos con traducciones resueltas

### Tarea 3.1: Schemas comunes
**Archivo**: `app/schemas/common.py`
**Que hace**: Schemas reutilizables: PriceRange, PaginatedResponse
```python
class PriceRange(BaseModel):
    from_price: float = Field(alias="from", serialization_alias="from")
    to: float
    currency: str

class PaginatedResponse(BaseModel, Generic[T]):
    data: list[T]
    total: int
    page: int
    page_size: int
```
**Criterio**: PriceRange serializa como `{"from": 899, "to": 3200, "currency": "EUR"}`

### Tarea 3.2: Schemas de Destination
**Archivo**: `app/schemas/destination.py`
**Que hace**: Response schema con traducciones resueltas (name, country, description directos)
```python
class DestinationResponse(BaseModel):
    name: str
    country: str
    description: str
    image: str
```
**Nota**: Sin id porque el frontend no lo usa. Incluye accommodations y experiences anidados.
**Criterio**: Coincide exactamente con la interfaz Destination del frontend

### Tarea 3.3: Schemas de Accommodation
**Archivo**: `app/schemas/accommodation.py`
```python
class AccommodationResponse(BaseModel):
    id: str
    name: str
    tier: str
    description: str
    pricePerNight: float  # alias de price_per_night
    currency: str
    image: str
    amenities: list[str]
    rating: float
```
**Clave**: Usar `model_config = ConfigDict(populate_by_name=True)` y Field aliases para camelCase
**Criterio**: JSON output en camelCase coincide con el frontend

### Tarea 3.4: Schemas de Experience
**Archivo**: `app/schemas/experience.py`
```python
class ExperienceResponse(BaseModel):
    id: str
    title: str
    description: str
    provider: str
    affiliateUrl: str
    price: float
    currency: str
    duration: str
    image: str
    rating: float
```
**Criterio**: Coincide con interfaz Experience del frontend

### Tarea 3.5: Schemas de RouteStep
**Archivo**: `app/schemas/route_step.py`
```python
class RouteStepResponse(BaseModel):
    day: int
    title: str
    description: str
    destination: str  # nombre del destino, no id
```
**Criterio**: `destination` es el nombre traducido del destino, no el id

### Tarea 3.6: Schemas de Pack
**Archivo**: `app/schemas/pack.py`
**Que hace**: Schema completo del pack con todos los sub-schemas anidados
```python
class PackResponse(BaseModel):
    id: str
    slug: str
    title: str
    description: str
    shortDescription: str
    destinations: list[DestinationResponse]
    route: list[RouteStepResponse]
    accommodations: list[AccommodationResponse]  # aplanado: todos los de todos los destinos
    experiences: list[ExperienceResponse]         # aplanado: todos los de todos los destinos
    coverImage: str
    duration: str
    durationDays: int
    price: PriceRange
    featured: bool

class PackListResponse(BaseModel):
    # Version reducida para listado (sin route, accommodations, experiences)
    id: str
    slug: str
    title: str
    shortDescription: str
    destinations: list[DestinationResponse]
    coverImage: str
    duration: str
    durationDays: int
    price: PriceRange
    featured: bool
```
**CRITICO**: `accommodations` y `experiences` se aplanan al nivel de pack para compatibilidad con frontend.
El service recoge todos los accommodations/experiences de todos los destinos y los pone en un array plano.
**Criterio**: El JSON de PackResponse coincide EXACTAMENTE con la interfaz Pack del frontend TS

### Tarea 3.7: Schemas de Product
**Archivo**: `app/schemas/product.py`
```python
class ProductResponse(BaseModel):
    id: str
    slug: str
    name: str
    description: str
    category: str
    price: float
    currency: str
    affiliateUrl: str
    image: str
    rating: float
```
**Criterio**: Coincide con interfaz Product del frontend

---

## Fase 4: Service Layer
**Complejidad**: Media
**Dependencias**: Fases 2 y 3 completadas
**Objetivo**: Logica de negocio que transforma modelos SQLAlchemy en schemas Pydantic

### Tarea 4.1: Pack Service
**Archivo**: `app/services/pack_service.py`
**Que hace**: Queries para packs con eager loading de TODAS las relaciones anidadas, resolucion de locale
**Metodos**:
```python
async def get_packs(db: AsyncSession, locale: str, featured: bool | None = None) -> list[PackListResponse]:
    """Lista packs con traducciones resueltas. Filtro opcional por featured."""

async def get_pack_by_slug(db: AsyncSession, slug: str, locale: str) -> PackResponse | None:
    """Pack completo con destinos, rutas, alojamientos y experiencias."""

async def get_featured_packs(db: AsyncSession, locale: str) -> list[PackListResponse]:
    """Packs con featured=True."""
```
**Eager Loading critico** (para evitar N+1 y errores async):
```python
options = [
    selectinload(Pack.translations),
    selectinload(Pack.destinations).selectinload(Destination.translations),
    selectinload(Pack.destinations).selectinload(Destination.accommodations).selectinload(Accommodation.translations),
    selectinload(Pack.destinations).selectinload(Destination.experiences).selectinload(Experience.translations),
    selectinload(Pack.route_steps).selectinload(RouteStep.translations),
    selectinload(Pack.route_steps).selectinload(RouteStep.destination).selectinload(Destination.translations),
]
```
**Resolucion de locale**: Funcion helper que dado un objeto con `.translations`, busca la traduccion para el locale solicitado:
```python
def resolve_translation(obj, locale: str):
    for t in obj.translations:
        if t.locale == locale:
            return t
    # Fallback a 'es'
    for t in obj.translations:
        if t.locale == "es":
            return t
    return None
```
**Aplanamiento de accommodations/experiences**: Recorrer todos los destinations del pack y recoger sus accommodations/experiences en un solo array.
**Criterio**: `get_pack_by_slug` devuelve PackResponse completo y correcto

### Tarea 4.2: Product Service
**Archivo**: `app/services/product_service.py`
**Metodos**:
```python
async def get_products(db: AsyncSession, locale: str, category: str | None = None) -> list[ProductResponse]:
    """Lista productos con traducciones. Filtro por categoria."""

async def get_product_by_slug(db: AsyncSession, slug: str, locale: str) -> ProductResponse | None:
    """Producto individual con traduccion."""
```
**Criterio**: Productos filtrados por categoria y traducidos correctamente

### Tarea 4.3: __init__ services
**Archivo**: `app/services/__init__.py`
**Que hace**: Exporta los services
**Criterio**: `from app.services import pack_service, product_service`

---

## Fase 5: API Endpoints
**Complejidad**: Media
**Dependencias**: Fase 4 completada
**Objetivo**: Todos los endpoints funcionales y documentados en /docs

### Tarea 5.1: Packs endpoints
**Archivo**: `app/api/v1/packs.py`
**Endpoints**:
```python
@router.get("/packs", response_model=PaginatedResponse[PackListResponse])
async def list_packs(
    locale: str = Depends(get_locale),
    featured: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: AsyncSession = Depends(get_db),
):
    """Lista packs con filtros y paginacion."""

@router.get("/packs/featured", response_model=list[PackListResponse])
async def featured_packs(
    locale: str = Depends(get_locale),
    db: AsyncSession = Depends(get_db),
):
    """Packs destacados."""

@router.get("/packs/{slug}", response_model=PackResponse)
async def get_pack(
    slug: str,
    locale: str = Depends(get_locale),
    db: AsyncSession = Depends(get_db),
):
    """Detalle completo de pack."""
    # 404 si no existe
```
**IMPORTANTE**: `/packs/featured` debe declararse ANTES de `/packs/{slug}` para que FastAPI no interprete "featured" como slug.
**Cache headers**: Cada respuesta incluye `Cache-Control: public, s-maxage=3600, stale-while-revalidate=86400`
**Criterio**: Todos los endpoints devuelven datos correctos con traducciones

### Tarea 5.2: Products endpoints
**Archivo**: `app/api/v1/products.py`
**Endpoints**:
```python
@router.get("/products", response_model=PaginatedResponse[ProductResponse])
async def list_products(...)

@router.get("/products/categories")
async def list_categories():
    """Devuelve categorias disponibles."""
    return ["luggage", "electronics", "accessories", "comfort", "photography"]

@router.get("/products/{slug}", response_model=ProductResponse)
async def get_product(...)
```
**Criterio**: Filtro por categoria funcional, 404 para slug inexistente

### Tarea 5.3: Actualizar router v1
**Archivo**: `app/api/v1/router.py`
**Que hace**: Incluye routers de packs y products
```python
api_router.include_router(packs_router, prefix="/packs", tags=["packs"])
api_router.include_router(products_router, prefix="/products", tags=["products"])
```
**Criterio**: `/docs` muestra todos los endpoints organizados por tags

### Tarea 5.4: Cache middleware / response headers
**Archivo**: `app/api/v1/packs.py` y `app/api/v1/products.py`
**Que hace**: Anade Cache-Control headers a las respuestas GET
**Implementacion**: Usar `Response` de FastAPI para setear headers:
```python
response.headers["Cache-Control"] = "public, s-maxage=3600, stale-while-revalidate=86400"
```
**Criterio**: `curl -I localhost:8000/api/v1/packs` muestra Cache-Control header

---

## Fase 6: Seed Data
**Complejidad**: Alta (muchos datos, 2 idiomas)
**Dependencias**: Fase 2 completada (modelos), Fase 5 recomendada
**Objetivo**: `docker-compose exec api python -m app.seeds.seed_data` puebla BD con datos del frontend

### Tarea 6.1: Script de seed
**Archivo**: `app/seeds/seed_data.py`
**Que hace**: Puebla la BD con los datos exactos de los mocks del frontend
**Datos a seedear**:
- 6 packs (Tailandia, Japon, Marruecos, Italia, Peru, Islandia)
- Cada pack: 3 destinos con traducciones es/en
- Cada pack: route_steps dia a dia con traducciones es/en
- Cada pack: 3 accommodations (1 budget, 1 standard, 1 premium) - POR DESTINO en la BD, pero el seed original tiene 3 por pack, asi que se asignan al primer destino de cada pack
- Cada pack: 2-3 experiences - POR DESTINO igualmente
- 12 productos con traducciones es/en

**DECISION CRITICA sobre accommodations/experiences en seed**:
Los mocks del frontend tienen 3 accommodations y 2-3 experiences por PACK (no por destino).
En la BD modelamos por DESTINO. Para el seed, asignamos:
- Los accommodations al primer destino del pack (ya que el mock solo tiene 3 por pack)
- Las experiences se distribuyen: asignar a destinos segun contexto (e.g. "Tour canales Bangkok" -> destino Bangkok)
Esto mantiene compatibilidad: el endpoint aplanara todo al nivel pack igualmente.

**Estructura del script**:
```python
async def seed():
    async with async_session_factory() as session:
        # Verificar si ya hay datos
        result = await session.execute(select(func.count()).select_from(Pack))
        if result.scalar() > 0:
            print("Database already seeded")
            return

        # Crear packs con todos los datos anidados
        pack1 = Pack(slug="tailandia-aventura-tropical", ...)
        # ... crear destinos, accommodations, experiences, route_steps
        session.add_all([pack1, pack2, ...])
        await session.commit()
```
**Criterio**: Tras ejecutar seed, GET /api/v1/packs devuelve 6 packs identicos a los mocks del frontend

### Tarea 6.2: __init__ seeds
**Archivo**: `app/seeds/__init__.py`
**Criterio**: `python -m app.seeds.seed_data` ejecutable

---

## Fase 7: Testing
**Complejidad**: Media
**Dependencias**: Fases 1-6 completadas
**Objetivo**: Tests que verifican endpoints y datos

### Tarea 7.1: conftest.py con fixtures async
**Archivo**: `tests/conftest.py`
**Que hace**: Fixtures para test database, async session, async client
**Detalles**:
- Test database URL apuntando a una BD separada o la misma (con truncate entre tests)
- Fixture `async_session`: crea tablas, yield session, drop tablas
- Fixture `client`: crea AsyncClient con dependency override de get_db
- Fixture `seeded_db`: ejecuta seed para tests que necesitan datos
```python
@pytest_asyncio.fixture
async def db_session():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()
```
**Criterio**: Tests ejecutan con BD aislada, sin afectar datos de desarrollo

### Tarea 7.2: Tests health check
**Archivo**: `tests/test_health.py`
```python
async def test_health_returns_200(client):
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
```
**Criterio**: Test pasa con `docker-compose exec api pytest tests/test_health.py`

### Tarea 7.3: Tests packs
**Archivo**: `tests/test_packs.py`
**Tests**:
- `test_list_packs_empty` - Sin datos devuelve lista vacia
- `test_list_packs_with_data` - Con seed devuelve 6 packs
- `test_get_pack_by_slug` - Pack completo con destinos, rutas, accommodations, experiences
- `test_get_pack_not_found` - Slug inexistente devuelve 404
- `test_pack_locale_es` - Traducciones en espanol
- `test_pack_locale_en` - Traducciones en ingles
- `test_featured_packs` - Solo devuelve packs con featured=true
- `test_pack_has_cache_headers` - Respuesta incluye Cache-Control
**Criterio**: Todos los tests pasan

### Tarea 7.4: Tests products
**Archivo**: `tests/test_products.py`
**Tests**:
- `test_list_products_empty`
- `test_list_products_with_data`
- `test_filter_products_by_category`
- `test_get_product_by_slug`
- `test_product_not_found`
- `test_product_locale_en`
- `test_product_categories`
**Criterio**: Todos los tests pasan

---

## Fase 8: Polish
**Complejidad**: Baja
**Dependencias**: Fases 1-7 completadas
**Objetivo**: Detalles finales de produccion

### Tarea 8.1: CORS configurado para frontend
**Archivo**: `app/main.py` (ya existe, actualizar)
**Que hace**: CORS con origenes del frontend en settings
```python
origins = settings.allowed_origins.split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET"],
    allow_headers=["*"],
)
```
**Criterio**: Frontend en localhost:3000 puede hacer fetch sin errores CORS

### Tarea 8.2: Exception handlers
**Archivo**: `app/main.py` (actualizar)
**Que hace**: Custom handlers para 404 y 500 con formato JSON consistente
```python
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(status_code=404, content={"detail": "Not found"})
```
**Criterio**: Errores devuelven JSON, no HTML

### Tarea 8.3: Logging
**Archivo**: `app/main.py` (actualizar)
**Que hace**: Logging basico con formato estructurado
```python
import logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ideatravel")
```
**Criterio**: Logs visibles en `docker-compose logs api`

---

## Orden de Ejecucion

```
Fase 0 (Setup) ──> Fase 1 (Arquitectura) ──> Fase 2 (Modelos)
                                                    │
                                              ┌─────┼─────┐
                                              ▼     ▼     ▼
                                          Fase 3  Fase 6  (paralelas)
                                          (Schemas)(Seed)
                                              │
                                              ▼
                                          Fase 4 (Services)
                                              │
                                              ▼
                                          Fase 5 (Endpoints)
                                              │
                                              ▼
                                          Fase 7 (Tests)
                                              │
                                              ▼
                                          Fase 8 (Polish)
```

## Verificacion Final

Al completar todas las fases, estos comandos deben funcionar:

```bash
# 1. Levantar todo
docker-compose up --build

# 2. Verificar health
curl http://localhost:8000/api/v1/health
# {"status": "healthy", "database": "connected"}

# 3. Poblar datos
docker-compose exec api python -m app.seeds.seed_data

# 4. Verificar packs
curl http://localhost:8000/api/v1/packs
# {"data": [...6 packs...], "total": 6, "page": 1, "page_size": 10}

curl http://localhost:8000/api/v1/packs/tailandia-aventura-tropical
# Pack completo con destinos, rutas, alojamientos, experiencias

curl "http://localhost:8000/api/v1/packs/tailandia-aventura-tropical?locale=en"
# Mismo pack en ingles

# 5. Verificar productos
curl http://localhost:8000/api/v1/products
# {"data": [...12 productos...], "total": 12, "page": 1, "page_size": 10}

curl "http://localhost:8000/api/v1/products?category=electronics"
# Solo productos de electronica

# 6. Ejecutar tests
docker-compose exec api pytest -v
# Todos los tests pasan

# 7. Ver documentacion
# Abrir http://localhost:8000/docs
```
