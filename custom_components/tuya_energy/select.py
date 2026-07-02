import logging
from typing import Any, Callable, Dict, Optional

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DP_ID_RELAY_STATUS,
    DP_ID_LIGHT_MODE,
)
from .__init__ import TuyaEnergyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)

# Options for Relay Status and Light Mode (based on common Tuya devices)
RELAY_STATUS_OPTIONS = ["on", "off", "memory"]
LIGHT_MODE_OPTIONS = ["relay", "none"]

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable,
):
    """Set up Tuya Energy select entities from a config entry."""
    coordinator: TuyaEnergyDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        TuyaEnergySelect(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.name} Relay Status",
            DP_ID_RELAY_STATUS,
            RELAY_STATUS_OPTIONS,
            "toggle-switch",
            entity_category=EntityCategory.CONFIG,
        ),
        TuyaEnergySelect(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.name} Light Mode",
            DP_ID_LIGHT_MODE,
            LIGHT_MODE_OPTIONS,
            "lightbulb-on",
            entity_category=EntityCategory.CONFIG,
        ),
    ]

    async_add_entities(entities)


class TuyaEnergySelect(CoordinatorEntity, SelectEntity):
    """Representation of a Tuya Energy Select entity."""

    def __init__(
        self,
        coordinator: TuyaEnergyDataUpdateCoordinator,
        entry_id: str,
        name: str,
        dp_id: int,
        options: list[str],
        icon: Optional[str] = None,
        entity_category: Optional[EntityCategory] = None,
    ):
        """Initialize the select entity."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._name = name
        self._dp_id = str(dp_id)  # Tuya DPs are often strings in status dict
        self._options = options
        self._icon = icon
        self._entity_category = entity_category

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{self._entry_id}_{self._dp_id}"

    @property
    def name(self) -> str:
        """Return the name of the select entity."""
        return self._name

    @property
    def current_option(self) -> Optional[str]:
        """Return the current selected option."""
        dps = self.coordinator.data.get("dps", {})
        return dps.get(self._dp_id)

    @property
    def options(self) -> list[str]:
        """Return a list of available options."""
        return self._options

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        await self.coordinator.protocol.async_set_dp(self._dp_id, option)
        await self.coordinator.async_refresh()

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        return f"mdi:{self._icon}" if self._icon else None

    @property
    def entity_category(self) -> Optional[EntityCategory]:
        """Return the entity category of the select entity."""
        return self._entity_category

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        """Return device information for the select entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.device_id)},
            "name": self.coordinator.name,
            "manufacturer": "Tuya",
            "model": "Energy Breaker",  # This can be made dynamic later
            "via_device": (DOMAIN, self.coordinator.device_id),
        }
