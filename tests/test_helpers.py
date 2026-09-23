import pytest
from custom_components.neuro_rooms.helpers import slugify, remove_by_id, replace_by_id

def test_slugify():
    assert slugify("My Room") == "my_room"
    assert slugify("Living Room (1st floor)") == "living_room_1st_floor"
    assert slugify("---Test---") == "test"

def test_remove_by_id():
    items = [{"id": "room1", "name": "Room 1"}, {"id": "room2", "name": "Room 2"}]
    result = remove_by_id(items, "room1")
    assert len(result) == 1
    assert result[0]["id"] == "room2"

def test_replace_by_id():
    items = [{"id": "room1", "name": "Room 1"}, {"id": "room2", "name": "Room 2"}]
    new_item = {"id": "room1", "name": "Updated Room 1"}
    result = replace_by_id(items, new_item)
    assert len(result) == 2
    assert result[1]["name"] == "Updated Room 1"
