"""
Timer Queue Implementation - Priority queue (min-heap) for timers

Provides efficient timer management ordered by expiration time.
Requirement: FR-P3-086 - Timer ordering guarantees
"""

import heapq
from dataclasses import dataclass, field
from typing import Callable, Any, Optional, List


@dataclass(order=True)
class TimerInfo:
    """
    Information about a scheduled timer.

    Ordered by expiration time (earliest first), with timer_id as tiebreaker
    to preserve insertion order for timers with the same expiration.
    """
    # Fields used for comparison (order matters)
    expiration: float = field(compare=True)
    timer_id: int = field(compare=True)

    # Fields not used for comparison
    callback: Callable = field(compare=False, default=None)
    args: List[Any] = field(compare=False, default_factory=list)
    repeat: bool = field(compare=False, default=False)
    interval: float = field(compare=False, default=0)
    nesting_level: int = field(compare=False, default=0)

    def __post_init__(self):
        """Ensure args is always a list"""
        if self.args is None:
            self.args = []


class TimerQueue:
    """
    Priority queue for timers ordered by expiration time.

    Uses a min-heap for O(log n) insertion and extraction.
    Timers with earlier expiration times have higher priority.
    Timers with the same expiration time are ordered by timer_id (creation order).
    """

    def __init__(self):
        """Initialize empty timer queue"""
        self._heap: List[TimerInfo] = []
        self._timer_map: dict[int, TimerInfo] = {}  # For O(1) lookup by ID

    def is_empty(self) -> bool:
        """Check if queue is empty"""
        return len(self._heap) == 0

    def size(self) -> int:
        """Get number of timers in queue"""
        return len(self._heap)

    def insert(self, timer: TimerInfo) -> None:
        """
        Insert a timer into the queue.

        Time complexity: O(log n)

        Args:
            timer: TimerInfo to insert
        """
        heapq.heappush(self._heap, timer)
        self._timer_map[timer.timer_id] = timer

    def peek(self) -> Optional[TimerInfo]:
        """
        Peek at the next timer without removing it.

        Time complexity: O(1)

        Returns:
            Next timer to expire, or None if queue is empty
        """
        if self.is_empty():
            return None
        return self._heap[0]

    def extract_min(self) -> Optional[TimerInfo]:
        """
        Remove and return the next timer to expire.

        Time complexity: O(log n)

        Returns:
            Next timer to expire, or None if queue is empty
        """
        if self.is_empty():
            return None

        timer = heapq.heappop(self._heap)
        self._timer_map.pop(timer.timer_id, None)
        return timer

    def remove_by_id(self, timer_id: int) -> bool:
        """
        Remove a specific timer by ID.

        Time complexity: O(n) - must search heap and re-heapify

        Args:
            timer_id: ID of timer to remove

        Returns:
            True if timer was found and removed, False otherwise
        """
        # Check if timer exists
        if timer_id not in self._timer_map:
            return False

        # Remove from map
        timer = self._timer_map.pop(timer_id)

        # Find and remove from heap
        try:
            index = self._heap.index(timer)
            # Replace with last element and re-heapify
            if index < len(self._heap) - 1:
                self._heap[index] = self._heap[-1]
                self._heap.pop()
                # Re-heapify from index
                if index < len(self._heap):
                    heapq._siftup(self._heap, index)
                    heapq._siftdown(self._heap, 0, index)
            else:
                # Last element, just pop
                self._heap.pop()
            return True
        except ValueError:
            # Timer not in heap (shouldn't happen if map is in sync)
            return False

    def get_expired_timers(self, current_time: float) -> List[TimerInfo]:
        """
        Get and remove all timers that have expired by current_time.

        Time complexity: O(k log n) where k is number of expired timers

        Args:
            current_time: Current timestamp

        Returns:
            List of expired timers in expiration order
        """
        expired = []

        while not self.is_empty():
            timer = self.peek()
            if timer is None or timer.expiration > current_time:
                break

            # Timer has expired
            expired.append(self.extract_min())

        return expired

    def has_timer(self, timer_id: int) -> bool:
        """
        Check if a timer with the given ID exists in the queue.

        Time complexity: O(1)

        Args:
            timer_id: ID to check

        Returns:
            True if timer exists, False otherwise
        """
        return timer_id in self._timer_map

    def get_timer(self, timer_id: int) -> Optional[TimerInfo]:
        """
        Get timer information by ID without removing it.

        Time complexity: O(1)

        Args:
            timer_id: ID of timer

        Returns:
            TimerInfo if found, None otherwise
        """
        return self._timer_map.get(timer_id)
