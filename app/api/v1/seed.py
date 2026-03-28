from fastapi import APIRouter, Header, HTTPException

from app.config import settings
from app.seeds.seed_data import seed, seed_projects

router = APIRouter()


@router.post(
    "/seed",
    summary="Ejecutar seed de datos iniciales",
    description="Endpoint protegido con ADMIN_SECRET para poblar la BD.",
)
async def run_seed(x_admin_secret: str = Header()) -> dict[str, str]:
    if x_admin_secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="Forbidden")
    await seed()
    return {"status": "ok", "message": "Seed ejecutado correctamente"}


@router.post(
    "/seed-projects",
    summary="Seed de proyectos",
    description="Crea el proyecto idea-travel y asigna external_id a los productos existentes.",
)
async def run_seed_projects(x_admin_secret: str = Header()) -> dict[str, str]:
    if x_admin_secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="Forbidden")
    await seed_projects()
    return {"status": "ok", "message": "Proyectos seeded correctamente"}
