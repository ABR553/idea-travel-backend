"""MCP server assembly — imports all tools and re-exports the FastMCP instance."""

from app.mcp.instance import mcp  # noqa: F401

# Import tool modules to trigger @mcp.tool() registration
import app.mcp.tools.products  # noqa: F401
import app.mcp.tools.packs  # noqa: F401
import app.mcp.tools.projects  # noqa: F401
import app.mcp.tools.destinations  # noqa: F401
