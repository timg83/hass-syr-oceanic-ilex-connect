"""API client for Syr Oceanic i-Lex Connect."""

import logging
from typing import Any

import aiohttp

from .const import BASE_URL, DEVICES_ENDPOINT, LOGIN_ENDPOINT

_LOGGER = logging.getLogger(__name__)


class ILexAuthError(Exception):
    """Exception for authentication errors."""


class ILexClient:
    """Client for interacting with the i-Lex Connect API."""

    def __init__(
        self, session: aiohttp.ClientSession, username: str, password: str
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._username = username
        self._password = password
        self._authenticated = False

    async def login(self) -> None:
        """Authenticate with the API."""
        _LOGGER.debug("Attempting to authenticate with i-Lex Connect API")
        async with self._session.post(
            f"{BASE_URL}{LOGIN_ENDPOINT}",
            json={"username": self._username, "password": self._password},
        ) as resp:
            if resp.status != 200:
                _LOGGER.error("Login failed with status %s", resp.status)
                raise ILexAuthError("Login failed")
            data = await resp.json()
            if "redirect" not in data:
                _LOGGER.error("Unexpected login response: %s", data)
                raise ILexAuthError("Unexpected login response")
        self._authenticated = True
        _LOGGER.debug("Authentication successful")

    async def get_devices(self) -> dict[str, Any]:
        """Get list of devices from the API."""
        _LOGGER.debug("Fetching devices from API")
        # Retry once with re-authentication if session expired
        for attempt in range(2):
            async with self._session.get(
                f"{BASE_URL}{DEVICES_ENDPOINT}",
                params={"filterconnect": "online", "filterproducent": "oceanic"},
            ) as resp:
                if resp.status == 401:
                    _LOGGER.warning("Received 401, session expired (attempt %d/2)", attempt + 1)
                    if attempt == 0:
                        # First attempt failed, try to re-authenticate
                        await self.login()
                        continue
                    # Second attempt also failed, credentials are likely invalid
                    _LOGGER.error("Re-authentication failed after 401")
                    raise ILexAuthError("Session expired and re-authentication failed")
                resp.raise_for_status()
                devices = await resp.json()
                _LOGGER.debug("Successfully fetched %d devices", len(devices.get("results", [])))
                return devices
        raise ILexAuthError("Failed to get devices after retry")

    async def get_live_data(self, serial: str) -> dict[str, Any]:
        """Get live data for a specific device."""
        _LOGGER.debug("Fetching live data for device %s", serial)
        # Retry once with re-authentication if session expired
        for attempt in range(2):
            async with self._session.get(
                f"{BASE_URL}/api/devices/{serial}/live"
            ) as resp:
                if resp.status == 401:
                    _LOGGER.warning(
                        "Received 401 for device %s (attempt %d/2)", serial, attempt + 1
                    )
                    if attempt == 0:
                        # First attempt failed, try to re-authenticate
                        await self.login()
                        continue
                    # Second attempt also failed, credentials are likely invalid
                    _LOGGER.error("Re-authentication failed for device %s", serial)
                    raise ILexAuthError("Session expired and re-authentication failed")
                resp.raise_for_status()
                live_data = await resp.json()
                _LOGGER.debug(
                    "Successfully fetched live data for device %s (%d fields)",
                    serial,
                    len(live_data),
                )
                return live_data
        raise ILexAuthError("Failed to get live data after retry")
