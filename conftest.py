"""
Root pytest configuration.
Adds the project root to Python path for 'from components.x.src import' style imports.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))
