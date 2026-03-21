# Feature: Admin Panel con SQLAdmin

- **Fecha**: 2026-03-21
- **Solicitado como**: crea o investiga como crear un admin para todas mis tablas con autenticacion de usuario y contrasena

## Descripcion
Panel de administracion web completo para gestionar todas las tablas de la base de datos. Usa SQLAdmin, una libreria diseñada especificamente para FastAPI + SQLAlchemy async. Incluye autenticacion por usuario/contraseña con sesiones firmadas.

## Archivos creados
- `app/admin/__init__.py` - Modulo admin
- `app/admin/auth.py` - Backend de autenticacion con sesiones (usuario/contraseña desde .env)
- `app/admin/views.py` - ModelView para las 12 tablas con columnas, busqueda y ordenacion configuradas
- `app/admin/setup.py` - Funcion que monta SQLAdmin en la app FastAPI

## Archivos modificados
- `requirements.txt` - Añadido sqladmin>=0.20.0 e itsdangerous>=2.2.0
- `app/config.py` - Añadidos settings: admin_username, admin_password, admin_secret
- `app/main.py` - Integrado setup_admin(app) despues del router
- `.env.example` - Añadidas variables ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_SECRET

## Migraciones
No se requieren migraciones. SQLAdmin usa los modelos SQLAlchemy existentes directamente.

## Endpoints nuevos
- `GET /admin/` - Panel de administracion (interfaz web)
- `GET /admin/login` - Pagina de login
- `POST /admin/login` - Autenticacion
- `GET /admin/logout` - Cerrar sesion

## Tablas registradas (12)
1. Pack - Packs de viaje
2. PackTranslation - Traducciones de packs
3. Destination - Destinos
4. DestinationTranslation - Traducciones de destinos
5. RouteStep - Pasos de ruta
6. RouteStepTranslation - Traducciones de pasos
7. Accommodation - Alojamientos
8. AccommodationTranslation - Traducciones de alojamientos
9. Experience - Experiencias
10. ExperienceTranslation - Traducciones de experiencias
11. Product - Productos
12. ProductTranslation - Traducciones de productos

## Decisiones tecnicas
- **SQLAdmin** elegido por: soporte nativo async SQLAlchemy, integracion directa con FastAPI, UI moderna con Tabler, CRUD automatico
- **Autenticacion por env vars** en vez de tabla de usuarios: simplicidad para un admin single-user
- **itsdangerous** para firmar cookies de sesion de forma segura
- Cada ModelView tiene column_list, column_searchable_list y column_sortable_list configurados para facilitar la gestion

## Verificacion
- `GET /admin/` -> 302 (redirige a login, autenticacion funciona)
- `GET /admin/login` -> 200 (pagina de login renderiza correctamente)
- `GET /api/v1/health` -> 200 (API existente no afectada)
