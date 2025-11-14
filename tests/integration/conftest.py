"""
Pytest fixtures for cross-component integration testing.

This module provides fixtures for integration testing of the JavaScript runtime.
Adds project root to sys.path to enable component imports.
"""

import sys
from pathlib import Path
import pytest

# Add project root to sys.path for component imports
project_root = Path(__file__).parent.parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))


@pytest.fixture(scope="session")
def get_project_root():
    """Path to project root directory."""
    return project_root
