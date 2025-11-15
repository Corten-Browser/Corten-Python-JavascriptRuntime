"""
Performance tests for ArrayBuffer extensions
Validates non-functional requirements for transfer and resize operations
"""

import pytest
import time
from src.arraybuffer_extensions import ArrayBufferExtensions
from src.resizable_buffer import ResizableArrayBuffer
from src.growable_shared_buffer import GrowableSharedArrayBuffer


class TestPerformance:
    """Performance validation tests"""

    def test_transfer_performance_small_buffer(self):
        """Transfer <1MB buffer should complete in <1ms"""
        ext = ArrayBufferExtensions()

        # Create 512KB buffer
        class TestBuffer:
            def __init__(self):
                self.byte_length = 512 * 1024  # 512KB
                self.detached = False
                self.data = bytearray(self.byte_length)

        buffer = TestBuffer()

        # Measure transfer time
        start = time.perf_counter()
        new_buffer = ext.transfer(buffer, new_byte_length=512 * 1024)
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

        assert elapsed < 2.0, f"Transfer took {elapsed:.2f}ms, expected <2ms"

    def test_resize_performance(self):
        """Resize operation should complete in <0.5ms"""
        buffer = ResizableArrayBuffer(byte_length=1024, max_byte_length=1024 * 1024)

        # Measure resize time
        start = time.perf_counter()
        buffer.resize(512 * 1024)  # Resize to 512KB
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

        assert elapsed < 0.5, f"Resize took {elapsed:.2f}ms, expected <0.5ms"

    def test_grow_performance(self):
        """Grow operation should complete in <0.5ms"""
        buffer = GrowableSharedArrayBuffer(byte_length=1024, max_byte_length=1024 * 1024)

        # Measure grow time
        start = time.perf_counter()
        buffer.grow(512 * 1024)  # Grow to 512KB
        elapsed = (time.perf_counter() - start) * 1000  # Convert to ms

        assert elapsed < 0.5, f"Grow took {elapsed:.2f}ms, expected <0.5ms"

    def test_to_reversed_performance(self):
        """toReversed should be efficient for large arrays"""
        from src.typedarray_extensions import TypedArrayExtensions
        from unittest.mock import Mock

        ext = TypedArrayExtensions()
        array = Mock()
        array.values = list(range(10000))  # 10k elements
        array.length = 10000

        # Should complete quickly
        start = time.perf_counter()
        reversed_array = ext.to_reversed(array)
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 15.0, f"toReversed took {elapsed:.2f}ms for 10k elements"

    def test_to_sorted_performance(self):
        """toSorted should be efficient for large arrays"""
        from src.typedarray_extensions import TypedArrayExtensions
        from unittest.mock import Mock
        import random

        ext = TypedArrayExtensions()
        array = Mock()
        array.values = [random.randint(0, 10000) for _ in range(10000)]
        array.length = 10000

        # Should complete quickly (O(n log n) expected)
        start = time.perf_counter()
        sorted_array = ext.to_sorted(array)
        elapsed = (time.perf_counter() - start) * 1000

        assert elapsed < 50.0, f"toSorted took {elapsed:.2f}ms for 10k elements"
