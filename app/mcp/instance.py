from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
    "idea-travel",
    instructions=(
        "MCP server for Idea Travel. Manage travel products (Amazon) and travel packs "
        "with destinations, accommodations, experiences, and route steps. "
        "All content supports bilingual translations (es/en). "
        "Use list_projects first to get the project slug before upserting products."
    ),
    streamable_http_path="/",
)
