"""Modifier defaults and helpers for rooms."""

from __future__ import annotations

from typing import Any

DEFAULT_MODIFIERS: list[dict[str, Any]] = [
    {
        "name": "none",
        "base_mode": "",
        "description": "No override.",
        "overrides": {},
    },
    {
        "name": "single",
        "base_mode": "bedroom",
        "description": "Single occupant bedroom profile.",
        "overrides": {},
    },
    {
        "name": "couple",
        "base_mode": "bedroom",
        "description": "Two-person bedroom profile.",
        "overrides": {},
    },
]

DEFAULT_MODIFIER_NAMES = [modifier["name"] for modifier in DEFAULT_MODIFIERS]


def normalize_modifier_names(modifiers: list[dict[str, Any]] | list[str] | None) -> list[str]:
    """Return a stable list of modifier names for selectors."""
    if not modifiers:
        return list(DEFAULT_MODIFIER_NAMES)
    names: list[str] = []
    for item in modifiers:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, dict) and item.get("name"):
            names.append(str(item["name"]))
    return names or list(DEFAULT_MODIFIER_NAMES)
