"""Custom admin views for SQLAdmin sidebar integration."""

from pathlib import Path

from sqladmin import BaseView, expose
from starlette.responses import HTMLResponse

TEMPLATES_DIR = Path(__file__).parent / "templates"


class BlogEditorView(BaseView):
    name = "Blog Editor"
    icon = "fa-solid fa-pen-to-square"

    @expose("/blog-editor", methods=["GET"])
    async def page(self, request):
        html = (TEMPLATES_DIR / "blog_editor.html").read_text(encoding="utf-8")
        return HTMLResponse(html)


class AIGeneratorView(BaseView):
    name = "AI Generator"
    icon = "fa-solid fa-wand-magic-sparkles"

    @expose("/ai-generator", methods=["GET"])
    async def page(self, request):
        html = (TEMPLATES_DIR / "ai_generator.html").read_text(encoding="utf-8")
        return HTMLResponse(html)
