import uuid

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.database import Base
from app.domain.models import (  # noqa: F401
    Accommodation,
    AccommodationTranslation,
    Destination,
    DestinationTranslation,
    Experience,
    ExperienceTranslation,
    Pack,
    PackTranslation,
    Product,
    ProductTranslation,
    RouteStep,
    RouteStepTranslation,
)
from app.main import app

TEST_DATABASE_URL = "postgresql+asyncpg://ideatravel:ideatravel@db:5432/ideatravel_test"


@pytest_asyncio.fixture
async def db_engine():
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(db_engine):
    session_factory = async_sessionmaker(db_engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


def _id():
    return uuid.uuid4()


@pytest_asyncio.fixture
async def seeded_db(db_session):
    """Seed a minimal pack and product for testing."""
    pack_id = _id()
    dest_id = _id()
    acc_id = _id()
    exp_id = _id()
    rs_id = _id()
    prod_id = _id()

    pack = Pack(
        id=pack_id, slug="test-pack", cover_image="https://example.com/img.jpg",
        duration_days=5, price_from=500, price_to=1500, price_currency="EUR", featured=True,
        translations=[
            PackTranslation(id=_id(), pack_id=pack_id, locale="es", title="Pack Test", description="Descripcion test", short_description="Corta test", duration="5 dias"),
            PackTranslation(id=_id(), pack_id=pack_id, locale="en", title="Test Pack", description="Test description", short_description="Short test", duration="5 days"),
        ],
    )
    db_session.add(pack)
    await db_session.flush()

    dest = Destination(
        id=dest_id, pack_id=pack_id, image="https://example.com/dest.jpg", display_order=0,
        translations=[
            DestinationTranslation(id=_id(), destination_id=dest_id, locale="es", name="Destino Test", country="Pais Test", description="Desc destino"),
            DestinationTranslation(id=_id(), destination_id=dest_id, locale="en", name="Test Destination", country="Test Country", description="Dest description"),
        ],
    )
    db_session.add(dest)
    await db_session.flush()

    acc = Accommodation(
        id=acc_id, destination_id=dest_id, tier="budget", price_per_night=30, currency="EUR",
        image="https://example.com/acc.jpg", amenities=["WiFi", "Pool"], rating=4.5,
        translations=[
            AccommodationTranslation(id=_id(), accommodation_id=acc_id, locale="es", name="Hotel Test", description="Desc hotel"),
            AccommodationTranslation(id=_id(), accommodation_id=acc_id, locale="en", name="Test Hotel", description="Hotel desc"),
        ],
    )
    exp = Experience(
        id=exp_id, destination_id=dest_id, provider="getyourguide",
        affiliate_url="https://example.com/exp", price=50, currency="EUR",
        image="https://example.com/exp.jpg", rating=4.8,
        translations=[
            ExperienceTranslation(id=_id(), experience_id=exp_id, locale="es", title="Experiencia Test", description="Desc exp", duration="3 horas"),
            ExperienceTranslation(id=_id(), experience_id=exp_id, locale="en", title="Test Experience", description="Exp desc", duration="3 hours"),
        ],
    )
    rs = RouteStep(
        id=rs_id, pack_id=pack_id, destination_id=dest_id, day=1,
        translations=[
            RouteStepTranslation(id=_id(), route_step_id=rs_id, locale="es", title="Dia 1", description="Llegada"),
            RouteStepTranslation(id=_id(), route_step_id=rs_id, locale="en", title="Day 1", description="Arrival"),
        ],
    )
    db_session.add_all([acc, exp, rs])

    product = Product(
        id=prod_id, slug="test-product", category="electronics", price=99.99,
        currency="EUR", affiliate_url="https://example.com/prod",
        image="https://example.com/prod.jpg", rating=4.6,
        translations=[
            ProductTranslation(id=_id(), product_id=prod_id, locale="es", name="Producto Test", description="Desc producto"),
            ProductTranslation(id=_id(), product_id=prod_id, locale="en", name="Test Product", description="Product desc"),
        ],
    )
    db_session.add(product)
    await db_session.commit()
    return db_session
