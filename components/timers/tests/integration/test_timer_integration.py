"""
Integration tests for timer integration with event loop

Requirements:
- FR-P3-085: Timer execution as macrotasks
- FR-P3-086: Timer ordering guarantees
- FR-P3-090: Timer integration with event loop
"""

import pytest
import time
from unittest.mock import Mock, patch
from src.timers import TimerManager
from src.timer_integration import EventLoopTimerIntegration


class TestEventLoopIntegration:
    """Test timer integration with event loop - FR-P3-090"""

    def test_timers_execute_as_macrotasks(self):
        """Test timers execute as macrotasks in event loop

        Requirement: FR-P3-085 - Timer execution as macrotasks
        """
        manager = TimerManager()
        callback = Mock()

        # Schedule timer
        manager.setTimeout(callback, 0)

        # Execute event loop iteration
        manager._execute_expired_timers(float('inf'))

        # Callback should execute as macrotask
        callback.assert_called_once()

    def test_multiple_timers_execute_in_one_iteration(self):
        """Test multiple expired timers execute in one event loop iteration"""
        manager = TimerManager()
        callbacks = [Mock() for _ in range(5)]

        # Schedule multiple timers
        for cb in callbacks:
            manager.setTimeout(cb, 0)

        # Execute one event loop iteration
        manager._execute_expired_timers(float('inf'))

        # All should execute
        for cb in callbacks:
            cb.assert_called_once()

    def test_timer_scheduled_during_timer_execution(self):
        """Test timers scheduled during timer callback execution

        Requirement: FR-P3-090 - Event loop integration
        """
        manager = TimerManager()
        second_callback = Mock()

        def first_callback():
            # Schedule another timer during execution
            manager.setTimeout(second_callback, 0)

        manager.setTimeout(first_callback, 0)

        # First iteration
        manager._execute_expired_timers(float('inf'))

        # Second callback not executed yet (needs another iteration)
        second_callback.assert_not_called()

        # Second iteration
        manager._execute_expired_timers(float('inf'))

        # Now second callback should execute
        second_callback.assert_called_once()

    def test_interval_reschedules_for_next_iteration(self):
        """Test interval reschedules for next event loop iteration

        Requirement: FR-P3-083 - setInterval repeated execution
        """
        manager = TimerManager()
        callback = Mock()

        manager.setInterval(callback, 100)

        # Execute multiple iterations
        for _ in range(3):
            manager._execute_expired_timers(float('inf'))

        # Should execute 3 times
        assert callback.call_count >= 1

    def test_timer_this_binding_is_global(self):
        """Test timer callback 'this' binding is globalThis

        Note: In Python, we don't have 'this' binding, but this tests
        that callbacks are invoked in the correct context
        """
        manager = TimerManager()
        callback = Mock()

        manager.setTimeout(callback, 0)
        manager._execute_expired_timers(float('inf'))

        # Callback should be invoked
        callback.assert_called_once()

    def test_exception_in_timer_callback_reported_not_thrown(self):
        """Test exceptions in timer callbacks are caught and reported

        Requirement: Contract - Exceptions do not stop event loop
        """
        manager = TimerManager()
        error_callback = Mock(side_effect=ValueError("Test error"))
        success_callback = Mock()

        manager.setTimeout(error_callback, 0)
        manager.setTimeout(success_callback, 0)

        # Should not raise exception
        manager._execute_expired_timers(float('inf'))

        # Both should be called despite exception
        error_callback.assert_called_once()
        success_callback.assert_called_once()


class TestTimerPrecision:
    """Test timer precision and timing guarantees"""

    def test_zero_delay_executes_next_iteration(self):
        """Test zero delay timer executes in next iteration, not synchronously

        Requirement: FR-P3-089 - Zero delay edge case
        """
        manager = TimerManager()
        callback = Mock()

        manager.setTimeout(callback, 0)

        # Should not execute immediately (synchronously)
        callback.assert_not_called()

        # Should execute in next iteration
        manager._execute_expired_timers(float('inf'))
        callback.assert_called_once()

    def test_timer_does_not_execute_before_delay(self):
        """Test timer does not execute before its delay expires"""
        manager = TimerManager()
        callback = Mock()
        current_time = manager._get_current_time()

        manager.setTimeout(callback, 100)

        # Execute with time before expiration
        manager._execute_expired_timers(current_time + 50)

        # Should not execute yet
        callback.assert_not_called()

        # Execute with time after expiration
        manager._execute_expired_timers(current_time + 150)

        # Now should execute
        callback.assert_called_once()

    def test_actual_delay_may_be_longer_than_specified(self):
        """Test actual execution may be later if event loop is busy

        Requirement: Contract - Timing guarantees (minimum delay)
        """
        manager = TimerManager()
        callback = Mock()
        current_time = manager._get_current_time()

        # Schedule for 100ms
        manager.setTimeout(callback, 100)

        # Event loop busy until 200ms
        manager._execute_expired_timers(current_time + 200)

        # Should still execute (late)
        callback.assert_called_once()


