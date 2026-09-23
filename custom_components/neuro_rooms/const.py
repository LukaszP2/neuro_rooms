"""Constants for Neuro Rooms."""

DOMAIN = "neuro_rooms"
EVENT_DESIRED_CHANGED = "neuro_rooms_desired_changed"

# ---------------------------------------------------------------------------
# Engine / entry-level config
# ---------------------------------------------------------------------------
CONF_ENGINE_NAME = "engine_name"
CONF_AUTO_DISCOVERY = "auto_discovery"
CONF_DEFAULT_LANGUAGE = "default_language"
DEFAULT_ENGINE_NAME = "Engine Neuro Rooms"
DEFAULT_LANGUAGE = "en"

# ---------------------------------------------------------------------------
# Generic shared keys
# ---------------------------------------------------------------------------
CONF_ID = "id"
CONF_NAME = "name"
CONF_SOURCE = "source"

# ---------------------------------------------------------------------------
# Top-level list keys
# ---------------------------------------------------------------------------
CONF_ROOMS = "rooms"
CONF_MODES = "modes"
CONF_MODIFIERS = "modifiers"
CONF_PROFILES = "profiles"

# ---------------------------------------------------------------------------
# Room config keys  (used by rooms.py, options_flow.py, config_flow.py)
# ---------------------------------------------------------------------------
CONF_ROOM_NAME = "room_name"
CONF_ROOM_AREA_ID = "room_area_id"
CONF_ROOM_MODE = "room_mode"
CONF_ROOM_MODIFIER = "room_modifier"
CONF_ROOM_PRESENCE_ENTITY = "presence_entity"
CONF_ROOM_HAS_LIGHTING = "room_has_lighting"
CONF_ROOM_HAS_HVAC = "room_has_hvac"
CONF_ROOM_HAS_MEDIA = "room_has_media"
CONF_ROOM_ADVANCED_JSON = "room_advanced_json"
CONF_ROOM_ACTION = "room_action"

# config_flow (legacy simple flow) keys
CONF_MODE = "mode"
CONF_MODIFIER = "modifier"
CONF_AREA_NAME = "area_name"

# ---------------------------------------------------------------------------
# Mode config keys (used by options_flow.py, config_flow.py)
# ---------------------------------------------------------------------------
CONF_MODE_NAME = "mode_name"
CONF_MODE_DESCRIPTION = "mode_description"
CONF_MODE_LIGHTING = "mode_lighting"  # legacy (config_flow)
CONF_MODE_HVAC = "mode_hvac"  # legacy (config_flow)
CONF_MODE_MEDIA = "mode_media"  # legacy (config_flow)
CONF_MODE_HAS_LIGHTING = "mode_has_lighting"
CONF_MODE_HAS_HVAC = "mode_has_hvac"
CONF_MODE_HAS_MEDIA = "mode_has_media"
CONF_MODE_ADVANCED_JSON = "mode_advanced_json"
CONF_MODE_ACTION = "mode_action"

# ---------------------------------------------------------------------------
# Modifier config keys
# ---------------------------------------------------------------------------
CONF_MODIFIER_NAME = "modifier_name"
CONF_MODIFIER_BASE_MODE = "modifier_base_mode"
CONF_MODIFIER_PRIORITY = "modifier_priority"
CONF_MODIFIER_DESCRIPTION = "modifier_description"
CONF_MODIFIER_OVERRIDES_JSON = "modifier_overrides_json"
CONF_MODIFIER_ADVANCED_JSON = "modifier_advanced_json"
CONF_MODIFIER_ACTION = "modifier_action"

# ---------------------------------------------------------------------------
# Advanced / bulk JSON edit keys
# ---------------------------------------------------------------------------
CONF_ADVANCED_ROOMS_JSON = "advanced_rooms_json"
CONF_ADVANCED_MODES_JSON = "advanced_modes_json"
CONF_ADVANCED_MODIFIERS_JSON = "advanced_modifiers_json"

# ---------------------------------------------------------------------------
# Capability keys  (used by modes.py)
# ---------------------------------------------------------------------------
CAPABILITY_LIGHTING = "lighting"
CAPABILITY_HVAC = "hvac"
CAPABILITY_MEDIA = "media"

# ---------------------------------------------------------------------------
# Action value constants — Room
# ---------------------------------------------------------------------------
ROOM_ACTION_ADD_BASIC = "add_basic"
ROOM_ACTION_ADD_ADVANCED = "add_advanced"
ROOM_ACTION_EDIT_JSON = "edit_json"
ROOM_ACTION_DONE = "done"
ROOM_ACTION_BACK = "back"

# ---------------------------------------------------------------------------
# Action value constants — Mode
# ---------------------------------------------------------------------------
MODE_ACTION_ADD_BASIC = "add_basic"
MODE_ACTION_ADD_ADVANCED = "add_advanced"
MODE_ACTION_EDIT_JSON = "edit_json"
MODE_ACTION_DONE = "done"
MODE_ACTION_BACK = "back"

# ---------------------------------------------------------------------------
# Action value constants — Modifier
# ---------------------------------------------------------------------------
MODIFIER_ACTION_ADD_BASIC = "add_basic"
MODIFIER_ACTION_ADD_ADVANCED = "add_advanced"
MODIFIER_ACTION_EDIT_JSON = "edit_json"
MODIFIER_ACTION_DONE = "done"
MODIFIER_ACTION_BACK = "back"

# ---------------------------------------------------------------------------
# Discovery
# ---------------------------------------------------------------------------
DEFAULT_ROOM_MODES = [
    "room",
    "living_room",
    "bedroom",
    "hallway",
    "bathroom",
    "office",
    "kitchen",
]
