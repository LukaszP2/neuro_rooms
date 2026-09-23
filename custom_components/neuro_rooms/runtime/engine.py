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
        
        rooms_list = self.config_data.get(CONF_ROOMS, [])
        for room_cfg in rooms_list:
            room_id = room_cfg.get("id")
            if room_id:
                self.rooms[room_id] = RoomController(hass, room_id, room_cfg)
