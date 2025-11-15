"""
Unit tests for DataView getter methods.
Tests FR-ES24-B-021, FR-ES24-B-023, FR-ES24-B-024, FR-ES24-B-026

Following TDD RED phase - These tests should fail initially.
"""

import pytest
import sys
import struct
import math
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "typed_arrays" / "src"))

from array_buffer import ArrayBuffer
from dataview import DataView
from exceptions import RangeError, TypeError as JSTypeError


class TestDataViewGetInt8:
    """Test getInt8 method (FR-ES24-B-021)"""

    def test_get_int8_positive(self):
        """getInt8 reads positive signed 8-bit integer"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 127)

        assert view.getInt8(0) == 127

    def test_get_int8_negative(self):
        """getInt8 reads negative signed 8-bit integer"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 128)  # -128 as signed

        assert view.getInt8(0) == -128

    def test_get_int8_zero(self):
        """getInt8 reads zero"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        assert view.getInt8(0) == 0

    def test_get_int8_minus_one(self):
        """getInt8 reads -1 (0xFF)"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 255)

        assert view.getInt8(0) == -1

    def test_get_int8_at_offset(self):
        """getInt8 reads from specified offset"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(3, 42)

        assert view.getInt8(3) == 42

    def test_get_int8_boundary_throws(self):
        """getInt8 at boundary throws RangeError"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.getInt8(4)

    def test_get_int8_detached_throws(self):
        """getInt8 on detached buffer throws TypeError"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform getInt8 on a detached ArrayBuffer"):
            view.getInt8(0)

    def test_get_int8_negative_offset_throws(self):
        """getInt8 with negative offset throws RangeError"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.getInt8(-1)


class TestDataViewGetUint8:
    """Test getUint8 method (FR-ES24-B-021)"""

    def test_get_uint8_max(self):
        """getUint8 reads maximum value 255"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 255)

        assert view.getUint8(0) == 255

    def test_get_uint8_zero(self):
        """getUint8 reads zero"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        assert view.getUint8(0) == 0

    def test_get_uint8_mid_value(self):
        """getUint8 reads mid-range value"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 128)

        assert view.getUint8(0) == 128

    def test_get_uint8_at_various_offsets(self):
        """getUint8 reads from various offsets"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 10)
        view.setUint8(1, 20)
        view.setUint8(2, 30)
        view.setUint8(3, 40)

        assert view.getUint8(0) == 10
        assert view.getUint8(1) == 20
        assert view.getUint8(2) == 30
        assert view.getUint8(3) == 40

    def test_get_uint8_boundary_throws(self):
        """getUint8 past boundary throws RangeError"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.getUint8(4)

    def test_get_uint8_detached_throws(self):
        """getUint8 on detached buffer throws TypeError"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform getUint8 on a detached ArrayBuffer"):
            view.getUint8(0)

    def test_get_uint8_partial_view(self):
        """getUint8 respects view boundaries"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 8, 4)

        # Should be able to read 4 bytes from offset 0-3
        view.getUint8(0)
        view.getUint8(3)

        # But not at offset 4
        with pytest.raises(RangeError):
            view.getUint8(4)

    def test_get_uint8_negative_offset_throws(self):
        """getUint8 with negative offset throws"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        with pytest.raises(RangeError):
            view.getUint8(-1)


class TestDataViewGetInt16:
    """Test getInt16 method with endianness (FR-ES24-B-021, FR-ES24-B-023)"""

    def test_get_int16_big_endian_default(self):
        """getInt16() defaults to big-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        # 0x7FFF = 32767 in big-endian: [0x7F, 0xFF]
        view.setUint8(0, 0x7F)
        view.setUint8(1, 0xFF)

        assert view.getInt16(0) == 32767

    def test_get_int16_big_endian_explicit(self):
        """getInt16(offset, false) reads big-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 0x7F)
        view.setUint8(1, 0xFF)

        assert view.getInt16(0, False) == 32767

    def test_get_int16_little_endian(self):
        """getInt16(offset, true) reads little-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        # 0x7FFF = 32767 in little-endian: [0xFF, 0x7F]
        view.setUint8(0, 0xFF)
        view.setUint8(1, 0x7F)

        assert view.getInt16(0, True) == 32767

    def test_get_int16_negative_big_endian(self):
        """getInt16 reads negative value in big-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        # -1 in big-endian: [0xFF, 0xFF]
        view.setUint8(0, 0xFF)
        view.setUint8(1, 0xFF)

        assert view.getInt16(0, False) == -1

    def test_get_int16_negative_little_endian(self):
        """getInt16 reads negative value in little-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        # -1 in little-endian: [0xFF, 0xFF]
        view.setUint8(0, 0xFF)
        view.setUint8(1, 0xFF)

        assert view.getInt16(0, True) == -1

    def test_get_int16_boundary_throws(self):
        """getInt16 past boundary throws (needs 2 bytes)"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.getInt16(3)  # Would read bytes 3-4, but buffer ends at 3

    def test_get_int16_detached_throws(self):
        """getInt16 on detached buffer throws"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform getInt16 on a detached ArrayBuffer"):
            view.getInt16(0)

    def test_get_int16_at_offset(self):
        """getInt16 reads from specified offset"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(2, 0x12)
        view.setUint8(3, 0x34)

        assert view.getInt16(2, False) == 0x1234


