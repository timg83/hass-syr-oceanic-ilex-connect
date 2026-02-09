"""The Syr Oceanic i-Lex Connect integration."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ILexClient
from .coordinator import ILexDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

_PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]

type ILexConfigEntry = ConfigEntry[ILexDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: ILexConfigEntry) -> bool:
    """Set up Syr Oceanic i-Lex Connect from a config entry."""
    _LOGGER.debug("Setting up Syr Oceanic i-Lex Connect integration")
    session = async_get_clientsession(hass)
    api = ILexClient(
        session=session,
        username=entry.data["username"],
        password=entry.data["password"],
    )

    # Perform initial authentication
    _LOGGER.debug("Performing initial authentication")
    await api.login()
    _LOGGER.debug("Authentication successful")

    coordinator = ILexDataUpdateCoordinator(hass, api, entry)
    _LOGGER.debug("Starting first coordinator refresh")
    await coordinator.async_config_entry_first_refresh()
    _LOGGER.debug("First refresh completed, setting up platforms")
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)
    _LOGGER.debug("Syr Oceanic i-Lex Connect integration setup complete")

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ILexConfigEntry) -> bool:
    """Unload a config entry."""
    _LOGGER.debug("Unloading Syr Oceanic i-Lex Connect integration")
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
