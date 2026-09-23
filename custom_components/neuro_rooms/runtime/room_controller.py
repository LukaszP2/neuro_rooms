"""Room controller state machine."""

from __future__ import annotations

from enum import Enum
from typing import Any


class RoomState(str, Enum):
    IDLE = "idle"
    OCCUPIED = "occupied"
    NIGHT = "night"
    AWAY = "away"
    # Custom modes can be evaluated dynamically, but we map to standard states
    # or return custom strings if needed.


class RoomController:
    """Room controller."""

    def __init__(self, hass, room_id: str, config: dict[str, Any]) -> None:
        self.hass = hass
        self.room_id = room_id
        self.config = config
        
        self.state = RoomState.IDLE
        self.is_occupied = False
        
        self.global_mode = "normal"
        self.global_modifiers: list[str] = []
        
        self.local_mode_override: str | None = None
        self.local_modifiers: list[str] = []
        
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
        # 1. Local overrides take absolute precedence
        active_mode = self.local_mode_override if self.local_mode_override else self.global_mode

        if active_mode == "night":
            self.state = RoomState.NIGHT
        elif active_mode == "away":
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
            
        elif event_type == "local_mode_changed":
            self.local_mode_override = payload.get("mode") # Can be None to clear
            self._evaluate_state()
            
        elif event_type == "modifier_changed":
            scope = payload.get("scope", "local") # local or global
            mod = payload.get("modifier")
            active = payload.get("active", False)
            
            target_list = self.global_modifiers if scope == "global" else self.local_modifiers
            if active and mod not in target_list:
                target_list.append(mod)
            elif not active and mod in target_list:
                target_list.remove(mod)
                
            self._evaluate_state()

