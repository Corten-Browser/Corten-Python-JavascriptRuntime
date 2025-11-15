"""
Integration tests for Atomics extensions.

Tests cross-component integration and real-world scenarios.
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
from components.event_loop.src import EventLoop


class TestAtomicsIntegration:
    """Integration tests for Atomics with EventLoop and Promises."""

    def setup_method(self):
        """Set up test fixtures."""
        self.event_loop = EventLoop()

    def test_wait_notify_across_event_loops(self):
        """
        Given multiple event loops with waiters
        When notify is called
        Then all waiters across event loops are notified
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab = SharedArrayBufferIntegration()
        shared_buffer = sab.create_shared_buffer(16)
        int32_array = Int32Array(shared_buffer)
        int32_array[0] = 0

        atomics = AtomicsExtensions()

        # Create waiters on different event loops
        loop1 = EventLoop()
        loop2 = EventLoop()

        result1 = atomics.wait_async(int32_array, 0, 0, event_loop=loop1)
        result2 = atomics.wait_async(int32_array, 0, 0, event_loop=loop2)

        resolved1 = [None]
        resolved2 = [None]

        result1.promise.then(lambda v: resolved1.__setitem__(0, v))
        result2.promise.then(lambda v: resolved2.__setitem__(0, v))

        # Notify
        count = atomics.notify(int32_array, 0, 2)

        assert count == 2

        # Process both event loops
        loop1.run()
        loop2.run()

        assert resolved1[0] == "ok"
        assert resolved2[0] == "ok"

    def test_concurrent_wait_notify_stress(self):
        """
        Given 100 concurrent waiters
        When notify is called
        Then all waiters are notified within performance budget
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab = SharedArrayBufferIntegration()
        shared_buffer = sab.create_shared_buffer(16)
        int32_array = Int32Array(shared_buffer)
        int32_array[0] = 0

        atomics = AtomicsExtensions()

        # Create 100 waiters
        num_waiters = 100
        results = []
        resolved_values = []

        for _ in range(num_waiters):
            result = atomics.wait_async(int32_array, 0, 0, event_loop=self.event_loop)
            results.append(result)

            resolved_value = [None]
            result.promise.then(lambda v, rv=resolved_value: rv.__setitem__(0, v))
            resolved_values.append(resolved_value)

        # Measure notification latency
        start_time = time.time()
        count = atomics.notify(int32_array, 0, num_waiters)
        notify_time = (time.time() - start_time) * 1000  # Convert to ms

        assert count == num_waiters

        # Notification should be fast (< 10ms per spec)
        assert notify_time < 10, f"Notification took {notify_time}ms, expected < 10ms"

        # Process microtasks
        self.event_loop.run()

        # All resolved
        for resolved_value in resolved_values:
            assert resolved_value[0] == "ok"

    def test_wait_notify_with_promise_chaining(self):
        """
        Given a waiter with promise chain
        When notify is called
        Then the entire promise chain executes correctly
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab = SharedArrayBufferIntegration()
        shared_buffer = sab.create_shared_buffer(16)
        int32_array = Int32Array(shared_buffer)
        int32_array[0] = 0

        atomics = AtomicsExtensions()

        result = atomics.wait_async(int32_array, 0, 0, event_loop=self.event_loop)

        # Chain promises
        final_value = [None]
        result.promise.then(
            lambda v: f"got-{v}"
        ).then(
            lambda v: final_value.__setitem__(0, v)
        )

        # Notify
        atomics.notify(int32_array, 0, 1)

        # Process all microtasks
        self.event_loop.run()

        assert final_value[0] == "got-ok"

    def test_timeout_with_multiple_waiters(self):
        """
        Given multiple waiters with different timeouts
        When timeouts expire
        Then each waiter times out at the correct time
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab = SharedArrayBufferIntegration()
        shared_buffer = sab.create_shared_buffer(16)
        int32_array = Int32Array(shared_buffer)
        int32_array[0] = 0

        atomics = AtomicsExtensions()

        # Create waiters with different timeouts
        result_50ms = atomics.wait_async(int32_array, 0, 0, timeout=50, event_loop=self.event_loop)
        result_100ms = atomics.wait_async(int32_array, 0, 0, timeout=100, event_loop=self.event_loop)
        result_150ms = atomics.wait_async(int32_array, 0, 0, timeout=150, event_loop=self.event_loop)

        resolved_50 = [None]
        resolved_100 = [None]
        resolved_150 = [None]

        result_50ms.promise.then(lambda v: resolved_50.__setitem__(0, v))
        result_100ms.promise.then(lambda v: resolved_100.__setitem__(0, v))
        result_150ms.promise.then(lambda v: resolved_150.__setitem__(0, v))

        # No notify - let them timeout

        # Process with time progression
        start = time.time()

        # Wait 60ms
        time.sleep(0.06)
        self.event_loop.run()
        assert resolved_50[0] == "timed-out"
        assert resolved_100[0] is None  # Still waiting
        assert resolved_150[0] is None  # Still waiting

        # Wait another 60ms (total 120ms)
        time.sleep(0.06)
        self.event_loop.run()
        assert resolved_100[0] == "timed-out"
        assert resolved_150[0] is None  # Still waiting

        # Wait another 60ms (total 180ms)
        time.sleep(0.06)
        self.event_loop.run()
        assert resolved_150[0] == "timed-out"

    def test_notify_after_some_waiters_timeout(self):
        """
        Given waiters with timeouts
        When some timeout and then notify is called
        Then only non-timed-out waiters are notified
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab = SharedArrayBufferIntegration()
        shared_buffer = sab.create_shared_buffer(16)
        int32_array = Int32Array(shared_buffer)
        int32_array[0] = 0

        atomics = AtomicsExtensions()

        # Create one waiter with short timeout, one without
        result_timeout = atomics.wait_async(int32_array, 0, 0, timeout=50, event_loop=self.event_loop)
        result_no_timeout = atomics.wait_async(int32_array, 0, 0, event_loop=self.event_loop)

        resolved_timeout = [None]
        resolved_no_timeout = [None]

        result_timeout.promise.then(lambda v: resolved_timeout.__setitem__(0, v))
        result_no_timeout.promise.then(lambda v: resolved_no_timeout.__setitem__(0, v))

        # Wait for timeout to expire
        time.sleep(0.06)
        self.event_loop.run()

        assert resolved_timeout[0] == "timed-out"
        assert resolved_no_timeout[0] is None  # Still waiting

        # Now notify
        count = atomics.notify(int32_array, 0, 10)

        # Only 1 waiter should be notified (the one that didn't timeout)
        assert count == 1

        self.event_loop.run()

        assert resolved_no_timeout[0] == "ok"

    def test_large_scale_concurrent_waiters(self):
        """
        Given 1000+ concurrent waiters (stress test)
        When notify is called
        Then all waiters are notified successfully
        """
        from components.atomics_extensions.src.atomics_extensions import AtomicsExtensions
        from components.atomics_extensions.src.shared_array_buffer import SharedArrayBufferIntegration

        sab = SharedArrayBufferIntegration()
        shared_buffer = sab.create_shared_buffer(16)
        int32_array = Int32Array(shared_buffer)
        int32_array[0] = 0

        atomics = AtomicsExtensions()

        # Create 1000 waiters
        num_waiters = 1000
        results = []
        resolved_count = [0]

        for _ in range(num_waiters):
            result = atomics.wait_async(int32_array, 0, 0, event_loop=self.event_loop)
            results.append(result)

            result.promise.then(lambda v: resolved_count.__setitem__(0, resolved_count[0] + 1))

        # Notify all
        start_time = time.time()
        count = atomics.notify(int32_array, 0, float('inf'))
        notify_time = (time.time() - start_time) * 1000

        assert count == num_waiters

        # Should still be fast
        assert notify_time < 50, f"Notification took {notify_time}ms for {num_waiters} waiters"

        # Process microtasks
        self.event_loop.run()

        # All resolved
        assert resolved_count[0] == num_waiters
