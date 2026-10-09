import logging
import sys


def setup_logger(name: str = "anki_mcp") -> logging.Logger:
    """
    Configure and return a centralized application logger.

    Streams strictly to sys.stderr to avoid polluting sys.stdout,
    which is reserved exclusively for the MCP JSON-RPC protocol.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger


logger = setup_logger()
