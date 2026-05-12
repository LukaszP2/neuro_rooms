"""Main Neuro Rooms runtime engine."""

from .room_controller import RoomController


class NeuroRoomsEngine:
    """NR runtime engine."""

    def __init__(self, hass, config_entry):
        self.hass = hass
        self.config_entry = config_entry
        self.rooms = {}
