"""Add a single pack to the database from a JSON file.

Usage:
    python -m app.seeds.add_pack path/to/pack.json

The JSON file must follow this structure:
{
  "slug": "paris-ciudad-de-la-luz",
  "cover_image": "https://images.unsplash.com/photo-...",
  "duration_days": 5,
  "price_from": 480,
  "price_to": 3200,
  "price_currency": "EUR",
  "featured": true,
  "translations": {
    "es": { "title": "...", "description": "...", "short_description": "...", "duration": "5 dias" },
    "en": { "title": "...", "description": "...", "short_description": "...", "duration": "5 days" }
  },
  "destinations": [
    {
      "image": "https://...",
      "display_order": 0,
      "translations": {
        "es": { "name": "...", "country": "...", "description": "..." },
        "en": { "name": "...", "country": "...", "description": "..." }
      },
      "accommodations": [
        {
          "tier": "budget",
          "price_per_night": 30,
          "currency": "EUR",
          "image": "https://...",
          "amenities": ["WiFi", "..."],
          "rating": 4.2,
          "translations": {
            "es": { "name": "...", "description": "..." },
            "en": { "name": "...", "description": "..." }
          }
        }
      ],
      "experiences": [
        {
          "provider": "getyourguide",
          "affiliate_url": "https://...",
          "price": 75,
          "currency": "EUR",
          "image": "https://...",
          "rating": 4.8,
          "translations": {
            "es": { "title": "...", "description": "...", "duration": "..." },
            "en": { "title": "...", "description": "...", "duration": "..." }
          }
        }
      ]
    }
  ],
  "route_steps": [
    {
      "day": 1,
      "destination_index": 0,
      "translations": {
        "es": { "title": "...", "description": "..." },
        "en": { "title": "...", "description": "..." }
      }
    }
  ]
}
"""
import asyncio
import json
import sys
import uuid

from sqlalchemy import select

from app.database import async_session_factory
from app.domain.models.accommodation import Accommodation, AccommodationTranslation
from app.domain.models.destination import Destination, DestinationTranslation
from app.domain.models.experience import Experience, ExperienceTranslation
from app.domain.models.pack import Pack, PackTranslation
from app.domain.models.route_step import RouteStep, RouteStepTranslation


def _id() -> uuid.UUID:
    return uuid.uuid4()


def build_pack_from_json(data: dict) -> Pack:
    pack_id = _id()

    # Pack translations
    pack_translations = []
    for locale, t in data["translations"].items():
        pack_translations.append(PackTranslation(
            id=_id(), pack_id=pack_id, locale=locale,
            title=t["title"], description=t["description"],
            short_description=t["short_description"], duration=t["duration"],
        ))

    # Destinations
    destinations = []
    dest_ids: list[uuid.UUID] = []
    for dest_data in data["destinations"]:
        dest_id = _id()
        dest_ids.append(dest_id)

        # Destination translations
        dest_translations = []
        for locale, t in dest_data["translations"].items():
            dest_translations.append(DestinationTranslation(
                id=_id(), destination_id=dest_id, locale=locale,
                name=t["name"], country=t["country"], description=t["description"],
            ))

        # Accommodations
        accommodations = []
        for acc_data in dest_data.get("accommodations", []):
            acc_id = _id()
            acc_translations = []
            for locale, t in acc_data["translations"].items():
                acc_translations.append(AccommodationTranslation(
                    id=_id(), accommodation_id=acc_id, locale=locale,
                    name=t["name"], description=t["description"],
                ))
            accommodations.append(Accommodation(
                id=acc_id, destination_id=dest_id,
                tier=acc_data["tier"], price_per_night=acc_data["price_per_night"],
                currency=acc_data.get("currency", "EUR"), image=acc_data["image"],
                amenities=acc_data.get("amenities", []), rating=acc_data["rating"],
                booking_url=acc_data.get("booking_url"),
                translations=acc_translations,
            ))

        # Experiences
        experiences = []
        for exp_data in dest_data.get("experiences", []):
            exp_id = _id()
            exp_translations = []
            for locale, t in exp_data["translations"].items():
                exp_translations.append(ExperienceTranslation(
                    id=_id(), experience_id=exp_id, locale=locale,
                    title=t["title"], description=t["description"], duration=t["duration"],
                ))
            experiences.append(Experience(
                id=exp_id, destination_id=dest_id,
                provider=exp_data["provider"], affiliate_url=exp_data["affiliate_url"],
                price=exp_data["price"], currency=exp_data.get("currency", "EUR"),
                image=exp_data["image"], rating=exp_data["rating"],
                translations=exp_translations,
            ))

        destinations.append(Destination(
            id=dest_id, pack_id=pack_id,
            image=dest_data["image"], display_order=dest_data.get("display_order", 0),
            translations=dest_translations,
            accommodations=accommodations,
            experiences=experiences,
        ))

    # Route steps
    route_steps = []
    for step_data in data.get("route_steps", []):
        rs_id = _id()
        dest_index = step_data["destination_index"]
        dest_id = dest_ids[dest_index]
        rs_translations = []
        for locale, t in step_data["translations"].items():
            rs_translations.append(RouteStepTranslation(
                id=_id(), route_step_id=rs_id, locale=locale,
                title=t["title"], description=t["description"],
            ))
        route_steps.append(RouteStep(
            id=rs_id, pack_id=pack_id, destination_id=dest_id,
            day=step_data["day"], translations=rs_translations,
        ))

    return Pack(
        id=pack_id, slug=data["slug"],
        cover_image=data["cover_image"],
        duration_days=data["duration_days"],
        price_from=data["price_from"], price_to=data["price_to"],
        price_currency=data.get("price_currency", "EUR"),
        featured=data.get("featured", False),
        translations=pack_translations,
        destinations=destinations,
        route_steps=route_steps,
    )


async def add_pack(json_path: str) -> None:
    with open(json_path, encoding="utf-8") as f:
        data = json.load(f)

    slug = data["slug"]

    async with async_session_factory() as session:
        # Check if pack already exists
        result = await session.execute(select(Pack).where(Pack.slug == slug))
        existing = result.scalars().first()
        if existing:
            print(f"Pack '{slug}' already exists (id={existing.id}). Skipping.")
            return

        pack = build_pack_from_json(data)
        session.add(pack)
        await session.commit()

        n_dest = len(data["destinations"])
        n_acc = sum(len(d.get("accommodations", [])) for d in data["destinations"])
        n_exp = sum(len(d.get("experiences", [])) for d in data["destinations"])
        n_steps = len(data.get("route_steps", []))

        print(f"Pack '{slug}' added successfully!")
        print(f"  - {n_dest} destinations")
        print(f"  - {n_acc} accommodations")
        print(f"  - {n_exp} experiences")
        print(f"  - {n_steps} route steps")
        print(f"  - 2 translations (es/en) per entity")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m app.seeds.add_pack <path-to-pack.json>")
        sys.exit(1)
    asyncio.run(add_pack(sys.argv[1]))
