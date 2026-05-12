"""Config flow for Neuro Rooms."""

from __future__ import annotations

from copy import deepcopy
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.config_entries import OptionsFlowWithReload
from homeassistant.helpers.selector import (
    BooleanSelector,
    NumberSelector,
    NumberSelectorConfig,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
)

from .const import (
    CONF_AUTO_DISCOVERY,
    CONF_ENGINE_NAME,
    CONF_ID,
    CONF_MODE,
    CONF_MODE_HVAC,
    CONF_MODE_LIGHTING,
    CONF_MODE_MEDIA,
    CONF_MODE_NAME,
    CONF_MODIFIER,
    CONF_MODIFIER_BASE_MODE,
    CONF_MODIFIER_NAME,
    CONF_MODIFIER_PRIORITY,
    CONF_MODIFIERS,
    CONF_MODES,
    CONF_NAME,
    CONF_ROOMS,
    CONF_SOURCE,
    DEFAULT_ENGINE_NAME,
    DOMAIN,
)
from .helpers import (
    available_area_names,
    available_modifier_choices,
    available_room_choices,
    available_room_mode_choices,
    discover_rooms_from_areas,
    ensure_structure,
    remove_by_id,
    replace_by_id,
    slugify,
)


class NeuroRoomsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle Neuro Rooms config flow."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_ENGINE_NAME],
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_ENGINE_NAME, default=DEFAULT_ENGINE_NAME): str,
                vol.Required(CONF_AUTO_DISCOVERY, default=True): bool,
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema)

    @staticmethod
    def async_get_options_flow(config_entry):
        return NeuroRoomsOptionsFlow(config_entry)


