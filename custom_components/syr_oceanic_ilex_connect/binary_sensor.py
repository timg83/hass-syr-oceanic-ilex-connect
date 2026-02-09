"""Binary sensor component for Syr Oceanic water filter system via Ilex Connect."""

from __future__ import annotations

from collections.abc import Callable
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

if TYPE_CHECKING:
    from . import ILexConfigEntry
from .const import DOMAIN
from .coordinator import ILexDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


def _check_online(value: str) -> bool:
    """Check if device is online."""
    return value == "online"


def _check_bool(value: Any) -> bool:
    """Check if value is truthy."""
    return bool(value)


def _check_not_empty(value: str) -> bool:
    """Check if value is not empty."""
    return value != ""


BINARY_MAP: list[dict[str, str | Callable[[Any], bool]]] = [
    {"translation_key": "connected", "key": "status", "check": _check_online},
    {
        "translation_key": "regeneration_active",
        "key": "regeneration",
        "check": _check_bool,
    },
    {
        "translation_key": "alarm_active",
        "key": "current_alarm",
        "check": _check_not_empty,
    },
    {
        "translation_key": "network_connected",
        "key": "getNET",
        "check": _check_not_empty,
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ILexConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Syr Oceanic binary sensors based on a config entry."""
    coordinator: ILexDataUpdateCoordinator = entry.runtime_data
    _LOGGER.debug("Setting up binary sensors for %d device(s)", len(coordinator.data))
    entities = [
        ILexBinarySensor(coordinator, serial, bin_def)
        for serial in coordinator.data
        for bin_def in BINARY_MAP
    ]
    _LOGGER.debug("Adding %d binary sensor entities", len(entities))
    async_add_entities(entities)


class ILexBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Syr Oceanic binary sensor."""

    def __init__(
        self,
        coordinator: ILexDataUpdateCoordinator,
        serial: str,
        bin_def: dict[str, str | Callable[[Any], bool]],
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.serial = serial
        self.bin_def = bin_def
        self._attr_has_entity_name = True
        self._attr_translation_key = str(bin_def["translation_key"])
        self._attr_unique_id = f"{serial}_{bin_def['key']}"
        _LOGGER.debug(
            "Initialized binary sensor %s for device %s",
            bin_def["translation_key"],
            serial,
        )

    @property
    def is_on(self) -> bool | None:
        """Return true if the binary sensor is on."""
        value = self.coordinator.data[self.serial]["live"].get(self.bin_def["key"])
        check_func = self.bin_def["check"]
        if callable(check_func):
            result = check_func(value)
            _LOGGER.debug(
                "Binary sensor %s (%s) value: %s -> %s",
                self.bin_def["translation_key"],
                self.bin_def["key"],
                value,
                result,
            )
            return result
        return None

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information about this sensor."""
        meta = self.coordinator.data[self.serial]["meta"]
        live = self.coordinator.data[self.serial]["live"]
        return DeviceInfo(
            identifiers={(DOMAIN, meta["serial"])},
            name=f"Syr Oceanic {meta['dtype']}",
            manufacturer="Syr / Oceanic",
            model=meta["dtype"],
            sw_version=live.get("firmware_version"),
        )
