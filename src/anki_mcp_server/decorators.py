from functools import wraps
from typing import Any

from anki_mcp_server.core import logger
from anki_mcp_server.core.exceptions import AnkiAPIError, AnkiConnectionError


def handle_anki_errors(func):
    @wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> str:
        try:
            return await func(*args, **kwargs)
        except (AnkiConnectionError, AnkiAPIError) as exc:
            error_msg = f"Error executing '{func.__name__}': {exc}"
            logger.error(error_msg)
            return error_msg
        except Exception as exc:
            logger.exception("Unexpected error in '%s'", func.__name__)
            return f"Unexpected Error: {exc}"

    return wrapper