class TestDataViewGetUint16:
    """Test getUint16 method with endianness (FR-ES24-B-021, FR-ES24-B-023)"""

    def test_get_uint16_big_endian_default(self):
        """getUint16() defaults to big-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 0x12)
        view.setUint8(1, 0x34)

        assert view.getUint16(0) == 0x1234

    def test_get_uint16_little_endian(self):
        """getUint16(offset, true) reads little-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        # 0x1234 in little-endian: [0x34, 0x12]
        view.setUint8(0, 0x34)
        view.setUint8(1, 0x12)

        assert view.getUint16(0, True) == 0x1234

    def test_get_uint16_max_value(self):
        """getUint16 reads maximum value 65535"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 0xFF)
        view.setUint8(1, 0xFF)

        assert view.getUint16(0) == 65535

    def test_get_uint16_zero(self):
        """getUint16 reads zero"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        assert view.getUint16(0) == 0

    def test_get_uint16_endianness_matters(self):
        """Endianness produces different results for same bytes"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 0x12)
        view.setUint8(1, 0x34)

        big = view.getUint16(0, False)
        little = view.getUint16(0, True)

        assert big == 0x1234
        assert little == 0x3412

    def test_get_uint16_boundary_throws(self):
        """getUint16 past boundary throws"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.getUint16(3)

    def test_get_uint16_detached_throws(self):
        """getUint16 on detached buffer throws"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform getUint16 on a detached ArrayBuffer"):
            view.getUint16(0)

    def test_get_uint16_at_offset(self):
        """getUint16 reads from specified offset"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(2, 0xAB)
        view.setUint8(3, 0xCD)

        assert view.getUint16(2) == 0xABCD


class TestDataViewGetInt32:
    """Test getInt32 method with endianness (FR-ES24-B-021, FR-ES24-B-023)"""

    def test_get_int32_big_endian_default(self):
        """getInt32() defaults to big-endian"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        # 0x12345678 in big-endian
        view.setUint8(0, 0x12)
        view.setUint8(1, 0x34)
        view.setUint8(2, 0x56)
        view.setUint8(3, 0x78)

        assert view.getInt32(0) == 0x12345678

    def test_get_int32_little_endian(self):
        """getInt32(offset, true) reads little-endian"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        # 0x12345678 in little-endian: [0x78, 0x56, 0x34, 0x12]
        view.setUint8(0, 0x78)
        view.setUint8(1, 0x56)
        view.setUint8(2, 0x34)
        view.setUint8(3, 0x12)

        assert view.getInt32(0, True) == 0x12345678

    def test_get_int32_max_positive(self):
        """getInt32 reads maximum positive value"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        # 2147483647 = 0x7FFFFFFF
        view.setUint8(0, 0x7F)
        view.setUint8(1, 0xFF)
        view.setUint8(2, 0xFF)
        view.setUint8(3, 0xFF)

        assert view.getInt32(0) == 2147483647

    def test_get_int32_negative(self):
        """getInt32 reads negative value"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        # -1 = 0xFFFFFFFF
        view.setUint8(0, 0xFF)
        view.setUint8(1, 0xFF)
        view.setUint8(2, 0xFF)
        view.setUint8(3, 0xFF)

        assert view.getInt32(0) == -1

    def test_get_int32_min_negative(self):
        """getInt32 reads minimum negative value"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        # -2147483648 = 0x80000000
        view.setUint8(0, 0x80)
        view.setUint8(1, 0x00)
        view.setUint8(2, 0x00)
        view.setUint8(3, 0x00)

        assert view.getInt32(0) == -2147483648

    def test_get_int32_boundary_throws(self):
        """getInt32 past boundary throws (needs 4 bytes)"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.getInt32(5)  # Would read bytes 5-8, but buffer ends at 7

    def test_get_int32_detached_throws(self):
        """getInt32 on detached buffer throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform getInt32 on a detached ArrayBuffer"):
            view.getInt32(0)

    def test_get_int32_at_offset(self):
        """getInt32 reads from specified offset"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setUint8(4, 0x12)
        view.setUint8(5, 0x34)
        view.setUint8(6, 0x56)
        view.setUint8(7, 0x78)

        assert view.getInt32(4) == 0x12345678


