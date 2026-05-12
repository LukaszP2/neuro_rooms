"""Helper utilities for Neuro Rooms."""

from __future__ import annotations

from copy import deepcopy
import re
from typing import Any

from homeassistant.helpers import area_registry

from .const import DEFAULT_ROOM_MODES


def slugify(value: str) -> str:
    """Create a stable internal id from a display name."""
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    value = re.sub(r"_+", "_", value).strip("_")
    return value or "room"


def infer_room_mode(name: str) -> str:
    """Guess a room mode from an area name."""
    lowered = name.casefold()
    if any(word in lowered for word in ("sypial", "bed", "sleep")):
        return "bedroom"
    if any(word in lowered for word in ("korytar", "hall", "corridor", "przej", "passage")):
        return "hallway"
    if any(word in lowered for word in ("łazien", "lazien", "bath")):
        return "bathroom"
    if any(word in lowered for word in ("gabinet", "office", "biuro", "study")):
        return "office"
    if any(word in lowered for word in ("kuch", "kitchen")):
        return "kitchen"
    if any(word in lowered for word in ("salon", "living", "lounge")):
        return "living_room"
    return "room"


def ensure_structure(config: dict[str, Any]) -> dict[str, Any]:
    """Ensure the working config has all expected keys."""
    result = deepcopy(config)
    result.setdefault("rooms", [])
    result.setdefault("modes", [])
    result.setdefault("modifiers", [])
    return result


def replace_by_id(items: list[dict[str, Any]], item: dict[str, Any]) -> list[dict[str, Any]]:
    """Insert or replace an item by id."""
    return [existing for existing in items if existing.get("id") != item.get("id")] + [item]


def remove_by_id(items: list[dict[str, Any]], item_id: str) -> list[dict[str, Any]]:
    """Remove an item by id."""
    return [existing for existing in items if existing.get("id") != item_id]


async def discover_rooms_from_areas(hass, existing_room_ids: set[str]) -> list[dict[str, Any]]:
    """Generate room definitions from HA areas."""
    registry = area_registry.async_get(hass)
    discovered: list[dict[str, Any]] = []

    for area in registry.async_list_areas():
        if not area.name:
            continue

        room_id = slugify(area.name)
        if room_id in existing_room_ids:
            continue

        discovered.append(
            {
                "id": room_id,
                "name": area.name,
                "area_name": area.name,
                "mode": infer_room_mode(area.name),
                "modifier": None,
                "source": "discovered",
            }
        )

    return discovered


def available_room_mode_choices(working: dict[str, Any]) -> list[str]:
    """Build mode choices for selectors."""
    values = [m.get("id") for m in working.get("modes", []) if m.get("id")]
    return values or DEFAULT_ROOM_MODES


def available_modifier_choices(working: dict[str, Any]) -> list[str]:
    """Build modifier choices for selectors."""
    values = [m.get("id") for m in working.get("modifiers", []) if m.get("id")]
    return [""] + values


def available_room_choices(working: dict[str, Any]) -> list[str]:
    """Build room choices for removal/editing."""
    values = [r.get("id") for r in working.get("rooms", []) if r.get("id")]
    return [""] + values


def available_area_names(hass) -> list[str]:
    """Return area names for pairing rooms."""
    registry = area_registry.async_get(hass)
    return [area.name for area in registry.async_list_areas() if area.name]
