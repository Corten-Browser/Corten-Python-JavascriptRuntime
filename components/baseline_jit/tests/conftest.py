"""Pytest configuration for baseline_jit tests."""

import sys
from pathlib import Path

# Add project root to path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add component root to path
component_root = Path(__file__).parent.parent
sys.path.insert(0, str(component_root))
