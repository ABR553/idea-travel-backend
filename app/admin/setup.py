from fastapi import FastAPI
from sqladmin import Admin

from app.admin.auth import authentication_backend
from app.admin.views import ALL_VIEWS
from app.database import engine


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
    return admin
