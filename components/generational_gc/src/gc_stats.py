"""
GCStats - Statistics tracking for garbage collection.

Tracks minor and major collection statistics including counts,
bytes allocated/freed, pause times, and throughput.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class GCStats:
    """
    Statistics for garbage collection.

    Tracks cumulative statistics for minor and major GCs including
    collection counts, memory management, and performance metrics.

    Attributes:
        minor_collections (int): Number of minor GCs performed
        major_collections (int): Number of major GCs performed
        bytes_allocated (int): Total bytes allocated
        bytes_freed (int): Total bytes freed by GC
        pause_time_ms (float): Total GC pause time in milliseconds
        throughput_percent (float): Application throughput (0-100%)

    Example:
        >>> stats = GCStats()
        >>> stats.minor_collections = 10
        >>> stats.major_collections = 2
        >>> stats.throughput_percent
        0.0
    """

    minor_collections: int = 0
    major_collections: int = 0
    bytes_allocated: int = 0
    bytes_freed: int = 0
    pause_time_ms: float = 0.0
    throughput_percent: float = 0.0

    # Internal tracking for throughput calculation
    _minor_pause_times: List[float] = field(default_factory=list, repr=False)
    _major_pause_times: List[float] = field(default_factory=list, repr=False)
    _total_time_ms: float = field(default=0.0, repr=False)

    def record_minor_gc(self, pause_ms: float, bytes_freed: int) -> None:
        """
        Record a minor GC event.

        Args:
            pause_ms: Pause time in milliseconds
            bytes_freed: Bytes reclaimed by GC

        Example:
            >>> stats = GCStats()
            >>> stats.record_minor_gc(pause_ms=3.5, bytes_freed=1024)
            >>> stats.minor_collections
            1
            >>> stats.pause_time_ms
            3.5
        """
        self.minor_collections += 1
        self.bytes_freed += bytes_freed
        self.pause_time_ms += pause_ms
        self._minor_pause_times.append(pause_ms)
        self._total_time_ms += pause_ms
        self._update_throughput()

    def record_major_gc(self, pause_ms: float, bytes_freed: int) -> None:
        """
        Record a major GC event.

        Args:
            pause_ms: Pause time in milliseconds
            bytes_freed: Bytes reclaimed by GC

        Example:
            >>> stats = GCStats()
            >>> stats.record_major_gc(pause_ms=45.0, bytes_freed=10240)
            >>> stats.major_collections
            1
            >>> stats.pause_time_ms
            45.0
        """
        self.major_collections += 1
        self.bytes_freed += bytes_freed
        self.pause_time_ms += pause_ms
        self._major_pause_times.append(pause_ms)
        self._total_time_ms += pause_ms
        self._update_throughput()

    def record_allocation(self, bytes_allocated: int) -> None:
        """
        Record memory allocation.

        Args:
            bytes_allocated: Bytes allocated

        Example:
            >>> stats = GCStats()
            >>> stats.record_allocation(bytes_allocated=512)
            >>> stats.bytes_allocated
            512
        """
        self.bytes_allocated += bytes_allocated

    def _update_throughput(self) -> None:
        """
        Update throughput percentage.

        Throughput = (total_time - gc_pause_time) / total_time * 100
        """
        if self._total_time_ms > 0:
            app_time = self._total_time_ms - self.pause_time_ms
            self.throughput_percent = (app_time / self._total_time_ms) * 100
        else:
            self.throughput_percent = 100.0  # No GC yet

    def get_average_minor_pause(self) -> float:
        """
        Get average minor GC pause time.

        Returns:
            Average pause time in milliseconds, or 0.0 if no minor GCs

        Example:
            >>> stats = GCStats()
            >>> stats.record_minor_gc(pause_ms=2.0, bytes_freed=100)
            >>> stats.record_minor_gc(pause_ms=4.0, bytes_freed=200)
            >>> stats.get_average_minor_pause()
            3.0
        """
        if not self._minor_pause_times:
            return 0.0
        return sum(self._minor_pause_times) / len(self._minor_pause_times)

    def get_average_major_pause(self) -> float:
        """
        Get average major GC pause time.

        Returns:
            Average pause time in milliseconds, or 0.0 if no major GCs

        Example:
            >>> stats = GCStats()
            >>> stats.record_major_gc(pause_ms=40.0, bytes_freed=1000)
            >>> stats.record_major_gc(pause_ms=50.0, bytes_freed=2000)
            >>> stats.get_average_major_pause()
            45.0
        """
        if not self._major_pause_times:
            return 0.0
        return sum(self._major_pause_times) / len(self._major_pause_times)

    def to_dict(self) -> dict:
        """
        Convert stats to dictionary.

        Returns:
            Dictionary representation of stats

        Example:
            >>> stats = GCStats(minor_collections=5, major_collections=1)
            >>> d = stats.to_dict()
            >>> d['minor_collections']
            5
        """
        return {
            'minor_collections': self.minor_collections,
            'major_collections': self.major_collections,
            'bytes_allocated': self.bytes_allocated,
            'bytes_freed': self.bytes_freed,
            'pause_time_ms': self.pause_time_ms,
            'throughput_percent': self.throughput_percent,
            'avg_minor_pause_ms': self.get_average_minor_pause(),
            'avg_major_pause_ms': self.get_average_major_pause()
        }

    def __repr__(self) -> str:
        """
        Get string representation.

        Returns:
            String with key statistics
        """
        return (f"GCStats(minor={self.minor_collections}, major={self.major_collections}, "
                f"freed={self.bytes_freed}, pause={self.pause_time_ms:.2f}ms)")
