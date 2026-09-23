"""Main Neuro Rooms runtime engine."""

from __future__ import annotations

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, Event, EventStateChangedData
from homeassistant.helpers.event import async_track_state_change_event

from ..const import CONF_ROOMS
from .room_controller import RoomController
from ..helpers import async_discover_global_mode_entity, async_discover_occupancy_entity

_LOGGER = logging.getLogger(__name__)

class NeuroRoomsEngine:
    """NR runtime engine."""

    def __init__(self, hass: HomeAssistant, config_entry: ConfigEntry, config_data: dict):
        self.hass = hass
        self.config_entry = config_entry
        self.config_data = config_data
        self.rooms: dict[str, RoomController] = {}
        self._unsubs = []
        self.is_active = True
        self.global_mode_entity = config_data.get("global_mode_entity")
        
        rooms_list = self.config_data.get(CONF_ROOMS, [])
        for room_cfg in rooms_list:
            room_id = room_cfg.get("id")
            if room_id:
                self.rooms[room_id] = RoomController(hass, room_id, room_cfg)

    async def async_start(self):
        """Start listening to HA events for occupancy and modes."""
        
        # 1. Discover Global Mode Entity if not configured
        if not self.global_mode_entity:
            self.global_mode_entity = await async_discover_global_mode_entity(self.hass)
            _LOGGER.debug(f"Discovered global mode entity: {self.global_mode_entity}")
            
        # 2. Discover Occupancy Entities for each room if not configured
        for room_id, controller in self.rooms.items():
            if not controller.config.get("presence_entity"):
                area_id = controller.config.get("area_id")
                discovered = await async_discover_occupancy_entity(self.hass, area_id)
                controller.presence_entity = discovered
                _LOGGER.debug(f"Room {room_id} discovered presence entity: {discovered}")
            else:
                controller.presence_entity = controller.config.get("presence_entity")

        async def _state_changed_listener(event: Event[EventStateChangedData]) -> None:
            if not self.is_active:
                return
                
            entity_id = event.data["entity_id"]
            new_state = event.data["new_state"]
            if not new_state:
                return

            # Check if this is the Global Mode entity
            if self.global_mode_entity and entity_id == self.global_mode_entity:
                mode_val = str(new_state.state).lower()
                mapped_mode = "normal"
                if "noc" in mode_val or "night" in mode_val:
                    mapped_mode = "night"
                elif "poza" in mode_val or "away" in mode_val:
                    mapped_mode = "away"
                
                for room_controller in self.rooms.values():
                    await room_controller.handle_event("global_mode_changed", {"mode": mapped_mode})
                    
            # Check if this is a Presence entity for any room
            for room_id, room_controller in self.rooms.items():
                if room_controller.presence_entity == entity_id:
                    is_occupied = new_state.state == "on"
                    await room_controller.handle_event("occupancy_changed", {"occupied": is_occupied})

        self._unsubs.append(
            self.hass.bus.async_listen("state_changed", _state_changed_listener)
        )

    async def async_stop(self):
        """Stop listening to events."""
        for unsub in self._unsubs:
            unsub()
        self._unsubs.clear()
