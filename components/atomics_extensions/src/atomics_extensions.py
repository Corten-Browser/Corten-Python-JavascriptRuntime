"""
ES2024 Atomics API extensions.

Implements Atomics.waitAsync() and enhanced notify() for asynchronous waiting
on shared memory locations.
"""

import threading
import time
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add typed_arrays src to path
typed_arrays_src = Path(__file__).parent.parent.parent / 'typed_arrays' / 'src'
if str(typed_arrays_src) not in sys.path:
    sys.path.insert(0, str(typed_arrays_src))

from components.promise.src.js_promise import JSPromise
from exceptions import TypeError as JSTypeError, RangeError
from .atomics_wait_async_result import AtomicsWaitAsyncResult
from .shared_array_buffer import SharedArrayBufferIntegration


class Waiter:
    """Represents a waiter on a shared memory location.

    Attributes:
        promise: JSPromise that will resolve when notified
        resolve: Function to resolve the promise
        timeout_handle: Handle for timeout timer (if timeout specified)
        timed_out: Flag indicating if waiter has timed out
    """

    def __init__(self, promise, resolve, timeout_handle=None):
        self.promise = promise
        self.resolve = resolve
        self.timeout_handle = timeout_handle
        self.timed_out = False


class AtomicsExtensions:
    """ES2024 Atomics API extensions.

    Provides Atomics.waitAsync() for asynchronous waiting on shared memory
    locations and enhanced notify() for waking waiters.
    """

    def __init__(self):
        """Initialize Atomics extensions."""
        # Waiter queue: (buffer_id, index) -> list of Waiter objects
        self._waiters: Dict[Tuple[int, int], List[Waiter]] = {}
        self._lock = threading.Lock()
        self._sab_integration = SharedArrayBufferIntegration()

    def wait_async(self, typed_array, index, value, timeout=None, event_loop=None):
        """Asynchronous wait on shared memory location.

        Waits for a notification on the specified index of a shared Int32Array.
        Returns immediately if the current value doesn't match the expected value.
        Otherwise, returns a promise that resolves when notified or on timeout.

        Args:
            typed_array: Shared Int32Array to wait on
            index: Index in the array to wait on
            value: Expected value at the index
            timeout: Optional timeout in milliseconds
            event_loop: EventLoop for scheduling promise resolution

        Returns:
            AtomicsWaitAsyncResult: Result object with status and optional promise

        Raises:
            TypeError: If typed_array is not backed by SharedArrayBuffer
            RangeError: If index is out of bounds

        Example:
            >>> atomics = AtomicsExtensions()
            >>> result = atomics.wait_async(shared_array, 0, 0, event_loop=loop)
            >>> if result.async_status:
            ...     result.promise.then(lambda v: print(f"Notified: {v}"))
        """
        # Validate typed array is shared
        if not self._sab_integration.is_shared_array_buffer(typed_array.buffer):
            raise JSTypeError("Atomics.waitAsync can only be used with SharedArrayBuffer")

        # Validate index
        index = int(index)
        if index < 0 or index >= typed_array.length:
            raise RangeError(f"Index {index} out of bounds for array length {typed_array.length}")

        # Check current value
        current_value = typed_array[index]
        if current_value != value:
            # Value doesn't match, return immediate "not-equal"
            return AtomicsWaitAsyncResult(
                async_status=False,
                value="not-equal",
                promise=None
            )

        # Value matches, create promise for async wait
        if event_loop is None:
            raise ValueError("event_loop is required for async wait")

        # Create promise using withResolvers pattern
        deferred = JSPromise.withResolvers(event_loop)
        promise = deferred["promise"]
        resolve = deferred["resolve"]

        # Create waiter
        waiter = Waiter(promise, resolve)

        # Set up timeout if specified
        if timeout is not None:
            timeout_ms = float(timeout)

            def on_timeout():
                """Handle timeout."""
                with self._lock:
                    waiter.timed_out = True

                    # Remove from waiters queue
                    buffer_id = id(typed_array.buffer)
                    key = (buffer_id, index)

                    if key in self._waiters:
                        try:
                            self._waiters[key].remove(waiter)
                            if not self._waiters[key]:
                                del self._waiters[key]
                        except ValueError:
                            pass  # Already removed

                # Resolve promise with "timed-out"
                event_loop.queue_microtask(lambda: resolve("timed-out"))

            # Schedule timeout
            timeout_timer = threading.Timer(timeout_ms / 1000.0, on_timeout)
            timeout_timer.daemon = True
            timeout_timer.start()
            waiter.timeout_handle = timeout_timer

        # Add to waiters queue
        buffer_id = id(typed_array.buffer)
        key = (buffer_id, index)

        with self._lock:
            if key not in self._waiters:
                self._waiters[key] = []
            self._waiters[key].append(waiter)

        return AtomicsWaitAsyncResult(
            async_status=True,
            value="ok",
            promise=promise
        )

    def notify(self, typed_array, index, count):
        """Notify waiters on shared memory location.

        Wakes up to 'count' waiters waiting on the specified index.
        Waiters are notified in FIFO order.

        Args:
            typed_array: Shared Int32Array
            index: Index to notify waiters on
            count: Number of waiters to wake (can be Infinity to wake all)

        Returns:
            int: Number of waiters actually notified

        Raises:
            TypeError: If typed_array is not backed by SharedArrayBuffer

        Example:
            >>> atomics = AtomicsExtensions()
            >>> num_woken = atomics.notify(shared_array, 0, 1)
            >>> print(f"Woke {num_woken} waiters")
        """
        # Validate typed array is shared
        if not self._sab_integration.is_shared_array_buffer(typed_array.buffer):
            raise JSTypeError("Atomics.notify can only be used with SharedArrayBuffer")

        buffer_id = id(typed_array.buffer)
        key = (buffer_id, int(index))

        # Determine how many to notify
        if count == float('inf'):
            count_to_notify = float('inf')
        else:
            count_to_notify = max(0, int(count))

        notified_count = 0
        waiters_to_notify = []

        with self._lock:
            if key not in self._waiters:
                return 0  # No waiters

            # Get waiters to notify (FIFO order)
            waiters = self._waiters[key]

            while waiters and (count_to_notify == float('inf') or notified_count < count_to_notify):
                waiter = waiters.pop(0)

                # Skip timed-out waiters
                if waiter.timed_out:
                    continue

                # Cancel timeout if present
                if waiter.timeout_handle is not None:
                    waiter.timeout_handle.cancel()

                waiters_to_notify.append(waiter)
                notified_count += 1

            # Clean up empty waiter list
            if not self._waiters[key]:
                del self._waiters[key]

        # Resolve promises outside lock
        for waiter in waiters_to_notify:
            # Queue resolution as microtask
            waiter.resolve("ok")

        return notified_count