class TestDataViewGetUint32:
    """Test getUint32 method with endianness (FR-ES24-B-021, FR-ES24-B-023)"""

    def test_get_uint32_big_endian_default(self):
        """getUint32() defaults to big-endian"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setUint8(0, 0x12)
        view.setUint8(1, 0x34)
        view.setUint8(2, 0x56)
        view.setUint8(3, 0x78)

        assert view.getUint32(0) == 0x12345678

    def test_get_uint32_little_endian(self):
        """getUint32(offset, true) reads little-endian"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setUint8(0, 0x78)
        view.setUint8(1, 0x56)
        view.setUint8(2, 0x34)
        view.setUint8(3, 0x12)

        assert view.getUint32(0, True) == 0x12345678

    def test_get_uint32_max_value(self):
        """getUint32 reads maximum value 4294967295"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setUint8(0, 0xFF)
        view.setUint8(1, 0xFF)
        view.setUint8(2, 0xFF)
        view.setUint8(3, 0xFF)

        assert view.getUint32(0) == 4294967295

    def test_get_uint32_zero(self):
        """getUint32 reads zero"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        assert view.getUint32(0) == 0

    def test_get_uint32_endianness_matters(self):
        """Endianness produces different results"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setUint8(0, 0x12)
        view.setUint8(1, 0x34)
        view.setUint8(2, 0x56)
        view.setUint8(3, 0x78)

        big = view.getUint32(0, False)
        little = view.getUint32(0, True)

        assert big == 0x12345678
        assert little == 0x78563412

    def test_get_uint32_boundary_throws(self):
        """getUint32 past boundary throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.getUint32(5)

    def test_get_uint32_detached_throws(self):
        """getUint32 on detached buffer throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform getUint32 on a detached ArrayBuffer"):
            view.getUint32(0)

    def test_get_uint32_at_offset(self):
        """getUint32 reads from specified offset"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setUint8(4, 0xAB)
        view.setUint8(5, 0xCD)
        view.setUint8(6, 0xEF)
        view.setUint8(7, 0x01)

        assert view.getUint32(4) == 0xABCDEF01


class TestDataViewGetFloat32:
    """Test getFloat32 method with endianness (FR-ES24-B-021, FR-ES24-B-023)"""

    def test_get_float32_positive(self):
        """getFloat32 reads positive float"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setFloat32(0, 3.14)

        result = view.getFloat32(0)
        assert abs(result - 3.14) < 0.001

    def test_get_float32_negative(self):
        """getFloat32 reads negative float"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setFloat32(0, -123.456)

        result = view.getFloat32(0)
        assert abs(result - (-123.456)) < 0.001

    def test_get_float32_zero(self):
        """getFloat32 reads zero"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setFloat32(0, 0.0)

        assert view.getFloat32(0) == 0.0

    def test_get_float32_nan(self):
        """getFloat32 reads NaN"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setFloat32(0, float('nan'))

        result = view.getFloat32(0)
        assert math.isnan(result)

    def test_get_float32_infinity(self):
        """getFloat32 reads infinity"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setFloat32(0, float('inf'))

        assert view.getFloat32(0) == float('inf')

    def test_get_float32_negative_infinity(self):
        """getFloat32 reads negative infinity"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setFloat32(0, float('-inf'))

        assert view.getFloat32(0) == float('-inf')

    def test_get_float32_endianness(self):
        """getFloat32 respects endianness"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setFloat32(0, 3.14, False)  # Big-endian
        view.setFloat32(4, 3.14, True)   # Little-endian

        # Bytes should be in different order
        assert view.getUint8(0) != view.getUint8(4) or view.getUint8(1) != view.getUint8(5)

    def test_get_float32_boundary_throws(self):
        """getFloat32 past boundary throws (needs 4 bytes)"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.getFloat32(5)


class TestDataViewGetFloat64:
    """Test getFloat64 method with endianness (FR-ES24-B-021, FR-ES24-B-023)"""

    def test_get_float64_pi(self):
        """getFloat64 reads PI with full precision"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        view.setFloat64(0, math.pi)

        result = view.getFloat64(0)
        assert abs(result - math.pi) < 1e-15

    def test_get_float64_negative(self):
        """getFloat64 reads negative value"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        view.setFloat64(0, -123.456789012345)

        result = view.getFloat64(0)
        assert abs(result - (-123.456789012345)) < 1e-15

    def test_get_float64_zero(self):
        """getFloat64 reads zero"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        assert view.getFloat64(0) == 0.0

    def test_get_float64_nan(self):
        """getFloat64 reads NaN"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        view.setFloat64(0, float('nan'))

        result = view.getFloat64(0)
        assert math.isnan(result)

    def test_get_float64_infinity(self):
        """getFloat64 reads infinity"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        view.setFloat64(0, float('inf'))

        assert view.getFloat64(0) == float('inf')

    def test_get_float64_negative_infinity(self):
        """getFloat64 reads negative infinity"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        view.setFloat64(0, float('-inf'))

        assert view.getFloat64(0) == float('-inf')

    def test_get_float64_endianness(self):
        """getFloat64 respects endianness"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        view.setFloat64(0, math.pi, False)  # Big-endian
        view.setFloat64(8, math.pi, True)   # Little-endian

        # Bytes should be in different order
        assert view.getUint8(0) != view.getUint8(8) or view.getUint8(1) != view.getUint8(9)

    def test_get_float64_boundary_throws(self):
        """getFloat64 past boundary throws (needs 8 bytes)"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.getFloat64(9)  # Would read bytes 9-16, but buffer ends at 15

    def test_get_float64_detached_throws(self):
        """getFloat64 on detached buffer throws"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform getFloat64 on a detached ArrayBuffer"):
            view.getFloat64(0)
