import logging
from typing import Any, Callable, Dict, Optional

from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DP_ID_CYCLE_TIME,
)
from .__init__ import TuyaEnergyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable,
):
    """Set up Tuya Energy text entities from a config entry."""
    coordinator: TuyaEnergyDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        TuyaEnergyText(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.name} Cycle Time",
            DP_ID_CYCLE_TIME,
            "clock-outline",
            entity_category=EntityCategory.CONFIG,
        ),
    ]

    async_add_entities(entities)


class TuyaEnergyText(CoordinatorEntity, TextEntity):
    """Representation of a Tuya Energy Text entity."""

    def __init__(
        self,
        coordinator: TuyaEnergyDataUpdateCoordinator,
        entry_id: str,
        name: str,
        dp_id: int,
        icon: Optional[str] = None,
        entity_category: Optional[EntityCategory] = None,
    ):
        """Initialize the text entity."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._name = name
        self._dp_id = str(dp_id)  # Tuya DPs are often strings in status dict
        self._icon = icon
        self._entity_category = entity_category

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{self._entry_id}_{self._dp_id}"

    @property
    def name(self) -> str:
        """Return the name of the text entity."""
        return self._name

    @property
    def native_value(self) -> Optional[str]:
        """Return the current value."""
        return self.coordinator.data.get(self._dp_id)

    async def async_set_value(self, value: str) -> None:
        """Set new value."""
        await self.coordinator.protocol.async_set_dp(self._dp_id, value)
        await self.coordinator.async_refresh()

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        return f"mdi:{self._icon}" if self._icon else None

    @property
    def entity_category(self) -> Optional[EntityCategory]:
        """Return the entity category of the text entity."""
        return self._entity_category

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        """Return device information for the text entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.device_id)},
            "name": self.coordinator.name,
            "manufacturer": "Tuya",
            "model": "Energy Breaker",  # This can be made dynamic later
            "via_device": (DOMAIN, self.coordinator.device_id),
        }
