"""Unit tests for Event Loop implementation."""

import pytest
from components.event_loop.src import EventLoop


class TestEventLoopBasics:
    """Basic event loop functionality tests."""

    def test_event_loop_creation(self):
        """Test creating an event loop."""
        loop = EventLoop()
        assert loop.macrotask_queue is not None
        assert loop.microtask_queue is not None
        assert loop.running is False

    def test_empty_loop_exits_immediately(self):
        """Empty event loop should exit without hanging."""
        loop = EventLoop()
        loop.run()  # Should complete immediately
        assert loop.running is False

    def test_single_microtask_executes(self):
        """Single microtask should execute."""
        loop = EventLoop()
        executed = []

        loop.queue_microtask(lambda: executed.append(1))
        loop.run()

        assert executed == [1]

    def test_multiple_microtasks_execute_in_order(self):
        """Multiple microtasks should execute in FIFO order."""
        loop = EventLoop()
        executed = []

        loop.queue_microtask(lambda: executed.append(1))
        loop.queue_microtask(lambda: executed.append(2))
        loop.queue_microtask(lambda: executed.append(3))
        loop.run()

        assert executed == [1, 2, 3]

    def test_single_macrotask_executes(self):
        """Single macrotask should execute."""
        loop = EventLoop()
        executed = []

        loop.queue_task(lambda: executed.append(1))
        loop.run()

        assert executed == [1]

    def test_multiple_macrotasks_execute_in_order(self):
        """Multiple macrotasks should execute in FIFO order."""
        loop = EventLoop()
        executed = []

        loop.queue_task(lambda: executed.append(1))
        loop.queue_task(lambda: executed.append(2))
        loop.queue_task(lambda: executed.append(3))
        loop.run()

        assert executed == [1, 2, 3]


class TestMicrotaskPriority:
    """Test microtask priority over macrotasks."""

    def test_microtasks_have_priority_over_macrotasks(self):
        """Microtasks should execute before macrotasks."""
        loop = EventLoop()
        executed = []

        loop.queue_task(lambda: executed.append('macro1'))
        loop.queue_microtask(lambda: executed.append('micro1'))
        loop.queue_task(lambda: executed.append('macro2'))
        loop.queue_microtask(lambda: executed.append('micro2'))
        loop.run()

        # All microtasks should execute first
        assert executed[:2] == ['micro1', 'micro2']
        assert executed[2:] == ['macro1', 'macro2']

    def test_microtasks_queued_during_execution_run_in_same_batch(self):
        """New microtasks queued during microtask execution should run immediately."""
        loop = EventLoop()
        executed = []

        def micro1():
            executed.append('micro1')
            # Queue another microtask during execution
            loop.queue_microtask(lambda: executed.append('micro2'))

        loop.queue_task(lambda: executed.append('macro1'))
        loop.queue_microtask(micro1)
        loop.run()

        # micro2 should execute before macro1
        assert executed == ['micro1', 'micro2', 'macro1']

    def test_all_microtasks_execute_before_next_macrotask(self):
        """ALL microtasks must execute before next macrotask."""
        loop = EventLoop()
        executed = []

        loop.queue_task(lambda: executed.append('macro1'))
        loop.queue_task(lambda: executed.append('macro2'))
        loop.queue_microtask(lambda: executed.append('micro1'))
        loop.queue_microtask(lambda: executed.append('micro2'))
        loop.queue_microtask(lambda: executed.append('micro3'))
        loop.run()

        # All 3 microtasks before any macrotask
        assert executed[:3] == ['micro1', 'micro2', 'micro3']


class TestEventLoopEdgeCases:
    """Test edge cases and error handling."""

    def test_exception_in_microtask_doesnt_stop_loop(self):
        """Exception in one microtask shouldn't stop others."""
        loop = EventLoop()
        executed = []

        def failing_task():
            executed.append('before_error')
            raise ValueError("Test error")

        loop.queue_microtask(failing_task)
        loop.queue_microtask(lambda: executed.append('after_error'))

        with pytest.raises(ValueError):
            loop.run()

        # First task should have executed
        assert 'before_error' in executed

    def test_can_stop_running_loop(self):
        """stop() method should halt event loop."""
        loop = EventLoop()
        executed = []

        def task_that_stops():
            executed.append(1)
            loop.stop()

        loop.queue_microtask(task_that_stops)
        loop.queue_microtask(lambda: executed.append(2))  # Should not execute
        loop.run()

        assert executed == [1]
        assert loop.running is False

    def test_loop_can_run_multiple_times(self):
        """Event loop should be reusable."""
        loop = EventLoop()
        executed = []

        # First run
        loop.queue_microtask(lambda: executed.append(1))
        loop.run()

        # Second run
        loop.queue_microtask(lambda: executed.append(2))
        loop.run()

        assert executed == [1, 2]
        assert loop.running is False
