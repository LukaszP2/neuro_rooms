"""Runtime engine placeholder for Neuro Rooms."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from .registry import RoomRegistry


@dataclass
class NeuroRoomsEngine:
    """Minimal engine state holder for the scaffold."""

    config: dict[str, Any]
    registry: RoomRegistry = field(default_factory=RoomRegistry)

    def update_config(self, updates: dict[str, Any]) -> None:
        self.config.update(updates)
