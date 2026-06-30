import logging
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.const import (
    CONF_NAME,
)

from .const import (
    DOMAIN,
    CONF_DEVICE_ID,
    CONF_LOCAL_KEY,
    CONF_IP_ADDRESS,
    CONF_PROTOCOL_VERSION,
)
from .protocol import TuyaDeviceProtocol

_LOGGER = logging.getLogger(__name__)

class TuyaEnergyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Tuya Energy."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            # Validate user input and attempt to connect to the device
            self._async_abort_if_unique_id_configured(user_input[CONF_DEVICE_ID])

            protocol = TuyaDeviceProtocol(self.hass, user_input)
            if await protocol.async_connect():
                await protocol.async_disconnect()
                return self.async_create_entry(title=user_input[CONF_NAME], data=user_input)
            else:
                errors["base"] = "cannot_connect"

        try:
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_NAME, default="Tuya Energy Device"): str,
                    vol.Required(CONF_IP_ADDRESS): str,
                    vol.Required(CONF_DEVICE_ID): str,
                    vol.Required(CONF_LOCAL_KEY): str,
                    vol.Required(CONF_PROTOCOL_VERSION, default="3.3"): vol.All(vol.Coerce(float), vol.Any(3.1, 3.3, 3.5))
                }),
                errors=errors,
            )
        except Exception as e:
            _LOGGER.error("Error showing config flow form: %s", e)
            errors["base"] = "unknown"
            return self.async_show_form(
                step_id="user",
                data_schema=vol.Schema({
                    vol.Required(CONF_NAME, default="Tuya Energy Device"): str,
                    vol.Required(CONF_IP_ADDRESS): str,
                    vol.Required(CONF_DEVICE_ID): str,
                    vol.Required(CONF_LOCAL_KEY): str,
                    vol.Required(CONF_PROTOCOL_VERSION, default="3.3"): vol.All(vol.Coerce(float), vol.Any(3.1, 3.3, 3.5))
                }),
                errors=errors,
            )

    @callback
    def _async_get_existing_entries(self):
        """Return existing entries for this domain."""
        return {entry.unique_id for entry in self.hass.config_entries.async_entries(DOMAIN)}

    async def async_step_reauth(self, user_input=None):
        """Handle reauthentication if the local key changes or connection fails."""
        errors = {}
        if user_input is not None:
            protocol = TuyaDeviceProtocol(self.hass, user_input)
            if await protocol.async_connect():
                await protocol.async_disconnect()
                existing_entry = await self.async_get_entry(self.context["entry_id"])
                self.hass.config_entries.async_update_entry(existing_entry, data=user_input)
                return self.async_abort(reason="reauth_successful")
            else:
                errors["base"] = "cannot_connect"

        return self.async_show_form(
            step_id="reauth",
            data_schema=vol.Schema({
                vol.Required(CONF_IP_ADDRESS, default=self.initial_data[CONF_IP_ADDRESS]): str,
                vol.Required(CONF_DEVICE_ID, default=self.initial_data[CONF_DEVICE_ID]): str,
                vol.Required(CONF_LOCAL_KEY, default=self.initial_data[CONF_LOCAL_KEY]): str,
                vol.Required(CONF_PROTOCOL_VERSION, default=self.initial_data[CONF_PROTOCOL_VERSION]): vol.All(vol.Coerce(float), vol.Any(3.1, 3.3, 3.5))
            }),
            errors=errors,
        )

    async def async_step_import(self, import_config):
        """Import a config entry from configuration.yaml."""
        self._async_abort_if_unique_id_configured(import_config[CONF_DEVICE_ID])
        return self.async_create_entry(title=import_config[CONF_NAME], data=import_config)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return TuyaEnergyOptionsFlowHandler(config_entry)


class TuyaEnergyOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Tuya Energy options."""

    def __init__(self, config_entry: config_entries.ConfigEntry):
        """Initialize Tuya Energy options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional("scan_interval", default=self.config_entry.options.get("scan_interval", 30)): int,
            })
        )
