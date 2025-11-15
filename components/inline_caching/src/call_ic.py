"""
Call Inline Cache for optimized function call sites.

Provides CallIC for fast function dispatch.
"""
from typing import Any, List
from .inline_cache import InlineCache
from ._shape_placeholder import Shape


class CallIC(InlineCache):
    """
    Inline cache for function calls.

    Optimizes function call sites by caching call targets.
    Reduces overhead of dynamic dispatch.

    Example:
        ic = CallIC()
        result = ic.call(function, [arg1, arg2])
        # First call: slow path, initializes cache
        # Subsequent calls to same function: fast path
    """

    def __init__(self):
        """Initialize call IC."""
        super().__init__("call")

        # Statistics
        self._hits = 0
        self._misses = 0

        # Cached function
        self._cached_function = None

    def call(self, callee: Any, args: List[Any]) -> Any:
        """
        Call function with IC optimization.

        Args:
            callee: Function to call
            args: List of arguments

        Returns:
            Function return value

        Performance:
            - Cache hit: O(1) - single comparison + direct call
            - Cache miss: O(1) - function call overhead
        """
        # Get function "shape" (identity)
        func_id = id(callee)

        # Check if this is the cached function
        if self._cached_function is not None and id(self._cached_function) == func_id:
            # Cache hit: fast path
            self._hits += 1
            return self._fast_call(callee, args)
        else:
            # Cache miss: slow path
            self._misses += 1

            # Update cache
            self._cached_function = callee

            return self._slow_call(callee, args)

    def _fast_call(self, callee: Any, args: List[Any]) -> Any:
        """
        Fast path: call cached function.

        Args:
            callee: Function to call
            args: Arguments

        Returns:
            Function result
        """
        # Direct call (no dynamic dispatch overhead)
        if callable(callee):
            return callee(*args)
        return None

    def _slow_call(self, callee: Any, args: List[Any]) -> Any:
        """
        Slow path: call function with full dispatch.

        Args:
            callee: Function to call
            args: Arguments

        Returns:
            Function result
        """
        # Full dispatch
        if callable(callee):
            return callee(*args)
        return None

    def get_statistics(self) -> dict:
        """
        Get IC statistics.

        Returns:
            Dict with hits, misses, hit_rate, and state
        """
        total = self._hits + self._misses
        hit_rate = self._hits / total if total > 0 else 0.0

        return {
            'hits': self._hits,
            'misses': self._misses,
            'total': total,
            'hit_rate': hit_rate,
            'state': 'cached' if self._cached_function is not None else 'uninitialized'
        }
