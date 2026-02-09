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
        _LOGGER.debug("Starting data update cycle")
        try:
            devices = await self.client.get_devices()
            _LOGGER.debug("Retrieved %d device(s) from API", len(devices.get("results", [])))
        except ILexAuthError as err:
            # If re-authentication failed, trigger reauth flow
            if "re-authentication failed" in str(err):
                _LOGGER.error("Re-authentication failed, triggering reauth flow")
                raise ConfigEntryAuthFailed(
                    "Authentication failed. Please re-authenticate."
                ) from err
            # Otherwise treat as temporary failure
            _LOGGER.error("Authentication error during update: %s", err)
            raise UpdateFailed(f"Authentication error: {err}") from err
        except Exception as err:
            _LOGGER.error("Error communicating with API: %s", err, exc_info=True)
            raise UpdateFailed(f"Error communicating with API: {err}") from err

        data = {}
        for device in devices["results"]:
            serial = device["serial"]
            _LOGGER.debug("Fetching live data for device %s", serial)
            try:
                live = await self.client.get_live_data(serial)
                data[serial] = {"meta": device, "live": live}
                _LOGGER.debug(
                    "Successfully retrieved live data for device %s. Sample data: %s",
                    serial,
                    {k: v for k, v in list(live.items())[:3]},  # Log first 3 items
                )
            except ILexAuthError as err:
                if "re-authentication failed" in str(err):
                    _LOGGER.error("Re-authentication failed for device %s", serial)
                    raise ConfigEntryAuthFailed(
                        "Authentication failed. Please re-authenticate."
                    ) from err
                _LOGGER.warning(
                    "Failed to get live data for device %s: %s", serial, err
                )
            except Exception as err:
                _LOGGER.warning(
                    "Failed to get live data for device %s: %s", serial, err, exc_info=True
                )
        _LOGGER.debug("Data update cycle completed. Retrieved data for %d device(s)", len(data))
        return data
