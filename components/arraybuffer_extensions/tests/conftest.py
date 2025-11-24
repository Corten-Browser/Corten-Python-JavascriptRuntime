"""
Pytest configuration for arraybuffer_extensions tests.
Adds the src directory to Python path for imports.
"""

import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))
