"""Starter behavior profiles; users can replace them in integration options."""

from __future__ import annotations

from copy import deepcopy

DEFAULT_PROFILES = [
    {"id": "noc", "when": {"state": "night"}, "desired": {"lighting": "off", "hvac": "sleep", "media": "off"}},
    {"id": "poza", "when": {"state": "away"}, "desired": {"lighting": "off", "hvac": "eco", "media": "off"}},
    {"id": "bezczynny", "when": {"state": "idle"}, "desired": {"lighting": "off", "hvac": "eco", "media": "off"}},
    {"id": "skupienie", "when": {"state": "occupied", "mode": "office", "modifier": "focus"}, "desired": {"lighting": "work", "hvac": "comfort", "media": "off"}},
    {"id": "zajety", "when": {"state": "occupied"}, "desired": {"lighting": "normal", "hvac": "comfort", "media": "off"}},
]


def get_profiles(config: dict) -> list[dict]:
    """Return configured profiles or a fresh copy of the starter set."""
    return deepcopy(config.get("profiles") or DEFAULT_PROFILES)
