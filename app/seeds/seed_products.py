#!/usr/bin/env python3
"""Seed de productos Amazon via endpoint de upsert masivo.

Uso:
    BASE_URL=https://api.tengounviaje.com PROJECT_SLUG=tengounviaje-21 python -m app.seeds.seed_products

Variables de entorno:
    BASE_URL        URL base de la API (default: https://api.tengounviaje.com)
    PROJECT_SLUG    Slug del proyecto destino (default: tengounviaje-21)
    JSON_PATH       Ruta al JSON de datos (default: ../../../amazon-scrapper/result_merged.json)
    BATCH_SIZE      Productos por peticion (default: 50)
"""

import json
import os
import re
import sys
import unicodedata
from pathlib import Path

import requests

# ─── Configuración ────────────────────────────────────────────────────────────

BASE_URL: str = os.getenv("BASE_URL", "https://api.tengounviaje.com").rstrip("/")
PROJECT_SLUG: str = os.getenv("PROJECT_SLUG", "tengounviaje-21")
BATCH_SIZE: int = int(os.getenv("BATCH_SIZE", "50"))

_DEFAULT_JSON_PATH = (
    Path(__file__).resolve().parents[4] / "amazon-scrapper" / "result_merged.json"
)
JSON_PATH: Path = Path(os.getenv("JSON_PATH", str(_DEFAULT_JSON_PATH)))

UPSERT_URL: str = f"{BASE_URL}/api/v1/projects/{PROJECT_SLUG}/products/upsert"

# ─── Helpers ──────────────────────────────────────────────────────────────────


def slugify(text: str) -> str:
    """Convierte texto a slug URL-friendly."""
    normalized = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    lowered = normalized.lower()
    cleaned = re.sub(r"[^\w\s-]", "", lowered)
    slugged = re.sub(r"[-\s]+", "-", cleaned).strip("-")
    return slugged[:80]


def parse_price(price_str: str) -> float:
    """Convierte '47,99' o '47.99' a float 47.99."""
    return float(price_str.replace(".", "").replace(",", "."))


def build_item(asin: str, data: dict) -> dict | None:
    """Construye un ProductUpsertItem desde la entrada del JSON."""
    try:
        scraped: dict = data["scraped"]
        images: list[str] = scraped.get("images", [])
        image: str = images[0] if images else ""

        description: dict = data.get("description", {})
        name: str = scraped.get("name", asin)

        return {
            "external_id": asin,
            "slug": slugify(name) or asin.lower(),
            "category": data["category"],
            "price": parse_price(scraped["price"]),
            "currency": "EUR",
            "affiliate_url": scraped["url"],
            "image": image,
            "rating": float(data.get("rating", 0)),
            "images": images,
            "translations": [
                {
                    "locale": "es",
                    "name": name,
                    "description": description.get("es", ""),
                },
                {
                    "locale": "en",
                    "name": name,
                    "description": description.get("en", ""),
                },
            ],
        }
    except (KeyError, ValueError, TypeError) as exc:
        print(f"  [WARN] Saltando {asin}: {exc}")
        return None


def send_batch(
    session: requests.Session,
    items: list[dict],
    batch_num: int,
    total_batches: int,
) -> tuple[int, int]:
    """Envía un batch al endpoint y devuelve (created, updated)."""
    print(f"  Enviando batch {batch_num}/{total_batches} ({len(items)} productos)...", end=" ", flush=True)
    response = session.post(UPSERT_URL, json={"items": items}, timeout=60)
    response.raise_for_status()
    result: dict = response.json()
    created: int = result.get("created", 0)
    updated: int = result.get("updated", 0)
    print(f"creados={created}, actualizados={updated}")
    return created, updated


# ─── Main ─────────────────────────────────────────────────────────────────────


def main() -> None:
    print("=" * 60)
    print("Seed de productos Amazon")
    print("=" * 60)
    print(f"  URL endpoint : {UPSERT_URL}")
    print(f"  JSON fuente  : {JSON_PATH}")
    print(f"  Batch size   : {BATCH_SIZE}")
    print()

    # Validaciones previas
    if not JSON_PATH.exists():
        print(f"[ERROR] No se encontró el archivo JSON: {JSON_PATH}")
        sys.exit(1)

    # Cargar JSON
    print("Cargando datos...", end=" ", flush=True)
    with JSON_PATH.open(encoding="utf-8") as fh:
        raw: dict = json.load(fh)
    print(f"{len(raw)} entradas encontradas.")

    # Construir items
    items: list[dict] = []
    skipped: int = 0
    for asin, data in raw.items():
        item = build_item(asin, data)
        if item is not None:
            items.append(item)
        else:
            skipped += 1

    print(f"Items válidos: {len(items)} | Saltados: {skipped}")
    print()

    if not items:
        print("[ERROR] No hay items válidos para enviar.")
        sys.exit(1)

    # Confirmar antes de enviar
    print(f"Se enviarán {len(items)} productos al proyecto '{PROJECT_SLUG}'.")
    confirm = input("¿Continuar? [s/N] ").strip().lower()
    if confirm not in ("s", "si", "sí", "y", "yes"):
        print("Cancelado.")
        sys.exit(0)

    print()

    # Dividir en batches y enviar
    session = requests.Session()
    session.headers.update({"Content-Type": "application/json", "Accept": "application/json"})

    total_created: int = 0
    total_updated: int = 0
    batches = [items[i : i + BATCH_SIZE] for i in range(0, len(items), BATCH_SIZE)]
    total_batches = len(batches)

    for idx, batch in enumerate(batches, start=1):
        try:
            created, updated = send_batch(session, batch, idx, total_batches)
            total_created += created
            total_updated += updated
        except requests.HTTPError as exc:
            print(f"\n[ERROR] HTTP {exc.response.status_code}: {exc.response.text[:300]}")
            sys.exit(1)
        except requests.RequestException as exc:
            print(f"\n[ERROR] Conexión fallida: {exc}")
            sys.exit(1)

    # Resumen
    print()
    print("=" * 60)
    print("Seed completado:")
    print(f"  Creados     : {total_created}")
    print(f"  Actualizados: {total_updated}")
    print(f"  Total       : {total_created + total_updated}")
    print("=" * 60)


if __name__ == "__main__":
    main()
