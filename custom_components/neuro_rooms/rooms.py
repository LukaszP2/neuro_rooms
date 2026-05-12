"""Room helpers for Neuro Rooms."""

from __future__ import annotations

import json
from typing import Any

from .const import (
    CONF_ROOM_ADVANCED_JSON,
    CONF_ROOM_AREA_ID,
    CONF_ROOM_HAS_HVAC,
    CONF_ROOM_HAS_LIGHTING,
    CONF_ROOM_HAS_MEDIA,
    CONF_ROOM_MODE,
    CONF_ROOM_MODIFIER,
    CONF_ROOM_NAME,
)


def parse_json_payload(value: str) -> Any:
    """Parse JSON safely and return a Python object."""
    if not value.strip():
        return None
    return json.loads(value)


def build_basic_room_payload(user_input: dict[str, Any]) -> dict[str, Any]:
    """Normalize a basic room form into stored payload."""
    return {
        CONF_ROOM_NAME: user_input[CONF_ROOM_NAME],
        CONF_ROOM_AREA_ID: user_input[CONF_ROOM_AREA_ID],
        CONF_ROOM_MODE: user_input[CONF_ROOM_MODE],
        CONF_ROOM_MODIFIER: user_input[CONF_ROOM_MODIFIER],
        CONF_ROOM_HAS_LIGHTING: user_input[CONF_ROOM_HAS_LIGHTING],
        CONF_ROOM_HAS_HVAC: user_input[CONF_ROOM_HAS_HVAC],
        CONF_ROOM_HAS_MEDIA: user_input[CONF_ROOM_HAS_MEDIA],
        "kind": "basic",
    }


def build_advanced_room_payload(user_input: dict[str, Any]) -> dict[str, Any]:
    """Normalize an advanced room form into stored payload."""
    payload = parse_json_payload(user_input[CONF_ROOM_ADVANCED_JSON])
    if not isinstance(payload, dict):
        raise ValueError("Advanced room JSON must be a JSON object")
    payload.setdefault("kind", "advanced")
    return payload
