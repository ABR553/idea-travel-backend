import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.pack import Pack
from app.domain.models.product import Product
from app.domain.models.route_step import RouteStep, RouteStepProduct, RouteStepTranslation


async def enrich_route_steps(
    db: AsyncSession,
    pack_slug: str,
    steps: list[dict],
) -> dict:
    """Create or update route steps for a pack and associate products.

    For each step: if a route step for that day exists, update descriptions and re-link
    products. If it doesn't exist, create it with translations.

    Returns {steps_created, links_created, descriptions_updated, warnings}.
    """
    result = await db.execute(
        select(Pack)
        .where(Pack.slug == pack_slug)
        .options(selectinload(Pack.route_steps).selectinload(RouteStep.translations))
    )
    pack = result.scalar_one_or_none()
    if not pack:
        raise ValueError(f"Pack '{pack_slug}' not found")

    steps_by_day: dict[int, RouteStep] = {rs.day: rs for rs in pack.route_steps}

    # Batch load all referenced products
    all_slugs = {p["product_slug"] for step in steps for p in step.get("products", [])}
    if all_slugs:
        prod_result = await db.execute(select(Product).where(Product.slug.in_(all_slugs)))
        products_by_slug: dict[str, Product] = {p.slug: p for p in prod_result.scalars().all()}
    else:
        products_by_slug = {}

    total_links = 0
    total_descs = 0
    steps_created = 0
    warnings: list[str] = []

    for step_data in steps:
        day = step_data["day"]
        route_step = steps_by_day.get(day)

        if not route_step:
            # Create route step
            dest_id = step_data.get("destination_id")
            if not dest_id:
                warnings.append(f"Day {day}: destination_id required to create route step")
                continue
            rs_id = uuid.uuid4()
            route_step = RouteStep(
                id=rs_id,
                pack_id=pack.id,
                destination_id=uuid.UUID(dest_id),
                day=day,
            )
            route_step.translations.append(RouteStepTranslation(
                id=uuid.uuid4(), route_step_id=rs_id, locale="es",
                title=step_data.get("title_es", f"Día {day}"),
                description=step_data.get("description_es", ""),
                detailed_description=step_data.get("detailed_description_es"),
            ))
            route_step.translations.append(RouteStepTranslation(
                id=uuid.uuid4(), route_step_id=rs_id, locale="en",
                title=step_data.get("title_en", f"Day {day}"),
                description=step_data.get("description_en", ""),
                detailed_description=step_data.get("detailed_description_en"),
            ))
            db.add(route_step)
            steps_created += 1
        else:
            # Update detailed descriptions on existing translations
            for trans in route_step.translations:
                if trans.locale == "es" and step_data.get("detailed_description_es"):
                    trans.detailed_description = step_data["detailed_description_es"]
                    total_descs += 1
                elif trans.locale == "en" and step_data.get("detailed_description_en"):
                    trans.detailed_description = step_data["detailed_description_en"]
                    total_descs += 1

        # Delete existing product links for this step (idempotent)
        await db.execute(
            delete(RouteStepProduct).where(RouteStepProduct.route_step_id == route_step.id)
        )

        # Create product links
        seen_product_ids: set[str] = set()
        for pl in step_data.get("products", []):
            product = products_by_slug.get(pl["product_slug"])
            if not product:
                warnings.append(f"Product '{pl['product_slug']}' not found")
                continue
            pid = str(product.id)
            if pid in seen_product_ids:
                continue
            seen_product_ids.add(pid)
            db.add(RouteStepProduct(
                id=uuid.uuid4(),
                route_step_id=route_step.id,
                product_id=product.id,
                position=pl.get("position", 0),
                context_text=pl.get("context_text"),
            ))
            total_links += 1

    await db.flush()
    return {
        "steps_created": steps_created,
        "links_created": total_links,
        "descriptions_updated": total_descs,
        "warnings": warnings,
    }
