import asyncio
import logging
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.const import CONF_NAME

from .const import (
    DOMAIN,
    DEFAULT_NAME,
    DEFAULT_SCAN_INTERVAL,
    FAST_SCAN_INTERVAL,
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_IP_ADDRESS,
    CONF_PROTOCOL_VERSION,
    DP_ID_POWER,
)
from .protocol import TuyaDeviceProtocol

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["switch", "sensor", "select", "number", "text", "binary_sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up Tuya Energy from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    config = entry.data
    protocol = TuyaDeviceProtocol(hass, config)

    try:
        if not await protocol.async_connect():
            raise ConfigEntryNotReady("Failed to connect to Tuya device during setup.")
    except Exception as e:
        _LOGGER.error("Error during Tuya Energy setup for %s: %s", entry.entry_id, e)
        raise ConfigEntryNotReady(f"Error during setup: {e}") from e

    coordinator = TuyaEnergyDataUpdateCoordinator(hass, entry, protocol)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    # async_forward_entry_setup foi removido no HA 2025.6; usar a versão
    # plural, que carrega todas as plataformas de uma vez e já é awaitable.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = all(
        await asyncio.gather(
            *[hass.config_entries.async_forward_entry_unload(entry, platform) for platform in PLATFORMS]
        )
    )
    if unload_ok:
        coordinator: TuyaEnergyDataUpdateCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.protocol.async_disconnect()

    return unload_ok


class TuyaEnergyDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Tuya Energy device data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, protocol: TuyaDeviceProtocol):
        """Initialize."""
        self.protocol = protocol
        self.device_id = entry.data[CONF_DEVICE_ID]
        # NOTE: "name" is a reserved attribute on DataUpdateCoordinator (it's
        # set internally by DataUpdateCoordinator.__init__ below and is used
        # for its internal logger name). Storing the user-facing device name
        # in self.name gets silently overwritten by super().__init__(), which
        # caused every device to end up named after DOMAIN ("tuya_energy")
        # regardless of what the user typed in the config flow. Use a
        # dedicated attribute instead so it survives the base class init.
        self.device_name = entry.data.get(CONF_NAME) or entry.title or DEFAULT_NAME
        self.scan_interval = timedelta(seconds=entry.options.get("scan_interval", DEFAULT_SCAN_INTERVAL))

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=self.scan_interval,
        )

    async def _async_update_data(self):
        """Fetch data from the device."""
        try:
            status = await self.protocol.async_get_status()
            if status is None:
                raise UpdateFailed("Failed to get status from device.")
            
            # Implement intelligent polling: if power consumption is detected, switch to fast polling
            dps = status.get("dps", {})
            current_power = dps.get(str(DP_ID_POWER))
            
            if current_power is not None and float(current_power) > 0:
                if self.update_interval.seconds != FAST_SCAN_INTERVAL:
                    _LOGGER.debug("Device %s is consuming power, switching to fast polling (%s s)", self.device_id, FAST_SCAN_INTERVAL)
                    self.update_interval = timedelta(seconds=FAST_SCAN_INTERVAL)
            else:
                if self.update_interval.seconds != DEFAULT_SCAN_INTERVAL:
                    _LOGGER.debug("Device %s is not consuming power, switching to default polling (%s s)", self.device_id, DEFAULT_SCAN_INTERVAL)
                    self.update_interval = timedelta(seconds=DEFAULT_SCAN_INTERVAL)

            return status
        except Exception as err:
            raise UpdateFailed(f"Error communicating with device {self.device_id}: {err}")
