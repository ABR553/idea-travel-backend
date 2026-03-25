"""Genera contenido de viaje (pack + blog) usando el CLI local de Claude.

Uso:
    python scripts/generate_content.py "Un viaje de 7 dias por Japon visitando Tokio, Kioto y Osaka"

Requisitos:
    - Claude CLI instalado y autenticado (https://docs.anthropic.com/claude-code)
    - Ejecutar desde la raiz del proyecto (idea-travel-backend/)

El resultado se guarda en generated/pending/<timestamp>-<slug>.json
"""

import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
PENDING_DIR = PROJECT_ROOT / "generated" / "pending"

SYSTEM_PROMPT = """\
Eres un experto creador de contenido de viajes para la plataforma "Tengo Un Viaje".
Tu trabajo es generar packs de viaje completos y articulos de blog asociados.

Reglas:
- Genera contenido BILINGUE (espanol e ingles) para cada campo.
- Los slugs deben ser URL-friendly en espanol (ej: "japon-en-7-dias").
- Las imagenes deben ser URLs validas de Unsplash con formato: https://images.unsplash.com/photo-XXXXX?w=800
- Cada destino debe tener EXACTAMENTE 3 alojamientos: uno budget, uno standard, uno premium.
- Cada destino debe tener al menos 2 experiencias con proveedores reales (getyourguide o civitatis).
- Los precios deben ser realistas en EUR.
- Los ratings deben estar entre 3.5 y 5.0.
- La ruta debe cubrir TODOS los dias del viaje, asignando cada dia a un destino.
- El blog debe ser un articulo completo en Markdown (minimo 500 palabras por idioma) relacionado con el pack.
- La categoria del blog debe ser una de: guia, presupuesto, epoca, consejos, lista.
- El cover_image del pack y del blog deben ser diferentes.
- Amenities de alojamiento en espanol.

IMPORTANTE: Responde UNICAMENTE con un JSON valido, sin texto adicional, sin bloques de codigo markdown.
El JSON debe seguir EXACTAMENTE esta estructura:

{
  "pack": {
    "slug": "string",
    "cover_image": "string",
    "duration_days": 0,
    "price_from": 0.0,
    "price_to": 0.0,
    "featured": false,
    "title_es": "string",
    "title_en": "string",
    "description_es": "string",
    "description_en": "string",
    "short_description_es": "string",
    "short_description_en": "string",
    "duration_es": "string",
    "duration_en": "string",
    "destinations": [
      {
        "name_es": "string",
        "name_en": "string",
        "country_es": "string",
        "country_en": "string",
        "description_es": "string",
        "description_en": "string",
        "image": "string",
        "days": 0,
        "accommodations": [
          {
            "tier": "budget|standard|premium",
            "name_es": "string",
            "name_en": "string",
            "description_es": "string",
            "description_en": "string",
            "price_per_night": 0.0,
            "currency": "EUR",
            "amenities": ["string"],
            "rating": 0.0,
            "image": "string",
            "nights": 0
          }
        ],
        "experiences": [
          {
            "title_es": "string",
            "title_en": "string",
            "description_es": "string",
            "description_en": "string",
            "duration_es": "string",
            "duration_en": "string",
            "provider": "getyourguide|civitatis",
            "price": 0.0,
            "currency": "EUR",
            "rating": 0.0,
            "image": "string"
          }
        ]
      }
    ],
    "route_steps": [
      {
        "day": 0,
        "title_es": "string",
        "title_en": "string",
        "description_es": "string",
        "description_en": "string",
        "destination_name": "string"
      }
    ]
  },
  "blog": {
    "slug": "string",
    "cover_image": "string",
    "category": "guia|presupuesto|epoca|consejos|lista",
    "title_es": "string",
    "title_en": "string",
    "excerpt_es": "string",
    "excerpt_en": "string",
    "content_es": "string (Markdown completo, minimo 500 palabras)",
    "content_en": "string (Markdown completo, minimo 500 palabras)"
  }
}
"""


def slugify(text: str) -> str:
    """Convierte texto a slug simple."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-+", "-", text)[:60].strip("-")


def extract_json(text: str) -> str:
    """Extrae el JSON de la respuesta, eliminando bloques de codigo markdown si los hay."""
    # Buscar bloque ```json ... ```
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    # Buscar el primer { ... } completo
    start = text.find("{")
    if start == -1:
        return text
    depth = 0
    for i, char in enumerate(text[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return text[start:]


def generate(description: str) -> None:
    PENDING_DIR.mkdir(parents=True, exist_ok=True)

    prompt = (
        f"Genera un pack de viaje completo y un articulo de blog basado en esta descripcion:\n\n"
        f"{description}"
    )

    print(f"Generando contenido para: {description[:80]}...")
    print("Invocando Claude CLI (esto puede tardar 1-2 minutos)...\n")

    try:
        result = subprocess.run(
            [
                "claude",
                "--print",
                "--output-format", "text",
                "--system-prompt", SYSTEM_PROMPT,
                prompt,
            ],
            capture_output=True,
            text=True,
            timeout=300,
        )
    except FileNotFoundError:
        print("ERROR: El CLI de Claude no esta instalado o no esta en el PATH.")
        print("Instala con: npm install -g @anthropic-ai/claude-code")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print("ERROR: Timeout - la generacion tardo mas de 5 minutos.")
        sys.exit(1)

    if result.returncode != 0:
        print(f"ERROR: Claude CLI retorno codigo {result.returncode}")
        if result.stderr:
            print(f"stderr: {result.stderr[:500]}")
        sys.exit(1)

    raw_output = result.stdout.strip()
    if not raw_output:
        print("ERROR: Claude CLI no devolvio ninguna respuesta.")
        sys.exit(1)

    json_str = extract_json(raw_output)

    try:
        data = json.loads(json_str)
    except json.JSONDecodeError as e:
        print(f"ERROR: La respuesta no es JSON valido: {e}")
        # Guardar respuesta raw para debug
        debug_path = PENDING_DIR / "last_error_raw.txt"
        debug_path.write_text(raw_output, encoding="utf-8")
        print(f"Respuesta raw guardada en: {debug_path}")
        sys.exit(1)

    # Validar estructura minima
    if "pack" not in data or "blog" not in data:
        print("ERROR: El JSON no contiene las claves 'pack' y 'blog'.")
        sys.exit(1)

    # Generar nombre de archivo
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    slug = data.get("pack", {}).get("slug", slugify(description))
    filename = f"{timestamp}-{slug}.json"
    filepath = PENDING_DIR / filename

    filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Contenido generado correctamente!")
    print(f"Archivo: {filepath}")
    print(f"Pack: {data['pack'].get('title_es', 'N/A')}")
    print(f"Blog: {data['blog'].get('title_es', 'N/A')}")
    print(f"\nRevisa y aprueba desde el panel de admin: /admin/ai-generator")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/generate_content.py \"Descripcion del viaje\"")
        sys.exit(1)
    generate(" ".join(sys.argv[1:]))
