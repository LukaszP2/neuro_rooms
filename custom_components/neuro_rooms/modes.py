"""Mode defaults and helpers for rooms."""

from __future__ import annotations

from typing import Any

from .const import CAPABILITY_HVAC, CAPABILITY_LIGHTING, CAPABILITY_MEDIA

DEFAULT_MODES: list[dict[str, Any]] = [
    {
        "name": "bedroom",
        "description": "Sleep room with low-noise defaults.",
        "capabilities": {
            CAPABILITY_LIGHTING: True,
            CAPABILITY_HVAC: True,
            CAPABILITY_MEDIA: False,
        },
    },
    {
        "name": "living_room",
        "description": "Shared social room.",
        "capabilities": {
            CAPABILITY_LIGHTING: True,
            CAPABILITY_HVAC: True,
            CAPABILITY_MEDIA: True,
        },
    },
    {
        "name": "hallway",
        "description": "Transit area.",
        "capabilities": {
            CAPABILITY_LIGHTING: True,
            CAPABILITY_HVAC: False,
            CAPABILITY_MEDIA: False,
        },
    },
]

DEFAULT_MODE_NAMES = [mode["name"] for mode in DEFAULT_MODES]


def normalize_mode_names(modes: list[dict[str, Any]] | list[str] | None) -> list[str]:
    """Return a stable list of mode names for selectors."""
    if not modes:
        return list(DEFAULT_MODE_NAMES)
    names: list[str] = []
    for item in modes:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict) and item.get("name"):
            names.append(str(item["name"]))
    return names or list(DEFAULT_MODE_NAMES)
