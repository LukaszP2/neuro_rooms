"""Diagnostics support."""

async def async_get_config_entry_diagnostics(hass, entry):
    return {
        "entry_id": entry.entry_id,
        "title": entry.title,
    }
