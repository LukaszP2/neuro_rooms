"""Room controller state machine."""

from __future__ import annotations

from enum import Enum
from typing import Any


class RoomState(str, Enum):
    IDLE = "idle"
    OCCUPIED = "occupied"
    NIGHT = "night"
    AWAY = "away"


class RoomController:
    """Room controller."""

    def __init__(self, hass, room_id: str, config: dict[str, Any]) -> None:
        self.hass = hass
        self.room_id = room_id
        self.config = config
        self.state = RoomState.IDLE
        self._entity = None

    def set_entity(self, entity):
        """Link HA entity to controller."""
        self._entity = entity

    def _update_ha_state(self):
        """Trigger HA state update."""
        if self._entity:
            self._entity.async_write_ha_state()

    async def handle_event(self, event_type: str, payload=None):
        """Handle important room events only."""

        payload = payload or {}

        if event_type == "occupancy_changed":
            self.state = (
                RoomState.OCCUPIED if payload.get("occupied") else RoomState.IDLE
            )
            self._update_ha_state()

        elif event_type == "global_mode_changed":
            mode = payload.get("mode")

            if mode == "night":
                self.state = RoomState.NIGHT
            elif mode == "away":
                self.state = RoomState.AWAY
            
            self._update_ha_state()
