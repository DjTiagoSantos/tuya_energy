import logging
from typing import Any, Callable, Dict, Optional

from homeassistant.components.number import NumberEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    DP_ID_COUNTDOWN,
    DP_ID_CYCLE_TIME,
)
from .__init__ import TuyaEnergyDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: Callable,
):
    """Set up Tuya Energy number entities from a config entry."""
    coordinator: TuyaEnergyDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = [
        TuyaEnergyNumber(
            coordinator,
            config_entry.entry_id,
            f"{coordinator.device_name} Countdown",
            DP_ID_COUNTDOWN,
            0, # Min value
            86400, # Max value (24 hours in seconds)
            1, # Step
            "seconds",
            "timer",
            entity_category=EntityCategory.CONFIG,
        ),
        # DP_ID_CYCLE_TIME is a string, will be a text entity
    ]

    async_add_entities(entities)


class TuyaEnergyNumber(CoordinatorEntity, NumberEntity):
    """Representation of a Tuya Energy Number entity."""

    def __init__(
        self,
        coordinator: TuyaEnergyDataUpdateCoordinator,
        entry_id: str,
        name: str,
        dp_id: int,
        min_value: float,
        max_value: float,
        step: float,
        unit_of_measurement: Optional[str] = None,
        icon: Optional[str] = None,
        entity_category: Optional[EntityCategory] = None,
    ):
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._entry_id = entry_id
        self._name = name
        self._dp_id = str(dp_id)  # Tuya DPs are often strings in status dict
        self._min_value = min_value
        self._max_value = max_value
        self._step = step
        self._unit_of_measurement = unit_of_measurement
        self._icon = icon
        self._entity_category = entity_category

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{self._entry_id}_{self._dp_id}"

    @property
    def name(self) -> str:
        """Return the name of the number entity."""
        return self._name

    @property
    def native_value(self) -> Optional[float]:
        """Return the current value."""
        dps = self.coordinator.data.get("dps", {})
        value = dps.get(self._dp_id)
        return float(value) if value is not None else None

    async def async_set_native_value(self, value: float) -> None:
        """Set new value."""
        await self.coordinator.protocol.async_set_dp(self._dp_id, int(value))
        await self.coordinator.async_refresh()

    @property
    def native_min_value(self) -> float:
        """Return the minimum value."""
        return self._min_value

    @property
    def native_max_value(self) -> float:
        """Return the maximum value."""
        return self._max_value

    @property
    def native_step(self) -> float:
        """Return the step value."""
        return self._step

    @property
    def native_unit_of_measurement(self) -> Optional[str]:
        """Return the unit of measurement."""
        return self._unit_of_measurement

    @property
    def icon(self) -> Optional[str]:
        """Return the icon to use in the frontend, if any."""
        return f"mdi:{self._icon}" if self._icon else None

    @property
    def entity_category(self) -> Optional[EntityCategory]:
        """Return the entity category of the number entity."""
        return self._entity_category

    @property
    def device_info(self) -> Optional[Dict[str, Any]]:
        """Return device information for the number entity."""
        return {
            "identifiers": {(DOMAIN, self.coordinator.device_id)},
            "name": self.coordinator.device_name,
            "manufacturer": "Tuya",
            "model": "Energy Breaker",  # This can be made dynamic later
            "via_device": (DOMAIN, self.coordinator.device_id),
        }
