"""
Event Loop Timer Integration

Provides integration between the timer system and the event loop.

Requirement: FR-P3-090 - Timer integration with event loop
"""

from typing import Optional
from .timers import TimerManager


class EventLoopTimerIntegration:
    """
    Helper class to integrate timers with the event loop.

    The event loop should create an instance of this class and call
    process_timers() on each iteration.
    """

    def __init__(self, timer_manager: Optional[TimerManager] = None):
        """
        Initialize event loop timer integration.

        Args:
            timer_manager: TimerManager instance (creates new one if None)
        """
        self.timer_manager = timer_manager or TimerManager()

    def process_timers(self) -> None:
        """
        Process all expired timers.

        Should be called during the macrotask phase of each event loop iteration.

        Requirement: FR-P3-085 - Timer execution as macrotasks
        """
        current_time = self.timer_manager._get_current_time()
        self.timer_manager._execute_expired_timers(current_time)

    def get_next_timer_timeout(self) -> Optional[float]:
        """
        Get time in milliseconds until next timer expires.

        Useful for the event loop to determine how long to sleep/wait.

        Returns:
            Milliseconds until next timer, or None if no timers pending
        """
        next_expiration = self.timer_manager.get_next_timer_expiration()

        if next_expiration is None:
            return None

        current_time = self.timer_manager._get_current_time()
        timeout = next_expiration - current_time

        # Don't return negative timeout
        return max(0, timeout)

    def has_pending_timers(self) -> bool:
        """
        Check if there are any pending timers.

        Returns:
            True if timers are pending, False otherwise
        """
        return self.timer_manager.get_pending_timer_count() > 0

    def setTimeout(self, callback, delay=0, *args):
        """
        Proxy to timer_manager.setTimeout for convenience.

        See TimerManager.setTimeout for documentation.
        """
        return self.timer_manager.setTimeout(callback, delay, *args)

    def clearTimeout(self, timer_id):
        """
        Proxy to timer_manager.clearTimeout for convenience.

        See TimerManager.clearTimeout for documentation.
        """
        self.timer_manager.clearTimeout(timer_id)

    def setInterval(self, callback, delay=0, *args):
        """
        Proxy to timer_manager.setInterval for convenience.

        See TimerManager.setInterval for documentation.
        """
        return self.timer_manager.setInterval(callback, delay, *args)

    def clearInterval(self, interval_id):
        """
        Proxy to timer_manager.clearInterval for convenience.

        See TimerManager.clearInterval for documentation.
        """
        self.timer_manager.clearInterval(interval_id)
