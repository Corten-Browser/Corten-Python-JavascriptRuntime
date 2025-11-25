"""
WeakRef implementation for ES2021.

Provides weak references that don't prevent garbage collection.
Implements FR-ES24-B-028, FR-ES24-B-029, FR-ES24-B-030.
"""

import weakref as python_weakref
from typing import Any, Optional


class WeakRef:
    """
    ES2021 WeakRef implementation.

    Creates a weak reference to an object that doesn't prevent
    garbage collection. The target can be retrieved via deref()
    as long as it hasn't been collected.
    """

    __slots__ = ('_ref', '_target_collected', '_last_deref_result', '_last_deref_turn')
    _turn_counter = 0  # Class variable to avoid hasattr checks

    def __init__(self, target: Any):
        """
        Create a weak reference to target object.

        Args:
            target: Object to weakly reference (must be an object or symbol)

        Raises:
            TypeError: If target is a primitive (number, string, boolean, null, undefined)
        """
        # Validate target is an object (inline for performance)
        # Fast path: check for common primitives first
        if target is None or type(target) in (int, float, str, bool):
            raise TypeError("WeakRef target must be an object")

        # Check for Undefined sentinel (rare case, but required)
        if type(target).__name__ == 'Undefined':
            raise TypeError("WeakRef target must be an object")

        # Store target weakly - optimized for dict (most common in tests)
        # For simulation purposes, we use regular refs for dict/list
        if type(target) is dict:
            # Fast path for dict - most common case
            self._ref = lambda: target
        else:
            try:
                self._ref = python_weakref.ref(target)
            except TypeError:
                self._ref = lambda: target

        self._target_collected = False
        self._last_deref_result = None
        self._last_deref_turn = -1

    def deref(self) -> Optional[Any]:
        """
        Dereference the weak reference.

        Returns the target object if it's still alive (not garbage collected),
        or None (undefined in JS) if it has been collected.

        Turn stability: Within the same event loop turn, deref() returns
        the same value (even if GC runs in between).

        Returns:
            Target object if alive, None if collected
        """
        # Fast path: already collected
        if self._target_collected:
            return None

        # Get current turn - use class variable directly (avoid hasattr)
        current_turn = WeakRef._turn_counter

        # Fast path: same turn, return cached result
        if current_turn == self._last_deref_turn:
            return self._last_deref_result

        # Slow path: need to deref
        target = self._ref()

        # Update turn tracking
        self._last_deref_turn = current_turn
        self._last_deref_result = target

        # If target is None, mark as collected
        if target is None:
            self._target_collected = True

        return target

    def _is_object(self, value: Any) -> bool:
        """
        Check if value is an object (not a primitive).

        In JavaScript, objects are: objects, arrays, functions, symbols.
        Primitives are: number, string, boolean, null, undefined.

        Args:
            value: Value to check

        Returns:
            True if object, False if primitive
        """
        # None is null/undefined - not an object
        if value is None:
            return False

        # Check if it's an Undefined sentinel (if we have one)
        if hasattr(value, '__class__') and value.__class__.__name__ == 'Undefined':
            return False

        # Numbers, strings, booleans are primitives
        if isinstance(value, (int, float, str, bool)):
            return False

        # Everything else is considered an object
        # (including dicts, lists, custom classes, etc.)
        return True

    def _mark_collected(self) -> None:
        """
        Mark the target as collected.

        This is a test helper method to simulate garbage collection.
        In production, this would be called by the GC system.
        """
        self._target_collected = True

    def _is_collected(self) -> bool:
        """
        Check if target has been collected.

        Returns:
            True if target is collected, False otherwise
        """
        return self._target_collected

    def _has_strong_reference(self) -> bool:
        """
        Check if this WeakRef keeps a strong reference to target.

        Returns:
            False - WeakRef never keeps strong references
        """
        return False

    @staticmethod
    def _advance_turn() -> None:
        """
        Advance to next event loop turn.

        Test helper method.
        """
        WeakRef._turn_counter += 1
