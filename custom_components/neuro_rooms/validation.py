"""Validation helpers for Neuro Rooms."""

from __future__ import annotations

import json


def validate_json_text(value: str) -> None:
    """Raise ValueError if the text is not valid JSON."""
    if not value.strip():
        return
    json.loads(value)
