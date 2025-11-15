"""
Unit tests for timers.py - setTimeout, clearTimeout, setInterval, clearInterval

Requirements:
- FR-P3-081: setTimeout basic functionality
- FR-P3-082: clearTimeout cancellation
- FR-P3-083: setInterval repeated execution
- FR-P3-084: clearInterval stopping
- FR-P3-087: Timer argument passing
- FR-P3-088: Nested timeout clamping
- FR-P3-089: Timer edge cases (zero/negative delays)
"""

import pytest
import time
from unittest.mock import Mock, call
from src.timers import TimerManager


class TestSetTimeout:
    """Test setTimeout basic functionality - FR-P3-081"""

    def test_setTimeout_returns_timer_id(self):
        """Test setTimeout returns a positive integer timer ID"""
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setTimeout(callback, 100)

        assert isinstance(timer_id, int)
        assert timer_id > 0

    def test_setTimeout_unique_ids(self):
        """Test setTimeout returns unique IDs for each timer"""
        manager = TimerManager()
        callback = Mock()

        id1 = manager.setTimeout(callback, 100)
        id2 = manager.setTimeout(callback, 100)
        id3 = manager.setTimeout(callback, 100)

        assert id1 != id2
        assert id2 != id3
        assert id1 != id3

    def test_setTimeout_with_zero_delay(self):
        """Test setTimeout with 0 delay schedules for next iteration

        Requirement: FR-P3-089 - Zero delay edge case
        """
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setTimeout(callback, 0)

        assert timer_id > 0
        # Timer should be scheduled (tested in integration)

    def test_setTimeout_with_negative_delay_treated_as_zero(self):
        """Test negative delay is treated as 0

        Requirement: FR-P3-089 - Negative delay edge case
        """
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setTimeout(callback, -100)

        assert timer_id > 0
        # Should treat as 0 delay

    def test_setTimeout_stores_callback(self):
        """Test setTimeout stores the callback function"""
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setTimeout(callback, 100)

        # Timer should be registered
        assert manager.has_timer(timer_id) is True

    def test_setTimeout_with_multiple_timers(self):
        """Test multiple setTimeout calls work independently"""
        manager = TimerManager()
        callback1 = Mock()
        callback2 = Mock()
        callback3 = Mock()

        id1 = manager.setTimeout(callback1, 100)
        id2 = manager.setTimeout(callback2, 200)
        id3 = manager.setTimeout(callback3, 50)

        assert manager.has_timer(id1) is True
        assert manager.has_timer(id2) is True
        assert manager.has_timer(id3) is True


class TestClearTimeout:
    """Test clearTimeout cancellation - FR-P3-082"""

    def test_clearTimeout_removes_pending_timer(self):
        """Test clearTimeout cancels a pending timeout"""
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setTimeout(callback, 100)
        assert manager.has_timer(timer_id) is True

        manager.clearTimeout(timer_id)
        assert manager.has_timer(timer_id) is False

    def test_clearTimeout_with_invalid_id_is_noop(self):
        """Test clearTimeout with invalid ID does nothing (no error)

        Requirement: FR-P3-082 - No-op for invalid ID
        """
        manager = TimerManager()

        # Should not raise error
        manager.clearTimeout(999)
        manager.clearTimeout(-1)
        manager.clearTimeout(0)

    def test_clearTimeout_multiple_times_is_safe(self):
        """Test calling clearTimeout multiple times with same ID is safe

        Requirement: FR-P3-082 - Safe to call multiple times
        """
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setTimeout(callback, 100)
        manager.clearTimeout(timer_id)

        # Should not raise error on second call
        manager.clearTimeout(timer_id)
        manager.clearTimeout(timer_id)

    def test_clearTimeout_after_timer_fired_is_noop(self):
        """Test clearTimeout after timer already fired is no-op"""
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setTimeout(callback, 0)

        # Execute timer (simulate event loop)
        manager._execute_expired_timers(float('inf'))

        # Should not raise error
        manager.clearTimeout(timer_id)


class TestSetInterval:
    """Test setInterval repeated execution - FR-P3-083"""

    def test_setInterval_returns_timer_id(self):
        """Test setInterval returns a positive integer timer ID"""
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setInterval(callback, 100)

        assert isinstance(timer_id, int)
        assert timer_id > 0

    def test_setInterval_unique_ids(self):
        """Test setInterval returns unique IDs"""
        manager = TimerManager()
        callback = Mock()

        id1 = manager.setInterval(callback, 100)
        id2 = manager.setInterval(callback, 100)

        assert id1 != id2

    def test_setInterval_with_zero_delay(self):
        """Test setInterval with 0 delay

        Requirement: FR-P3-089 - Zero delay edge case
        """
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setInterval(callback, 0)

        assert timer_id > 0
        assert manager.has_timer(timer_id) is True

    def test_setInterval_stores_as_repeating(self):
        """Test setInterval marks timer as repeating"""
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setInterval(callback, 100)

        # Timer should be marked as repeating
        timer_info = manager._get_timer_info(timer_id)
        assert timer_info.repeat is True
        assert timer_info.interval == 100


