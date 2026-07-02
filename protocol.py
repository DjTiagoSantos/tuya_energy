import tinytuya
import logging

from .const import (
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_IP_ADDRESS,
    CONF_PROTOCOL_VERSION,
)

_LOGGER = logging.getLogger(__name__)

class TuyaDeviceProtocol:
    """Handles communication with a Tuya device."""

    def __init__(self, hass, config):
        self.hass = hass
        self._device_id = config.get(CONF_DEVICE_ID)
        self._local_key = config.get(CONF_LOCAL_KEY)
        self._ip_address = config.get(CONF_IP_ADDRESS)
        self._protocol_version = float(config.get(CONF_PROTOCOL_VERSION))
        self._device = None
        self._is_connected = False

    async def async_connect(self):
        """Creates the tinytuya device object and verifies it's reachable.

        tinytuya has no explicit connect() call — the socket is opened
        lazily on the first status()/set_dps() request. We do a real
        status() call here just to confirm the device answers before we
        report the connection as successful.
        """
        if self._device:
            await self.async_disconnect()

        try:
            self._device = tinytuya.OutletDevice(
                self._device_id,
                self._ip_address,
                self._local_key,
                version=self._protocol_version,
            )
            # Keep the socket open between polls; tinytuya reconnects
            # transparently if the session drops.
            self._device.set_socketPersistent(True)
        except Exception as e:
            _LOGGER.error("Error initializing Tuya device object for %s: %s", self._device_id, e)
            return False

        try:
            status = await self.hass.async_add_executor_job(self._device.status)
            if isinstance(status, dict) and status.get("Error"):
                _LOGGER.error(
                    "Failed to connect to Tuya device %s: %s",
                    self._device_id, status.get("Error"),
                )
                self._is_connected = False
                return False
            self._is_connected = True
            _LOGGER.debug("Successfully connected to Tuya device %s", self._device_id)
            return True
        except Exception as e:
            _LOGGER.error("Failed to connect to Tuya device %s: %s", self._device_id, e)
            self._is_connected = False
            return False

    async def async_disconnect(self):
        """Disconnects from the Tuya device."""
        if self._device and self._is_connected:
            try:
                await self.hass.async_add_executor_job(self._device.close)
                self._is_connected = False
                _LOGGER.debug("Disconnected from Tuya device %s", self._device_id)
            except Exception as e:
                _LOGGER.warning("Error disconnecting from Tuya device %s: %s", self._device_id, e)

    async def async_get_status(self):
        """Gets the current status of the device."""
        if not self._is_connected:
            if not await self.async_connect():
                return None
        try:
            status = await self.hass.async_add_executor_job(self._device.status)
            if isinstance(status, dict) and status.get("Error"):
                # tinytuya nem sempre lança exceção em erro de comunicação;
                # às vezes devolve um payload tipo {"Error": ..., "Err": ...}.
                _LOGGER.error(
                    "Device %s returned an error status: %s", self._device_id, status
                )
                self._is_connected = False
                return None
            _LOGGER.debug("Status for %s: %s", self._device_id, status)
            return status
        except Exception as e:
            _LOGGER.error("Failed to get status for Tuya device %s: %s", self._device_id, e)
            self._is_connected = False # Assume connection lost
            return None

    async def async_set_dp(self, dp_id, value):
        """Sets a DP value on the device."""
        if not self._is_connected:
            if not await self.async_connect():
                return False
        try:
            # TinyTuya's set_version and set_status are synchronous
            result = await self.hass.async_add_executor_job(
                self._device.set_dps, {dp_id: value}
            )
            if isinstance(result, dict) and result.get("Error"):
                _LOGGER.error(
                    "Device %s rejected DP %s=%s: %s",
                    self._device_id, dp_id, value, result,
                )
                self._is_connected = False
                return False
            _LOGGER.debug("Set DP %s to %s for device %s", dp_id, value, self._device_id)
            return True
        except Exception as e:
            _LOGGER.error("Failed to set DP %s to %s for Tuya device %s: %s", dp_id, value, self._device_id, e)
            self._is_connected = False
            return False

    @property
    def device_id(self):
        return self._device_id

    @property
    def ip_address(self):
        return self._ip_address

    @property
    def is_connected(self):
        return self._is_connected
