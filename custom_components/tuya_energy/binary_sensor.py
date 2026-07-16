import logging
from typing import Any, Callable, Dict, Optional

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DP_ID_ONLINE_STATE,
    DP_ID_FAULT,
)
from .__init__ import TuyaEnergyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable,
):
    """Set up Tuya Energy binary sensors from a config entry."""
    coordinator: TuyaEnergyDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        TuyaEnergyBinarySensor(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.device_name} Online",
            DP_ID_ONLINE_STATE,
            "connectivity",
            device_class="connectivity",
        ),
        TuyaEnergyBinarySensor(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.device_name} Fault",
            DP_ID_FAULT,
            "alert",
            device_class="problem",
        ),
    ]

    async_add_entities(entities)


class TuyaEnergyBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Representation of a Tuya Energy Binary Sensor."""

    def __init__(
        self,
        coordinator: TuyaEnergyDataUpdateCoordinator,
        entry_id: str,
        name: str,
        dp_id: int,
        icon: Optional[str] = None,
        device_class: Optional[str] = None,
        entity_category: Optional[EntityCategory] = None,
    ):
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._name = name
        self._dp_id = str(dp_id)  # Tuya DPs are often strings in status dict
        self._icon = icon
        self._device_class = device_class
        self._entity_category = entity_category

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{self._entry_id}_{self._dp_id}"

    @property
    def name(self) -> str:
        """Return the name of the binary sensor."""
        return self._name

    @property
    def is_on(self) -> Optional[bool]:
        """Return true if the binary sensor is on."""
        dps = self.coordinator.data.get("dps", {})
        value = dps.get(self._dp_id)
        if self._dp_id == str(DP_ID_ONLINE_STATE):
            return value == "online"
        elif self._dp_id == str(DP_ID_FAULT):
            return value is not None and int(value) != 0 # Fault is a bitmap, 0 means no fault
        return None

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        return f"mdi:{self._icon}" if self._icon else None

    @property
    def device_class(self) -> Optional[str]:
        """Return the device class of the binary sensor."""
        return self._device_class

    @property
    def entity_category(self) -> Optional[EntityCategory]:
        """Return the entity category of the binary sensor."""
        return self._entity_category

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        """Return device information for the binary sensor."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.device_id)},
            "name": self.coordinator.device_name,
            "manufacturer": "Tuya",
            "model": "Energy Breaker",  # This can be made dynamic later
            "via_device": (DOMAIN, self.coordinator.device_id),
        }