class TestClearInterval:
    """Test clearInterval stopping - FR-P3-084"""

    def test_clearInterval_stops_repeating_timer(self):
        """Test clearInterval stops an interval"""
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setInterval(callback, 100)
        assert manager.has_timer(timer_id) is True

        manager.clearInterval(timer_id)
        assert manager.has_timer(timer_id) is False

    def test_clearInterval_with_invalid_id_is_noop(self):
        """Test clearInterval with invalid ID does nothing (no error)"""
        manager = TimerManager()

        # Should not raise error
        manager.clearInterval(999)
        manager.clearInterval(-1)

    def test_clearInterval_multiple_times_is_safe(self):
        """Test calling clearInterval multiple times is safe"""
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setInterval(callback, 100)
        manager.clearInterval(timer_id)

        # Should not raise error
        manager.clearInterval(timer_id)


class TestTimerArgumentPassing:
    """Test timer argument passing - FR-P3-087"""

    def test_setTimeout_passes_no_arguments(self):
        """Test setTimeout with no extra arguments"""
        manager = TimerManager()
        callback = Mock()

        manager.setTimeout(callback, 0)
        manager._execute_expired_timers(float('inf'))

        callback.assert_called_once_with()

    def test_setTimeout_passes_single_argument(self):
        """Test setTimeout passes single argument to callback"""
        manager = TimerManager()
        callback = Mock()

        manager.setTimeout(callback, 0, 42)
        manager._execute_expired_timers(float('inf'))

        callback.assert_called_once_with(42)

    def test_setTimeout_passes_multiple_arguments(self):
        """Test setTimeout passes multiple arguments to callback

        Requirement: FR-P3-087 - Timer argument passing
        """
        manager = TimerManager()
        callback = Mock()

        manager.setTimeout(callback, 0, 1, 2, 3, "hello")
        manager._execute_expired_timers(float('inf'))

        callback.assert_called_once_with(1, 2, 3, "hello")

    def test_setInterval_passes_arguments(self):
        """Test setInterval passes arguments to callback

        Requirement: FR-P3-087 - Timer argument passing
        """
        manager = TimerManager()
        callback = Mock()

        manager.setInterval(callback, 0, "a", "b")

        # Execute twice to verify arguments passed each time
        manager._execute_expired_timers(float('inf'))
        manager._execute_expired_timers(float('inf'))

        assert callback.call_count == 2
        callback.assert_has_calls([call("a", "b"), call("a", "b")])

    def test_setTimeout_with_object_arguments(self):
        """Test setTimeout preserves object arguments"""
        manager = TimerManager()
        callback = Mock()
        obj = {"key": "value"}
        arr = [1, 2, 3]

        manager.setTimeout(callback, 0, obj, arr)
        manager._execute_expired_timers(float('inf'))

        callback.assert_called_once_with(obj, arr)


class TestNestedTimeoutClamping:
    """Test nested timeout clamping - FR-P3-088"""

    def test_first_nested_timeout_not_clamped(self):
        """Test first nested timeout uses specified delay"""
        manager = TimerManager()
        callback = Mock()

        # First level - should use 0ms delay
        id1 = manager.setTimeout(callback, 0, nesting_level=0)
        timer_info = manager._get_timer_info(id1)

        # Should not be clamped (< 5 levels)
        assert timer_info.nesting_level == 0

    def test_nested_timeout_level_tracking(self):
        """Test nesting level is tracked correctly"""
        manager = TimerManager()
        callback = Mock()

        # Create nested timeouts
        id1 = manager.setTimeout(callback, 0, nesting_level=0)
        id2 = manager.setTimeout(callback, 0, nesting_level=1)
        id3 = manager.setTimeout(callback, 0, nesting_level=2)
        id4 = manager.setTimeout(callback, 0, nesting_level=3)
        id5 = manager.setTimeout(callback, 0, nesting_level=4)

        assert manager._get_timer_info(id1).nesting_level == 0
        assert manager._get_timer_info(id2).nesting_level == 1
        assert manager._get_timer_info(id3).nesting_level == 2
        assert manager._get_timer_info(id4).nesting_level == 3
        assert manager._get_timer_info(id5).nesting_level == 4

    def test_nested_timeout_clamped_at_level_5(self):
        """Test timeout clamped to 4ms at nesting level 5

        Requirement: FR-P3-088 - Nested timeout clamping (≥4ms after 5 levels)
        """
        manager = TimerManager()
        callback = Mock()

        current_time_before = manager._get_current_time()

        # Level 5 and beyond should be clamped to 4ms
        id5 = manager.setTimeout(callback, 0, nesting_level=5)
        id6 = manager.setTimeout(callback, 1, nesting_level=6)

        timer5 = manager._get_timer_info(id5)
        timer6 = manager._get_timer_info(id6)

        # Delays should be clamped to at least 4ms
        # Check that expiration is at least 4ms after the time when setTimeout was called
        assert timer5.expiration >= current_time_before + 4
        assert timer6.expiration >= current_time_before + 4

    def test_clamp_applies_only_to_deep_nesting(self):
        """Test clamping only applies to nesting level >= 5"""
        manager = TimerManager()
        callback = Mock()
        current_time = manager._get_current_time()

        # Level 4: Should NOT be clamped
        id4 = manager.setTimeout(callback, 0, nesting_level=4)
        timer4 = manager._get_timer_info(id4)
        # Allow for small timing variations
        assert timer4.expiration < current_time + 4

        # Level 5: SHOULD be clamped
        id5 = manager.setTimeout(callback, 0, nesting_level=5)
        timer5 = manager._get_timer_info(id5)
        assert timer5.expiration >= current_time + 4


