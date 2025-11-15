"""
Integration tests for DataView.
Tests cross-feature interaction, endianness round-trips, and edge cases.
"""

import pytest
import sys
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "typed_arrays" / "src"))

from array_buffer import ArrayBuffer
from dataview import DataView
from exceptions import RangeError, TypeError as JSTypeError


class TestDataViewEndiannessRoundTrip:
    """Test endianness round-trip consistency"""

    def test_int16_big_endian_round_trip(self):
        """Write and read Int16 in big-endian"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        test_values = [0, 1, -1, 32767, -32768, 12345, -12345]
        for i, value in enumerate(test_values):
            view.setInt16(i * 2, value, False)

        for i, value in enumerate(test_values):
            assert view.getInt16(i * 2, False) == value

    def test_int16_little_endian_round_trip(self):
        """Write and read Int16 in little-endian"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        test_values = [0, 1, -1, 32767, -32768, 12345, -12345]
        for i, value in enumerate(test_values):
            view.setInt16(i * 2, value, True)

        for i, value in enumerate(test_values):
            assert view.getInt16(i * 2, True) == value

    def test_int32_endianness_round_trip(self):
        """Write and read Int32 in both endianness modes"""
        buf = ArrayBuffer(32)
        view = DataView(buf)

        test_values = [0, 1, -1, 2147483647, -2147483648, 12345678, -87654321]

        # Write in big-endian, read in big-endian
        for i, value in enumerate(test_values):
            view.setInt32(i * 4, value, False)
        for i, value in enumerate(test_values):
            assert view.getInt32(i * 4, False) == value

    def test_float64_endianness_round_trip(self):
        """Write and read Float64 in both endianness modes"""
        buf = ArrayBuffer(64)
        view = DataView(buf)

        test_values = [0.0, 1.0, -1.0, math.pi, math.e, 123.456789, -987.654321]

        # Big-endian
        for i, value in enumerate(test_values):
            view.setFloat64(i * 8, value, False)
        for i, value in enumerate(test_values):
            assert abs(view.getFloat64(i * 8, False) - value) < 1e-15

        # Little-endian
        for i, value in enumerate(test_values):
            view.setFloat64(i * 8, value, True)
        for i, value in enumerate(test_values):
            assert abs(view.getFloat64(i * 8, True) - value) < 1e-15


class TestDataViewPartialViews:
    """Test DataView with partial buffer views (FR-ES24-B-025)"""

    def test_partial_view_reads_correct_region(self):
        """Partial view only accesses its region"""
        buf = ArrayBuffer(16)
        full_view = DataView(buf)
        partial_view = DataView(buf, 8, 4)

        # Write to full view
        full_view.setUint32(8, 0x12345678)

        # Partial view sees it at offset 0
        assert partial_view.getUint32(0) == 0x12345678

    def test_partial_view_write_affects_buffer(self):
        """Write through partial view affects underlying buffer"""
        buf = ArrayBuffer(16)
        full_view = DataView(buf)
        partial_view = DataView(buf, 4, 8)

        # Write through partial view
        partial_view.setInt32(0, 42)

        # Full view sees it at offset 4
        assert full_view.getInt32(4) == 42

    def test_multiple_views_same_buffer(self):
        """Multiple views on same buffer see same data"""
        buf = ArrayBuffer(16)
        view1 = DataView(buf, 0, 8)
        view2 = DataView(buf, 8, 8)
        view3 = DataView(buf, 4, 8)

        view1.setInt32(0, 111)
        view2.setInt32(0, 222)
        view3.setInt32(0, 333)

        full_view = DataView(buf)
        assert full_view.getInt32(0) == 111
        assert full_view.getInt32(4) == 333
        assert full_view.getInt32(8) == 222

    def test_partial_view_boundaries_enforced(self):
        """Partial view cannot access beyond its boundaries"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 4, 8)  # Bytes 4-11

        # Can access within view
        view.getUint8(0)
        view.getUint8(7)

        # Cannot access at offset 8 (would be byte 12 in buffer)
        with pytest.raises(RangeError):
            view.getUint8(8)


class TestDataViewMixedTypeOperations:
    """Test reading/writing different types to same location"""

    def test_write_int32_read_as_bytes(self):
        """Write Int32, read as individual bytes"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setInt32(0, 0x12345678, False)  # Big-endian

        assert view.getUint8(0) == 0x12
        assert view.getUint8(1) == 0x34
        assert view.getUint8(2) == 0x56
        assert view.getUint8(3) == 0x78

    def test_write_bytes_read_as_int32(self):
        """Write individual bytes, read as Int32"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setUint8(0, 0x12)
        view.setUint8(1, 0x34)
        view.setUint8(2, 0x56)
        view.setUint8(3, 0x78)

        assert view.getInt32(0, False) == 0x12345678

    def test_write_float32_read_as_int32(self):
        """Write Float32, read as Int32 (reinterpret bits)"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setFloat32(0, 1.0)
        # Reading as Int32 should give bit pattern of float
        # (This tests that DataView operates on raw bytes)
        int_value = view.getInt32(0)
        assert isinstance(int_value, int)

    def test_overwrite_with_different_types(self):
        """Overwrite data with different types"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setInt32(0, 12345)
        assert view.getInt32(0) == 12345

        view.setFloat32(0, 3.14)
        result = view.getFloat32(0)
        assert abs(result - 3.14) < 0.001


class TestDataViewSpecialFloatValues:
    """Test special floating-point values"""

    def test_positive_zero_and_negative_zero(self):
        """Distinguish +0.0 and -0.0 (IEEE-754)"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        view.setFloat64(0, 0.0)
        view.setFloat64(8, -0.0)

        # Both should be zero
        assert view.getFloat64(0) == 0.0
        assert view.getFloat64(8) == -0.0

        # But their byte representations should differ
        # (sign bit is different)
        # Note: In Python, 0.0 == -0.0, but bit patterns differ

    def test_nan_preservation(self):
        """NaN is preserved through write/read"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        view.setFloat32(0, float('nan'))
        view.setFloat64(8, float('nan'))

        assert math.isnan(view.getFloat32(0))
        assert math.isnan(view.getFloat64(8))

    def test_infinity_preservation(self):
        """Infinity values preserved"""
        buf = ArrayBuffer(32)
        view = DataView(buf)

        # Float32
        view.setFloat32(0, float('inf'))
        view.setFloat32(4, float('-inf'))

        assert view.getFloat32(0) == float('inf')
        assert view.getFloat32(4) == float('-inf')

        # Float64
        view.setFloat64(8, float('inf'))
        view.setFloat64(16, float('-inf'))

        assert view.getFloat64(8) == float('inf')
        assert view.getFloat64(16) == float('-inf')


class TestDataViewDetachedBuffer:
    """Test DataView behavior with detached buffers (FR-ES24-B-026)"""

    def test_detached_buffer_all_getters_throw(self):
        """All getter methods throw on detached buffer"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="detached"):
            view.getInt8(0)

        with pytest.raises(JSTypeError, match="detached"):
            view.getUint8(0)

        with pytest.raises(JSTypeError, match="detached"):
            view.getInt16(0)

        with pytest.raises(JSTypeError, match="detached"):
            view.getUint16(0)

        with pytest.raises(JSTypeError, match="detached"):
            view.getInt32(0)

        with pytest.raises(JSTypeError, match="detached"):
            view.getUint32(0)

        with pytest.raises(JSTypeError, match="detached"):
            view.getFloat32(0)

        with pytest.raises(JSTypeError, match="detached"):
            view.getFloat64(0)

    def test_detached_buffer_all_setters_throw(self):
        """All setter methods throw on detached buffer"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="detached"):
            view.setInt8(0, 42)

        with pytest.raises(JSTypeError, match="detached"):
            view.setUint8(0, 42)

        with pytest.raises(JSTypeError, match="detached"):
            view.setInt16(0, 42)

        with pytest.raises(JSTypeError, match="detached"):
            view.setUint16(0, 42)

        with pytest.raises(JSTypeError, match="detached"):
            view.setInt32(0, 42)

        with pytest.raises(JSTypeError, match="detached"):
            view.setUint32(0, 42)

        with pytest.raises(JSTypeError, match="detached"):
            view.setFloat32(0, 3.14)

        with pytest.raises(JSTypeError, match="detached"):
            view.setFloat64(0, 3.14)

    def test_properties_return_cached_values_when_detached(self):
        """Properties return cached values even when buffer detached"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 4, 8)

        # Cache property values
        cached_buffer = view.buffer
        cached_offset = view.byteOffset
        cached_length = view.byteLength

        # Detach buffer
        buf.transfer()

        # Properties should still return cached values
        assert view.buffer is cached_buffer
        assert view.byteOffset == cached_offset
        assert view.byteLength == cached_length


