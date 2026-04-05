from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

mcp = FastMCP(
    "idea-travel",
    instructions=(
        "MCP server for Idea Travel. Manage travel products (Amazon) and travel packs "
        "with destinations, accommodations, experiences, and route steps. "
        "All content supports bilingual translations (es/en). "
        "Use list_projects first to get the project slug before upserting products."
    ),
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
