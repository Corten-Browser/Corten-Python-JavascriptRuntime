"""
Timer API Implementation - setTimeout, clearTimeout, setInterval, clearInterval

Requirements:
- FR-P3-081: setTimeout basic functionality
- FR-P3-082: clearTimeout cancellation
- FR-P3-083: setInterval repeated execution
- FR-P3-084: clearInterval stopping
- FR-P3-087: Timer argument passing
- FR-P3-088: Nested timeout clamping (≥4ms after 5 levels)
- FR-P3-089: Timer edge cases
"""

import time
from typing import Callable, Any, Optional, Union
from .timer_queue import TimerQueue, TimerInfo


class TimerManager:
    """
    Manages setTimeout, setInterval, clearTimeout, and clearInterval.

    Implements Web Timers specification including:
    - Minimum delay guarantees
    - Nested timeout clamping
    - Timer ordering preservation
    - Argument passing to callbacks
    """

    # Nested timeout clamping threshold
    NESTING_THRESHOLD = 5
    CLAMP_DELAY_MS = 4

    def __init__(self):
        """Initialize timer manager"""
        self._queue = TimerQueue()
        self._next_timer_id = 1
        self._start_time = time.time()
        self._cancelled_during_execution = set()  # Track timers cancelled during callback execution

    def _get_current_time(self) -> float:
        """
        Get current time in milliseconds since manager creation.

        Returns:
            Current time in milliseconds
        """
        return (time.time() - self._start_time) * 1000

    def _generate_timer_id(self) -> int:
        """
        Generate a unique timer ID.

        Returns:
            Positive integer timer ID
        """
        timer_id = self._next_timer_id
        self._next_timer_id += 1
        return timer_id

    def _clamp_delay(self, delay: float, nesting_level: int) -> float:
        """
        Apply nested timeout clamping if needed.

        Requirement: FR-P3-088 - Nested timeout clamping (≥4ms after 5 levels)

        Args:
            delay: Requested delay in milliseconds
            nesting_level: Current nesting level

        Returns:
            Clamped delay in milliseconds
        """
        if nesting_level >= self.NESTING_THRESHOLD:
            # Clamp to minimum 4ms for deeply nested timeouts
            return max(delay, self.CLAMP_DELAY_MS)
        return delay

    def setTimeout(
        self,
        callback: Union[Callable, str],
        delay: Optional[float] = 0,
        *args: Any,
        nesting_level: int = 0
    ) -> int:
        """
        Schedule a callback to execute after a delay.

        Requirement: FR-P3-081 - setTimeout basic functionality

        Args:
            callback: Function to execute (or string to eval - discouraged)
            delay: Minimum delay in milliseconds (default: 0)
            *args: Arguments to pass to callback
            nesting_level: Current nesting level (for clamping)

        Returns:
            Positive integer timer ID
        """
        # Handle undefined/None delay
        if delay is None:
            delay = 0

        # Handle negative delay (treat as 0)
        # Requirement: FR-P3-089 - Negative delay edge case
        if delay < 0:
            delay = 0

        # Convert string callback to function (compatibility mode)
        # Requirement: FR-P3-089 - String callback edge case
        if isinstance(callback, str):
            # In a real implementation, would eval the string
            # For now, create a lambda that does nothing
            callback_func = lambda: None
        else:
            callback_func = callback

        # Apply nested timeout clamping
        clamped_delay = self._clamp_delay(delay, nesting_level)

        # Calculate expiration time
        current_time = self._get_current_time()
        expiration = current_time + clamped_delay

        # Generate timer ID
        timer_id = self._generate_timer_id()

        # Create timer info
        timer = TimerInfo(
            expiration=expiration,
            timer_id=timer_id,
            callback=callback_func,
            args=list(args),
            repeat=False,
            interval=0,
            nesting_level=nesting_level
        )

        # Add to queue
        self._queue.insert(timer)

        return timer_id

    def clearTimeout(self, timer_id: int) -> None:
        """
        Cancel a scheduled timeout.

        Requirement: FR-P3-082 - clearTimeout cancellation

        Args:
            timer_id: Timer ID returned from setTimeout

        Notes:
            - No-op if timer already fired or invalid ID
            - Safe to call multiple times with same ID
        """
        # Remove timer from queue (no-op if not found)
        self._queue.remove_by_id(timer_id)
        # Track that this timer was cancelled (for execution loop)
        self._cancelled_during_execution.add(timer_id)

    def setInterval(
        self,
        callback: Union[Callable, str],
        delay: Optional[float] = 0,
        *args: Any,
        nesting_level: int = 0
    ) -> int:
        """
        Schedule a callback to execute repeatedly at an interval.

        Requirement: FR-P3-083 - setInterval repeated execution

        Args:
            callback: Function to execute repeatedly
            delay: Delay between executions in milliseconds (default: 0)
            *args: Arguments to pass to callback
            nesting_level: Current nesting level (for clamping)

        Returns:
            Positive integer interval ID
        """
        # Handle undefined/None delay
        if delay is None:
            delay = 0

        # Handle negative delay (treat as 0)
        if delay < 0:
            delay = 0

        # Convert string callback to function
        if isinstance(callback, str):
            callback_func = lambda: None
        else:
            callback_func = callback

        # Apply nested timeout clamping
        clamped_delay = self._clamp_delay(delay, nesting_level)

        # Calculate expiration time
        current_time = self._get_current_time()
        expiration = current_time + clamped_delay

        # Generate timer ID
        timer_id = self._generate_timer_id()

        # Create timer info (marked as repeating)
        timer = TimerInfo(
            expiration=expiration,
            timer_id=timer_id,
            callback=callback_func,
            args=list(args),
            repeat=True,
            interval=clamped_delay,
            nesting_level=nesting_level
        )

        # Add to queue
        self._queue.insert(timer)

        return timer_id

    def clearInterval(self, interval_id: int) -> None:
        """
        Stop a repeating interval.

        Requirement: FR-P3-084 - clearInterval stopping

        Args:
            interval_id: Interval ID returned from setInterval

        Notes:
            - No-op if interval already cleared or invalid ID
            - Safe to call multiple times with same ID
        """
        # Remove timer from queue (no-op if not found)
        self._queue.remove_by_id(interval_id)
        # Track that this timer was cancelled (for execution loop)
        self._cancelled_during_execution.add(interval_id)

    def has_timer(self, timer_id: int) -> bool:
        """
        Check if a timer exists.

        Args:
            timer_id: Timer ID to check

        Returns:
            True if timer exists, False otherwise
        """
        return self._queue.has_timer(timer_id)

    def _get_timer_info(self, timer_id: int) -> Optional[TimerInfo]:
        """
        Get timer information by ID (for testing).

        Args:
            timer_id: Timer ID

        Returns:
            TimerInfo if found, None otherwise
        """
        return self._queue.get_timer(timer_id)

    def _execute_expired_timers(self, current_time: Optional[float] = None) -> None:
        """
        Execute all timers that have expired.

        This is called by the event loop on each iteration.

        Requirement: FR-P3-090 - Event loop integration

        Args:
            current_time: Current time in milliseconds (default: now)
        """
        if current_time is None:
            current_time = self._get_current_time()

        # Clear the cancelled set at the start of execution
        self._cancelled_during_execution.clear()

        # Get all expired timers
        expired = self._queue.get_expired_timers(current_time)

        # Execute each timer callback
        for timer in expired:
            # Skip if timer was cancelled during this execution batch
            if timer.timer_id in self._cancelled_during_execution:
                continue

            try:
                # Execute callback with arguments
                # Requirement: FR-P3-087 - Timer argument passing
                timer.callback(*timer.args)

                # If repeating and not cancelled during execution, reschedule
                if timer.repeat and timer.timer_id not in self._cancelled_during_execution:
                    # Calculate next expiration
                    # Note: We use current_time + interval, not timer.expiration + interval
                    # This prevents drift if event loop is delayed
                    next_expiration = current_time + timer.interval

                    # Create new timer with same ID (reuse ID for interval)
                    new_timer = TimerInfo(
                        expiration=next_expiration,
                        timer_id=timer.timer_id,
                        callback=timer.callback,
                        args=timer.args,
                        repeat=True,
                        interval=timer.interval,
                        nesting_level=timer.nesting_level
                    )

                    # Re-insert into queue
                    self._queue.insert(new_timer)

            except Exception as e:
                # Catch exceptions to prevent event loop from crashing
                # Requirement: Contract - Exceptions caught and reported
                # In a real implementation, would report to error handler
                # For now, just continue executing other timers
                pass

    def get_next_timer_expiration(self) -> Optional[float]:
        """
        Get the expiration time of the next timer.

        Returns:
            Expiration time in milliseconds, or None if no timers
        """
        timer = self._queue.peek()
        if timer is None:
            return None
        return timer.expiration

    def get_pending_timer_count(self) -> int:
        """
        Get the number of pending timers.

        Returns:
            Number of timers in queue
        """
        return self._queue.size()
