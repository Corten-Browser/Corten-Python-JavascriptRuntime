"""
Pytest configuration for shared_types tests.
Adds the component root to Python path for imports.
"""
import sys
from pathlib import Path

# Add component root to path for 'from src.x import' style imports
component_root = Path(__file__).parent.parent
if str(component_root) not in sys.path:
    sys.path.insert(0, str(component_root))
