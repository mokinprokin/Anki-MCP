from mcp.server.mcpserver import MCPServer

from anki_mcp_server.core.config import settings
from anki_mcp_server.core.utils import app_lifespan, load_prompt
from anki_mcp_server.resources import register_anki_resources
from anki_mcp_server.tools import register_anki_tools

mcp = MCPServer(
    name="AnkiMCPServer",
    lifespan=app_lifespan,
    instructions=load_prompt(settings.instructions_filename),
)

register_anki_tools(mcp)
register_anki_resources(mcp)


def main():
    mcp.run()


if __name__ == "__main__":
    main()
