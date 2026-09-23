"""Options flow for Engine Neuro Rooms."""

from __future__ import annotations

import json
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import OptionsFlowWithReload
from homeassistant.helpers import selector

from .const import (
    CONF_ADVANCED_MODES_JSON,
    CONF_ADVANCED_MODIFIERS_JSON,
    CONF_ADVANCED_ROOMS_JSON,
    CONF_AUTO_DISCOVERY,
    CONF_DEFAULT_LANGUAGE,
    CONF_MODE_ACTION,
    CONF_MODE_ADVANCED_JSON,
    CONF_MODE_DESCRIPTION,
    CONF_MODE_HAS_HVAC,
    CONF_MODE_HAS_LIGHTING,
    CONF_MODE_HAS_MEDIA,
    CONF_MODE_NAME,
    CONF_MODES,
    CONF_MODIFIER_ACTION,
    CONF_MODIFIER_ADVANCED_JSON,
    CONF_MODIFIER_BASE_MODE,
    CONF_MODIFIER_DESCRIPTION,
    CONF_MODIFIER_NAME,
    CONF_MODIFIER_OVERRIDES_JSON,
    CONF_MODIFIERS,
    CONF_ROOM_ACTION,
    CONF_ROOM_ADVANCED_JSON,
    CONF_ROOM_AREA_ID,
    CONF_ROOM_HAS_HVAC,
    CONF_ROOM_HAS_LIGHTING,
    CONF_ROOM_HAS_MEDIA,
    CONF_ROOM_MODE,
    CONF_ROOM_MODIFIER,
    CONF_ROOM_NAME,
    CONF_ROOMS,
    DEFAULT_LANGUAGE,
    MODE_ACTION_ADD_ADVANCED,
    MODE_ACTION_ADD_BASIC,
    MODE_ACTION_BACK,
    MODE_ACTION_EDIT_JSON,
    MODIFIER_ACTION_ADD_ADVANCED,
    MODIFIER_ACTION_ADD_BASIC,
    MODIFIER_ACTION_BACK,
    MODIFIER_ACTION_EDIT_JSON,
    ROOM_ACTION_ADD_ADVANCED,
    ROOM_ACTION_ADD_BASIC,
    ROOM_ACTION_BACK,
    ROOM_ACTION_EDIT_JSON,
)
from .modes import DEFAULT_MODES, normalize_mode_names
from .modifiers import DEFAULT_MODIFIERS, normalize_modifier_names
from .rooms import (
    build_advanced_room_payload,
    build_basic_room_payload,
    parse_json_payload,
)
from .validation import validate_json_text