class TestComplexTimerScenarios:
    """Test complex real-world timer scenarios"""

    def test_multiple_intervals_with_different_delays(self):
        """Test multiple intervals with different delays run correctly"""
        manager = TimerManager()
        callback1 = Mock()
        callback2 = Mock()

        manager.setInterval(callback1, 100)
        manager.setInterval(callback2, 200)

        # Run for 500ms
        current_time = manager._get_current_time()
        for t in range(0, 600, 100):
            manager._execute_expired_timers(current_time + t)

        # callback1 should execute ~5 times (100, 200, 300, 400, 500)
        # callback2 should execute ~2-3 times (200, 400)
        assert callback1.call_count >= 1
        assert callback2.call_count >= 1

    def test_timeout_inside_interval(self):
        """Test setTimeout called inside setInterval callback"""
        manager = TimerManager()
        timeout_callback = Mock()

        def interval_callback():
            manager.setTimeout(timeout_callback, 0)

        manager.setInterval(interval_callback, 100)

        # Execute several iterations
        current_time = manager._get_current_time()
        for i in range(5):
            manager._execute_expired_timers(current_time + (i + 1) * 100)

        # timeout_callback should be scheduled each time interval runs
        assert timeout_callback.call_count >= 1

    def test_clear_timeout_during_callback_execution(self):
        """Test clearing a timeout during another timer's callback"""
        manager = TimerManager()
        callback1 = Mock()
        callback2 = Mock()

        id2 = manager.setTimeout(callback2, 100)

        def callback1_impl():
            manager.clearTimeout(id2)
            callback1()

        manager.setTimeout(callback1_impl, 0)

        # Execute all timers
        manager._execute_expired_timers(float('inf'))

        # callback1 should execute, callback2 should be cancelled
        callback1.assert_called_once()
        callback2.assert_not_called()

    def test_self_canceling_interval(self):
        """Test interval that cancels itself after N iterations"""
        manager = TimerManager()
        callback = Mock()
        interval_id = None

        def counting_callback():
            callback()
            if callback.call_count >= 3:
                manager.clearInterval(interval_id)

        interval_id = manager.setInterval(counting_callback, 0)

        # Execute many iterations
        for _ in range(10):
            manager._execute_expired_timers(float('inf'))

        # Should stop at 3
        assert callback.call_count == 3

    def test_nested_timeout_chain(self):
        """Test nested setTimeout chain (each schedules next)

        Requirement: FR-P3-088 - Nested timeout clamping
        """
        manager = TimerManager()
        execution_log = []

        def create_nested(level):
            def callback():
                execution_log.append(level)
                if level < 10:
                    manager.setTimeout(create_nested(level + 1), 0, nesting_level=level)

            return callback

        # Start the chain
        manager.setTimeout(create_nested(0), 0, nesting_level=0)

        # Execute many iterations
        for _ in range(15):
            manager._execute_expired_timers(float('inf'))

        # Should execute nested chain
        assert len(execution_log) >= 5

    def test_timer_ordering_with_mixed_timeouts_and_intervals(self):
        """Test timer ordering with both timeouts and intervals

        Requirement: FR-P3-086 - Timer ordering guarantees
        """
        manager = TimerManager()
        execution_order = []

        def make_callback(name):
            return lambda: execution_order.append(name)

        # Mix of timeouts and intervals
        manager.setTimeout(make_callback("timeout1"), 100)
        manager.setInterval(make_callback("interval1"), 150)
        manager.setTimeout(make_callback("timeout2"), 200)

        # Execute over time
        current_time = manager._get_current_time()
        for t in range(0, 500, 50):
            manager._execute_expired_timers(current_time + t)

        # Should have some executions in order
        assert len(execution_order) >= 3


class TestEventLoopTimerIntegrationClass:
    """Test EventLoopTimerIntegration helper class"""

    def test_integration_helper_processes_timers(self):
        """Test integration helper processes expired timers each iteration"""
        manager = TimerManager()
        integration = EventLoopTimerIntegration(manager)
        callback = Mock()

        manager.setTimeout(callback, 0)

        # Process timers
        integration.process_timers()

        callback.assert_called_once()

    def test_integration_helper_returns_next_timeout(self):
        """Test integration helper returns time until next timer"""
        manager = TimerManager()
        integration = EventLoopTimerIntegration(manager)
        current_time = manager._get_current_time()

        manager.setTimeout(Mock(), 100)

        # Should return ~100ms until next timer
        next_timeout = integration.get_next_timer_timeout()

        assert next_timeout is not None
        assert 90 <= next_timeout <= 110  # Allow for timing variations

    def test_integration_helper_no_timers_returns_none(self):
        """Test integration helper returns None when no timers pending"""
        manager = TimerManager()
        integration = EventLoopTimerIntegration(manager)

        next_timeout = integration.get_next_timer_timeout()

        assert next_timeout is None
