from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .runtime.room_controller import RoomController


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the Neuro Rooms sensors."""
    engine = hass.data[DOMAIN][entry.entry_id]["engine"]

    sensors = []
    for controller in engine.rooms.values():
        sensors.append(NeuroRoomSensor(controller, entry))

    if sensors:
        async_add_entities(sensors)


class NeuroRoomSensor(SensorEntity):
    """Representation of a Neuro Room state sensor."""

    _attr_has_entity_name = True
    _attr_name = "State"

    def __init__(self, controller: RoomController, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        self._controller = controller
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{controller.room_id}_state"
        
        # Link controller back to entity to allow pushing updates
        self._controller.set_entity(self)

        room_name = self._controller.config.get("name", self._controller.room_id)
        area_id = self._controller.config.get("area_id") or self._controller.config.get("area_name")

        # Link this entity to a device so it belongs to the proper Area
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._controller.room_id)},
            name=f"Neuro Room: {room_name}",
            suggested_area=area_id,
            manufacturer="Neuro Rooms",
            model="Virtual Room Controller",
        )

    @property
    def native_value(self) -> str:
        """Return the state of the room."""
        return self._controller.state.value if self._controller.state else "unknown"

    @property
    def extra_state_attributes(self) -> dict:
        """Return the extra state attributes."""
        # Include all configuration and runtime info for the frontend
        return {
            "room_id": self._controller.room_id,
            "room_config": self._controller.config,
        }

