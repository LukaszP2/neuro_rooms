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
    CONF_MODES,
    CONF_MODIFIER,
    CONF_MODIFIER_BASE_MODE,
    CONF_MODIFIER_NAME,
    CONF_MODIFIER_PRIORITY,
    CONF_MODIFIERS,
    CONF_NAME,
    CONF_ROOMS,
    CONF_SOURCE,
    DEFAULT_ENGINE_NAME,
    DOMAIN,
)
from .helpers import (
    NO_MODIFIER_VALUE,
    async_discover_rooms_from_areas_for_entry,
    available_area_select_options,
    available_mode_select_options,
    available_modifier_select_options,
    available_room_select_options,
    ensure_structure,
    normalize_modifier,
    remove_by_id,
    replace_by_id,
    slugify,
)


class NeuroRoomsConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
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
    def __init__(self, config_entry):
        self._config_entry = config_entry

    def _working(self) -> dict[str, Any]:
        if not hasattr(self, "_working_config"):
            self._working_config = ensure_structure(
                {
                    CONF_ENGINE_NAME: self._config_entry.data.get(
                        CONF_ENGINE_NAME, DEFAULT_ENGINE_NAME
                    ),
                    CONF_AUTO_DISCOVERY: self._config_entry.data.get(
                        CONF_AUTO_DISCOVERY, True
                    ),
                    CONF_ROOMS: deepcopy(
                        self._config_entry.options.get(CONF_ROOMS, [])
                    ),
                    CONF_MODES: deepcopy(
                        self._config_entry.options.get(CONF_MODES, [])
                    ),
                    CONF_MODIFIERS: deepcopy(
                        self._config_entry.options.get(CONF_MODIFIERS, [])
                    ),
                }
            )
        return self._working_config

    async def _persist(self) -> None:
        w = self._working()
        self.hass.config_entries.async_update_entry(
            self._config_entry,
            data={
                CONF_ENGINE_NAME: w[CONF_ENGINE_NAME],
                CONF_AUTO_DISCOVERY: w[CONF_AUTO_DISCOVERY],
            },
            options={
                CONF_ROOMS: w[CONF_ROOMS],
                CONF_MODES: w[CONF_MODES],
                CONF_MODIFIERS: w[CONF_MODIFIERS],
            },
        )

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        self._working()
        return self.async_show_menu(
            step_id="init",
            menu_options=["engine", "rooms", "modes", "modifiers"],
        )

    async def async_step_engine(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        if user_input is not None:
            new_auto = user_input[CONF_AUTO_DISCOVERY]
            old_auto = w[CONF_AUTO_DISCOVERY]
            w[CONF_ENGINE_NAME] = user_input[CONF_ENGINE_NAME]
            w[CONF_AUTO_DISCOVERY] = new_auto
            if new_auto and not old_auto and w[CONF_ROOMS]:
                return await self.async_step_engine_autodiscovery_confirm()
            await self._persist()
            return self.async_show_menu(
                step_id="init", menu_options=["engine", "rooms", "modes", "modifiers"]
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_ENGINE_NAME, default=w[CONF_ENGINE_NAME]): str,
                vol.Required(
                    CONF_AUTO_DISCOVERY, default=w[CONF_AUTO_DISCOVERY]
                ): BooleanSelector(),
            }
        )
        return self.async_show_form(step_id="engine", data_schema=schema)

    async def async_step_engine_autodiscovery_confirm(
        self, user_input: dict[str, Any] | None = None
    ):
        w = self._working()
        if user_input is not None:
            if user_input.get("confirm"):
                existing_ids = {
                    room.get(CONF_ID) for room in w[CONF_ROOMS] if room.get(CONF_ID)
                }
                discovered = await async_discover_rooms_from_areas_for_entry(
                    self.hass, existing_ids
                )
                for room in discovered:
                    w[CONF_ROOMS] = replace_by_id(w[CONF_ROOMS], room)
                await self._persist()
            else:
                w[CONF_AUTO_DISCOVERY] = False
            return self.async_show_menu(
                step_id="init", menu_options=["engine", "rooms", "modes", "modifiers"]
            )

        return self.async_show_form(
            step_id="engine_autodiscovery_confirm",
            data_schema=vol.Schema(
                {vol.Required("confirm", default=False): BooleanSelector()}
            ),
        )

    async def async_step_rooms(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        menu = ["rooms_add", "rooms_discover"]
        if w[CONF_ROOMS]:
            menu += ["rooms_edit", "rooms_remove"]
        menu += ["init"]
        return self.async_show_menu(step_id="rooms", menu_options=menu)

    async def async_step_rooms_add(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        areas = available_area_select_options(self.hass)
        mode_opts = available_mode_select_options(w)
        mod_opts = available_modifier_select_options(w)

        if user_input is not None:
            room_name = user_input[CONF_NAME]
            room = {
                CONF_ID: slugify(room_name),
                CONF_NAME: room_name,
                CONF_SOURCE: "manual",
                CONF_MODE: user_input[CONF_MODE],
                CONF_MODIFIER: normalize_modifier(user_input.get(CONF_MODIFIER)),
            }
            w[CONF_ROOMS] = replace_by_id(w[CONF_ROOMS], room)
            await self._persist()
            return self.async_show_menu(
                step_id="rooms",
                menu_options=["rooms_add", "rooms_discover"]
                + (["rooms_edit", "rooms_remove"] if w[CONF_ROOMS] else [])
                + ["init"],
            )

        if areas:
            schema = vol.Schema(
                {
                    vol.Required(CONF_NAME, default=areas[0]["value"]): SelectSelector(
                        SelectSelectorConfig(
                            options=areas, mode=SelectSelectorMode.LIST
                        )
                    ),
                    vol.Required(
                        CONF_MODE, default=mode_opts[0]["value"]
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=mode_opts, mode=SelectSelectorMode.LIST
                        )
                    ),
                    vol.Required(
                        CONF_MODIFIER, default=NO_MODIFIER_VALUE
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=mod_opts, mode=SelectSelectorMode.LIST
                        )
                    ),
                }
            )
        else:
            schema = vol.Schema(
                {
                    vol.Required(CONF_NAME): TextSelector(TextSelectorConfig()),
                    vol.Required(
                        CONF_MODE, default=mode_opts[0]["value"]
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=mode_opts, mode=SelectSelectorMode.LIST
                        )
                    ),
                    vol.Required(
                        CONF_MODIFIER, default=NO_MODIFIER_VALUE
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=mod_opts, mode=SelectSelectorMode.LIST
                        )
                    ),
                }
            )

        return self.async_show_form(step_id="rooms_add", data_schema=schema)

    async def async_step_rooms_edit(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        options = available_room_select_options(w)

        if not options:
            return self.async_show_menu(
                step_id="rooms", menu_options=["rooms_add", "rooms_discover", "init"]
            )

        if user_input is not None and CONF_ID in user_input:
            selected = user_input[CONF_ID]
            self._edit_room = next(
                (r for r in w[CONF_ROOMS] if r.get(CONF_ID) == selected), None
            )
            if self._edit_room is not None:
                return await self.async_step_rooms_edit_form()

        if len(options) == 1:
            self._edit_room = next(
                r for r in w[CONF_ROOMS] if r.get(CONF_ID) == options[0]["value"]
            )
            return await self.async_step_rooms_edit_form()

        return self.async_show_form(
            step_id="rooms_edit",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ID, default=options[0]["value"]): SelectSelector(
                        SelectSelectorConfig(
                            options=options, mode=SelectSelectorMode.LIST
                        )
                    )
                }
            ),
        )

    async def async_step_rooms_edit_form(
        self, user_input: dict[str, Any] | None = None
    ):
        w = self._working()
        room = getattr(self, "_edit_room", None)
        if room is None:
            return self.async_show_menu(
                step_id="rooms",
                menu_options=["rooms_add", "rooms_discover"]
                + (["rooms_edit", "rooms_remove"] if w[CONF_ROOMS] else [])
                + ["init"],
            )

        mode_opts = available_mode_select_options(w)
        mod_opts = available_modifier_select_options(w)

        if user_input is not None:
            updated = {
                CONF_ID: room[CONF_ID],
                CONF_NAME: room[
                    CONF_NAME
                ],  # keep paired room name, no second room list here
                CONF_SOURCE: room.get(CONF_SOURCE, "manual"),
                CONF_MODE: user_input[CONF_MODE],
                CONF_MODIFIER: normalize_modifier(user_input.get(CONF_MODIFIER)),
            }
            w[CONF_ROOMS] = replace_by_id(w[CONF_ROOMS], updated)
            await self._persist()
            return self.async_show_menu(
                step_id="rooms",
                menu_options=["rooms_add", "rooms_discover"]
                + (["rooms_edit", "rooms_remove"] if w[CONF_ROOMS] else [])
                + ["init"],
            )

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_MODE,
                    default=room.get(CONF_MODE, mode_opts[0]["value"]),
                ): SelectSelector(
                    SelectSelectorConfig(
                        options=mode_opts, mode=SelectSelectorMode.LIST
                    )
                ),
                vol.Required(
                    CONF_MODIFIER,
                    default=room.get(CONF_MODIFIER) or NO_MODIFIER_VALUE,
                ): SelectSelector(
                    SelectSelectorConfig(options=mod_opts, mode=SelectSelectorMode.LIST)
                ),
            }
        )
        return self.async_show_form(step_id="rooms_edit_form", data_schema=schema)

    async def async_step_rooms_discover(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        if user_input is not None:
            if user_input.get("run_discovery"):
                if w[CONF_ROOMS]:
                    # Existing rooms present — ask before overwriting
                    return await self.async_step_rooms_discover_confirm()
                # No existing rooms — discover immediately without confirmation
                discovered = await async_discover_rooms_from_areas_for_entry(
                    self.hass, set()
                )
                for room in discovered:
                    w[CONF_ROOMS] = replace_by_id(w[CONF_ROOMS], room)
                await self._persist()
            return self.async_show_menu(
                step_id="rooms",
                menu_options=["rooms_add", "rooms_discover"]
                + (["rooms_edit", "rooms_remove"] if w[CONF_ROOMS] else [])
                + ["init"],
            )

        return self.async_show_form(
            step_id="rooms_discover",
            data_schema=vol.Schema(
                {vol.Required("run_discovery", default=True): BooleanSelector()}
            ),
        )

    async def async_step_rooms_discover_confirm(
        self, user_input: dict[str, Any] | None = None
    ):
        w = self._working()
        if user_input is not None:
            if user_input.get("confirm"):
                existing_ids = {
                    room.get(CONF_ID) for room in w[CONF_ROOMS] if room.get(CONF_ID)
                }
                discovered = await async_discover_rooms_from_areas_for_entry(
                    self.hass, existing_ids
                )
                for room in discovered:
                    w[CONF_ROOMS] = replace_by_id(w[CONF_ROOMS], room)
                await self._persist()
            return self.async_show_menu(
                step_id="rooms",
                menu_options=["rooms_add", "rooms_discover"]
                + (["rooms_edit", "rooms_remove"] if w[CONF_ROOMS] else [])
                + ["init"],
            )

        return self.async_show_form(
            step_id="rooms_discover_confirm",
            data_schema=vol.Schema(
                {vol.Required("confirm", default=False): BooleanSelector()}
            ),
        )

    async def async_step_rooms_remove(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        options = available_room_select_options(w)
        if not options:
            return self.async_show_menu(
                step_id="rooms", menu_options=["rooms_add", "rooms_discover", "init"]
            )

        if user_input is not None and CONF_ID in user_input:
            selected = user_input[CONF_ID]
            self._remove_room = next(
                (r for r in w[CONF_ROOMS] if r.get(CONF_ID) == selected), None
            )
            if self._remove_room is not None:
                return await self.async_step_rooms_remove_confirm()

        return self.async_show_form(
            step_id="rooms_remove",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ID, default=options[0]["value"]): SelectSelector(
                        SelectSelectorConfig(
                            options=options, mode=SelectSelectorMode.LIST
                        )
                    )
                }
            ),
        )

    async def async_step_rooms_remove_confirm(
        self, user_input: dict[str, Any] | None = None
    ):
        w = self._working()
        room = getattr(self, "_remove_room", None)
        if room is None:
            return self.async_show_menu(
                step_id="rooms",
                menu_options=["rooms_add", "rooms_discover"]
                + (["rooms_edit", "rooms_remove"] if w[CONF_ROOMS] else [])
                + ["init"],
            )

        if user_input is not None:
            if user_input.get("confirm"):
                w[CONF_ROOMS] = remove_by_id(w[CONF_ROOMS], room[CONF_ID])
                await self._persist()
            return self.async_show_menu(
                step_id="rooms",
                menu_options=["rooms_add", "rooms_discover"]
                + (["rooms_edit", "rooms_remove"] if w[CONF_ROOMS] else [])
                + ["init"],
            )

        return self.async_show_form(
            step_id="rooms_remove_confirm",
            data_schema=vol.Schema(
                {vol.Required("confirm", default=False): BooleanSelector()}
            ),
        )

    async def async_step_modes(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        menu = ["modes_add"]
        if w[CONF_MODES]:
            menu += ["modes_edit", "modes_remove"]
        menu += ["init"]
        return self.async_show_menu(step_id="modes", menu_options=menu)

    async def async_step_modes_add(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        if user_input is not None:
            mode = {
                CONF_ID: slugify(user_input[CONF_MODE_NAME]),
                CONF_NAME: user_input[CONF_MODE_NAME].strip(),
                CONF_MODE_LIGHTING: user_input[CONF_MODE_LIGHTING],
                CONF_MODE_HVAC: user_input[CONF_MODE_HVAC],
                CONF_MODE_MEDIA: user_input[CONF_MODE_MEDIA],
            }
            w[CONF_MODES] = replace_by_id(w[CONF_MODES], mode)
            await self._persist()
            return self.async_show_menu(
                step_id="modes",
                menu_options=["modes_add"]
                + (["modes_edit", "modes_remove"] if w[CONF_MODES] else [])
                + ["init"],
            )

        return self.async_show_form(
            step_id="modes_add",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODE_NAME): TextSelector(TextSelectorConfig()),
                    vol.Required(CONF_MODE_LIGHTING, default=True): BooleanSelector(),
                    vol.Required(CONF_MODE_HVAC, default=True): BooleanSelector(),
                    vol.Required(CONF_MODE_MEDIA, default=True): BooleanSelector(),
                }
            ),
        )

    async def async_step_modes_edit(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        options = available_mode_select_options(w)
        if not options:
            return self.async_show_menu(
                step_id="modes", menu_options=["modes_add", "init"]
            )

        if user_input is not None and CONF_ID in user_input:
            selected = user_input[CONF_ID]
            self._edit_mode = next(
                (m for m in w[CONF_MODES] if m.get(CONF_ID) == selected), None
            )
            if self._edit_mode is not None:
                return await self.async_step_modes_edit_form()

        if len(options) == 1:
            self._edit_mode = next(
                m for m in w[CONF_MODES] if m.get(CONF_ID) == options[0]["value"]
            )
            return await self.async_step_modes_edit_form()

        return self.async_show_form(
            step_id="modes_edit",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ID, default=options[0]["value"]): SelectSelector(
                        SelectSelectorConfig(
                            options=options, mode=SelectSelectorMode.LIST
                        )
                    )
                }
            ),
        )

    async def async_step_modes_edit_form(
        self, user_input: dict[str, Any] | None = None
    ):
        w = self._working()
        mode = getattr(self, "_edit_mode", None)
        if mode is None:
            return self.async_show_menu(
                step_id="modes",
                menu_options=["modes_add"]
                + (["modes_edit", "modes_remove"] if w[CONF_MODES] else [])
                + ["init"],
            )

        if user_input is not None:
            updated = {
                CONF_ID: mode[CONF_ID],
                CONF_NAME: user_input[CONF_MODE_NAME],
                CONF_MODE_LIGHTING: user_input[CONF_MODE_LIGHTING],
                CONF_MODE_HVAC: user_input[CONF_MODE_HVAC],
                CONF_MODE_MEDIA: user_input[CONF_MODE_MEDIA],
            }
            w[CONF_MODES] = replace_by_id(w[CONF_MODES], updated)
            await self._persist()
            return self.async_show_menu(
                step_id="modes",
                menu_options=["modes_add"]
                + (["modes_edit", "modes_remove"] if w[CONF_MODES] else [])
                + ["init"],
            )

        return self.async_show_form(
            step_id="modes_edit_form",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MODE_NAME, default=mode.get(CONF_NAME, "")
                    ): TextSelector(TextSelectorConfig()),
                    vol.Required(
                        CONF_MODE_LIGHTING, default=mode.get(CONF_MODE_LIGHTING, True)
                    ): BooleanSelector(),
                    vol.Required(
                        CONF_MODE_HVAC, default=mode.get(CONF_MODE_HVAC, True)
                    ): BooleanSelector(),
                    vol.Required(
                        CONF_MODE_MEDIA, default=mode.get(CONF_MODE_MEDIA, True)
                    ): BooleanSelector(),
                }
            ),
        )

    async def async_step_modes_remove(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        options = available_mode_select_options(w)
        if not options:
            return self.async_show_menu(
                step_id="modes", menu_options=["modes_add", "init"]
            )

        if user_input is not None and CONF_ID in user_input:
            selected = user_input[CONF_ID]
            self._remove_mode = next(
                (m for m in w[CONF_MODES] if m.get(CONF_ID) == selected), None
            )
            if self._remove_mode is not None:
                return await self.async_step_modes_remove_confirm()

        return self.async_show_form(
            step_id="modes_remove",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ID, default=options[0]["value"]): SelectSelector(
                        SelectSelectorConfig(
                            options=options, mode=SelectSelectorMode.LIST
                        )
                    )
                }
            ),
        )

    async def async_step_modes_remove_confirm(
        self, user_input: dict[str, Any] | None = None
    ):
        w = self._working()
        mode = getattr(self, "_remove_mode", None)
        if mode is None:
            return self.async_show_menu(
                step_id="modes",
                menu_options=["modes_add"]
                + (["modes_edit", "modes_remove"] if w[CONF_MODES] else [])
                + ["init"],
            )

        if user_input is not None:
            if user_input.get("confirm"):
                w[CONF_MODES] = remove_by_id(w[CONF_MODES], mode[CONF_ID])
                await self._persist()
            return self.async_show_menu(
                step_id="modes",
                menu_options=["modes_add"]
                + (["modes_edit", "modes_remove"] if w[CONF_MODES] else [])
                + ["init"],
            )

        return self.async_show_form(
            step_id="modes_remove_confirm",
            data_schema=vol.Schema(
                {vol.Required("confirm", default=False): BooleanSelector()}
            ),
        )

    async def async_step_modifiers(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        menu = ["modifiers_add"]
        if w[CONF_MODIFIERS]:
            menu += ["modifiers_edit", "modifiers_remove"]
        menu += ["init"]
        return self.async_show_menu(step_id="modifiers", menu_options=menu)

    async def async_step_modifiers_add(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        mode_opts = available_mode_select_options(w)
        if user_input is not None:
            mod = {
                CONF_ID: slugify(user_input[CONF_MODIFIER_NAME]),
                CONF_NAME: user_input[CONF_MODIFIER_NAME].strip(),
                CONF_MODIFIER_BASE_MODE: user_input[CONF_MODIFIER_BASE_MODE],
                CONF_MODIFIER_PRIORITY: user_input[CONF_MODIFIER_PRIORITY],
            }
            w[CONF_MODIFIERS] = replace_by_id(w[CONF_MODIFIERS], mod)
            await self._persist()
            return self.async_show_menu(
                step_id="modifiers",
                menu_options=["modifiers_add"]
                + (["modifiers_edit", "modifiers_remove"] if w[CONF_MODIFIERS] else [])
                + ["init"],
            )

        return self.async_show_form(
            step_id="modifiers_add",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_MODIFIER_NAME): TextSelector(
                        TextSelectorConfig()
                    ),
                    vol.Required(
                        CONF_MODIFIER_BASE_MODE, default=mode_opts[0]["value"]
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=mode_opts, mode=SelectSelectorMode.LIST
                        )
                    ),
                    vol.Required(CONF_MODIFIER_PRIORITY, default=50): NumberSelector(
                        NumberSelectorConfig(mode="box", min=0, max=100, step=1)
                    ),
                }
            ),
        )

    async def async_step_modifiers_edit(self, user_input: dict[str, Any] | None = None):
        w = self._working()
        options = [
            opt
            for opt in available_modifier_select_options(w)
            if opt["value"] != NO_MODIFIER_VALUE
        ]
        if not options:
            return self.async_show_menu(
                step_id="modifiers", menu_options=["modifiers_add", "init"]
            )

        if user_input is not None and CONF_ID in user_input:
            selected = user_input[CONF_ID]
            self._edit_modifier = next(
                (m for m in w[CONF_MODIFIERS] if m.get(CONF_ID) == selected), None
            )
            if self._edit_modifier is not None:
                return await self.async_step_modifiers_edit_form()

        if len(options) == 1:
            self._edit_modifier = next(
                m for m in w[CONF_MODIFIERS] if m.get(CONF_ID) == options[0]["value"]
            )
            return await self.async_step_modifiers_edit_form()

        return self.async_show_form(
            step_id="modifiers_edit",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ID, default=options[0]["value"]): SelectSelector(
                        SelectSelectorConfig(
                            options=options, mode=SelectSelectorMode.LIST
                        )
                    )
                }
            ),
        )

    async def async_step_modifiers_edit_form(
        self, user_input: dict[str, Any] | None = None
    ):
        w = self._working()
        mod = getattr(self, "_edit_modifier", None)
        if mod is None:
            return self.async_show_menu(
                step_id="modifiers",
                menu_options=["modifiers_add"]
                + (["modifiers_edit", "modifiers_remove"] if w[CONF_MODIFIERS] else [])
                + ["init"],
            )

        mode_opts = available_mode_select_options(w)

        if user_input is not None:
            updated = {
                CONF_ID: mod[CONF_ID],
                CONF_NAME: user_input[CONF_MODIFIER_NAME],
                CONF_MODIFIER_BASE_MODE: user_input[CONF_MODIFIER_BASE_MODE],
                CONF_MODIFIER_PRIORITY: user_input[CONF_MODIFIER_PRIORITY],
            }
            w[CONF_MODIFIERS] = replace_by_id(w[CONF_MODIFIERS], updated)
            await self._persist()
            return self.async_show_menu(
                step_id="modifiers",
                menu_options=["modifiers_add"]
                + (["modifiers_edit", "modifiers_remove"] if w[CONF_MODIFIERS] else [])
                + ["init"],
            )

        return self.async_show_form(
            step_id="modifiers_edit_form",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_MODIFIER_NAME, default=mod.get(CONF_NAME, "")
                    ): TextSelector(TextSelectorConfig()),
                    vol.Required(
                        CONF_MODIFIER_BASE_MODE,
                        default=mod.get(CONF_MODIFIER_BASE_MODE, mode_opts[0]["value"]),
                    ): SelectSelector(
                        SelectSelectorConfig(
                            options=mode_opts, mode=SelectSelectorMode.LIST
                        )
                    ),
                    vol.Required(
                        CONF_MODIFIER_PRIORITY,
                        default=mod.get(CONF_MODIFIER_PRIORITY, 50),
                    ): NumberSelector(
                        NumberSelectorConfig(mode="box", min=0, max=100, step=1)
                    ),
                }
            ),
        )

    async def async_step_modifiers_remove(
        self, user_input: dict[str, Any] | None = None
    ):
        w = self._working()
        options = [
            opt
            for opt in available_modifier_select_options(w)
            if opt["value"] != NO_MODIFIER_VALUE
        ]
        if not options:
            return self.async_show_menu(
                step_id="modifiers", menu_options=["modifiers_add", "init"]
            )

        if user_input is not None and CONF_ID in user_input:
            selected = user_input[CONF_ID]
            self._remove_modifier = next(
                (m for m in w[CONF_MODIFIERS] if m.get(CONF_ID) == selected), None
            )
            if self._remove_modifier is not None:
                return await self.async_step_modifiers_remove_confirm()

        return self.async_show_form(
            step_id="modifiers_remove",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_ID, default=options[0]["value"]): SelectSelector(
                        SelectSelectorConfig(
                            options=options, mode=SelectSelectorMode.LIST
                        )
                    )
                }
            ),
        )

    async def async_step_modifiers_remove_confirm(
        self, user_input: dict[str, Any] | None = None
    ):
        w = self._working()
        mod = getattr(self, "_remove_modifier", None)
        if mod is None:
            return self.async_show_menu(
                step_id="modifiers",
                menu_options=["modifiers_add"]
                + (["modifiers_edit", "modifiers_remove"] if w[CONF_MODIFIERS] else [])
                + ["init"],
            )

        if user_input is not None:
            if user_input.get("confirm"):
                w[CONF_MODIFIERS] = remove_by_id(w[CONF_MODIFIERS], mod[CONF_ID])
                await self._persist()
            return self.async_show_menu(
                step_id="modifiers",
                menu_options=["modifiers_add"]
                + (["modifiers_edit", "modifiers_remove"] if w[CONF_MODIFIERS] else [])
                + ["init"],
            )

        return self.async_show_form(
            step_id="modifiers_remove_confirm",
            data_schema=vol.Schema(
                {vol.Required("confirm", default=False): BooleanSelector()}
            ),
        )
