"""Room controller state machine."""

from __future__ import annotations

from enum import Enum


class RoomState(str, Enum):
    IDLE = "idle"
    OCCUPIED = "occupied"
    NIGHT = "night"
    AWAY = "away"


class RoomController:
    """Room controller."""

    def __init__(self, hass, room_id: str, config: dict):
        self.hass = hass
        self.room_id = room_id
        self.config = config
        self.state = RoomState.IDLE

    async def handle_event(self, event_type: str, payload=None):
        """Handle important room events only."""

        payload = payload or {}

        if event_type == "occupancy_changed":
            self.state = (
                RoomState.OCCUPIED
                if payload.get("occupied")
                else RoomState.IDLE
            )

        elif event_type == "global_mode_changed":
            mode = payload.get("mode")

            if mode == "night":
                self.state = RoomState.NIGHT
            elif mode == "away":
                self.state = RoomState.AWAY
