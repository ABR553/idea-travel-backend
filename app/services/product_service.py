from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.product import Product, ProductImage, ProductTranslation
from app.domain.models.project import Project
from app.schemas.product import ProductResponse
from app.services.utils import resolve_translation, to_float


def _build_link(product: Product) -> str | None:
    """Construye el link de afiliado del proyecto sustituyendo external_id y tag_id."""
    if not product.project or not product.external_id:
        return None
    return (
        product.project.link_template
        .replace("{external_id}", product.external_id)
        .replace("{tag_id}", product.project.tag_id)
    )


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
        link=_build_link(product),
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
    base = select(Product)

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
        ordered.options(selectinload(Product.translations), selectinload(Product.images), selectinload(Product.project))
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


async def get_product_by_slug(
    db: AsyncSession, slug: str, locale: str
) -> ProductResponse | None:
    query = (
        select(Product)
        .where(Product.slug == slug)
        .options(selectinload(Product.translations), selectinload(Product.images), selectinload(Product.project))
    )
    result = await db.execute(query)
    product = result.scalars().unique().first()
    if not product:
        return None
    return _product_to_response(product, locale)
