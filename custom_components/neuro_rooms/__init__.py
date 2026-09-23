"""Neuro Rooms integration."""

from __future__ import annotations

import pathlib

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_AUTO_DISCOVERY, CONF_ROOMS, DOMAIN
from .helpers import async_discover_rooms_from_areas_for_entry
from .runtime.engine import NeuroRoomsEngine

PLATFORMS: list[str] = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up Neuro Rooms from YAML (unused)."""
    hass.data.setdefault(DOMAIN, {})
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Neuro Rooms config entry."""
    hass.data.setdefault(DOMAIN, {})
    data: dict = {**entry.data, **entry.options}

    # Auto-discover if not set
    if entry.data.get(CONF_AUTO_DISCOVERY, True) and not entry.options.get(CONF_ROOMS):
        discovered = await async_discover_rooms_from_areas_for_entry(hass, set())
        if discovered:
            options = dict(entry.options)
            options[CONF_ROOMS] = discovered
            hass.config_entries.async_update_entry(entry, options=options)
            data = {**entry.data, **options}

    # Migrate rooms: backfill area_id from area_name for existing entries
    rooms = data.get(CONF_ROOMS, [])
    migrated = False
    if rooms:
        from homeassistant.helpers import area_registry as ar

        area_reg = ar.async_get(hass)
        name_to_id = {a.name: a.id for a in area_reg.async_list_areas()}
        for room in rooms:
            if not room.get("area_id") and room.get("area_name"):
                area_id = name_to_id.get(room["area_name"])
                if area_id:
                    room["area_id"] = area_id
                    migrated = True
        if migrated:
            options = dict(entry.options)
            options[CONF_ROOMS] = rooms
            hass.config_entries.async_update_entry(entry, options=options)
            data = {**entry.data, **options}

    engine = NeuroRoomsEngine(hass, entry, data)
    hass.data[DOMAIN][entry.entry_id] = {
        "config": data,
        "engine": engine,
    }

    # Register frontend static files
    frontend_path = pathlib.Path(__file__).parent / "www"
    await hass.http.async_register_static_paths(
        [StaticPathConfig("/neuro_rooms_frontend", str(frontend_path), cache_headers=False)]
    )

    await engine.async_start()

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload Neuro Rooms config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        data = hass.data.get(DOMAIN, {}).pop(entry.entry_id, None)
        if data and "engine" in data:
            await data["engine"].async_stop()
    return unload_ok
