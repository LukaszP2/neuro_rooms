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
        self.is_occupied = False
        self.global_mode = "normal"
        self._entity = None

    def set_entity(self, entity):
        """Link HA entity to controller."""
        self._entity = entity

    def _update_ha_state(self):
        """Trigger HA state update."""
        if self._entity:
            self._entity.async_write_ha_state()

    def _evaluate_state(self):
        """Evaluate and set the correct state based on flags."""
        if self.global_mode == "night":
            self.state = RoomState.NIGHT
        elif self.global_mode == "away":
            self.state = RoomState.AWAY
        elif self.is_occupied:
            self.state = RoomState.OCCUPIED
        else:
            self.state = RoomState.IDLE
            
        self._update_ha_state()

    async def handle_event(self, event_type: str, payload=None):
        """Handle important room events only."""
        payload = payload or {}

        if event_type == "occupancy_changed":
            self.is_occupied = bool(payload.get("occupied"))
            self._evaluate_state()

        elif event_type == "global_mode_changed":
            self.global_mode = payload.get("mode", "normal")
            self._evaluate_state()
