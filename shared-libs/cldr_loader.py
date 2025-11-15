"""
CLDR Data Loader

Utilities for loading Unicode CLDR (Common Locale Data Repository) data
for Intl API components.
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional, List

class CLDRLoader:
    """Loader for CLDR locale data."""

    def __init__(self, data_dir: Optional[Path] = None):
        """
        Initialize CLDR loader.

        Args:
            data_dir: Directory containing CLDR JSON data
                     (defaults to shared-libs/cldr-data)
        """
        if data_dir is None:
            # Default to shared-libs/cldr-data relative to this file
            base_dir = Path(__file__).parent
            data_dir = base_dir / "cldr-data"

        self.data_dir = Path(data_dir)
        self._cache: Dict[str, Dict[str, Any]] = {}

    def load_locale_data(self, locale: str, category: str) -> Dict[str, Any]:
        """
        Load CLDR data for a specific locale and category.

        Args:
            locale: BCP 47 locale identifier (e.g., "en-US")
            category: Data category (e.g., "dates", "numbers", "currencies")

        Returns:
            Dictionary containing locale data
        """
        cache_key = f"{locale}:{category}"

        # Check cache
        if cache_key in self._cache:
            return self._cache[cache_key]

        # Load from file
        file_path = self.data_dir / locale / f"{category}.json"

        if not file_path.exists():
            # Try fallback to language-only locale
            lang = locale.split("-")[0]
            fallback_path = self.data_dir / lang / f"{category}.json"

            if not fallback_path.exists():
                # Final fallback to en-US
                fallback_path = self.data_dir / "en-US" / f"{category}.json"

                if not fallback_path.exists():
                    # Return empty data
                    return {}

            file_path = fallback_path

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Cache and return
            self._cache[cache_key] = data
            return data
        except (IOError, json.JSONDecodeError):
            return {}

    def get_available_locales(self) -> List[str]:
        """
        Get list of available locales.

        Returns:
            List of locale identifiers
        """
        if not self.data_dir.exists():
            return []

        locales = []
        for item in self.data_dir.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                locales.append(item.name)

        return sorted(locales)

    def clear_cache(self):
        """Clear the data cache."""
        self._cache.clear()


# Singleton instance
_loader = None

def get_cldr_loader() -> CLDRLoader:
    """Get singleton CLDR loader instance."""
    global _loader
    if _loader is None:
        _loader = CLDRLoader()
    return _loader