class NeuroRoomsOptionsFlow(OptionsFlowWithReload):
    """Menu-driven options flow."""

    def __init__(self, config_entry):
        self._config_entry = config_entry

    def _working(self) -> dict[str, Any]:
        if not hasattr(self, "_working_config"):
            self._working_config = ensure_structure(
                {
                    CONF_ENGINE_NAME: self._config_entry.data.get(CONF_ENGINE_NAME, DEFAULT_ENGINE_NAME),
                    CONF_AUTO_DISCOVERY: self._config_entry.data.get(CONF_AUTO_DISCOVERY, True),
                    CONF_ROOMS: deepcopy(self._config_entry.options.get(CONF_ROOMS, [])),
                    CONF_MODES: deepcopy(self._config_entry.options.get(CONF_MODES, [])),
                    CONF_MODIFIERS: deepcopy(self._config_entry.options.get(CONF_MODIFIERS, [])),
                }
            )
        return self._working_config

    async def _persist(self) -> None:
        working = self._working()
        self.hass.config_entries.async_update_entry(
            self._config_entry,
            data={
                CONF_ENGINE_NAME: working[CONF_ENGINE_NAME],
                CONF_AUTO_DISCOVERY: working[CONF_AUTO_DISCOVERY],
            },
            options={
                CONF_ROOMS: working[CONF_ROOMS],
                CONF_MODES: working[CONF_MODES],
                CONF_MODIFIERS: working[CONF_MODIFIERS],
            },
        )

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        self._working()
        return self.async_show_menu(
            step_id="init",
            menu_options=["engine", "rooms", "modes", "modifiers"],
        )

    async def async_step_engine(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        if user_input is not None:
            new_auto = user_input[CONF_AUTO_DISCOVERY]
            old_auto = working[CONF_AUTO_DISCOVERY]
            working[CONF_ENGINE_NAME] = user_input[CONF_ENGINE_NAME]
            working[CONF_AUTO_DISCOVERY] = new_auto

            if new_auto and not old_auto and working[CONF_ROOMS]:
                return await self.async_step_engine_autodiscovery_confirm()

            await self._persist()
            return self.async_show_menu(step_id="init", menu_options=["engine", "rooms", "modes", "modifiers"])

        schema = vol.Schema(
            {
                vol.Required(CONF_ENGINE_NAME, default=working[CONF_ENGINE_NAME]): str,
                vol.Required(CONF_AUTO_DISCOVERY, default=working[CONF_AUTO_DISCOVERY]): BooleanSelector(),
            }
        )
        return self.async_show_form(step_id="engine", data_schema=schema)

    async def async_step_engine_autodiscovery_confirm(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            if user_input.get("confirm"):
                await self._persist()
            else:
                self._working()[CONF_AUTO_DISCOVERY] = False
            return self.async_show_menu(step_id="init", menu_options=["engine", "rooms", "modes", "modifiers"])

        schema = vol.Schema({vol.Required("confirm", default=False): BooleanSelector()})
        return self.async_show_form(step_id="engine_autodiscovery_confirm", data_schema=schema)

    async def async_step_rooms(self, user_input: dict[str, Any] | None = None):
        rooms = self._working()[CONF_ROOMS]
        menu = ["rooms_add", "rooms_discover"]
        if rooms:
            menu += ["rooms_edit", "rooms_remove"]
        menu += ["init"]
        return self.async_show_menu(step_id="rooms", menu_options=menu)

    async def async_step_rooms_add(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        area_names = available_area_names(self.hass)

        if user_input is not None:
            area_name = user_input[CONF_NAME]
            room_id = slugify(area_name)
            room = {
                CONF_ID: room_id,
                CONF_NAME: area_name,
                CONF_SOURCE: "manual",
                CONF_MODE: user_input[CONF_MODE],
                CONF_MODIFIER: user_input[CONF_MODIFIER] or None,
            }
            working[CONF_ROOMS] = replace_by_id(working[CONF_ROOMS], room)
            await self._persist()
            return self.async_show_menu(step_id="rooms", menu_options=["rooms_add", "rooms_discover"] + (["rooms_edit", "rooms_remove"] if working[CONF_ROOMS] else []) + ["init"])

        if area_names:
            schema = vol.Schema(
                {
                    vol.Required(CONF_NAME, default=area_names[0]): SelectSelector(
                        SelectSelectorConfig(options=area_names, mode=SelectSelectorMode.LIST)
                    ),
                    vol.Required(CONF_MODE, default=available_room_mode_choices(working)[0]): SelectSelector(
                        SelectSelectorConfig(options=available_room_mode_choices(working), mode=SelectSelectorMode.LIST)
                    ),
                    vol.Required(CONF_MODIFIER, default=""): SelectSelector(
                        SelectSelectorConfig(options=available_modifier_choices(working), mode=SelectSelectorMode.LIST)
                    ),
                }
            )
        else:
            schema = vol.Schema(
                {
                    vol.Required(CONF_NAME): TextSelector(TextSelectorConfig()),
                    vol.Required(CONF_MODE, default=available_room_mode_choices(working)[0]): SelectSelector(
                        SelectSelectorConfig(options=available_room_mode_choices(working), mode=SelectSelectorMode.LIST)
                    ),
                    vol.Required(CONF_MODIFIER, default=""): SelectSelector(
                        SelectSelectorConfig(options=available_modifier_choices(working), mode=SelectSelectorMode.LIST)
                    ),
                }
            )
        return self.async_show_form(step_id="rooms_add", data_schema=schema)

    async def async_step_rooms_edit(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        rooms = working[CONF_ROOMS]
        room_ids = [room.get(CONF_ID) for room in rooms if room.get(CONF_ID)]
        if not room_ids:
            return self.async_show_menu(step_id="rooms", menu_options=["rooms_add", "rooms_discover", "init"])

        if user_input is not None and CONF_ID in user_input:
            selected = user_input[CONF_ID]
            self._edit_room = next((r for r in rooms if r.get(CONF_ID) == selected), None)
            if self._edit_room is not None:
                return await self.async_step_rooms_edit_form()

        if len(room_ids) == 1:
            self._edit_room = next(r for r in rooms if r.get(CONF_ID) == room_ids[0])
            return await self.async_step_rooms_edit_form()

        schema = vol.Schema(
            {
                vol.Required(CONF_ID, default=room_ids[0]): SelectSelector(
                    SelectSelectorConfig(options=room_ids, mode=SelectSelectorMode.LIST)
                )
            }
        )
        return self.async_show_form(step_id="rooms_edit", data_schema=schema)

    async def async_step_rooms_edit_form(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        room = getattr(self, "_edit_room", None)
        if room is None:
            return self.async_show_menu(step_id="rooms", menu_options=["rooms_add", "rooms_discover"] + (["rooms_edit", "rooms_remove"] if working[CONF_ROOMS] else []) + ["init"])

        area_names = available_area_names(self.hass)
        mode_choices = available_room_mode_choices(working)
        modifier_choices = available_modifier_choices(working)

        if user_input is not None:
            updated = {
                CONF_ID: room[CONF_ID],
                CONF_NAME: user_input[CONF_NAME],
                CONF_SOURCE: room.get(CONF_SOURCE, "manual"),
                CONF_MODE: user_input[CONF_MODE],
                CONF_MODIFIER: user_input[CONF_MODIFIER] or None,
            }
            working[CONF_ROOMS] = replace_by_id(working[CONF_ROOMS], updated)
            await self._persist()
            return self.async_show_menu(step_id="rooms", menu_options=["rooms_add", "rooms_discover"] + (["rooms_edit", "rooms_remove"] if working[CONF_ROOMS] else []) + ["init"])

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=room.get(CONF_NAME, "")): SelectSelector(
                    SelectSelectorConfig(options=area_names or [room.get(CONF_NAME, "")], mode=SelectSelectorMode.LIST)
                ) if area_names else TextSelector(TextSelectorConfig()),
                vol.Required(CONF_MODE, default=room.get(CONF_MODE, mode_choices[0])): SelectSelector(
                    SelectSelectorConfig(options=mode_choices, mode=SelectSelectorMode.LIST)
                ),
                vol.Required(CONF_MODIFIER, default=room.get(CONF_MODIFIER) or ""): SelectSelector(
                    SelectSelectorConfig(options=modifier_choices, mode=SelectSelectorMode.LIST)
                ),
            }
        )
        return self.async_show_form(step_id="rooms_edit_form", data_schema=schema)

    async def async_step_rooms_discover(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        if user_input is not None:
            if user_input.get("run_discovery"):
                if working[CONF_ROOMS]:
                    return await self.async_step_rooms_discover_confirm()
                existing_ids = {room.get(CONF_ID) for room in working[CONF_ROOMS] if room.get(CONF_ID)}
                discovered = await discover_rooms_from_areas(self.hass, existing_ids)
                for room in discovered:
                    working[CONF_ROOMS] = replace_by_id(working[CONF_ROOMS], room)
                await self._persist()
            return self.async_show_menu(step_id="rooms", menu_options=["rooms_add", "rooms_discover"] + (["rooms_edit", "rooms_remove"] if working[CONF_ROOMS] else []) + ["init"])

        schema = vol.Schema({vol.Required("run_discovery", default=True): BooleanSelector()})
        return self.async_show_form(step_id="rooms_discover", data_schema=schema)

    async def async_step_rooms_discover_confirm(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        if user_input is not None:
            if user_input.get("confirm"):
                existing_ids = {room.get(CONF_ID) for room in working[CONF_ROOMS] if room.get(CONF_ID)}
                discovered = await discover_rooms_from_areas(self.hass, existing_ids)
                for room in discovered:
                    working[CONF_ROOMS] = replace_by_id(working[CONF_ROOMS], room)
                await self._persist()
            return self.async_show_menu(step_id="rooms", menu_options=["rooms_add", "rooms_discover"] + (["rooms_edit", "rooms_remove"] if working[CONF_ROOMS] else []) + ["init"])

        schema = vol.Schema({vol.Required("confirm", default=False): BooleanSelector()})
        return self.async_show_form(step_id="rooms_discover_confirm", data_schema=schema)

    async def async_step_rooms_remove(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        room_ids = [room.get(CONF_ID) for room in working[CONF_ROOMS] if room.get(CONF_ID)]
        if not room_ids:
            return self.async_show_menu(step_id="rooms", menu_options=["rooms_add", "rooms_discover", "init"])

        if user_input is not None and CONF_ID in user_input:
            selected = user_input[CONF_ID]
            self._remove_room = next((r for r in working[CONF_ROOMS] if r.get(CONF_ID) == selected), None)
            if self._remove_room is not None:
                return await self.async_step_rooms_remove_confirm()

        schema = vol.Schema(
            {
                vol.Required(CONF_ID, default=room_ids[0]): SelectSelector(
                    SelectSelectorConfig(options=room_ids, mode=SelectSelectorMode.LIST)
                )
            }
        )
        return self.async_show_form(step_id="rooms_remove", data_schema=schema)

    async def async_step_rooms_remove_confirm(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        room = getattr(self, "_remove_room", None)
        if room is None:
            return self.async_show_menu(step_id="rooms", menu_options=["rooms_add", "rooms_discover"] + (["rooms_edit", "rooms_remove"] if working[CONF_ROOMS] else []) + ["init"])

        if user_input is not None:
            if user_input.get("confirm"):
                working[CONF_ROOMS] = remove_by_id(working[CONF_ROOMS], room[CONF_ID])
                await self._persist()
            return self.async_show_menu(step_id="rooms", menu_options=["rooms_add", "rooms_discover"] + (["rooms_edit", "rooms_remove"] if working[CONF_ROOMS] else []) + ["init"])

        schema = vol.Schema({vol.Required("confirm", default=False): BooleanSelector()})
        return self.async_show_form(step_id="rooms_remove_confirm", data_schema=schema)

    async def async_step_modes(self, user_input: dict[str, Any] | None = None):
        modes = self._working()[CONF_MODES]
        menu = ["modes_add"]
        if modes:
            menu += ["modes_edit", "modes_remove"]
        menu += ["init"]
        return self.async_show_menu(step_id="modes", menu_options=menu)

    async def async_step_modes_add(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        if user_input is not None:
            mode_name = user_input[CONF_MODE_NAME].strip()
            mode = {
                CONF_ID: slugify(mode_name),
                CONF_NAME: mode_name,
                CONF_MODE_LIGHTING: user_input[CONF_MODE_LIGHTING],
                CONF_MODE_HVAC: user_input[CONF_MODE_HVAC],
                CONF_MODE_MEDIA: user_input[CONF_MODE_MEDIA],
            }
            working[CONF_MODES] = replace_by_id(working[CONF_MODES], mode)
            await self._persist()
            return self.async_show_menu(step_id="modes", menu_options=["modes_add"] + (["modes_edit", "modes_remove"] if working[CONF_MODES] else []) + ["init"])

        schema = vol.Schema(
            {
                vol.Required(CONF_MODE_NAME): TextSelector(TextSelectorConfig()),
                vol.Required(CONF_MODE_LIGHTING, default=True): BooleanSelector(),
                vol.Required(CONF_MODE_HVAC, default=True): BooleanSelector(),
                vol.Required(CONF_MODE_MEDIA, default=True): BooleanSelector(),
            }
        )
        return self.async_show_form(step_id="modes_add", data_schema=schema)

    async def async_step_modes_edit(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        modes = working[CONF_MODES]
        mode_ids = [mode.get(CONF_ID) for mode in modes if mode.get(CONF_ID)]
        if not mode_ids:
            return self.async_show_menu(step_id="modes", menu_options=["modes_add", "init"])

        if user_input is not None and CONF_ID in user_input:
            selected = user_input[CONF_ID]
            self._edit_mode = next((m for m in modes if m.get(CONF_ID) == selected), None)
            if self._edit_mode is not None:
                return await self.async_step_modes_edit_form()

        if len(mode_ids) == 1:
            self._edit_mode = next(m for m in modes if m.get(CONF_ID) == mode_ids[0])
            return await self.async_step_modes_edit_form()

        schema = vol.Schema(
            {
                vol.Required(CONF_ID, default=mode_ids[0]): SelectSelector(
                    SelectSelectorConfig(options=mode_ids, mode=SelectSelectorMode.LIST)
                )
            }
        )
        return self.async_show_form(step_id="modes_edit", data_schema=schema)

    async def async_step_modes_edit_form(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        mode = getattr(self, "_edit_mode", None)
        if mode is None:
            return self.async_show_menu(step_id="modes", menu_options=["modes_add"] + (["modes_edit", "modes_remove"] if working[CONF_MODES] else []) + ["init"])

        if user_input is not None:
            updated = {
                CONF_ID: mode[CONF_ID],
                CONF_NAME: user_input[CONF_MODE_NAME],
                CONF_MODE_LIGHTING: user_input[CONF_MODE_LIGHTING],
                CONF_MODE_HVAC: user_input[CONF_MODE_HVAC],
                CONF_MODE_MEDIA: user_input[CONF_MODE_MEDIA],
            }
            working[CONF_MODES] = replace_by_id(working[CONF_MODES], updated)
            await self._persist()
            return self.async_show_menu(step_id="modes", menu_options=["modes_add"] + (["modes_edit", "modes_remove"] if working[CONF_MODES] else []) + ["init"])

        schema = vol.Schema(
            {
                vol.Required(CONF_MODE_NAME, default=mode.get(CONF_NAME, "")): TextSelector(TextSelectorConfig()),
                vol.Required(CONF_MODE_LIGHTING, default=mode.get(CONF_MODE_LIGHTING, True)): BooleanSelector(),
                vol.Required(CONF_MODE_HVAC, default=mode.get(CONF_MODE_HVAC, True)): BooleanSelector(),
                vol.Required(CONF_MODE_MEDIA, default=mode.get(CONF_MODE_MEDIA, True)): BooleanSelector(),
            }
        )
        return self.async_show_form(step_id="modes_edit_form", data_schema=schema)

    async def async_step_modes_remove(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        mode_ids = [mode.get(CONF_ID) for mode in working[CONF_MODES] if mode.get(CONF_ID)]
        if not mode_ids:
            return self.async_show_menu(step_id="modes", menu_options=["modes_add", "init"])

        if user_input is not None and CONF_ID in user_input:
            selected = user_input[CONF_ID]
            self._remove_mode = next((m for m in working[CONF_MODES] if m.get(CONF_ID) == selected), None)
            if self._remove_mode is not None:
                return await self.async_step_modes_remove_confirm()

        schema = vol.Schema(
            {
                vol.Required(CONF_ID, default=mode_ids[0]): SelectSelector(
                    SelectSelectorConfig(options=mode_ids, mode=SelectSelectorMode.LIST)
                )
            }
        )
        return self.async_show_form(step_id="modes_remove", data_schema=schema)

    async def async_step_modes_remove_confirm(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        mode = getattr(self, "_remove_mode", None)
        if mode is None:
            return self.async_show_menu(step_id="modes", menu_options=["modes_add"] + (["modes_edit", "modes_remove"] if working[CONF_MODES] else []) + ["init"])

        if user_input is not None:
            if user_input.get("confirm"):
                working[CONF_MODES] = remove_by_id(working[CONF_MODES], mode[CONF_ID])
                await self._persist()
            return self.async_show_menu(step_id="modes", menu_options=["modes_add"] + (["modes_edit", "modes_remove"] if working[CONF_MODES] else []) + ["init"])

        schema = vol.Schema({vol.Required("confirm", default=False): BooleanSelector()})
        return self.async_show_form(step_id="modes_remove_confirm", data_schema=schema)

    async def async_step_modifiers(self, user_input: dict[str, Any] | None = None):
        modifiers = self._working()[CONF_MODIFIERS]
        menu = ["modifiers_add"]
        if modifiers:
            menu += ["modifiers_edit", "modifiers_remove"]
        menu += ["init"]
        return self.async_show_menu(step_id="modifiers", menu_options=menu)

    async def async_step_modifiers_add(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        mode_ids = [mode.get(CONF_ID) for mode in working[CONF_MODES] if mode.get(CONF_ID)] or ["room"]

        if user_input is not None:
            modifier_name = user_input[CONF_MODIFIER_NAME].strip()
            modifier = {
                CONF_ID: slugify(modifier_name),
                CONF_NAME: modifier_name,
                CONF_MODIFIER_BASE_MODE: user_input[CONF_MODIFIER_BASE_MODE],
                CONF_MODIFIER_PRIORITY: user_input[CONF_MODIFIER_PRIORITY],
            }
            working[CONF_MODIFIERS] = replace_by_id(working[CONF_MODIFIERS], modifier)
            await self._persist()
            return self.async_show_menu(step_id="modifiers", menu_options=["modifiers_add"] + (["modifiers_edit", "modifiers_remove"] if working[CONF_MODIFIERS] else []) + ["init"])

        schema = vol.Schema(
            {
                vol.Required(CONF_MODIFIER_NAME): TextSelector(TextSelectorConfig()),
                vol.Required(CONF_MODIFIER_BASE_MODE, default=mode_ids[0]): SelectSelector(
                    SelectSelectorConfig(options=mode_ids, mode=SelectSelectorMode.LIST)
                ),
                vol.Required(CONF_MODIFIER_PRIORITY, default=50): NumberSelector(
                    NumberSelectorConfig(mode="box", min=0, max=100, step=1)
                ),
            }
        )
        return self.async_show_form(step_id="modifiers_add", data_schema=schema)

    async def async_step_modifiers_edit(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        modifiers = working[CONF_MODIFIERS]
        modifier_ids = [modifier.get(CONF_ID) for modifier in modifiers if modifier.get(CONF_ID)]
        if not modifier_ids:
            return self.async_show_menu(step_id="modifiers", menu_options=["modifiers_add", "init"])

        if user_input is not None and CONF_ID in user_input:
            selected = user_input[CONF_ID]
            self._edit_modifier = next((m for m in modifiers if m.get(CONF_ID) == selected), None)
            if self._edit_modifier is not None:
                return await self.async_step_modifiers_edit_form()

        if len(modifier_ids) == 1:
            self._edit_modifier = next(m for m in modifiers if m.get(CONF_ID) == modifier_ids[0])
            return await self.async_step_modifiers_edit_form()

        schema = vol.Schema(
            {
                vol.Required(CONF_ID, default=modifier_ids[0]): SelectSelector(
                    SelectSelectorConfig(options=modifier_ids, mode=SelectSelectorMode.LIST)
                )
            }
        )
        return self.async_show_form(step_id="modifiers_edit", data_schema=schema)

    async def async_step_modifiers_edit_form(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        modifier = getattr(self, "_edit_modifier", None)
        if modifier is None:
            return self.async_show_menu(step_id="modifiers", menu_options=["modifiers_add"] + (["modifiers_edit", "modifiers_remove"] if working[CONF_MODIFIERS] else []) + ["init"])

        mode_ids = [mode.get(CONF_ID) for mode in working[CONF_MODES] if mode.get(CONF_ID)] or ["room"]

        if user_input is not None:
            updated = {
                CONF_ID: modifier[CONF_ID],
                CONF_NAME: user_input[CONF_MODIFIER_NAME],
                CONF_MODIFIER_BASE_MODE: user_input[CONF_MODIFIER_BASE_MODE],
                CONF_MODIFIER_PRIORITY: user_input[CONF_MODIFIER_PRIORITY],
            }
            working[CONF_MODIFIERS] = replace_by_id(working[CONF_MODIFIERS], updated)
            await self._persist()
            return self.async_show_menu(step_id="modifiers", menu_options=["modifiers_add"] + (["modifiers_edit", "modifiers_remove"] if working[CONF_MODIFIERS] else []) + ["init"])

        schema = vol.Schema(
            {
                vol.Required(CONF_MODIFIER_NAME, default=modifier.get(CONF_NAME, "")): TextSelector(TextSelectorConfig()),
                vol.Required(CONF_MODIFIER_BASE_MODE, default=modifier.get(CONF_MODIFIER_BASE_MODE, mode_ids[0])): SelectSelector(
                    SelectSelectorConfig(options=mode_ids, mode=SelectSelectorMode.LIST)
                ),
                vol.Required(CONF_MODIFIER_PRIORITY, default=modifier.get(CONF_MODIFIER_PRIORITY, 50)): NumberSelector(
                    NumberSelectorConfig(mode="box", min=0, max=100, step=1)
                ),
            }
        )
        return self.async_show_form(step_id="modifiers_edit_form", data_schema=schema)

    async def async_step_modifiers_remove(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        modifier_ids = [modifier.get(CONF_ID) for modifier in working[CONF_MODIFIERS] if modifier.get(CONF_ID)]
        if not modifier_ids:
            return self.async_show_menu(step_id="modifiers", menu_options=["modifiers_add", "init"])

        if user_input is not None and CONF_ID in user_input:
            selected = user_input[CONF_ID]
            self._remove_modifier = next((m for m in working[CONF_MODIFIERS] if m.get(CONF_ID) == selected), None)
            if self._remove_modifier is not None:
                return await self.async_step_modifiers_remove_confirm()

        schema = vol.Schema(
            {
                vol.Required(CONF_ID, default=modifier_ids[0]): SelectSelector(
                    SelectSelectorConfig(options=modifier_ids, mode=SelectSelectorMode.LIST)
                )
            }
        )
        return self.async_show_form(step_id="modifiers_remove", data_schema=schema)

    async def async_step_modifiers_remove_confirm(self, user_input: dict[str, Any] | None = None):
        working = self._working()
        modifier = getattr(self, "_remove_modifier", None)
        if modifier is None:
            return self.async_show_menu(step_id="modifiers", menu_options=["modifiers_add"] + (["modifiers_edit", "modifiers_remove"] if working[CONF_MODIFIERS] else []) + ["init"])

        if user_input is not None:
            if user_input.get("confirm"):
                working[CONF_MODIFIERS] = remove_by_id(working[CONF_MODIFIERS], modifier[CONF_ID])
                await self._persist()
            return self.async_show_menu(step_id="modifiers", menu_options=["modifiers_add"] + (["modifiers_edit", "modifiers_remove"] if working[CONF_MODIFIERS] else []) + ["init"])

        schema = vol.Schema({vol.Required("confirm", default=False): BooleanSelector()})
        return self.async_show_form(step_id="modifiers_remove_confirm", data_schema=schema)
