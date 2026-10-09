import html
import re
from contextlib import asynccontextmanager
from functools import lru_cache
from pathlib import Path

from mcp.server import MCPServer

from .http_client import http_client
from .logger import logger


def clean_html(raw_html: str) -> str:
    if not raw_html:
        return ""

    text = re.sub(r"<(br|p|div|li)[^>]*>", "\n", raw_html, flags=re.IGNORECASE)

    text = re.sub(r"<[^>]+>", "", text)

    text = html.unescape(text)

    lines = [re.sub(r"[ \t]+", " ", line).strip() for line in text.split("\n")]
    return "\n".join(line for line in lines if line).strip()


@lru_cache(maxsize=1)
def load_prompt(file_name: str) -> str:

    instructions_path = Path(__file__).parent / file_name

    if not instructions_path.exists():
        return "You are the agent who addes the words to Anki."

    return instructions_path.read_text(encoding="utf-8").strip()


@asynccontextmanager
async def app_lifespan(server: MCPServer):
    logger.info("Initializing HTTP client and connection pool...")
    await http_client.start()
    try:
        yield
    finally:
        logger.info("Shutting down HTTP client...")
        await http_client.close()
