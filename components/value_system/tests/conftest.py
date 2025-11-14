"""
Pytest configuration for value_system component tests.

This module configures the Python path to allow imports from the
component source code and from other components.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

# Add component src to Python path for direct imports
component_src = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(component_src))