class NeuroRoomsOptionsFlow(OptionsFlowWithReload):
    """Handle options for Engine Neuro Rooms."""

    def __init__(self) -> None:
        super().__init__()
        self._data: dict[str, Any] = {}
        self._options: dict[str, Any] = {}
        self._rooms: list[dict[str, Any]] = []
        self._modes: list[dict[str, Any]] = []
        self._modifiers: list[dict[str, Any]] = []

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if not self._data:
            self._data = dict(self.config_entry.data)
            self._options = dict(self.config_entry.options)
            self._rooms = list(self._options.get(CONF_ROOMS, []))
            self._modes = list(self._options.get(CONF_MODES, DEFAULT_MODES))
            self._modifiers = list(self._options.get(CONF_MODIFIERS, DEFAULT_MODIFIERS))

        if user_input is not None:
            self._options[CONF_AUTO_DISCOVERY] = user_input[CONF_AUTO_DISCOVERY]
            self._options[CONF_DEFAULT_LANGUAGE] = user_input[CONF_DEFAULT_LANGUAGE]
            return await self.async_step_menu()

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_AUTO_DISCOVERY,
                    default=self._options.get(
                        CONF_AUTO_DISCOVERY, self._data.get(CONF_AUTO_DISCOVERY, True)
                    ),
                ): selector.BooleanSelector(),
                vol.Required(
                    CONF_DEFAULT_LANGUAGE,
                    default=self._options.get(
                        CONF_DEFAULT_LANGUAGE,
                        self._data.get(CONF_DEFAULT_LANGUAGE, DEFAULT_LANGUAGE),
                    ),
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["en", "pl"],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, self._options),
        )

    async def async_step_menu(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            action = user_input["action"]
            if action == "rooms":
                return await self.async_step_rooms_menu()
            if action == "modes":
                return await self.async_step_modes_menu()
            if action == "modifiers":
                return await self.async_step_modifiers_menu()
            return await self.async_step_done()

        schema = vol.Schema(
            {
                vol.Required("action", default="rooms"): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=["rooms", "modes", "modifiers", "done"],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="menu", data_schema=schema)

    async def async_step_rooms_menu(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            action = user_input[CONF_ROOM_ACTION]
            if action == ROOM_ACTION_ADD_BASIC:
                return await self.async_step_room_basic()
            if action == ROOM_ACTION_ADD_ADVANCED:
                return await self.async_step_room_advanced()
            if action == ROOM_ACTION_EDIT_JSON:
                return await self.async_step_rooms_json()
            return await self.async_step_menu()

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_ROOM_ACTION, default=ROOM_ACTION_ADD_BASIC
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            ROOM_ACTION_ADD_BASIC,
                            ROOM_ACTION_ADD_ADVANCED,
                            ROOM_ACTION_EDIT_JSON,
                            ROOM_ACTION_BACK,
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="rooms_menu", data_schema=schema)

    async def async_step_room_basic(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            self._rooms.append(build_basic_room_payload(user_input))
            self._options[CONF_ROOMS] = self._rooms
            return await self.async_step_rooms_menu()

        mode_options = normalize_mode_names(self._modes)
        modifier_options = normalize_modifier_names(self._modifiers)
        schema = vol.Schema(
            {
                vol.Required(CONF_ROOM_NAME): str,
                vol.Required(CONF_ROOM_AREA_ID): str,
                vol.Required(
                    CONF_ROOM_MODE, default=mode_options[0]
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=mode_options, mode=selector.SelectSelectorMode.DROPDOWN
                    )
                ),
                vol.Required(
                    CONF_ROOM_MODIFIER, default=modifier_options[0]
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=modifier_options,
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
                vol.Required(
                    CONF_ROOM_HAS_LIGHTING, default=True
                ): selector.BooleanSelector(),
                vol.Required(
                    CONF_ROOM_HAS_HVAC, default=False
                ): selector.BooleanSelector(),
                vol.Required(
                    CONF_ROOM_HAS_MEDIA, default=False
                ): selector.BooleanSelector(),
            }
        )
        return self.async_show_form(step_id="room_basic", data_schema=schema)

    async def async_step_room_advanced(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            try:
                self._rooms.append(build_advanced_room_payload(user_input))
            except (TypeError, ValueError, json.JSONDecodeError):
                return self.async_show_form(
                    step_id="room_advanced",
                    data_schema=self._room_advanced_schema(
                        default=user_input.get(CONF_ROOM_ADVANCED_JSON, "")
                    ),
                    errors={CONF_ROOM_ADVANCED_JSON: "invalid_json"},
                )
            self._options[CONF_ROOMS] = self._rooms
            return await self.async_step_rooms_menu()

        return self.async_show_form(
            step_id="room_advanced", data_schema=self._room_advanced_schema()
        )

    async def async_step_rooms_json(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            try:
                validate_json_text(user_input[CONF_ADVANCED_ROOMS_JSON])
                parsed = parse_json_payload(user_input[CONF_ADVANCED_ROOMS_JSON])
                if parsed is None:
                    self._rooms = []
                elif isinstance(parsed, list):
                    self._rooms = parsed
                else:
                    raise ValueError("rooms json must be a list")
            except (ValueError, json.JSONDecodeError):
                return self.async_show_form(
                    step_id="rooms_json",
                    data_schema=self._rooms_json_schema(
                        default=user_input.get(CONF_ADVANCED_ROOMS_JSON, "")
                    ),
                    errors={CONF_ADVANCED_ROOMS_JSON: "invalid_json"},
                )
            self._options[CONF_ROOMS] = self._rooms
            return await self.async_step_rooms_menu()

        return self.async_show_form(
            step_id="rooms_json", data_schema=self._rooms_json_schema()
        )

    async def async_step_modes_menu(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            action = user_input[CONF_MODE_ACTION]
            if action == MODE_ACTION_ADD_BASIC:
                return await self.async_step_mode_basic()
            if action == MODE_ACTION_ADD_ADVANCED:
                return await self.async_step_mode_advanced()
            if action == MODE_ACTION_EDIT_JSON:
                return await self.async_step_modes_json()
            return await self.async_step_menu()

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_MODE_ACTION, default=MODE_ACTION_ADD_BASIC
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            MODE_ACTION_ADD_BASIC,
                            MODE_ACTION_ADD_ADVANCED,
                            MODE_ACTION_EDIT_JSON,
                            MODE_ACTION_BACK,
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="modes_menu", data_schema=schema)

    async def async_step_mode_basic(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            self._modes.append(
                {
                    "name": user_input[CONF_MODE_NAME],
                    "description": user_input[CONF_MODE_DESCRIPTION],
                    "capabilities": {
                        "lighting": user_input[CONF_MODE_HAS_LIGHTING],
                        "hvac": user_input[CONF_MODE_HAS_HVAC],
                        "media": user_input[CONF_MODE_HAS_MEDIA],
                    },
                    "kind": "basic",
                }
            )
            self._options[CONF_MODES] = self._modes
            return await self.async_step_modes_menu()

        schema = vol.Schema(
            {
                vol.Required(CONF_MODE_NAME): str,
                vol.Required(CONF_MODE_DESCRIPTION): str,
                vol.Required(
                    CONF_MODE_HAS_LIGHTING, default=True
                ): selector.BooleanSelector(),
                vol.Required(
                    CONF_MODE_HAS_HVAC, default=True
                ): selector.BooleanSelector(),
                vol.Required(
                    CONF_MODE_HAS_MEDIA, default=True
                ): selector.BooleanSelector(),
            }
        )
        return self.async_show_form(step_id="mode_basic", data_schema=schema)

    async def async_step_mode_advanced(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            try:
                payload = parse_json_payload(user_input[CONF_MODE_ADVANCED_JSON])
                if not isinstance(payload, dict):
                    raise TypeError("mode json must be an object")
                self._modes.append(payload)
            except (TypeError, ValueError, json.JSONDecodeError):
                return self.async_show_form(
                    step_id="mode_advanced",
                    data_schema=self._mode_advanced_schema(
                        default=user_input.get(CONF_MODE_ADVANCED_JSON, "")
                    ),
                    errors={CONF_MODE_ADVANCED_JSON: "invalid_json"},
                )
            self._options[CONF_MODES] = self._modes
            return await self.async_step_modes_menu()

        return self.async_show_form(
            step_id="mode_advanced", data_schema=self._mode_advanced_schema()
        )

    async def async_step_modes_json(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            try:
                validate_json_text(user_input[CONF_ADVANCED_MODES_JSON])
            except (ValueError, json.JSONDecodeError):
                return self.async_show_form(
                    step_id="modes_json",
                    data_schema=self._modes_json_schema(
                        default=user_input.get(CONF_ADVANCED_MODES_JSON, "")
                    ),
                    errors={CONF_ADVANCED_MODES_JSON: "invalid_json"},
                )
            parsed = parse_json_payload(user_input[CONF_ADVANCED_MODES_JSON])
            if parsed is None:
                self._modes = []
            elif isinstance(parsed, list):
                self._modes = parsed
            else:
                return self.async_show_form(
                    step_id="modes_json",
                    data_schema=self._modes_json_schema(
                        default=user_input.get(CONF_ADVANCED_MODES_JSON, "")
                    ),
                    errors={CONF_ADVANCED_MODES_JSON: "invalid_json"},
                )
            self._options[CONF_MODES] = self._modes
            return await self.async_step_modes_menu()

        return self.async_show_form(
            step_id="modes_json", data_schema=self._modes_json_schema()
        )

    async def async_step_modifiers_menu(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            action = user_input[CONF_MODIFIER_ACTION]
            if action == MODIFIER_ACTION_ADD_BASIC:
                return await self.async_step_modifier_basic()
            if action == MODIFIER_ACTION_ADD_ADVANCED:
                return await self.async_step_modifier_advanced()
            if action == MODIFIER_ACTION_EDIT_JSON:
                return await self.async_step_modifiers_json()
            return await self.async_step_menu()

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_MODIFIER_ACTION, default=MODIFIER_ACTION_ADD_BASIC
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=[
                            MODIFIER_ACTION_ADD_BASIC,
                            MODIFIER_ACTION_ADD_ADVANCED,
                            MODIFIER_ACTION_EDIT_JSON,
                            MODIFIER_ACTION_BACK,
                        ],
                        mode=selector.SelectSelectorMode.DROPDOWN,
                    )
                ),
            }
        )
        return self.async_show_form(step_id="modifiers_menu", data_schema=schema)

    async def async_step_modifier_basic(self, user_input: dict[str, Any] | None = None):
        mode_options = normalize_mode_names(self._modes)
        if user_input is not None:
            overrides_raw = user_input.get(CONF_MODIFIER_OVERRIDES_JSON, "").strip()
            try:
                overrides = json.loads(overrides_raw) if overrides_raw else {}
                if not isinstance(overrides, dict):
                    raise TypeError("overrides must be a JSON object")
            except (TypeError, json.JSONDecodeError):
                return self.async_show_form(
                    step_id="modifier_basic",
                    data_schema=self._modifier_basic_schema(
                        mode_options, default_overrides=overrides_raw
                    ),
                    errors={CONF_MODIFIER_OVERRIDES_JSON: "invalid_json"},
                )
            self._modifiers.append(
                {
                    "name": user_input[CONF_MODIFIER_NAME],
                    "base_mode": user_input[CONF_MODIFIER_BASE_MODE],
                    "description": user_input[CONF_MODIFIER_DESCRIPTION],
                    "overrides": overrides,
                    "kind": "basic",
                }
            )
            self._options[CONF_MODIFIERS] = self._modifiers
            return await self.async_step_modifiers_menu()

        return self.async_show_form(
            step_id="modifier_basic",
            data_schema=self._modifier_basic_schema(mode_options),
        )

    def _modifier_basic_schema(
        self, mode_options: list[str], default_overrides: str = "{}"
    ) -> vol.Schema:
        return vol.Schema(
            {
                vol.Required(CONF_MODIFIER_NAME): str,
                vol.Required(
                    CONF_MODIFIER_BASE_MODE, default=mode_options[0]
                ): selector.SelectSelector(
                    selector.SelectSelectorConfig(
                        options=mode_options, mode=selector.SelectSelectorMode.DROPDOWN
                    )
                ),
                vol.Required(CONF_MODIFIER_DESCRIPTION): str,
                vol.Optional(
                    CONF_MODIFIER_OVERRIDES_JSON, default=default_overrides
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT, multiline=True
                    )
                ),
            }
        )

    async def async_step_modifier_advanced(
        self, user_input: dict[str, Any] | None = None
    ):
        if user_input is not None:
            try:
                payload = parse_json_payload(user_input[CONF_MODIFIER_ADVANCED_JSON])
                if not isinstance(payload, dict):
                    raise TypeError("modifier json must be an object")
                self._modifiers.append(payload)
            except (TypeError, ValueError, json.JSONDecodeError):
                return self.async_show_form(
                    step_id="modifier_advanced",
                    data_schema=self._modifier_advanced_schema(
                        default=user_input.get(CONF_MODIFIER_ADVANCED_JSON, "")
                    ),
                    errors={CONF_MODIFIER_ADVANCED_JSON: "invalid_json"},
                )
            self._options[CONF_MODIFIERS] = self._modifiers
            return await self.async_step_modifiers_menu()

        return self.async_show_form(
            step_id="modifier_advanced", data_schema=self._modifier_advanced_schema()
        )

    async def async_step_modifiers_json(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            try:
                validate_json_text(user_input[CONF_ADVANCED_MODIFIERS_JSON])
                parsed = parse_json_payload(user_input[CONF_ADVANCED_MODIFIERS_JSON])
                if parsed is None:
                    self._modifiers = []
                elif isinstance(parsed, list):
                    self._modifiers = parsed
                else:
                    raise ValueError("modifiers json must be a list")
            except (ValueError, json.JSONDecodeError):
                return self.async_show_form(
                    step_id="modifiers_json",
                    data_schema=self._modifiers_json_schema(
                        default=user_input.get(CONF_ADVANCED_MODIFIERS_JSON, "")
                    ),
                    errors={CONF_ADVANCED_MODIFIERS_JSON: "invalid_json"},
                )
            self._options[CONF_MODIFIERS] = self._modifiers
            return await self.async_step_modifiers_menu()

        return self.async_show_form(
            step_id="modifiers_json", data_schema=self._modifiers_json_schema()
        )

    def _rooms_json_schema(self, default: str = "") -> vol.Schema:
        return vol.Schema(
            {
                vol.Optional(
                    CONF_ADVANCED_ROOMS_JSON,
                    default=default
                    or json.dumps(self._rooms, indent=2, ensure_ascii=False),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT, multiline=True
                    )
                ),
            }
        )

    def _room_advanced_schema(self, default: str = "") -> vol.Schema:
        return vol.Schema(
            {
                vol.Optional(
                    CONF_ROOM_ADVANCED_JSON, default=default
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT, multiline=True
                    )
                ),
            }
        )

    def _modes_json_schema(self, default: str = "") -> vol.Schema:
        return vol.Schema(
            {
                vol.Optional(
                    CONF_ADVANCED_MODES_JSON,
                    default=default
                    or json.dumps(self._modes, indent=2, ensure_ascii=False),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT, multiline=True
                    )
                ),
            }
        )

    def _mode_advanced_schema(self, default: str = "") -> vol.Schema:
        return vol.Schema(
            {
                vol.Optional(
                    CONF_MODE_ADVANCED_JSON, default=default
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT, multiline=True
                    )
                ),
            }
        )

    def _modifiers_json_schema(self, default: str = "") -> vol.Schema:
        return vol.Schema(
            {
                vol.Optional(
                    CONF_ADVANCED_MODIFIERS_JSON,
                    default=default
                    or json.dumps(self._modifiers, indent=2, ensure_ascii=False),
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT, multiline=True
                    )
                ),
            }
        )

    def _modifier_advanced_schema(self, default: str = "") -> vol.Schema:
        return vol.Schema(
            {
                vol.Optional(
                    CONF_MODIFIER_ADVANCED_JSON, default=default
                ): selector.TextSelector(
                    selector.TextSelectorConfig(
                        type=selector.TextSelectorType.TEXT, multiline=True
                    )
                ),
            }
        )

    async def async_step_done(self):
        self._options[CONF_ROOMS] = self._rooms
        self._options[CONF_MODES] = self._modes
        self._options[CONF_MODIFIERS] = self._modifiers
        return self.async_create_entry(title="", data=self._options)
