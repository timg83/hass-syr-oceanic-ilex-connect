"""Data coordinator for Syr Oceanic i-Lex Connect."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ILexAuthError, ILexClient
from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class ILexDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
    """Class to manage fetching Syr Oceanic data."""

    def __init__(
        self, hass: HomeAssistant, client: ILexClient, config_entry: ConfigEntry
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
            config_entry=config_entry,
        )
        self.client = client

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch data from API endpoint."""
        try:
            devices = await self.client.get_devices()
        except ILexAuthError as err:
            # If re-authentication failed, trigger reauth flow
            if "re-authentication failed" in str(err):
                raise ConfigEntryAuthFailed(
                    "Authentication failed. Please re-authenticate."
                ) from err
            # Otherwise treat as temporary failure
            raise UpdateFailed(f"Authentication error: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        data = {}
        for device in devices["results"]:
            serial = device["serial"]
            try:
                live = await self.client.get_live_data(serial)
                data[serial] = {"meta": device, "live": live}
            except ILexAuthError as err:
                if "re-authentication failed" in str(err):
                    raise ConfigEntryAuthFailed(
                        "Authentication failed. Please re-authenticate."
                    ) from err
                _LOGGER.warning(
                    "Failed to get live data for device %s: %s", serial, err
                )
            except Exception as err:
                _LOGGER.warning(
                    "Failed to get live data for device %s: %s", serial, err
                )
        return data