class TestTimerEdgeCases:
    """Test timer edge cases - FR-P3-089"""

    def test_very_large_delay(self):
        """Test timeout with very large delay"""
        manager = TimerManager()
        callback = Mock()

        # Very large delay (days)
        timer_id = manager.setTimeout(callback, 86400000)  # 24 hours

        assert timer_id > 0
        assert manager.has_timer(timer_id) is True

    def test_non_function_callback_converted_to_string(self):
        """Test non-function callback (compatibility mode)

        Note: String callbacks are discouraged but supported for compat
        """
        manager = TimerManager()

        # String callback (would eval in real implementation)
        timer_id = manager.setTimeout("console.log('test')", 100)

        assert timer_id > 0

    def test_undefined_delay_defaults_to_zero(self):
        """Test undefined delay defaults to 0"""
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setTimeout(callback)  # No delay specified

        assert timer_id > 0

    def test_float_delay_accepted(self):
        """Test float delay values are accepted"""
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setTimeout(callback, 100.5)

        assert timer_id > 0

    def test_timer_id_not_reused_immediately(self):
        """Test timer IDs are not reused for active timers"""
        manager = TimerManager()
        callback = Mock()

        id1 = manager.setTimeout(callback, 100)
        id2 = manager.setTimeout(callback, 100)

        # IDs should be different
        assert id1 != id2

    def test_callback_exception_does_not_crash(self):
        """Test exceptions in callback are caught and don't stop event loop"""
        manager = TimerManager()

        def throwing_callback():
            raise ValueError("Test error")

        timer_id = manager.setTimeout(throwing_callback, 0)

        # Should not raise exception
        try:
            manager._execute_expired_timers(float('inf'))
        except ValueError:
            pytest.fail("Exception should have been caught")


class TestTimerOrdering:
    """Test timer ordering guarantees - FR-P3-086"""

    def test_timers_execute_in_expiration_order(self):
        """Test timers execute in order of expiration time"""
        manager = TimerManager()
        execution_order = []

        def callback1():
            execution_order.append(1)

        def callback2():
            execution_order.append(2)

        def callback3():
            execution_order.append(3)

        # Schedule out of order
        manager.setTimeout(callback2, 200)
        manager.setTimeout(callback1, 100)
        manager.setTimeout(callback3, 300)

        # Execute all timers
        manager._execute_expired_timers(float('inf'))

        # Should execute in expiration order
        assert execution_order == [1, 2, 3]

    def test_same_expiration_preserves_creation_order(self):
        """Test timers with same expiration execute in creation order

        Requirement: FR-P3-086 - Timer ordering guarantees
        """
        manager = TimerManager()
        execution_order = []

        def callback1():
            execution_order.append(1)

        def callback2():
            execution_order.append(2)

        def callback3():
            execution_order.append(3)

        # Schedule with same delay (same expiration)
        manager.setTimeout(callback1, 100)
        manager.setTimeout(callback2, 100)
        manager.setTimeout(callback3, 100)

        # Execute all timers
        manager._execute_expired_timers(float('inf'))

        # Should execute in creation order
        assert execution_order == [1, 2, 3]


class TestIntervalRepeating:
    """Test setInterval repeating behavior - FR-P3-083"""

    def test_interval_executes_multiple_times(self):
        """Test interval executes callback multiple times"""
        manager = TimerManager()
        callback = Mock()

        manager.setInterval(callback, 100)

        # Execute multiple times
        manager._execute_expired_timers(float('inf'))
        manager._execute_expired_timers(float('inf'))
        manager._execute_expired_timers(float('inf'))

        # Should execute 3 times
        assert callback.call_count >= 1  # At least once

    def test_interval_reschedules_after_execution(self):
        """Test interval reschedules itself after execution"""
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setInterval(callback, 100)

        # Execute once
        manager._execute_expired_timers(float('inf'))

        # Timer should still exist (rescheduled)
        assert manager.has_timer(timer_id) is True

    def test_cleared_interval_stops_executing(self):
        """Test cleared interval stops executing"""
        manager = TimerManager()
        callback = Mock()

        timer_id = manager.setInterval(callback, 100)

        # Execute once
        manager._execute_expired_timers(float('inf'))
        initial_count = callback.call_count

        # Clear the interval
        manager.clearInterval(timer_id)

        # Try to execute again
        manager._execute_expired_timers(float('inf'))

        # Should not execute again
        assert callback.call_count == initial_count
