import uuid

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db
from app.config import settings
from app.domain.models.pack import Pack
from app.domain.models.product import Product
from app.domain.models.route_step import RouteStep, RouteStepProduct
from app.schemas.route_step import EnrichRoutesRequest
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


@router.post(
    "/seed-route-products/{pack_slug}",
    summary="Enriquecer rutas de un pack con productos y descripciones",
    description=(
        "Asocia productos a route steps de un pack y actualiza "
        "detailed_description. Idempotente: reemplaza enlaces existentes."
    ),
)
async def enrich_pack_routes(
    pack_slug: str,
    payload: EnrichRoutesRequest,
    x_admin_secret: str = Header(),
    db: AsyncSession = Depends(get_db),
) -> dict:
    if x_admin_secret != settings.admin_secret:
        raise HTTPException(status_code=403, detail="Forbidden")

    # Look up pack with route steps + translations
    result = await db.execute(
        select(Pack)
        .where(Pack.slug == pack_slug)
        .options(
            selectinload(Pack.route_steps).selectinload(RouteStep.translations),
        )
    )
    pack = result.scalar_one_or_none()
    if not pack:
        raise HTTPException(status_code=404, detail=f"Pack '{pack_slug}' not found")

    steps_by_day: dict[int, RouteStep] = {rs.day: rs for rs in pack.route_steps}

    # Resolve all referenced product slugs in one query
    all_slugs = {p.product_slug for step in payload.steps for p in step.products}
    if all_slugs:
        prod_result = await db.execute(
            select(Product).where(Product.slug.in_(all_slugs))
        )
        products_by_slug = {p.slug: p for p in prod_result.scalars().all()}
    else:
        products_by_slug = {}

    total_links = 0
    total_descs = 0
    warnings: list[str] = []

    for step_data in payload.steps:
        route_step = steps_by_day.get(step_data.day)
        if not route_step:
            warnings.append(f"Day {step_data.day} not found in '{pack_slug}'")
            continue

        # Delete existing product links for this step (idempotent upsert)
        await db.execute(
            delete(RouteStepProduct).where(
                RouteStepProduct.route_step_id == route_step.id
            )
        )

        # Create new product links (skip duplicates)
        seen_product_ids: set[str] = set()
        for pl in step_data.products:
            product = products_by_slug.get(pl.product_slug)
            if not product:
                warnings.append(f"Product '{pl.product_slug}' not found")
                continue
            if str(product.id) in seen_product_ids:
                warnings.append(f"Duplicate product '{pl.product_slug}' in day {step_data.day}, skipping")
                continue
            seen_product_ids.add(str(product.id))
            db.add(RouteStepProduct(
                id=uuid.uuid4(),
                route_step_id=route_step.id,
                product_id=product.id,
                position=pl.position,
                context_text=pl.context_text,
            ))
            total_links += 1

        # Update detailed_description on translations
        for trans in route_step.translations:
            if trans.locale == "es" and step_data.detailed_description_es:
                trans.detailed_description = step_data.detailed_description_es
                total_descs += 1
            elif trans.locale == "en" and step_data.detailed_description_en:
                trans.detailed_description = step_data.detailed_description_en
                total_descs += 1

    await db.commit()
    return {
        "status": "ok",
        "pack": pack_slug,
        "links_created": total_links,
        "descriptions_updated": total_descs,
        "warnings": warnings,
    }
