"""
Unit tests for timer_queue.py - Priority queue implementation

Requirements: FR-P3-086 (Timer ordering guarantees)
"""

import pytest
import time
from src.timer_queue import TimerQueue, TimerInfo


class TestTimerQueue:
    """Test priority queue for timers ordered by expiration time"""

    def test_create_empty_queue(self):
        """Test creating an empty timer queue"""
        queue = TimerQueue()
        assert queue.is_empty() is True
        assert queue.size() == 0

    def test_insert_single_timer(self):
        """Test inserting a single timer"""
        queue = TimerQueue()
        timer = TimerInfo(
            timer_id=1,
            callback=lambda: None,
            args=[],
            expiration=1000.0,
            repeat=False,
            interval=0,
            nesting_level=0
        )
        queue.insert(timer)
        assert queue.is_empty() is False
        assert queue.size() == 1

    def test_peek_min_without_remove(self):
        """Test peeking at next timer without removing it"""
        queue = TimerQueue()
        timer = TimerInfo(
            timer_id=1,
            callback=lambda: None,
            args=[],
            expiration=1000.0,
            repeat=False,
            interval=0,
            nesting_level=0
        )
        queue.insert(timer)

        # Peek should not remove
        peeked = queue.peek()
        assert peeked.timer_id == 1
        assert queue.size() == 1

    def test_extract_min_removes_timer(self):
        """Test extracting minimum timer removes it"""
        queue = TimerQueue()
        timer = TimerInfo(
            timer_id=1,
            callback=lambda: None,
            args=[],
            expiration=1000.0,
            repeat=False,
            interval=0,
            nesting_level=0
        )
        queue.insert(timer)

        extracted = queue.extract_min()
        assert extracted.timer_id == 1
        assert queue.is_empty() is True

    def test_priority_ordering_by_expiration(self):
        """Test timers are ordered by expiration time (min-heap)

        Requirement: FR-P3-086 - Timer ordering guarantees
        """
        queue = TimerQueue()

        # Insert timers out of order
        timer3 = TimerInfo(expiration=3000.0, timer_id=3, callback=lambda: None, args=[], repeat=False, interval=0, nesting_level=0)
        timer1 = TimerInfo(expiration=1000.0, timer_id=1, callback=lambda: None, args=[], repeat=False, interval=0, nesting_level=0)
        timer2 = TimerInfo(expiration=2000.0, timer_id=2, callback=lambda: None, args=[], repeat=False, interval=0, nesting_level=0)

        queue.insert(timer3)
        queue.insert(timer1)
        queue.insert(timer2)

        # Extract in priority order (earliest expiration first)
        assert queue.extract_min().timer_id == 1  # 1000ms
        assert queue.extract_min().timer_id == 2  # 2000ms
        assert queue.extract_min().timer_id == 3  # 3000ms

    def test_same_expiration_preserves_insertion_order(self):
        """Test timers with same expiration fire in creation order

        Requirement: FR-P3-086 - Timer ordering guarantees
        """
        queue = TimerQueue()

        # Insert multiple timers with same expiration
        timer1 = TimerInfo(expiration=1000.0, timer_id=1, callback=lambda: None, args=[], repeat=False, interval=0, nesting_level=0)
        timer2 = TimerInfo(expiration=1000.0, timer_id=2, callback=lambda: None, args=[], repeat=False, interval=0, nesting_level=0)
        timer3 = TimerInfo(expiration=1000.0, timer_id=3, callback=lambda: None, args=[], repeat=False, interval=0, nesting_level=0)

        queue.insert(timer1)
        queue.insert(timer2)
        queue.insert(timer3)

        # Should extract in insertion order
        assert queue.extract_min().timer_id == 1
        assert queue.extract_min().timer_id == 2
        assert queue.extract_min().timer_id == 3

    def test_remove_specific_timer_by_id(self):
        """Test removing a specific timer by ID (for clearTimeout/clearInterval)"""
        queue = TimerQueue()

        timer1 = TimerInfo(expiration=1000.0, timer_id=1, callback=lambda: None, args=[], repeat=False, interval=0, nesting_level=0)
        timer2 = TimerInfo(expiration=2000.0, timer_id=2, callback=lambda: None, args=[], repeat=False, interval=0, nesting_level=0)
        timer3 = TimerInfo(expiration=3000.0, timer_id=3, callback=lambda: None, args=[], repeat=False, interval=0, nesting_level=0)

        queue.insert(timer1)
        queue.insert(timer2)
        queue.insert(timer3)

        # Remove timer 2
        removed = queue.remove_by_id(2)
        assert removed is True
        assert queue.size() == 2

        # Verify remaining timers
        assert queue.extract_min().timer_id == 1
        assert queue.extract_min().timer_id == 3

    def test_remove_nonexistent_timer(self):
        """Test removing a timer that doesn't exist"""
        queue = TimerQueue()
        timer1 = TimerInfo(1, lambda: None, [], 1000.0, False, 0, 0)
        queue.insert(timer1)

        # Try to remove non-existent timer
        removed = queue.remove_by_id(999)
        assert removed is False
        assert queue.size() == 1

    def test_peek_empty_queue(self):
        """Test peeking at empty queue returns None"""
        queue = TimerQueue()
        assert queue.peek() is None

    def test_extract_from_empty_queue(self):
        """Test extracting from empty queue returns None"""
        queue = TimerQueue()
        assert queue.extract_min() is None

    def test_get_expired_timers(self):
        """Test getting all expired timers at current time"""
        queue = TimerQueue()
        current_time = 1500.0

        # Insert timers before and after current time
        timer1 = TimerInfo(expiration=1000.0, timer_id=1, callback=lambda: None, args=[], repeat=False, interval=0, nesting_level=0)  # Expired
        timer2 = TimerInfo(expiration=1200.0, timer_id=2, callback=lambda: None, args=[], repeat=False, interval=0, nesting_level=0)  # Expired
        timer3 = TimerInfo(expiration=2000.0, timer_id=3, callback=lambda: None, args=[], repeat=False, interval=0, nesting_level=0)  # Not expired

        queue.insert(timer1)
        queue.insert(timer2)
        queue.insert(timer3)

        # Get expired timers
        expired = queue.get_expired_timers(current_time)
        assert len(expired) == 2
        assert expired[0].timer_id == 1
        assert expired[1].timer_id == 2

        # Only timer3 should remain
        assert queue.size() == 1
        assert queue.peek().timer_id == 3


