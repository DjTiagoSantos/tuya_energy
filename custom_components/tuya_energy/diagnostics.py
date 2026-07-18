"""Diagnostics support for Tuya Energy."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntry

from .const import (
    DOMAIN,
    CONF_LOCAL_KEY,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
)
from .__init__ import TuyaEnergyDataUpdateCoordinator

# Campos que NUNCA devem sair no arquivo de diagnostico.
# local_key e o segredo de criptografia do dispositivo; device_id e ip_address
# identificam o hardware/rede da pessoa. async_redact_data troca cada um
# desses valores por "**REDACTED**" automaticamente, em qualquer nivel do dict.
TO_REDACT = {
    CONF_LOCAL_KEY,
    CONF_DEVICE_ID,
    CONF_IP_ADDRESS,
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: TuyaEnergyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    return {
        "config_entry": {
            "title": entry.title,
            "data": async_redact_data(dict(entry.data), TO_REDACT),
            "options": dict(entry.options),
        },
        "coordinator": {
            "device_name": coordinator.device_name,
            "last_update_success": coordinator.last_update_success,
            "update_interval_seconds": (
                coordinator.update_interval.total_seconds()
                if coordinator.update_interval
                else None
            ),
            "protocol_connected": coordinator.protocol.is_connected,
        },
        # Este e o payload bruto de "dps" que o dispositivo devolveu na
        # ultima atualizacao -- exatamente o que precisamos para depurar
        # problemas de DP errado, escala errada, ou DP ausente (como o
        # add_ele que discutimos). Nao contem nada sensivel, so numeros de
        # DP e seus valores.
        "last_status": coordinator.data,
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: DeviceEntry
) -> dict[str, Any]:
    """Return diagnostics for a specific device (same data as the entry)."""
    return await async_get_config_entry_diagnostics(hass, entry)
