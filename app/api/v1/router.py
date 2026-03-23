from fastapi import APIRouter

from app.api.v1.blog import router as blog_router
from app.api.v1.clicks import router as clicks_router
from app.api.v1.health import router as health_router
from app.api.v1.packs import router as packs_router
from app.api.v1.products import router as products_router
from app.api.v1.seed import router as seed_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(health_router, tags=["health"])
api_router.include_router(packs_router, prefix="/packs", tags=["packs"])
api_router.include_router(products_router, prefix="/products", tags=["products"])
api_router.include_router(blog_router, prefix="/blog", tags=["blog"])
api_router.include_router(clicks_router, prefix="/clicks", tags=["clicks"])
api_router.include_router(seed_router, tags=["seed"])
