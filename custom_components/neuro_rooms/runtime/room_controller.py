"""Room controller state machine."""

from __future__ import annotations

from enum import Enum
from copy import deepcopy
from typing import Any

from ..const import EVENT_DESIRED_CHANGED


class RoomState(str, Enum):
    IDLE = "idle"
    OCCUPIED = "occupied"
    NIGHT = "night"
    AWAY = "away"
    # Custom modes can be evaluated dynamically, but we map to standard states
    # or return custom strings if needed.


class RoomController:
    """Room controller."""

    def __init__(self, hass, room_id: str, config: dict[str, Any], profiles: list[dict[str, Any]] | None = None) -> None:
        self.hass = hass
        self.room_id = room_id
        self.config = config
        self.profiles = profiles or []
        
        self.state = RoomState.IDLE
        self.is_occupied = False
        
        self.global_mode = "normal"
        self.global_modifiers: list[str] = []
        self.global_context_mode = "unknown"
        
        self.local_mode_override: str | None = None
        self.local_modifiers: list[str] = []
        
        self._entity = None
        self.selected_profile: str | None = None
        self.desired: dict[str, Any] = {}
        self.context: dict[str, Any] = {}

    def update_context(self, global_mode: str, global_modifiers: list[str] | None = None) -> None:
        """Rebuild room context and resolve its desired behavior."""
        from ..helpers import select_profile

        previous_profile = self.selected_profile
        previous_desired = deepcopy(self.desired)
        self.global_context_mode = global_mode
        self.global_modifiers = global_modifiers or []
        self.context = {
            "global_mode": self.global_context_mode,
            "global_modifiers": list(self.global_modifiers),
            "mode": self.config.get("mode", self.config.get("room_mode")),
            "modifier": self.config.get("modifier", self.config.get("room_modifier")),
            "state": self.state.value,
        }
        if self.context["modifier"] in ("", "none", "__none__"):
            self.context["modifier"] = None
        profile = select_profile(self.context, self.profiles)
        self.selected_profile = profile.get("id") or profile.get("name") if profile else None
        self.desired = dict(profile.get("desired", {})) if profile else {}
        self._update_ha_state()
        if self.selected_profile != previous_profile or self.desired != previous_desired:
            self.hass.bus.async_fire(
                EVENT_DESIRED_CHANGED,
                {
                    "room_id": self.room_id,
                    "entity_id": self._entity.entity_id if self._entity else None,
                    "room_config": deepcopy(self.config),
                    "context": deepcopy(self.context),
                    "selected_profile": self.selected_profile,
                    "desired": deepcopy(self.desired),
                },
            )

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
            
        self.update_context(self.global_context_mode, self.global_modifiers)

    async def handle_event(self, event_type: str, payload=None):
        """Handle important room events only."""
        payload = payload or {}

        if event_type == "occupancy_changed":
            self.is_occupied = bool(payload.get("occupied"))
            self._evaluate_state()

        elif event_type == "global_mode_changed":
            self.global_mode = payload.get("mode", "normal")
            self.global_context_mode = payload.get("context_mode", self.global_context_mode)
            self.global_modifiers = payload.get("modifiers", self.global_modifiers)
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

