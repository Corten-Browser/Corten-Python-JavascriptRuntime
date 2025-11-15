"""Test configuration for json_extensions"""

import sys
from pathlib import Path

# Add component root to path so we can import json_extensions
component_root = Path(__file__).parent.parent
components_dir = component_root.parent
sys.path.insert(0, str(components_dir))
