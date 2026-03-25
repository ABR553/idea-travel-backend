import logging
from contextlib import asynccontextmanager
from pathlib import Path

import sqladmin as _sqladmin
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.staticfiles import StaticFiles

from app.admin.routes import router as admin_api_router
from app.admin.setup import setup_admin
from app.api.v1.router import api_router
from app.config import settings
from app.database import engine

SQLADMIN_STATICS = str(Path(_sqladmin.__file__).parent / "statics")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("ideatravel")


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Tengo Un Viaje API...")
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    logger.info("Database connection verified")
    yield
    await engine.dispose()
    logger.info("Shutting down...")


TAGS_METADATA = [
    {"name": "health", "description": "Health check y estado del servicio"},
    {"name": "packs", "description": "Packs de viaje con destinos, alojamientos, experiencias y rutas"},
    {"name": "products", "description": "Productos de viaje de Amazon con links de afiliado"},
    {"name": "clicks", "description": "Registro de clicks en links de afiliados y reservas"},
]

app = FastAPI(
    title="Tengo Un Viaje API",
    description=(
        "API REST para la plataforma de viajes **Tengo Un Viaje**.\n\n"
        "## Funcionalidades\n"
        "- **Packs de viaje**: CRUD completo con destinos, rutas dia a dia, "
        "alojamientos (budget/standard/premium) y experiencias con links de afiliados\n"
        "- **Productos Amazon**: catalogo de productos de viaje con links de afiliado\n"
        "- **Internacionalizacion**: soporte ES/EN via query param `?locale=es` o header `Accept-Language`\n\n"
        "## Cache\n"
        "Todas las respuestas GET incluyen `Cache-Control: public, s-maxage=3600` para ISR/SSG."
    ),
    version="1.0.0",
    lifespan=lifespan,
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

origins = [o.strip() for o in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(api_router)
app.include_router(admin_api_router)

app.mount("/admin/statics", StaticFiles(directory=SQLADMIN_STATICS), name="admin-statics")
setup_admin(app)


@app.exception_handler(404)
async def not_found_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": "Not found"})


@app.exception_handler(500)
async def internal_error_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Internal server error: %s", exc)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})
