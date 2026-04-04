import json

from app.mcp.db import get_mcp_session
from app.mcp.instance import mcp
from app.services import project_service


@mcp.tool()
async def list_projects() -> str:
    """List all available projects. Use this to get the project slug needed for product operations."""
    async with get_mcp_session() as db:
        projects = await project_service.get_projects(db)
        return json.dumps(
            [p.model_dump(by_alias=True) for p in projects],
            default=str,
        )
