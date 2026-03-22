# Bug: Admin panel y statics 404 en Railway por root_path

- **Fecha**: 2026-03-22
- **Tipo**: API / Routing / Deploy
- **Reportado como**: sigue dando problemas verse el admin en el railway

## Causa raiz

El parametro `root_path` de FastAPI (leido desde la variable de entorno `ROOT_PATH`) rompe el routing de TODAS las sub-aplicaciones montadas con `app.mount()` en Starlette 0.52+.

Cuando `root_path` es no-vacio (ej. `/api`), la funcion `get_route_path()` de Starlette intenta descontar el `root_path` del `path` del scope ASGI. Esto causa que las sub-aplicaciones montadas (SQLAdmin en `/admin` y StaticFiles en `/admin/statics`) no puedan resolver sus rutas internas, devolviendo 404 para todo:

- `/admin/` -> 404 (deberia ser 302 a login)
- `/admin/login` -> 404
- `/admin/statics/css/main.css` -> 404
- `/admin/statics/js/jquery.min.js` -> 404

## Reproduccion

```python
app = FastAPI(root_path='/api')
app.mount('/admin', sub_app)
# GET /admin/ -> 404

app = FastAPI(root_path='')
app.mount('/admin', sub_app)
# GET /admin/ -> 200
```

## Archivos modificados

- `app/main.py` - Eliminado `root_path=settings.root_path` de FastAPI(). Railway no usa prefijo de path, por lo que root_path debe ser vacio.
- `app/config.py` - Eliminado el campo `root_path` de Settings ya que no se usa.

## Solucion aplicada

Eliminar el parametro `root_path` de la inicializacion de FastAPI. Railway sirve la app directamente en la raiz del dominio (sin prefijo de path), por lo que `root_path` no es necesario y su presencia rompe el routing de sub-aplicaciones montadas.

## Verificacion

- TestClient: `/admin/` -> 302, `/admin/login` -> 200, `/admin/statics/css/main.css` -> 200
- Gunicorn local (mismo setup que Railway): todos los endpoints admin devuelven 200/302 correctamente
- Health check `/api/v1/health` -> 200

## Accion adicional requerida

Si existe la variable de entorno `ROOT_PATH` configurada en Railway, **eliminarla**. Cualquier valor no-vacio causara el mismo problema.
