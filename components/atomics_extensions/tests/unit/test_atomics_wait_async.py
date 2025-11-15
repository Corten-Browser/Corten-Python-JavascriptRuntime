"""
Unit tests for Atomics.waitAsync functionality.

Tests FR-ES24-009: Atomics.waitAsync() implementation
"""

import pytest
import threading
import time
import sys
from pathlib import Path

# Add typed_arrays src to path
typed_arrays_src = Path(__file__).parent.parent.parent.parent / 'typed_arrays' / 'src'
if str(typed_arrays_src) not in sys.path:
    sys.path.insert(0, str(typed_arrays_src))

from typed_array import Int32Array
from array_buffer import ArrayBuffer
from exceptions import TypeError as JSTypeError, RangeError
from components.event_loop.src import EventLoop


class TestAtomicsWaitAsync:
    """Test Atomics.waitAsync() implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.event_loop = EventLoop()

        # Create shared Int32Array for testing
        self.buffer = ArrayBuffer(16)  # 4 int32 values
        self.int32_array = Int32Array(self.buffer)

        # Mark buffer as shared (will implement this)
        self.buffer._shared = True

    def test_wait_async_returns_result_object(self):
        """
        Given a shared Int32Array
        When wait_async is called
        Then it returns an AtomicsWaitAsyncResult object
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()
        result = atomics.wait_async(self.int32_array, 0, 0, event_loop=self.event_loop)

        assert result is not None
        assert hasattr(result, 'async_status')
        assert hasattr(result, 'value')
        assert hasattr(result, 'promise')

    def test_wait_async_immediate_not_equal(self):
        """
        Given a shared Int32Array with value 42 at index 0
        When wait_async is called with expected value 0
        Then it returns immediately with "not-equal" status
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()
        self.int32_array[0] = 42  # Set value different from expected

        result = atomics.wait_async(self.int32_array, 0, 0, event_loop=self.event_loop)

        assert result.async_status is False  # Immediate, not async
        assert result.value == "not-equal"
        assert result.promise is None  # No promise for immediate return

    def test_wait_async_creates_promise_when_values_match(self):
        """
        Given a shared Int32Array with value 0 at index 0
        When wait_async is called with expected value 0
        Then it returns a promise that will resolve when notified
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()
        self.int32_array[0] = 0

        result = atomics.wait_async(self.int32_array, 0, 0, event_loop=self.event_loop)

        assert result.async_status is True  # Async operation
        assert result.value == "ok"
        assert result.promise is not None  # Promise created
        assert hasattr(result.promise, 'then')  # Is a JSPromise

    def test_wait_async_with_timeout(self):
        """
        Given a shared Int32Array
        When wait_async is called with a timeout
        And no notification occurs
        Then the promise resolves with "timed-out" after the timeout
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()
        self.int32_array[0] = 0

        result = atomics.wait_async(self.int32_array, 0, 0, timeout=100, event_loop=self.event_loop)

        assert result.async_status is True
        assert result.promise is not None

        # Track promise resolution
        resolved_value = [None]
        result.promise.then(lambda v: resolved_value.__setitem__(0, v))

        # Wait for timeout
        start = time.time()
        self.event_loop.run()  # Process microtasks
        time.sleep(0.15)  # Wait for timeout
        self.event_loop.run()  # Process timeout callback

        # Should have timed out
        assert resolved_value[0] == "timed-out"

    def test_wait_async_on_non_shared_buffer_throws(self):
        """
        Given a non-shared Int32Array
        When wait_async is called
        Then it raises TypeError
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()

        # Create non-shared buffer
        non_shared_buffer = ArrayBuffer(16)
        non_shared_array = Int32Array(non_shared_buffer)

        with pytest.raises(JSTypeError) as exc_info:
            atomics.wait_async(non_shared_array, 0, 0, event_loop=self.event_loop)

        assert "shared" in str(exc_info.value).lower()

    def test_wait_async_invalid_index_throws(self):
        """
        Given a shared Int32Array
        When wait_async is called with out-of-bounds index
        Then it raises RangeError
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()

        with pytest.raises(RangeError):
            atomics.wait_async(self.int32_array, 999, 0, event_loop=self.event_loop)

    def test_wait_async_multiple_waiters_on_same_location(self):
        """
        Given a shared Int32Array
        When multiple wait_async calls are made on the same index
        Then each returns its own promise
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()
        self.int32_array[0] = 0

        result1 = atomics.wait_async(self.int32_array, 0, 0, event_loop=self.event_loop)
        result2 = atomics.wait_async(self.int32_array, 0, 0, event_loop=self.event_loop)
        result3 = atomics.wait_async(self.int32_array, 0, 0, event_loop=self.event_loop)

        assert result1.promise is not None
        assert result2.promise is not None
        assert result3.promise is not None

        # All promises are distinct
        assert result1.promise is not result2.promise
        assert result1.promise is not result3.promise

    def test_wait_async_different_indices_independent(self):
        """
        Given a shared Int32Array
        When wait_async calls are made on different indices
        Then they are independent and don't interfere
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()
        self.int32_array[0] = 0
        self.int32_array[1] = 0

        result_index_0 = atomics.wait_async(self.int32_array, 0, 0, event_loop=self.event_loop)
        result_index_1 = atomics.wait_async(self.int32_array, 1, 0, event_loop=self.event_loop)

        assert result_index_0.promise is not None
        assert result_index_1.promise is not None
        assert result_index_0.promise is not result_index_1.promise


class TestAtomicsNotify:
    """Test Atomics.notify() implementation."""

    def setup_method(self):
        """Set up test fixtures."""
        self.event_loop = EventLoop()

        # Create shared Int32Array
        self.buffer = ArrayBuffer(16)
        self.int32_array = Int32Array(self.buffer)
        self.buffer._shared = True

    def test_notify_returns_count_of_woken_waiters(self):
        """
        Given no waiters on a location
        When notify is called
        Then it returns 0
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()

        count = atomics.notify(self.int32_array, 0, 1)

        assert count == 0

    def test_notify_wakes_single_waiter(self):
        """
        Given one waiter on a location
        When notify is called with count=1
        Then the waiter's promise resolves with "ok"
        And notify returns 1
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()
        self.int32_array[0] = 0

        # Create waiter
        result = atomics.wait_async(self.int32_array, 0, 0, event_loop=self.event_loop)

        # Track promise resolution
        resolved_value = [None]
        result.promise.then(lambda v: resolved_value.__setitem__(0, v))

        # Notify
        count = atomics.notify(self.int32_array, 0, 1)

        assert count == 1

        # Process microtasks to resolve promise
        self.event_loop.run()

        assert resolved_value[0] == "ok"

    def test_notify_wakes_multiple_waiters(self):
        """
        Given three waiters on a location
        When notify is called with count=3
        Then all three waiters are woken
        And notify returns 3
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()
        self.int32_array[0] = 0

        # Create three waiters
        results = []
        resolved_values = []

        for _ in range(3):
            result = atomics.wait_async(self.int32_array, 0, 0, event_loop=self.event_loop)
            results.append(result)

            resolved_value = [None]
            result.promise.then(lambda v, rv=resolved_value: rv.__setitem__(0, v))
            resolved_values.append(resolved_value)

        # Notify all
        count = atomics.notify(self.int32_array, 0, 3)

        assert count == 3

        # Process microtasks
        self.event_loop.run()

        # All resolved
        for resolved_value in resolved_values:
            assert resolved_value[0] == "ok"

    def test_notify_with_count_less_than_waiters(self):
        """
        Given three waiters on a location
        When notify is called with count=2
        Then only two waiters are woken
        And one remains waiting
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()
        self.int32_array[0] = 0

        # Create three waiters
        results = []
        resolved_values = []

        for _ in range(3):
            result = atomics.wait_async(self.int32_array, 0, 0, event_loop=self.event_loop)
            results.append(result)

            resolved_value = [None]
            result.promise.then(lambda v, rv=resolved_value: rv.__setitem__(0, v))
            resolved_values.append(resolved_value)

        # Notify only 2
        count = atomics.notify(self.int32_array, 0, 2)

        assert count == 2

        # Process microtasks
        self.event_loop.run()

        # Two resolved, one still waiting
        resolved_count = sum(1 for rv in resolved_values if rv[0] == "ok")
        assert resolved_count == 2

    def test_notify_infinity_wakes_all_waiters(self):
        """
        Given many waiters on a location
        When notify is called with count=Infinity
        Then all waiters are woken
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()
        self.int32_array[0] = 0

        # Create 10 waiters
        num_waiters = 10
        results = []
        resolved_values = []

        for _ in range(num_waiters):
            result = atomics.wait_async(self.int32_array, 0, 0, event_loop=self.event_loop)
            results.append(result)

            resolved_value = [None]
            result.promise.then(lambda v, rv=resolved_value: rv.__setitem__(0, v))
            resolved_values.append(resolved_value)

        # Notify all (count=Infinity)
        count = atomics.notify(self.int32_array, 0, float('inf'))

        assert count == num_waiters

        # Process microtasks
        self.event_loop.run()

        # All resolved
        for resolved_value in resolved_values:
            assert resolved_value[0] == "ok"

    def test_notify_on_non_shared_buffer_throws(self):
        """
        Given a non-shared Int32Array
        When notify is called
        Then it raises TypeError
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()

        # Create non-shared buffer
        non_shared_buffer = ArrayBuffer(16)
        non_shared_array = Int32Array(non_shared_buffer)

        with pytest.raises(JSTypeError):
            atomics.notify(non_shared_array, 0, 1)

    def test_notify_different_indices_independent(self):
        """
        Given waiters on indices 0 and 1
        When notify is called on index 0
        Then only waiters on index 0 are woken
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions

        atomics = AtomicsExtensions()
        self.int32_array[0] = 0
        self.int32_array[1] = 0

        # Waiter on index 0
        result0 = atomics.wait_async(self.int32_array, 0, 0, event_loop=self.event_loop)
        resolved0 = [None]
        result0.promise.then(lambda v: resolved0.__setitem__(0, v))

        # Waiter on index 1
        result1 = atomics.wait_async(self.int32_array, 1, 0, event_loop=self.event_loop)
        resolved1 = [None]
        result1.promise.then(lambda v: resolved1.__setitem__(0, v))

        # Notify only index 0
        count = atomics.notify(self.int32_array, 0, 1)

        assert count == 1

        # Process microtasks
        self.event_loop.run()

        # Only index 0 waiter resolved
        assert resolved0[0] == "ok"
        assert resolved1[0] is None  # Still waiting
