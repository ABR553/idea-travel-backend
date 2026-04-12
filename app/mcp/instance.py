from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

mcp = FastMCP(
    "idea-travel",
    instructions=(
        "MCP server for Idea Travel. Manage travel products (Amazon), travel packs "
        "with destinations, accommodations, experiences, and route steps, and blog posts. "
        "All content supports bilingual translations (es/en). "
        "Use list_projects first to get the project slug before upserting products. "
        "For blog posts use create_blog_post / update_blog_post / delete_blog_post / "
        "list_blog_posts / get_blog_post; always provide both es and en translations."
    ),
    stateless_http=True,
    streamable_http_path="/",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "localhost:*",
            "127.0.0.1:*",
            "api.tengounviaje.com",
            "api.tengounviaje.com:*",
            "*.railway.internal",
            "*.railway.internal:*",
        ],
        allowed_origins=[
            "https://api.tengounviaje.com",
            "http://localhost",
            "http://localhost:*",
            "https://localhost",
            "https://localhost:*",
            "http://127.0.0.1",
            "http://127.0.0.1:*",
        ],
    ),
)
