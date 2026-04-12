# Feature: MCP blog post tools (create / update / list / delete)

Date: 2026-04-12

## Descripcion
Expuesta la gestion completa de `BlogPost` a traves del servidor MCP `idea-travel`. Antes de este cambio, el backend ya soportaba blog posts a nivel de modelo, schemas, servicio y endpoints REST, pero el MCP server no ofrecia ninguna tool para operar sobre ellos. Ahora un cliente MCP puede crear, actualizar, listar, consultar y borrar articulos con traducciones bilingues (es/en) sin tocar la API REST.

## Alcance
- Solo backend (`idea-travel-backend`). No se toca frontend: la UI de blog (`/[locale]/blog`) sigue consumiendo la API REST sin cambios.
- No hay migracion, no hay cambios de modelo, schemas ni servicio. Solo se anade una capa MCP encima del `blog_service` existente.

## Archivos creados
- `app/mcp/tools/blogs.py` — 6 tools MCP:
  - `list_blog_posts(category?, search?, page, page_size, locale, include_unpublished)` — lista paginada. Con `include_unpublished=True` devuelve drafts via `blog_service.get_all_posts_admin`.
  - `get_blog_post(slug, locale, include_unpublished)` — detalle completo. Con `include_unpublished=True` usa `get_post_by_slug_admin`.
  - `list_blog_categories()` — categorias distintas con posts publicados.
  - `create_blog_post(slug, cover_image, category, translations, published, published_at?, related_pack_slug?)` — crea post + `BlogPostTranslation` para cada locale provisto. Valida con `BlogPostCreate`.
  - `update_blog_post(slug, new_slug?, cover_image?, category?, translations?, published?, published_at?, related_pack_slug?)` — todos los campos opcionales. Si `translations` se pasa, el service **reemplaza** el set completo de traducciones (comportamiento existente de `blog_service.update_post`).
  - `delete_blog_post(slug)` — borra el post y sus traducciones (cascada ya definida en el modelo).

- `docs/history/feature-2026-04-12-mcp-blog-tools.md` — este archivo.

## Archivos modificados
- `app/mcp/server.py` — anadido `import app.mcp.tools.blogs` para que las tools se registren al arrancar el servidor MCP.
- `app/mcp/instance.py` — extendidas las `instructions` del `FastMCP` para mencionar la gestion de blog posts y recordar que siempre se pasen traducciones es + en.

## Contrato ejemplo
```json
// create_blog_post input
{
  "slug": "10-consejos-tailandia",
  "cover_image": "https://.../cover.jpg",
  "category": "destinos",
  "published": true,
  "published_at": "2026-04-12",
  "related_pack_slug": "thailand-7-days",
  "translations": [
    {"locale":"es","title":"10 consejos...","excerpt":"Resumen","content":"# Markdown"},
    {"locale":"en","title":"10 tips...","excerpt":"Summary","content":"# Markdown"}
  ]
}
```

Respuesta (`_post_summary`): `{id, slug, category, cover_image, published, published_at, related_pack_id, translations:[{locale,title,excerpt}]}`.

## Decisiones tecnicas
- Reutilizar 100% `blog_service` sin tocarlo. Cada tool MCP es un wrapper fino que valida con los schemas Pydantic (`BlogPostCreate` / `BlogPostUpdate`) y convierte el resultado a `json.dumps(...)`, igual patron que `app/mcp/tools/products.py` y `app/mcp/tools/packs.py`.
- `translations` se expone como `list[dict]` (no `list[BlogPostTranslationCreate]`) por consistencia con las otras tools de escritura — el MCP llega habitualmente con JSON desde clientes LLM.
- `include_unpublished` se expone opcionalmente para permitir drafts desde el MCP sin romper los endpoints REST publicos (que siguen filtrando por `published=True`).
- `update_blog_post` replica el comportamiento actual del service: pasar `translations` reemplaza todas las existentes. Si se quiere upsert por locale, habra que tocar `blog_service.update_post` en un cambio posterior.
- `_post_summary` incluye solo `title` y `excerpt` por traduccion (no `content`) para mantener la respuesta ligera tras un create/update. Para leer contenido completo se usa `get_blog_post`.

## Verificacion
1. `docker-compose up -d --build` — contenedor api reconstruido.
2. Listado de tools registradas desde dentro del contenedor:
   ```python
   import app.mcp.server as s
   print(sorted(t.name for t in s.mcp._tool_manager._tools.values()))
   ```
   Resultado: 20 tools, incluyendo las 6 nuevas (`create_blog_post`, `update_blog_post`, `delete_blog_post`, `get_blog_post`, `list_blog_posts`, `list_blog_categories`).
3. Smoke test end-to-end contra PostgreSQL real dentro del contenedor:
   - `create_blog_post(slug='mcp-smoke-test-post', published=True, translations=[es, en])` -> OK, UUID devuelto.
   - `update_blog_post(slug, category='consejos', translations=[es, en])` -> categoria actualizada, traducciones reemplazadas.
   - `get_blog_post(slug, locale='en', include_unpublished=True)` -> content EN actualizado.
   - `list_blog_posts(include_unpublished=True)` -> total=4 incluyendo el post de prueba.
   - `delete_blog_post(slug)` -> borrado confirmado.

## Notas de uso para clientes MCP
- Proveer siempre ambos locales (`es` + `en`) en `translations` al crear o actualizar, para mantener paridad con el resto de entidades del sistema.
- `published_at` acepta formato ISO `YYYY-MM-DD`. Si `published=true` y se omite, el service lo fija a `now(UTC)`.
- `related_pack_slug` se resuelve internamente a `related_pack_id` via `Pack.slug`.
