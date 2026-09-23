"""Neuro Rooms integration."""

from __future__ import annotations

import pathlib

from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_AUTO_DISCOVERY, CONF_ROOMS, DOMAIN
from .helpers import async_discover_rooms_from_areas_for_entry
from .runtime.engine import NeuroRoomsEngine

PLATFORMS: list[str] = ["sensor", "switch", "select"]


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

    # Migrate existing rooms: recover their area_id and discover occupancy
    # sensors for rooms created before automatic presence discovery existed.
    rooms = data.get(CONF_ROOMS, [])
    migrated = False
    if rooms:
        from homeassistant.helpers import area_registry as ar

        from .helpers import async_discover_occupancy_entity, slugify

        area_reg = ar.async_get(hass)
        areas = area_reg.async_list_areas()
        id_to_area = {a.id: a for a in areas}
        name_to_area = {a.name.casefold(): a for a in areas if a.name}
        slug_to_area = {slugify(a.name): a for a in areas if a.name}
        for room in rooms:
            area = id_to_area.get(room.get("area_id"))
            if area is None and room.get("area_name"):
                area = name_to_area.get(room["area_name"].casefold())
            if area is None:
                area = name_to_area.get(str(room.get("name", "")).casefold())
            if area is None and room.get("id"):
                area = slug_to_area.get(room["id"])
            if area and not room.get("area_id"):
                room["area_id"] = area.id
                room.setdefault("area_name", area.name)
                migrated = True
            current_presence = room.get("presence_entity")
            current_is_magic = bool(
                current_presence
                and current_presence.startswith(
                    "binary_sensor.magic_areas_presence_tracking_"
                )
            )
            should_refresh_presence = not current_presence or (
                room.get("source") == "discovered" and not current_is_magic
            )
            if area and should_refresh_presence:
                presence_entity = await async_discover_occupancy_entity(hass, area.id)
                if presence_entity and presence_entity != current_presence:
                    room["presence_entity"] = presence_entity
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
