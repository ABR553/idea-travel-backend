# Bug: Admin statics devuelven 404 en produccion (Railway)

- **Fecha**: 2026-03-22
- **Tipo**: API / Static files / Deploy
- **Reportado como**: en produccion sigue sin verse el admin

## Causa raiz

sqladmin monta sus archivos estaticos (CSS/JS) usando `StaticFiles(packages=["sqladmin"])` dentro de un sub-mount `/admin`. Detras del proxy reverso de Railway, esta configuracion no resuelve los archivos correctamente, devolviendo 404 para todas las rutas `/admin/statics/*`.

El problema tiene dos capas:
1. El `StaticFiles(packages=["sqladmin"])` interno de sqladmin no servia los archivos en el entorno de produccion con gunicorn + proxy reverso.
2. Los intentos iniciales de montar statics explicitamente fallaron porque se registraban DESPUES del mount `/admin` de sqladmin, y Starlette resuelve rutas en orden de registro.

## Archivos modificados

- `app/main.py` - Montar `StaticFiles(directory=sqladmin/statics)` explicitamente ANTES de llamar a `setup_admin()`, para que Starlette resuelva `/admin/statics/*` antes que el catch-all `/admin`.
- `app/admin/setup.py` - Eliminar el mount duplicado de statics que se habia añadido aqui (no funcionaba por orden de registro).

## Solucion aplicada

Montar los statics de sqladmin directamente en la app FastAPI con ruta explícita al directorio del paquete, registrandolos antes de que sqladmin monte su sub-aplicacion en `/admin`. Esto asegura que las peticiones a `/admin/statics/*` se resuelvan con el mount explicito (posicion 14) antes de llegar al mount `/admin` de sqladmin (posicion 15).

## Verificacion

- Rebuild de imagen Docker de produccion
- TestClient confirma 200 en todos los statics: `main.css`, `tabler.min.css`, `main.js`, `jquery.min.js`
- `/admin/` devuelve 302 (redirect a login)
- `/admin/login` devuelve 200
