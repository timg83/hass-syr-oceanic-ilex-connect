"""The Syr Oceanic i-Lex Connect integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import ILexClient
from .coordinator import ILexDataUpdateCoordinator

_PLATFORMS: list[Platform] = [Platform.BINARY_SENSOR, Platform.SENSOR]

type ILexConfigEntry = ConfigEntry[ILexDataUpdateCoordinator]


async def async_setup_entry(hass: HomeAssistant, entry: ILexConfigEntry) -> bool:
    """Set up Syr Oceanic i-Lex Connect from a config entry."""
    session = async_get_clientsession(hass)
    api = ILexClient(
        session=session,
        username=entry.data["username"],
        password=entry.data["password"],
    )

    # Perform initial authentication
    await api.login()

    coordinator = ILexDataUpdateCoordinator(hass, api, entry)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ILexConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
