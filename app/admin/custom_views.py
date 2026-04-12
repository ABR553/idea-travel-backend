"""Custom admin views for SQLAdmin sidebar integration."""

from pathlib import Path
from uuid import UUID

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


from app.database import async_session_factory
from app.services import instagram_post_service

INSTAGRAM_TEMPLATES = TEMPLATES_DIR / "instagram"


class InstagramFeedView(BaseView):
    name = "Instagram Feed"
    icon = "fa-brands fa-instagram"

    @expose("/instagram-feed", methods=["GET"])
    async def page(self, request):
        async with async_session_factory() as db:
            posts, total = await instagram_post_service.list_posts(db, limit=60, offset=0)

        cards = []
        for p in posts:
            first_slide = (
                sorted(p.slides, key=lambda s: s.order)[0].image_url if p.slides else ""
            )
            cards.append(
                {
                    "id": str(p.id),
                    "topic": p.topic,
                    "status": p.status.value if hasattr(p.status, "value") else p.status,
                    "format": p.format.value if hasattr(p.format, "value") else p.format,
                    "image": first_slide,
                }
            )

        template = (INSTAGRAM_TEMPLATES / "feed.html").read_text(encoding="utf-8")
        # Extremely simple string templating — no Jinja env available here.
        import html
        cards_html = ""
        for c in cards:
            status_color = {
                "draft": "#6b7280",
                "pending_review": "#f59e0b",
                "approved": "#10b981",
                "scheduled": "#3b82f6",
                "published": "#8b5cf6",
                "rejected": "#ef4444",
            }.get(c["status"], "#6b7280")
            cards_html += (
                '<a class="card" href="/admin/instagram-preview?id=' + c["id"] + '">'
                '<img src="' + html.escape(c["image"]) + '" alt=""/>'
                '<span class="badge" style="background:' + status_color + '">'
                + html.escape(c["status"]) + '</span>'
                + ("<span class='carousel'>⊞</span>" if c["format"] == "carousel" else "")
                + '<div class="topic">' + html.escape(c["topic"]) + '</div>'
                '</a>'
            )
        html_body = template.replace("{{CARDS}}", cards_html).replace(
            "{{TOTAL}}", str(total)
        )
        return HTMLResponse(html_body)


class InstagramPreviewView(BaseView):
    name = "Instagram Preview"
    icon = "fa-solid fa-mobile-screen"

    @expose("/instagram-preview", methods=["GET"])
    async def page(self, request):
        post_id = request.query_params.get("id")
        if not post_id:
            return HTMLResponse("<p>Missing ?id=&lt;uuid&gt;</p>", status_code=400)
        async with async_session_factory() as db:
            post = await instagram_post_service.get_post(db, UUID(post_id))
        if post is None:
            return HTMLResponse("<p>Post not found</p>", status_code=404)

        import json as _json
        payload = {
            "id": str(post.id),
            "topic": post.topic,
            "status": post.status.value if hasattr(post.status, "value") else post.status,
            "language": post.language.value if hasattr(post.language, "value") else post.language,
            "locationName": post.location_name,
            "hashtags": post.hashtags,
            "translations": [
                {
                    "locale": t.locale,
                    "hook": t.hook,
                    "caption": t.caption,
                    "firstComment": t.first_comment,
                    "engagementHook": t.engagement_hook,
                }
                for t in post.translations
            ],
            "slides": [
                {
                    "order": s.order,
                    "imageUrl": s.image_url,
                    "overlayText": s.overlay_text,
                }
                for s in sorted(post.slides, key=lambda x: x.order)
            ],
            "targetAudience": post.target_audience,
            "postAngle": post.post_angle.value if post.post_angle else None,
            "bestPublishTime": post.best_publish_time.isoformat() if post.best_publish_time else None,
            "rationale": post.rationale,
            "sourceMcpRefs": post.source_mcp_refs,
            "publishAttempts": post.publish_attempts,
        }
        template = (INSTAGRAM_TEMPLATES / "preview.html").read_text(encoding="utf-8")
        return HTMLResponse(template.replace("{{PAYLOAD_JSON}}", _json.dumps(payload)))
