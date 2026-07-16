import logging
from typing import Any, Callable, Dict, Optional

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DP_ID_ENERGY,
    DP_ID_CURRENT,
    DP_ID_POWER,
    DP_ID_VOLTAGE,
    DP_ID_FAULT,
    DP_ID_ONLINE_STATE,
    VOLTAGE_SCALE,
    POWER_SCALE,
    CURRENT_SCALE,
    ENERGY_SCALE,
)
from .__init__ import TuyaEnergyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable,
):
    """Set up Tuya Energy sensors from a config entry."""
    coordinator: TuyaEnergyDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        TuyaEnergySensor(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.device_name} Voltage",
            DP_ID_VOLTAGE,
            "V",
            "voltage",
            VOLTAGE_SCALE,
        ),
        TuyaEnergySensor(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.device_name} Current",
            DP_ID_CURRENT,
            "A",
            "current",
            CURRENT_SCALE,
        ),
        TuyaEnergySensor(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.device_name} Power",
            DP_ID_POWER,
            "W",
            "power",
            POWER_SCALE,
        ),
        TuyaEnergySensor(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.device_name} Energy",
            DP_ID_ENERGY,
            "kWh",
            "energy",
            ENERGY_SCALE,
            device_class="energy",
            state_class="total_increasing",
        ),
        TuyaEnergySensor(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.device_name} Fault",
            DP_ID_FAULT,
            None,
            "alert-circle",
            None,
            entity_category=EntityCategory.DIAGNOSTIC,
        ),
        # DP_ID_ONLINE_STATE will be a binary_sensor
    ]

    async_add_entities(entities)


class TuyaEnergySensor(CoordinatorEntity, SensorEntity):
    """Representation of a Tuya Energy Sensor."""

    def __init__(
        self,
        coordinator: TuyaEnergyDataUpdateCoordinator,
        entry_id: str,
        name: str,
        dp_id: int,
        unit_of_measurement: Optional[str],
        icon: Optional[str],
        scale: Optional[int] = None,
        device_class: Optional[str] = None,
        state_class: Optional[str] = None,
        entity_category: Optional[EntityCategory] = None,
    ):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._name = name
        self._dp_id = str(dp_id) # Tuya DPs are often strings in status dict
        self._unit_of_measurement = unit_of_measurement
        self._icon = icon
        self._scale = scale
        self._device_class = device_class
        self._state_class = state_class
        self._entity_category = entity_category

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{self._entry_id}_{self._dp_id}"

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self) -> Any:
        """Return the state of the sensor."""
        dps = self.coordinator.data.get("dps", {})
        value = dps.get(self._dp_id)
        if value is None:
            return None
        if self._scale:
            return round(float(value) / self._scale, 3)
        return value

    @property
    def unit_of_measurement(self) -> Optional[str]:
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        return f"mdi:{self._icon}" if self._icon else None

    @property
    def device_class(self) -> Optional[str]:
        """Return the device class of the sensor."""
        return self._device_class

    @property
    def state_class(self) -> Optional[str]:
        """Return the state class of the sensor."""
        return self._state_class

    @property
    def entity_category(self) -> Optional[EntityCategory]:
        """Return the entity category of the sensor."""
        return self._entity_category

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        """Return device information for the sensor."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.device_id)},
            "name": self.coordinator.device_name,
            "manufacturer": "Tuya",
            "model": "Energy Breaker", # This can be made dynamic later
            "via_device": (DOMAIN, self.coordinator.device_id),
        }
