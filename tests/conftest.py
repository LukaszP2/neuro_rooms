import sys
from unittest.mock import MagicMock

# Mock homeassistant modules
sys.modules['homeassistant'] = MagicMock()
sys.modules['homeassistant.core'] = MagicMock()
sys.modules['homeassistant.config_entries'] = MagicMock()
sys.modules['homeassistant.helpers'] = MagicMock()
sys.modules['homeassistant.helpers.area_registry'] = MagicMock()
sys.modules['homeassistant.helpers.selector'] = MagicMock()
sys.modules['homeassistant.const'] = MagicMock()

