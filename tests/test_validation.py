import pytest
import json
from custom_components.neuro_rooms.validation import validate_json_text

def test_validate_json_text_valid():
    validate_json_text('{"key": "value"}')
    validate_json_text('[]')

def test_validate_json_text_empty():
    validate_json_text('   ')
    validate_json_text('')

def test_validate_json_text_invalid():
    with pytest.raises(json.JSONDecodeError):
        validate_json_text('{"key": "value" ')

