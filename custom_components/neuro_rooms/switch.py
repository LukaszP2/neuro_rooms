"""Switch platform for Neuro Rooms."""

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo

from .const import DOMAIN

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities):
    """Set up the Neuro Rooms switch."""
    async_add_entities([NeuroRoomsMasterSwitch(hass, entry)])

class NeuroRoomsMasterSwitch(SwitchEntity):
    """Master switch to enable or disable Neuro Rooms automation."""

    _attr_has_entity_name = True
    _attr_translation_key = "active"
    _attr_icon = "mdi:brain"

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        """Initialize the master switch."""
        self.hass = hass
        self.entry = entry
        self._attr_unique_id = f"{entry.entry_id}_master_switch"
        self._is_on = True

    @property
    def is_on(self) -> bool:
        """Return True if entity is on."""
        return self._is_on

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the entity on."""
        self._is_on = True
        self.async_write_ha_state()
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id)
        if data and "engine" in data:
            data["engine"].is_active = True

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the entity off."""
        self._is_on = False
        self.async_write_ha_state()
        data = self.hass.data.get(DOMAIN, {}).get(self.entry.entry_id)
        if data and "engine" in data:
            data["engine"].is_active = False

    @property
    def device_info(self) -> DeviceInfo:
        """Return device registry information for this entity."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.entry.entry_id)},
            name=self.entry.title,
            manufacturer="Neuro Home",
            model="Rooms Logic Engine",
        )
