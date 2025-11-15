"""Pytest configuration for atomics_extensions component."""

import sys
from pathlib import Path

# Add typed_arrays src to path for imports
typed_arrays_src = Path(__file__).parent.parent / 'typed_arrays' / 'src'
sys.path.insert(0, str(typed_arrays_src))
