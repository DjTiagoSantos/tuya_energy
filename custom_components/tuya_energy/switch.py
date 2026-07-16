import logging
from typing import Any, Callable, Dict, Optional

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DP_ID_SWITCH,
    DP_ID_CHILD_LOCK,
)
from .__init__ import TuyaEnergyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable,
):
    """Set up Tuya Energy switches from a config entry."""
    coordinator: TuyaEnergyDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        TuyaEnergySwitch(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.device_name} Power",
            DP_ID_SWITCH,
            "power",
        ),
        TuyaEnergySwitch(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.device_name} Child Lock",
            DP_ID_CHILD_LOCK,
            "lock",
            entity_category=EntityCategory.CONFIG,
        ),
    ]

    async_add_entities(entities)


class TuyaEnergySwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Tuya Energy Switch."""

    def __init__(
        self,
        coordinator: TuyaEnergyDataUpdateCoordinator,
        entry_id: str,
        name: str,
        dp_id: int,
        icon: Optional[str] = None,
        entity_category: Optional[EntityCategory] = None,
    ):
        """Initialize the switch."""
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
        """Return the name of the switch."""
        return self._name

    @property
    def is_on(self) -> Optional[bool]:
        """Return true if the switch is on."""
        return self.coordinator.data.get(self._dp_id)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the switch on."""
        await self.coordinator.protocol.async_set_dp(self._dp_id, True)
        await self.coordinator.async_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the switch off."""
        await self.coordinator.protocol.async_set_dp(self._dp_id, False)
        await self.coordinator.async_refresh()

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        return f"mdi:{self._icon}" if self._icon else None

    @property
    def entity_category(self) -> Optional[EntityCategory]:
        """Return the entity category of the switch."""
        return self._entity_category

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        """Return device information for the switch."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.device_id)},
            "name": self.coordinator.device_name,
            "manufacturer": "Tuya",
            "model": "Energy Breaker",  # This can be made dynamic later
            "via_device": (DOMAIN, self.coordinator.device_id),
        }
