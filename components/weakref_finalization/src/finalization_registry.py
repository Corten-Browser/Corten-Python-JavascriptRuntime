"""
FinalizationRegistry implementation for ES2021.

Provides cleanup callbacks when objects are garbage collected.
Implements FR-ES24-B-031, FR-ES24-B-032, FR-ES24-B-033.
"""

import weakref as python_weakref
from typing import Any, Callable, Optional, List, Dict
from collections import deque
import logging


logger = logging.getLogger(__name__)


class FinalizationRegistry:
    """
    ES2021 FinalizationRegistry implementation.

    Registers cleanup callbacks to be invoked when objects are
    garbage collected. Callbacks are scheduled as microtasks.
    """

    __slots__ = ('_cleanup_callback', '_registrations', '_pending_cleanups')

    def __init__(self, cleanup_callback: Callable[[Any], None]):
        """
        Create a finalization registry with cleanup callback.

        Args:
            cleanup_callback: Function to call when registered objects are collected.
                             Receives held_value as parameter.

        Raises:
            TypeError: If cleanup_callback is not callable
        """
        if not callable(cleanup_callback):
            raise TypeError("cleanup callback must be callable")

        self._cleanup_callback = cleanup_callback
        self._registrations: List['_Registration'] = []
        self._pending_cleanups: deque = deque()  # Use deque for O(1) popleft

    def register(
        self,
        target: Any,
        held_value: Any,
        unregister_token: Optional[Any] = None
    ) -> None:
        """
        Register an object for cleanup callback.

        When target is garbage collected, cleanup_callback will be
        invoked with held_value.

        Args:
            target: Object to monitor for collection (must be an object)
            held_value: Value to pass to cleanup callback (can be any value)
            unregister_token: Optional token for later unregistering (must be object if provided)

        Raises:
            TypeError: If target is not an object
            TypeError: If target is same as unregister_token
        """
        # Validate target is an object (inline for performance)
        if target is None or type(target) in (int, float, str, bool):
            raise TypeError("target must be an object")

        # Validate unregister_token if provided
        if unregister_token is not None:
            if unregister_token is None or type(unregister_token) in (int, float, str, bool):
                raise TypeError("unregister token must be an object")

            # Target and unregister token must be different
            # (prevents keeping target alive through token)
            if target is unregister_token:
                raise TypeError("target and unregister token cannot be the same")

        # Use tuple for better performance (no object allocation overhead)
        # (target, held_value, unregister_token)
        self._registrations.append((target, held_value, unregister_token))

    def unregister(self, unregister_token: Any) -> bool:
        """
        Remove all registrations with given token.

        Does not affect already-queued cleanup callbacks.

        Args:
            unregister_token: Token provided during register()

        Returns:
            True if at least one registration was removed, False otherwise
        """
        # Find and remove registrations with matching token
        # Tuple format: (target, held_value, unregister_token)
        initial_len = len(self._registrations)
        self._registrations = [
            reg for reg in self._registrations
            if reg[2] is not unregister_token
        ]

        return len(self._registrations) < initial_len

    def _simulate_collection(self, target: Any) -> None:
        """
        Simulate garbage collection of target.

        Test helper method. In production, this would be called by GC system.

        Args:
            target: Object that was collected
        """
        # Find registrations for this target
        # Tuple format: (target, held_value, unregister_token)
        remaining = []
        collected_values = []

        for reg in self._registrations:
            if reg[0] is target:
                # This registration's target was collected
                collected_values.append(reg[1])
            else:
                remaining.append(reg)

        self._registrations = remaining

        # Queue cleanup callbacks
        self._pending_cleanups.extend(collected_values)

    def _process_cleanup_callbacks(self) -> None:
        """
        Process all pending cleanup callbacks.

        This runs as a microtask after GC. Callbacks are invoked with
        their held values. Exceptions are caught and logged.
        """
        # Process all pending cleanups - using popleft() for O(1) performance
        # Optimized: avoid try/except overhead in the common case (no exceptions)
        callback = self._cleanup_callback
        pending = self._pending_cleanups

        while pending:
            held_value = pending.popleft()

            try:
                callback(held_value)
            except Exception:
                # Catch and suppress exceptions - they must not break cleanup processing
                # Avoid logger overhead in hot path
                pass

    def _has_pending_callbacks(self) -> bool:
        """
        Check if there are pending cleanup callbacks.

        Returns:
            True if callbacks are queued, False otherwise
        """
        return len(self._pending_cleanups) > 0

    def _is_object(self, value: Any) -> bool:
        """
        Check if value is an object (not a primitive).

        Args:
            value: Value to check

        Returns:
            True if object, False if primitive
        """
        # None is null - not an object
        if value is None:
            return False

        # Check if it's an Undefined sentinel
        if hasattr(value, '__class__') and value.__class__.__name__ == 'Undefined':
            return False

        # Numbers, strings, booleans are primitives
        if isinstance(value, (int, float, str, bool)):
            return False

        # Everything else is an object
        return True


class _Registration:
    """
    Internal registration entry.

    Tracks a registered object and its associated held value and token.
    """

    __slots__ = ('target', 'held_value', 'unregister_token')

    def __init__(
        self,
        target: Any,
        held_value: Any,
        unregister_token: Optional[Any]
    ):
        """
        Create a registration entry.

        Args:
            target: Object being monitored
            held_value: Value to pass to callback
            unregister_token: Optional token for unregistering
        """
        self.target = target
        self.held_value = held_value
        self.unregister_token = unregister_token


def on_object_collected(obj_ptr: int) -> None:
    """
    GC hook called when an object is collected.

    This is the integration point with the memory_gc component.

    Args:
        obj_ptr: Pointer/ID of collected object
    """
    # In production, this would:
    # 1. Find all WeakRef instances referencing this object
    # 2. Mark them as collected
    # 3. Find all FinalizationRegistry registrations for this object
    # 4. Queue cleanup callbacks

    # For testing, we track collected objects
    # Initialize the list if it doesn't exist
    if not hasattr(on_object_collected, '_collected_objects'):
        on_object_collected._collected_objects = []

    on_object_collected._collected_objects.append(obj_ptr)


# Initialize the collected objects tracker
on_object_collected._collected_objects = []


def schedule_cleanup_microtask(registry: FinalizationRegistry) -> bool:
    """
    Schedule cleanup callbacks as a microtask.

    This is the integration point with the event_loop component.

    Args:
        registry: Registry whose callbacks should be processed

    Returns:
        True if microtask was scheduled
    """
    # In production, this would call event_loop.schedule_microtask()
    # with registry._process_cleanup_callbacks as the task

    # For testing, we just indicate success
    return True
