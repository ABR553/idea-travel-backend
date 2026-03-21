from pathlib import Path

import sqladmin
from fastapi import FastAPI
from sqladmin import Admin
from starlette.staticfiles import StaticFiles

from app.admin.auth import authentication_backend
from app.admin.views import ALL_VIEWS
from app.database import engine

SQLADMIN_STATICS = str(Path(sqladmin.__file__).parent / "statics")


def setup_admin(app: FastAPI) -> Admin:
    admin = Admin(
        app,
        engine,
        authentication_backend=authentication_backend,
        title="Idea Travel Admin",
        base_url="/admin",
    )
    for view in ALL_VIEWS:
        admin.add_view(view)
    # Montar statics explicitamente para evitar problemas con proxy reverso
    app.mount("/admin/statics", StaticFiles(directory=SQLADMIN_STATICS), name="admin-statics")
    return admin
