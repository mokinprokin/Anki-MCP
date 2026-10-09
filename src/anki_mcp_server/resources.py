import json

from mcp.server.mcpserver import MCPServer

from anki_mcp_server.anki.service import anki_service
from anki_mcp_server.core.logger import logger
from anki_mcp_server.decorators import handle_anki_errors


def register_anki_resources(mcp: MCPServer) -> None:
    """
    Registers read-only data resources (Eyes of the LLM) to the MCP Server.
    """

    @mcp.resource("anki://decks")
    @handle_anki_errors
    async def list_decks_resource() -> str:
        """
        Resource containing the list of all available Anki deck names.
        """
        logger.info("Resource requested: list of decks")
        decks = await anki_service.get_deck_names()
        return json.dumps(decks, ensure_ascii=False, indent=2)
