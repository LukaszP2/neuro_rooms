"""Base plugin API for Neuro Rooms."""

from __future__ import annotations


class NeuroRoomsPlugin:
    """Base class for all Neuro Rooms plugins."""

    domain: str = "base"
    plugin_version: str = "0.1.0.nr0"


# Alias kept for backward compatibility with subclasses that import BasePlugin
BasePlugin = NeuroRoomsPlugin
