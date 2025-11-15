"""
Unit tests for ArrayBuffer class.
Tests FR-P3-051, FR-P3-057, FR-P3-058, FR-P3-066
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from array_buffer import ArrayBuffer
from exceptions import RangeError, TypeError


class TestArrayBufferConstructor:
    """Test ArrayBuffer construction (FR-P3-051)"""

    def test_create_empty_buffer(self):
        """Should create 0-byte buffer"""
        buf = ArrayBuffer(0)
        assert buf.byteLength == 0
        assert not buf.detached
        assert not buf.resizable

    def test_create_small_buffer(self):
        """Should create buffer with specified size"""
        buf = ArrayBuffer(16)
        assert buf.byteLength == 16
        assert not buf.detached

    def test_create_large_buffer(self):
        """Should handle large buffers"""
        buf = ArrayBuffer(1024 * 1024)  # 1MB
        assert buf.byteLength == 1024 * 1024

    def test_negative_length_throws(self):
        """Should throw RangeError for negative length"""
        with pytest.raises(RangeError):
            ArrayBuffer(-1)

    def test_non_integer_length_converts(self):
        """Should convert non-integer to integer"""
        buf = ArrayBuffer(16.7)
        assert buf.byteLength == 16

    def test_nan_length_throws(self):
        """Should throw RangeError for NaN"""
        with pytest.raises(RangeError):
            ArrayBuffer(float('nan'))


class TestArrayBufferResizable:
    """Test resizable ArrayBuffer (FR-P3-058, ES2024)"""

    def test_create_resizable_buffer(self):
        """Should create resizable buffer with maxByteLength"""
        buf = ArrayBuffer(16, {'maxByteLength': 64})
        assert buf.byteLength == 16
        assert buf.maxByteLength == 64
        assert buf.resizable

    def test_fixed_buffer_not_resizable(self):
        """Fixed buffers should not be resizable"""
        buf = ArrayBuffer(16)
        assert not buf.resizable
        assert buf.maxByteLength == 16  # Same as byteLength for fixed

    def test_max_byte_length_less_than_length_throws(self):
        """maxByteLength < byteLength should throw"""
        with pytest.raises(RangeError):
            ArrayBuffer(64, {'maxByteLength': 16})

    def test_resize_fixed_buffer_throws(self):
        """Cannot resize fixed buffer"""
        buf = ArrayBuffer(16)
        with pytest.raises(TypeError):
            buf.resize(32)

    def test_resize_within_max(self):
        """Should resize within maxByteLength"""
        buf = ArrayBuffer(16, {'maxByteLength': 64})
        buf.resize(32)
        assert buf.byteLength == 32

    def test_resize_beyond_max_throws(self):
        """Resizing beyond maxByteLength throws"""
        buf = ArrayBuffer(16, {'maxByteLength': 64})
        with pytest.raises(RangeError):
            buf.resize(128)


class TestArrayBufferSlice:
    """Test ArrayBuffer.slice() (FR-P3-051)"""

    def test_slice_entire_buffer(self):
        """slice() with no args copies entire buffer"""
        buf1 = ArrayBuffer(16)
        buf2 = buf1.slice()
        assert buf2.byteLength == 16
        assert buf2 is not buf1  # Different object

    def test_slice_with_start(self):
        """slice(start) copies from start to end"""
        buf1 = ArrayBuffer(16)
        buf2 = buf1.slice(8)
        assert buf2.byteLength == 8

    def test_slice_with_start_and_end(self):
        """slice(start, end) copies range"""
        buf1 = ArrayBuffer(16)
        buf2 = buf1.slice(4, 12)
        assert buf2.byteLength == 8

    def test_slice_negative_indices(self):
        """Negative indices count from end"""
        buf1 = ArrayBuffer(16)
        buf2 = buf1.slice(-8, -4)
        assert buf2.byteLength == 4

    def test_slice_detached_buffer_throws(self):
        """Slicing detached buffer throws"""
        buf = ArrayBuffer(16)
        buf.transfer()  # Detaches buf
        with pytest.raises(TypeError):
            buf.slice()

    def test_slice_clamping(self):
        """Out-of-range indices are clamped"""
        buf1 = ArrayBuffer(16)
        buf2 = buf1.slice(-100, 100)
        assert buf2.byteLength == 16


class TestArrayBufferTransfer:
    """Test ArrayBuffer transfer/detach (FR-P3-057, ES2024)"""

    def test_transfer_same_size(self):
        """transfer() creates new buffer, detaches old"""
        buf1 = ArrayBuffer(16)
        buf2 = buf1.transfer()

        assert buf2.byteLength == 16
        assert not buf2.detached
        assert buf1.detached

    def test_transfer_larger(self):
        """transfer() can increase size"""
        buf1 = ArrayBuffer(16)
        buf2 = buf1.transfer(32)

        assert buf2.byteLength == 32
        assert buf1.detached

    def test_transfer_smaller(self):
        """transfer() can decrease size"""
        buf1 = ArrayBuffer(32)
        buf2 = buf1.transfer(16)

        assert buf2.byteLength == 16
        assert buf1.detached

    def test_transfer_detached_throws(self):
        """Transferring already-detached buffer throws"""
        buf = ArrayBuffer(16)
        buf.transfer()

        with pytest.raises(TypeError):
            buf.transfer()

    def test_transfer_preserves_data(self):
        """transfer() preserves existing data"""
        # We'll test this via TypedArray in integration tests
        # Just verify the basic operation works
        buf1 = ArrayBuffer(16)
        buf2 = buf1.transfer(16)
        assert buf2.byteLength == 16


class TestArrayBufferDetached:
    """Test detached buffer behavior (FR-P3-069)"""

    def test_detached_property_initial(self):
        """New buffer is not detached"""
        buf = ArrayBuffer(16)
        assert not buf.detached

    def test_detached_after_transfer(self):
        """Buffer is detached after transfer"""
        buf1 = ArrayBuffer(16)
        buf1.transfer()
        assert buf1.detached

    def test_byteLength_on_detached(self):
        """byteLength is 0 for detached buffer"""
        buf = ArrayBuffer(16)
        buf.transfer()
        assert buf.byteLength == 0


class TestArrayBufferIsView:
    """Test ArrayBuffer.isView() static method (FR-P3-066)"""

    def test_is_view_with_non_view(self):
        """isView() returns false for non-views"""
        assert not ArrayBuffer.isView({})
        assert not ArrayBuffer.isView([])
        assert not ArrayBuffer.isView(42)
        assert not ArrayBuffer.isView("string")
        assert not ArrayBuffer.isView(None)

    def test_is_view_with_array_buffer(self):
        """isView() returns false for ArrayBuffer itself"""
        buf = ArrayBuffer(16)
        assert not ArrayBuffer.isView(buf)

    # TypedArray and DataView tests will be in integration tests


class TestArrayBufferEdgeCases:
    """Test edge cases and error conditions"""

    def test_very_large_buffer(self):
        """Should handle very large buffers (within memory limits)"""
        # 100MB - might be too large for some systems
        try:
            buf = ArrayBuffer(100 * 1024 * 1024)
            assert buf.byteLength == 100 * 1024 * 1024
        except MemoryError:
            pytest.skip("System doesn't have enough memory")

    def test_zero_length_slice(self):
        """Slice with start == end creates empty buffer"""
        buf1 = ArrayBuffer(16)
        buf2 = buf1.slice(8, 8)
        assert buf2.byteLength == 0

    def test_inverted_slice_indices(self):
        """Slice with start > end creates empty buffer"""
        buf1 = ArrayBuffer(16)
        buf2 = buf1.slice(12, 8)
        assert buf2.byteLength == 0
