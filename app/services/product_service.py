import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.product import Product, ProductImage, ProductTranslation
from app.domain.models.project import Project
from app.schemas.product import ProductBulkUpsertRequest, ProductBulkUpsertResponse, ProductResponse
from app.services.utils import resolve_translation, to_float


def _product_to_response(product: Product, locale: str) -> ProductResponse:
    pt = resolve_translation(product.translations, locale)
    return ProductResponse(
        id=str(product.id),
        slug=product.slug,
        name=pt.name if pt else "",
        description=pt.description if pt else "",
        category=product.category,
        price=to_float(product.price),
        currency=product.currency,
        affiliate_url=product.affiliate_url,
        image=product.image,
        images=[img.url for img in sorted(product.images, key=lambda i: i.position)],
        rating=to_float(product.rating),
        external_id=product.external_id,
        project_id=str(product.project_id) if product.project_id else None,
    )


async def get_products(
    db: AsyncSession,
    locale: str,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[ProductResponse], int]:
    base = select(Product).where(
        Product.external_id.isnot(None),
        Product.external_id != "",
    )

    if category:
        base = base.where(Product.category == category)
    if min_price is not None:
        base = base.where(Product.price >= min_price)
    if max_price is not None:
        base = base.where(Product.price <= max_price)
    if min_rating is not None:
        base = base.where(Product.rating >= min_rating)

    if search:
        search_term = f"%{search}%"
        base = base.where(
            Product.id.in_(
                select(ProductTranslation.product_id).where(
                    (ProductTranslation.name.ilike(search_term))
                    | (ProductTranslation.description.ilike(search_term))
                )
            )
        )

    count_result = await db.execute(select(func.count()).select_from(base.subquery()))
    total = count_result.scalar() or 0

    ordered = base
    if sort_by == "price_asc":
        ordered = ordered.order_by(Product.price.asc())
    elif sort_by == "price_desc":
        ordered = ordered.order_by(Product.price.desc())
    elif sort_by == "rating_desc":
        ordered = ordered.order_by(Product.rating.desc())
    else:
        ordered = ordered.order_by(Product.created_at.desc())

    query = (
        ordered.options(selectinload(Product.translations), selectinload(Product.images))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    products = result.scalars().unique().all()
    items = [_product_to_response(p, locale) for p in products]
    return items, total


async def get_distinct_categories(db: AsyncSession) -> list[str]:
    result = await db.execute(
        select(Product.category).distinct().order_by(Product.category)
    )
    return [row[0] for row in result.all()]


async def bulk_upsert_products(
    db: AsyncSession,
    project: Project,
    payload: ProductBulkUpsertRequest,
    locale: str,
) -> ProductBulkUpsertResponse:
    """Upsert masivo de productos usando (project_id, external_id) como clave."""
    external_ids = [item.external_id for item in payload.items]

    # Cargar los productos existentes de este proyecto con esos external_ids
    existing_result = await db.execute(
        select(Product)
        .where(Product.project_id == project.id)
        .where(Product.external_id.in_(external_ids))
        .options(
            selectinload(Product.translations),
            selectinload(Product.images),
        )
    )
    existing_products: dict[str, Product] = {
        p.external_id: p for p in existing_result.scalars().unique().all()
        if p.external_id is not None
    }

    created_count = 0
    updated_count = 0
    result_products: list[Product] = []

    for item in payload.items:
        product = existing_products.get(item.external_id)

        if product is None:
            # INSERT
            product = Product(
                id=uuid.uuid4(),
                slug=item.slug,
                category=item.category,
                price=item.price,
                currency=item.currency,
                affiliate_url=item.affiliate_url,
                image=item.image,
                rating=item.rating,
                external_id=item.external_id,
                project_id=project.id,
            )
            db.add(product)
            created_count += 1
        else:
            # UPDATE — el slug no se modifica
            product.category = item.category
            product.price = item.price
            product.currency = item.currency
            product.affiliate_url = item.affiliate_url
            product.image = item.image
            product.rating = item.rating
            updated_count += 1

        # Upsert de imágenes: reemplazar lista completa
        existing_image_urls = {img.url for img in product.images}
        for position, url in enumerate(item.images):
            if url not in existing_image_urls:
                db.add(ProductImage(product_id=product.id, url=url, position=position))

        # Upsert de traducciones: INSERT o UPDATE por locale
        existing_translations: dict[str, ProductTranslation] = {
            t.locale: t for t in product.translations
        }
        for trans_input in item.translations:
            existing_t = existing_translations.get(trans_input.locale)
            if existing_t is None:
                db.add(ProductTranslation(
                    product_id=product.id,
                    locale=trans_input.locale,
                    name=trans_input.name,
                    description=trans_input.description,
                ))
            else:
                existing_t.name = trans_input.name
                existing_t.description = trans_input.description

        result_products.append(product)

    await db.flush()

    # Recargar con todas las relaciones para serializar correctamente
    reloaded_result = await db.execute(
        select(Product)
        .where(Product.project_id == project.id)
        .where(Product.external_id.in_(external_ids))
        .options(
            selectinload(Product.translations),
            selectinload(Product.images),
        )
    )
    reloaded: dict[str, Product] = {
        p.external_id: p for p in reloaded_result.scalars().unique().all()
        if p.external_id is not None
    }
    ordered_products = [reloaded[item.external_id] for item in payload.items if item.external_id in reloaded]

    return ProductBulkUpsertResponse(
        created=created_count,
        updated=updated_count,
        items=[_product_to_response(p, locale) for p in ordered_products],
    )


async def bulk_delete_products(
    db: AsyncSession,
    project: Project,
    external_ids: list[str] | None,
) -> int:
    """Elimina productos de un proyecto. Si external_ids es None, elimina todos."""
    base = select(Product).where(Product.project_id == project.id)
    if external_ids is not None:
        base = base.where(Product.external_id.in_(external_ids))

    result = await db.execute(base)
    products = result.scalars().unique().all()
    count = len(products)
    for product in products:
        await db.delete(product)
    await db.flush()
    return count


async def get_product_by_slug(
    db: AsyncSession, slug: str, locale: str
) -> ProductResponse | None:
    query = (
        select(Product)
        .where(Product.slug == slug)
        .options(selectinload(Product.translations), selectinload(Product.images))
    )
    result = await db.execute(query)
    product = result.scalars().unique().first()
    if not product:
        return None
    return _product_to_response(product, locale)
