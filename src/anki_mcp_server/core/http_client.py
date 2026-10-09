import asyncio
from contextlib import asynccontextmanager
from typing import Any

import aiohttp

from .config import settings
from .exceptions import AnkiConnectionError, AnkiServiceNotInitializedError
from .logger import logger


class HttpClient:
    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None
        self._connector: aiohttp.TCPConnector | None = None

    async def start(self) -> None:
        """
        Initialize the TCP connection pool and client session.
        Called once during application startup.
        """
        if self._session and not self._session.closed:
            logger.warning("HttpClient is already running.")
            return

        self._connector = aiohttp.TCPConnector(
            limit=6, limit_per_host=3, force_close=True, enable_cleanup_closed=True
        )

        timeout = aiohttp.ClientTimeout(total=float(settings.request_timeout))

        self._session = aiohttp.ClientSession(
            connector=self._connector,
            timeout=timeout,
            headers={"Content-Type": "application/json", "Connection": "close"},
        )
        logger.info("HttpClient connection pool established successfully.")

    async def close(self) -> None:
        """
        Gracefully drain connection pool and shut down client session.
        Called during application shutdown.
        """
        if self._session and not self._session.closed:
            logger.info("Draining HTTP connection pool...")
            await self._session.close()
            await asyncio.sleep(0.25)
            self._session = None
            self._connector = None
            logger.info("HttpClient connection pool closed.")

    @asynccontextmanager
    async def request(self, method: str, url: str, **kwargs: Any):
        if self._session is None or self._session.closed:
            raise AnkiServiceNotInitializedError(
                "HttpClient is not initialized. Ensure lifespan context has started."
            )

        try:
            async with self._session.request(method, url, **kwargs) as response:
                yield response

        except TimeoutError as exc:
            logger.error(
                "Request to %s timed out after %ss", url, settings.request_timeout
            )
            raise AnkiConnectionError(
                f"HTTP request timed out after {settings.request_timeout} seconds."
            ) from exc

        except aiohttp.ClientConnectorError as exc:
            logger.error("Failed to establish TCP connection to %s: %s", url, exc)
            raise AnkiConnectionError(
                f"Failed to connect to host at '{url}'. Verify that the target service is running."
            ) from exc

        except aiohttp.ClientError as exc:
            logger.error("Unexpected aiohttp transport failure: %s", exc)
            raise AnkiConnectionError(f"HTTP transport failure: {exc}") from exc


http_client = HttpClient()
