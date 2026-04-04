import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.domain.models.accommodation import Accommodation, AccommodationTranslation
from app.domain.models.experience import Experience, ExperienceTranslation


async def create_accommodations(
    db: AsyncSession,
    destination_id: str,
    accommodations: list[dict],
) -> list[dict]:
    """Create accommodations for a destination. Returns list of {id, name, tier}."""
    dest_uuid = uuid.UUID(destination_id)
    created = []
    for acc_data in accommodations:
        acc_id = uuid.uuid4()
        acc = Accommodation(
            id=acc_id,
            destination_id=dest_uuid,
            tier=acc_data["tier"],
            price_per_night=acc_data["price_per_night"],
            currency=acc_data.get("currency", "EUR"),
            image=acc_data["image"],
            amenities=acc_data["amenities"],
            rating=acc_data["rating"],
            booking_url=acc_data.get("booking_url"),
            nights=acc_data["nights"],
        )
        for t in acc_data.get("translations", []):
            acc.translations.append(
                AccommodationTranslation(
                    id=uuid.uuid4(),
                    accommodation_id=acc_id,
                    locale=t["locale"],
                    name=t["name"],
                    description=t["description"],
                )
            )
        db.add(acc)
        es_name = next(
            (t["name"] for t in acc_data.get("translations", []) if t["locale"] == "es"),
            "",
        )
        created.append({"id": str(acc_id), "name": es_name, "tier": acc_data["tier"]})
    await db.flush()
    return created


async def create_experiences(
    db: AsyncSession,
    destination_id: str,
    experiences: list[dict],
) -> list[dict]:
    """Create experiences for a destination. Returns list of {id, title, provider}."""
    dest_uuid = uuid.UUID(destination_id)
    created = []
    for exp_data in experiences:
        exp_id = uuid.uuid4()
        exp = Experience(
            id=exp_id,
            destination_id=dest_uuid,
            provider=exp_data["provider"],
            affiliate_url=exp_data["affiliate_url"],
            price=exp_data["price"],
            currency=exp_data.get("currency", "EUR"),
            image=exp_data["image"],
            rating=exp_data["rating"],
        )
        for t in exp_data.get("translations", []):
            exp.translations.append(
                ExperienceTranslation(
                    id=uuid.uuid4(),
                    experience_id=exp_id,
                    locale=t["locale"],
                    title=t["title"],
                    description=t["description"],
                    duration=t["duration"],
                )
            )
        db.add(exp)
        es_title = next(
            (t["title"] for t in exp_data.get("translations", []) if t["locale"] == "es"),
            "",
        )
        created.append({"id": str(exp_id), "title": es_title, "provider": exp_data["provider"]})
    await db.flush()
    return created
