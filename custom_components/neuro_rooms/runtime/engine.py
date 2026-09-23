"""Main Neuro Rooms runtime engine."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from ..const import CONF_ROOMS
from .room_controller import RoomController


class NeuroRoomsEngine:
    """NR runtime engine."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, config_data: dict):
        self.hass = hass
        self.config_entry = config_entry
        self.config_data = config_data
        self.rooms: dict[str, RoomController] = {}
        self._unsubs = []
        
        rooms_list = self.config_data.get(CONF_ROOMS, [])
        for room_cfg in rooms_list:
            room_id = room_cfg.get("id")
            if room_id:
                self.rooms[room_id] = RoomController(hass, room_id, room_cfg)

    async def async_start(self):
        """Start listening to HA events for occupancy and modes."""
        from homeassistant.core import Event, EventStateChangedData

        async def _state_changed_listener(event: Event[EventStateChangedData]) -> None:
            entity_id = event.data["entity_id"]
            new_state = event.data["new_state"]
            
            if not new_state:
                return
                
            # Detect Magic Areas aggregate sensors:
            # Expected format: binary_sensor.magic_areas_presence_tracking_<room_id>_area_state
            if entity_id.startswith("binary_sensor.magic_areas_presence_tracking_") and entity_id.endswith("_area_state"):
                prefix_len = len("binary_sensor.magic_areas_presence_tracking_")
                suffix_len = len("_area_state")
                room_id = entity_id[prefix_len:-suffix_len]

                if room_id in self.rooms:
                    is_occupied = new_state.state == "on"
                    await self.rooms[room_id].handle_event("occupancy_changed", {"occupied": is_occupied})

            # Detect Neuro Modes global mode switches:
            # Expected format: switch.neuro_modes_<mode>_stan (e.g. domowy, noc)
            if entity_id.startswith("switch.neuro_modes_") and entity_id.endswith("_stan"):
                mode_slug = entity_id[len("switch.neuro_modes_"):-len("_stan")]
                
                # Only react if the mode was turned ON
                if new_state.state == "on":
                    mapped_mode = "normal"
                    if mode_slug == "noc":
                        mapped_mode = "night"
                    elif mode_slug in ["poza_domem", "away"]:
                        mapped_mode = "away"
                    
                    # Distribute to all rooms
                    for room_controller in self.rooms.values():
                        await room_controller.handle_event("global_mode_changed", {"mode": mapped_mode})

        # Listen to all binary_sensors (this is safe as we quickly filter by string prefix)
        self._unsubs.append(
            self.hass.bus.async_listen("state_changed", _state_changed_listener)
        )

    async def async_stop(self):
        """Stop listening to events."""
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
