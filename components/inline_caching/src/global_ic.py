"""
Global Variable Inline Cache for optimized global access.

Provides GlobalIC for fast global variable load/store.
"""
from typing import Any, Dict
from .inline_cache import InlineCache


class GlobalIC(InlineCache):
    """
    Inline cache for global variable access.

    Optimizes global variable loads and stores by caching offsets.

    Example:
        ic = GlobalIC()
        value = ic.load_global("globalVar")
        ic.store_global("globalVar", newValue)
    """

    def __init__(self, global_dict: Dict[str, Any] = None):
        """
        Initialize global IC.

        Args:
            global_dict: Global variable dictionary (default: empty)
        """
        super().__init__("global")

        # Global variable dictionary
        self._globals = global_dict or {}

        # Statistics
        self._load_hits = 0
        self._load_misses = 0
        self._store_hits = 0
        self._store_misses = 0

        # Cached global slots (name -> value cache)
        self._cached_globals = {}

    def load_global(self, name: str) -> Any:
        """
        Load global variable with IC.

        Args:
            name: Global variable name

        Returns:
            Global variable value (or None if undefined)

        Performance:
            - Cache hit: O(1) - dict lookup in cached_globals
            - Cache miss: O(1) - dict lookup in globals + cache update
        """
        # Check cache first
        if name in self._cached_globals:
            # Cache hit
            self._load_hits += 1
            return self._cached_globals[name]
        else:
            # Cache miss
            self._load_misses += 1

            # Load from globals
            value = self._globals.get(name)

            # Update cache
            self._cached_globals[name] = value

            return value

    def store_global(self, name: str, value: Any) -> None:
        """
        Store global variable with IC.

        Args:
            name: Global variable name
            value: Value to store

        Performance:
            - O(1) - dict insert + cache update
        """
        # Update globals
        self._globals[name] = value

        # Update cache
        self._cached_globals[name] = value

        self._store_hits += 1

    def invalidate_global(self, name: str) -> None:
        """
        Invalidate cached global variable.

        Args:
            name: Global variable name to invalidate
        """
        if name in self._cached_globals:
            del self._cached_globals[name]

    def get_statistics(self) -> dict:
        """
        Get IC statistics.

        Returns:
            Dict with load/store hits, misses, and hit rates
        """
        load_total = self._load_hits + self._load_misses
        load_hit_rate = self._load_hits / load_total if load_total > 0 else 0.0

        return {
            'load_hits': self._load_hits,
            'load_misses': self._load_misses,
            'load_total': load_total,
            'load_hit_rate': load_hit_rate,
            'store_count': self._store_hits,
            'cached_globals': len(self._cached_globals),
            'state': str(self.get_state())
        }
