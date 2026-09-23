"""Per-room configuration entities."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_MODES,
    CONF_MODIFIERS,
    DEFAULT_ROOM_MODES,
    DOMAIN,
)
from .helpers import NO_MODIFIER_LABEL, NO_MODIFIER_VALUE
from .modifiers import DEFAULT_MODIFIERS
from .runtime.engine import NeuroRoomsEngine
from .runtime.room_controller import RoomController


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add configuration selects to each room device."""
    engine: NeuroRoomsEngine = hass.data[DOMAIN][entry.entry_id]["engine"]
    modes = _option_values(
        engine.config_data.get(CONF_MODES),
        default=DEFAULT_ROOM_MODES,
    )
    modifiers = _option_values(
        engine.config_data.get(CONF_MODIFIERS),
        default=[item["name"] for item in DEFAULT_MODIFIERS],
    )
    modifiers = [
        modifier
        for modifier in modifiers
        if modifier not in (NO_MODIFIER_LABEL, NO_MODIFIER_VALUE, "none")
    ]

    entities: list[SelectEntity] = []
    for controller in engine.rooms.values():
        room_modes = list(modes)
        current_mode = controller.config.get("mode")
        if current_mode and current_mode not in room_modes:
            room_modes.append(current_mode)

        room_modifiers = [NO_MODIFIER_LABEL, *modifiers]
        current_modifier = controller.config.get("modifier")
        if current_modifier and current_modifier not in room_modifiers:
            room_modifiers.append(current_modifier)

        entities.extend(
            [
                RoomConfigSelect(
                    engine,
                    controller,
                    entry,
                    key="mode",
                    options=room_modes,
                    translation_key="room_mode",
                ),
                RoomConfigSelect(
                    engine,
                    controller,
                    entry,
                    key="modifier",
                    options=room_modifiers,
                    translation_key="room_modifier",
                ),
            ]
        )

    if entities:
        async_add_entities(entities)


def _option_values(configured: list | None, default: list[str]) -> list[str]:
    """Normalize configured mode/modifier records to select values."""
    if not configured:
        return default

    values = []
    for item in configured:
        if isinstance(item, str):
            values.append(item)
        elif isinstance(item, dict):
            value = item.get("id") or item.get("name")
            if value:
                values.append(str(value))
    return values or default


class RoomConfigSelect(SelectEntity):
    """Editable setting attached to a room's device page."""

    _attr_has_entity_name = True
    _attr_entity_category = EntityCategory.CONFIG

    def __init__(
        self,
        engine: NeuroRoomsEngine,
        controller: RoomController,
        entry: ConfigEntry,
        *,
        key: str,
        options: list[str],
        translation_key: str,
    ) -> None:
        self._engine = engine
        self._controller = controller
        self._key = key
        self._options = options
        self._modifier = key == "modifier"
        self._attr_translation_key = translation_key
        self._attr_unique_id = f"{entry.entry_id}_{controller.room_id}_{key}"

        room_name = controller.config.get("name", controller.room_id)
        area = controller.config.get("area_id") or controller.config.get("area_name")
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, controller.room_id)},
            name=f"Neuro Room: {room_name}",
            suggested_area=area,
            manufacturer="Neuro Rooms",
            model="Virtual Room Controller",
            via_device=(DOMAIN, entry.entry_id),
        )

    @property
    def options(self) -> list[str]:
        """Return valid room setting values."""
        return self._options

    @property
    def current_option(self) -> str | None:
        """Return the current setting."""
        value = self._controller.config.get(self._key)
        if self._modifier and value in (None, "", NO_MODIFIER_VALUE, "none"):
            return NO_MODIFIER_LABEL
        return value if value in self._options else None

    async def async_select_option(self, option: str) -> None:
        """Persist this room's mode or modifier and recalculate its profile."""
        value = None if self._modifier and option == NO_MODIFIER_LABEL else option
        await self._engine.async_update_room_config(
            self._controller.room_id, {self._key: value}
        )
        self.async_write_ha_state()
