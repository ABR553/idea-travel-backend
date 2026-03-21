"""Generate a Postman Collection v2.1 JSON from the FastAPI app OpenAPI spec.

Runs offline - imports the app directly, no HTTP needed.

Usage:
    python -m scripts.generate_postman
"""
import json
from pathlib import Path

from app.main import app

OUTPUT_PATH = Path("/app/docs/postman_collection.json")
BASE_URL = "{{base_url}}"


def openapi_to_postman(spec: dict) -> dict:
    collection: dict = {
        "info": {
            "name": spec.get("info", {}).get("title", "API Collection"),
            "description": spec.get("info", {}).get("description", ""),
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "variable": [
            {"key": "base_url", "value": "http://localhost:8100", "type": "string"},
            {"key": "locale", "value": "es", "type": "string"},
        ],
        "item": [],
    }

    folders: dict[str, list] = {}

    for path, methods in spec.get("paths", {}).items():
        for method, details in methods.items():
            if method not in ("get", "post", "put", "patch", "delete"):
                continue

            tags = details.get("tags", ["Other"])
            tag = tags[0] if tags else "Other"

            query_params = []
            path_vars = []
            for param in details.get("parameters", []):
                if param.get("in") == "query":
                    query_params.append({
                        "key": param["name"],
                        "value": "{{locale}}" if param["name"] == "locale" else "",
                        "description": param.get("schema", {}).get("title", ""),
                        "disabled": param["name"] != "locale",
                    })
                elif param.get("in") == "path":
                    path_vars.append({
                        "key": param["name"],
                        "description": param.get("schema", {}).get("title", ""),
                    })

            postman_path = path.replace("{", ":").replace("}", "")

            request_item = {
                "name": details.get("summary", f"{method.upper()} {path}"),
                "request": {
                    "method": method.upper(),
                    "header": [
                        {"key": "Accept-Language", "value": "{{locale}}", "type": "text", "disabled": True},
                    ],
                    "url": {
                        "raw": f"{BASE_URL}{postman_path}",
                        "host": [BASE_URL],
                        "path": [p for p in postman_path.strip("/").split("/") if p],
                        "query": query_params,
                        "variable": path_vars,
                    },
                    "description": details.get("description", ""),
                },
                "response": [],
            }

            if tag not in folders:
                folders[tag] = []
            folders[tag].append(request_item)

    for folder_name, items in folders.items():
        collection["item"].append({
            "name": folder_name.capitalize(),
            "item": items,
        })

    return collection


def main() -> None:
    spec = app.openapi()
    print(f"OpenAPI: {len(spec.get('paths', {}))} paths found")

    collection = openapi_to_postman(spec)

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(collection, f, indent=2, ensure_ascii=False)

    print(f"Postman collection saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
