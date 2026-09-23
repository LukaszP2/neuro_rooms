"""Helper utilities for Neuro Rooms."""

from __future__ import annotations

import re
from copy import deepcopy
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import area_registry
from homeassistant.helpers.selector import SelectOptionDict

from .const import DEFAULT_ROOM_MODES

NO_MODIFIER_VALUE = "__none__"
NO_MODIFIER_LABEL = "Brak"


def slugify(value: str) -> str:
    value = re.sub(r"[^a-z0-9]+", "_", value.strip().lower())
    return re.sub(r"_+", "_", value).strip("_") or "room"


def infer_room_mode(name: str) -> str:
    lowered = name.casefold()
    checks = [
        ("bedroom", ("sypial", "bed", "sleep")),
        ("hallway", ("korytar", "hall", "corridor", "przej", "passage")),
        ("bathroom", ("łazien", "lazien", "bath")),
        ("office", ("gabinet", "office", "biuro", "study")),
        ("kitchen", ("kuch", "kitchen")),
        ("living_room", ("salon", "living", "lounge")),
    ]
    for mode, words in checks:
        if any(word in lowered for word in words):
            return mode
    return "room"


def ensure_structure(config: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(config)
    result.setdefault("rooms", [])
    result.setdefault("modes", [])
    result.setdefault("modifiers", [])
    return result


def replace_by_id(
    items: list[dict[str, Any]], item: dict[str, Any]
) -> list[dict[str, Any]]:
    return [existing for existing in items if existing.get("id") != item.get("id")] + [
        item
    ]


def remove_by_id(items: list[dict[str, Any]], item_id: str) -> list[dict[str, Any]]:
    return [existing for existing in items if existing.get("id") != item_id]


async def async_discover_rooms_from_areas_for_entry(
    hass: HomeAssistant, existing_room_ids: set[str]
) -> list[dict[str, Any]]:
    registry = area_registry.async_get(hass)
    discovered = []
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
                "area_id": area.id,
                "area_name": area.name,
                "mode": infer_room_mode(area.name),
                "modifier": None,
                "source": "discovered",
            }
        )
    return discovered


def available_mode_select_options(working: dict[str, Any]) -> list[SelectOptionDict]:
    modes = working.get("modes", [])
    if not modes:
        return [SelectOptionDict(value=m, label=m) for m in DEFAULT_ROOM_MODES]
    return [
        SelectOptionDict(value=m.get("id"), label=m.get("name") or m.get("id"))
        for m in modes
        if m.get("id")
    ]


def available_modifier_select_options(
    working: dict[str, Any],
) -> list[SelectOptionDict]:
    options = [SelectOptionDict(value=NO_MODIFIER_VALUE, label=NO_MODIFIER_LABEL)]
    options.extend(
        SelectOptionDict(value=m.get("id"), label=m.get("name") or m.get("id"))
        for m in working.get("modifiers", [])
        if m.get("id")
    )
    return options


def available_room_select_options(working: dict[str, Any]) -> list[SelectOptionDict]:
    return [
        SelectOptionDict(value=r.get("id"), label=r.get("name") or r.get("id"))
        for r in working.get("rooms", [])
        if r.get("id")
    ]


def available_area_select_options(hass: HomeAssistant) -> list[SelectOptionDict]:
    registry = area_registry.async_get(hass)
    return [
        SelectOptionDict(value=a.name, label=a.name)
        for a in registry.async_list_areas()
        if a.name
    ]


def normalize_modifier(value: str | None) -> str | None:
    return None if value in (None, "", NO_MODIFIER_VALUE) else value
