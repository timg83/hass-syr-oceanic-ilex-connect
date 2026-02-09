"""Sensor component for Syr Oceanic water filter system via Ilex Connect."""

from __future__ import annotations

from typing import TYPE_CHECKING

from datetime import datetime

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import UnitOfPressure, UnitOfTime, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.typing import StateType

if TYPE_CHECKING:
    from . import ILexConfigEntry
from .const import DOMAIN, FRENCH_DEGREE_HARDNESS
from .coordinator import ILexDataUpdateCoordinator

SENSOR_MAP = [
    {
        "translation_key": "water_pressure",
        "key": "getPRS",
        "unit": UnitOfPressure.BAR,
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "translation_key": "current_flow",
        "key": "getFLO",
        "unit": UnitOfVolume.LITERS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "translation_key": "remaining_capacity",
        "key": "getRES",
        "unit": UnitOfVolume.LITERS,
        "state_class": SensorStateClass.MEASUREMENT,
    },
    {
        "translation_key": "water_used_today",
        "key": "getTOF",
        "unit": UnitOfVolume.CUBIC_METERS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL,
    },
    {
        "translation_key": "water_used_yesterday",
        "key": "getYEF",
        "unit": UnitOfVolume.CUBIC_METERS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL,
    },
    {
        "translation_key": "water_used_current_week",
        "key": "getCWF",
        "unit": UnitOfVolume.CUBIC_METERS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL,
    },
    {
        "translation_key": "water_used_last_week",
        "key": "getLWF",
        "unit": UnitOfVolume.CUBIC_METERS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL,
    },
    {
        "translation_key": "water_used_current_month",
        "key": "getCMF",
        "unit": UnitOfVolume.CUBIC_METERS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL,
    },
    {
        "translation_key": "water_used_last_month",
        "key": "getLMF",
        "unit": UnitOfVolume.CUBIC_METERS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL,
    },
    {"translation_key": "days_remaining", "key": "getRPD", "unit": UnitOfTime.DAYS},
    {
        "translation_key": "total_usage",
        "key": "getCOF",
        "unit": UnitOfVolume.CUBIC_METERS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {
        "translation_key": "total_usage_hard_water",
        "key": "getUWF",
        "unit": UnitOfVolume.CUBIC_METERS,
        "device_class": SensorDeviceClass.WATER,
        "state_class": SensorStateClass.TOTAL_INCREASING,
    },
    {"translation_key": "last_regeneration", "key": "getLAR"},
    {"translation_key": "normal_regenerations", "key": "getNOR"},
    {"translation_key": "service_regenerations", "key": "getSRE"},
    {"translation_key": "incomplete_regenerations", "key": "getINR"},
    {
        "translation_key": "inbound_water_hardness",
        "key": "getIWH",
        "unit": FRENCH_DEGREE_HARDNESS,
    },
    {
        "translation_key": "outbound_water_hardness",
        "key": "getOWH",
        "unit": FRENCH_DEGREE_HARDNESS,
    },
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ILexConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Syr Oceanic sensors based on a config entry."""
    coordinator: ILexDataUpdateCoordinator = entry.runtime_data
    entities: list[ILexSensor] = []
    for serial in coordinator.data:
        entities.extend(
            ILexSensor(coordinator, serial, sensor_def) for sensor_def in SENSOR_MAP
        )
        # Add last update sensor
        entities.append(ILexLastUpdateSensor(coordinator, serial))
    async_add_entities(entities)


class ILexSensor(SensorEntity):
    """Representation of a Syr Oceanic sensor."""

    def __init__(
        self,
        coordinator: ILexDataUpdateCoordinator,
        serial: str,
        sensor_def: dict[str, str],
    ) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.serial = serial
        self.sensor_def = sensor_def
        self._attr_has_entity_name = True
        self._attr_translation_key = sensor_def["translation_key"]
        self._attr_unique_id = f"{serial}_{sensor_def['key']}"
        self._attr_native_unit_of_measurement = sensor_def.get("unit")
        self._attr_device_class = sensor_def.get("device_class")
        self._attr_state_class = sensor_def.get("state_class")

    @property
    def native_value(self) -> StateType:
        """Return the state of the sensor."""
        value = self.coordinator.data[self.serial]["live"].get(self.sensor_def["key"])
        if value in (None, ""):
            return None
        # Only convert to float if sensor has a unit (numeric sensor)
        if self.sensor_def.get("unit"):
            try:
                return float(value)
            except (ValueError, TypeError):
                return None
        return value

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


class ILexLastUpdateSensor(SensorEntity):
    """Sensor that shows when data was last updated."""

    def __init__(
        self,
        coordinator: ILexDataUpdateCoordinator,
        serial: str,
    ) -> None:
        """Initialize the sensor."""
        self.coordinator = coordinator
        self.serial = serial
        self._attr_has_entity_name = True
        self._attr_translation_key = "last_update"
        self._attr_unique_id = f"{serial}_last_update"
        self._attr_device_class = SensorDeviceClass.TIMESTAMP

    @property
    def native_value(self) -> datetime | None:
        """Return the last update time."""
        return self.coordinator.last_update_success_time

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
