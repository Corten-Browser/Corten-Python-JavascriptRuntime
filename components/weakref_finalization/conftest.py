"""Pytest configuration for weakref_finalization tests."""

import sys
from pathlib import Path

# Add components directory to Python path so we can import weakref_finalization
component_root = Path(__file__).parent
components_dir = component_root.parent
sys.path.insert(0, str(components_dir))
