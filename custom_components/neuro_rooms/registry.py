"""Room registry for Neuro Rooms."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class RoomRegistry:
    """Store generated room definitions."""

    rooms: list[dict[str, Any]] = field(default_factory=list)

    def add_room(self, room: dict[str, Any]) -> None:
        self.rooms.append(room)

    def to_dict(self) -> dict[str, Any]:
        return {"rooms": list(self.rooms)}
