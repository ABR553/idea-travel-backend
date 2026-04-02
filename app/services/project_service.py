from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.models.product import Product
from app.domain.models.project import Project
from app.schemas.product import ProductResponse
from app.schemas.project import ProjectResponse
from app.services import product_service


def _project_to_response(project: Project) -> ProjectResponse:
    return ProjectResponse(
        id=str(project.id),
        slug=project.slug,
        name=project.name,
        tag_id=project.tag_id,
    )


async def get_projects(db: AsyncSession) -> list[ProjectResponse]:
    result = await db.execute(select(Project).order_by(Project.name))
    projects = result.scalars().unique().all()
    return [_project_to_response(p) for p in projects]


async def get_project_by_slug(db: AsyncSession, slug: str) -> ProjectResponse | None:
    result = await db.execute(select(Project).where(Project.slug == slug))
    project = result.scalars().unique().first()
    if not project:
        return None
    return _project_to_response(project)


async def get_project_model_by_slug(db: AsyncSession, slug: str) -> Project | None:
    """Devuelve el modelo SQLAlchemy del proyecto (para operaciones de escritura)."""
    result = await db.execute(select(Project).where(Project.slug == slug))
    return result.scalars().unique().first()


async def get_project_products(
    db: AsyncSession,
    project_slug: str,
    locale: str,
    category: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    min_rating: float | None = None,
    search: str | None = None,
    sort_by: str | None = None,
    page: int = 1,
    page_size: int = 10,
) -> tuple[list[ProductResponse], int] | None:
    """Devuelve los productos de un proyecto con filtros y paginacion."""
    project_result = await db.execute(select(Project).where(Project.slug == project_slug))
    project = project_result.scalars().unique().first()
    if not project:
        return None

    from app.domain.models.product import ProductTranslation

    base = select(Product).where(
        Product.project_id == project.id,
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
        ordered.options(selectinload(Product.translations), selectinload(Product.project))
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    products = result.scalars().unique().all()
    items = [product_service._product_to_response(p, locale) for p in products]
    return items, total