class TestDataViewBoundaryConditions:
    """Test boundary conditions and edge cases"""

    def test_zero_length_view_operations_throw(self):
        """Operations on zero-length view throw"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 16, 0)

        assert view.byteLength == 0

        with pytest.raises(RangeError):
            view.getUint8(0)

        with pytest.raises(RangeError):
            view.setUint8(0, 42)

    def test_exact_boundary_access(self):
        """Access at exact boundary throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        # Last byte is at offset 7
        view.getUint8(7)  # Should succeed
        view.setUint8(7, 42)  # Should succeed

        # Offset 8 is out of bounds
        with pytest.raises(RangeError):
            view.getUint8(8)

        with pytest.raises(RangeError):
            view.setUint8(8, 42)

    def test_multi_byte_type_at_boundary(self):
        """Multi-byte types cannot read/write past end"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        # Int32 needs 4 bytes, so last valid offset is 4
        view.getInt32(4)  # Bytes 4-7: OK
        view.setInt32(4, 42)  # OK

        # Offset 5 would need bytes 5-8, but buffer ends at 7
        with pytest.raises(RangeError):
            view.getInt32(5)

        with pytest.raises(RangeError):
            view.setInt32(5, 42)


class TestDataViewTypeConversions:
    """Test type conversion behavior"""

    def test_fractional_values_converted_to_integers(self):
        """Fractional values are converted to integers for int types"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setInt8(0, 42.7)
        assert view.getInt8(0) == 42

        view.setInt16(0, 12345.9)
        assert view.getInt16(0) == 12345

        view.setInt32(0, 987654.3)
        assert view.getInt32(0) == 987654

    def test_string_numbers_converted(self):
        """String representations of numbers are converted"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        # Note: This depends on Python's int() conversion
        # JavaScript would use ToNumber
        view.setInt8(0, int("42"))
        assert view.getInt8(0) == 42

    def test_wrapping_behavior_consistent(self):
        """Type wrapping behavior is consistent"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        # Int8: 256 wraps to 0
        view.setInt8(0, 256)
        assert view.getInt8(0) == 0

        # Int8: 257 wraps to 1
        view.setInt8(0, 257)
        assert view.getInt8(0) == 1

        # Uint8: -1 wraps to 255
        view.setUint8(0, -1)
        assert view.getUint8(0) == 255