class TestTimerInfo:
    """Test TimerInfo data structure"""

    def test_create_timeout_timer(self):
        """Test creating a timeout (one-shot) timer"""
        callback = lambda: None
        timer = TimerInfo(
            timer_id=42,
            callback=callback,
            args=[1, 2, 3],
            expiration=5000.0,
            repeat=False,
            interval=0,
            nesting_level=0
        )

        assert timer.timer_id == 42
        assert timer.callback is callback
        assert timer.args == [1, 2, 3]
        assert timer.expiration == 5000.0
        assert timer.repeat is False
        assert timer.interval == 0
        assert timer.nesting_level == 0

    def test_create_interval_timer(self):
        """Test creating an interval (repeating) timer"""
        callback = lambda: None
        timer = TimerInfo(
            timer_id=99,
            callback=callback,
            args=[],
            expiration=1000.0,
            repeat=True,
            interval=100,
            nesting_level=0
        )

        assert timer.timer_id == 99
        assert timer.repeat is True
        assert timer.interval == 100

    def test_timer_comparison_by_expiration(self):
        """Test timers can be compared by expiration time"""
        timer1 = TimerInfo(1, lambda: None, [], 1000.0, False, 0, 0)
        timer2 = TimerInfo(2, lambda: None, [], 2000.0, False, 0, 0)

        # Timer1 should be "less than" timer2 (earlier expiration)
        assert timer1 < timer2
        assert not (timer2 < timer1)

    def test_timer_comparison_same_expiration_uses_id(self):
        """Test timers with same expiration compare by timer_id (insertion order)"""
        timer1 = TimerInfo(1, lambda: None, [], 1000.0, False, 0, 0)
        timer2 = TimerInfo(2, lambda: None, [], 1000.0, False, 0, 0)

        # Lower ID comes first (insertion order preservation)
        assert timer1 < timer2
        assert not (timer2 < timer1)
