"""
Root pytest configuration for Corten-Python-JavascriptRuntime.
Sets up Python path for all component imports.
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Add all component src directories to path
components_dir = project_root / "components"
if components_dir.exists():
    for component in components_dir.iterdir():
        if component.is_dir():
            src_dir = component / "src"
            if src_dir.exists() and str(src_dir) not in sys.path:
                sys.path.insert(0, str(src_dir))
