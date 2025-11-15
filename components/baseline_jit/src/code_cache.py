"""
Code cache for compiled machine code.

Implements LRU (Least Recently Used) eviction policy when cache is full.
"""

from typing import Optional, Dict
from collections import OrderedDict


class CodeCache:
    """
    LRU cache for compiled machine code.

    Stores compiled code with automatic eviction when size limit is reached.
    Uses LRU policy: least recently used code is evicted first.

    Attributes:
        max_size: Maximum cache size in bytes (default: 10MB)

    Example:
        >>> cache = CodeCache(max_size=10 * 1024 * 1024)
        >>> cache.insert(function_id=42, code=compiled_code)
        >>> result = cache.lookup(function_id=42)
    """

    def __init__(self, max_size: int = 10485760):
        """
        Initialize code cache.

        Args:
            max_size: Maximum cache size in bytes (default: 10MB)
        """
        self.max_size = max_size
        self._cache: OrderedDict = OrderedDict()  # function_id -> CompiledCode
        self._current_size = 0

    def insert(self, function_id: int, code) -> None:
        """
        Insert compiled code into cache.

        If cache is full, evicts least recently used entries.

        Args:
            function_id: Unique function identifier
            code: CompiledCode to cache

        Example:
            >>> cache = CodeCache()
            >>> cache.insert(42, compiled_code)
        """
        # If already exists, remove old version
        if function_id in self._cache:
            old_code = self._cache[function_id]
            self._current_size -= old_code.size
            del self._cache[function_id]

        # Evict entries if needed to make space
        while self._current_size + code.size > self.max_size and self._cache:
            self._evict_one()

        # Insert new code
        self._cache[function_id] = code
        self._current_size += code.size

    def lookup(self, function_id: int):
        """
        Look up compiled code by function ID.

        Updates LRU order (marks as recently used).

        Args:
            function_id: Function ID to look up

        Returns:
            CompiledCode if found, None otherwise

        Example:
            >>> cache = CodeCache()
            >>> cache.insert(42, code)
            >>> result = cache.lookup(42)
            >>> result is not None
            True
        """
        if function_id not in self._cache:
            return None

        # Move to end (mark as recently used)
        code = self._cache.pop(function_id)
        self._cache[function_id] = code
        return code

    def evict(self) -> int:
        """
        Manually evict one entry from cache.

        Evicts least recently used entry.

        Returns:
            Number of bytes freed

        Example:
            >>> cache = CodeCache()
            >>> cache.insert(1, code)
            >>> freed = cache.evict()
            >>> freed > 0
            True
        """
        if not self._cache:
            return 0

        return self._evict_one()

    def _evict_one(self) -> int:
        """
        Evict least recently used entry.

        Returns:
            Number of bytes freed
        """
        # Remove first item (least recently used)
        function_id, code = self._cache.popitem(last=False)
        self._current_size -= code.size
        return code.size

    def clear(self) -> None:
        """Clear all entries from cache."""
        self._cache.clear()
        self._current_size = 0

    @property
    def size(self) -> int:
        """Get current cache size in bytes."""
        return self._current_size

    @property
    def count(self) -> int:
        """Get number of entries in cache."""
        return len(self._cache)
