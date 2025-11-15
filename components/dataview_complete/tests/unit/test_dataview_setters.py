"""
Unit tests for DataView setter methods.
Tests FR-ES24-B-022, FR-ES24-B-023, FR-ES24-B-024, FR-ES24-B-026

Following TDD RED phase - These tests should fail initially.
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


class TestDataViewSetInt8:
    """Test setInt8 method (FR-ES24-B-022)"""

    def test_set_int8_positive(self):
        """setInt8 writes positive value"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setInt8(0, 127)

        assert view.getInt8(0) == 127

    def test_set_int8_negative(self):
        """setInt8 writes negative value"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setInt8(0, -128)

        assert view.getInt8(0) == -128

    def test_set_int8_wrapping_positive(self):
        """setInt8 wraps values > 127"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setInt8(0, 128)  # Should wrap to -128

        assert view.getInt8(0) == -128

    def test_set_int8_wrapping_large_positive(self):
        """setInt8 wraps large positive values"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setInt8(0, 255)  # Should wrap to -1

        assert view.getInt8(0) == -1

    def test_set_int8_wrapping_negative(self):
        """setInt8 wraps values < -128"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setInt8(0, -129)  # Should wrap to 127

        assert view.getInt8(0) == 127

    def test_set_int8_at_various_offsets(self):
        """setInt8 writes to various offsets"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setInt8(0, 10)
        view.setInt8(1, 20)
        view.setInt8(2, 30)
        view.setInt8(3, 40)

        assert view.getInt8(0) == 10
        assert view.getInt8(1) == 20
        assert view.getInt8(2) == 30
        assert view.getInt8(3) == 40

    def test_set_int8_boundary_throws(self):
        """setInt8 past boundary throws RangeError"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.setInt8(4, 42)

    def test_set_int8_detached_throws(self):
        """setInt8 on detached buffer throws TypeError"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform setInt8 on a detached ArrayBuffer"):
            view.setInt8(0, 42)


class TestDataViewSetUint8:
    """Test setUint8 method (FR-ES24-B-022)"""

    def test_set_uint8_max(self):
        """setUint8 writes maximum value 255"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 255)

        assert view.getUint8(0) == 255

    def test_set_uint8_zero(self):
        """setUint8 writes zero"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 0)

        assert view.getUint8(0) == 0

    def test_set_uint8_wrapping(self):
        """setUint8 wraps values > 255"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 256)  # Should wrap to 0

        assert view.getUint8(0) == 0

    def test_set_uint8_wrapping_large(self):
        """setUint8 wraps large values"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, 1000)  # Should wrap to 1000 % 256 = 232

        assert view.getUint8(0) == 232

    def test_set_uint8_wrapping_negative(self):
        """setUint8 wraps negative values"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint8(0, -1)  # Should wrap to 255

        assert view.getUint8(0) == 255

    def test_set_uint8_multiple_values(self):
        """setUint8 writes multiple values correctly"""
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

    def test_set_uint8_boundary_throws(self):
        """setUint8 past boundary throws"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.setUint8(4, 42)

    def test_set_uint8_detached_throws(self):
        """setUint8 on detached buffer throws"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform setUint8 on a detached ArrayBuffer"):
            view.setUint8(0, 42)


class TestDataViewSetInt16:
    """Test setInt16 method with endianness (FR-ES24-B-022, FR-ES24-B-023)"""

    def test_set_int16_big_endian_default(self):
        """setInt16() defaults to big-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setInt16(0, 0x1234)

        assert view.getUint8(0) == 0x12
        assert view.getUint8(1) == 0x34

    def test_set_int16_big_endian_explicit(self):
        """setInt16(offset, value, false) writes big-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setInt16(0, 0x1234, False)

        assert view.getUint8(0) == 0x12
        assert view.getUint8(1) == 0x34

    def test_set_int16_little_endian(self):
        """setInt16(offset, value, true) writes little-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setInt16(0, 0x1234, True)

        assert view.getUint8(0) == 0x34
        assert view.getUint8(1) == 0x12

    def test_set_int16_max_positive(self):
        """setInt16 writes maximum positive value 32767"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setInt16(0, 32767)

        assert view.getInt16(0) == 32767

    def test_set_int16_negative(self):
        """setInt16 writes negative value"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setInt16(0, -1)

        assert view.getInt16(0) == -1

    def test_set_int16_wrapping(self):
        """setInt16 wraps values > 32767"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setInt16(0, 32768)  # Should wrap to -32768

        assert view.getInt16(0) == -32768

    def test_set_int16_boundary_throws(self):
        """setInt16 past boundary throws (needs 2 bytes)"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.setInt16(3, 0x1234)

    def test_set_int16_detached_throws(self):
        """setInt16 on detached buffer throws"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform setInt16 on a detached ArrayBuffer"):
            view.setInt16(0, 42)


class TestDataViewSetUint16:
    """Test setUint16 method with endianness (FR-ES24-B-022, FR-ES24-B-023)"""

    def test_set_uint16_big_endian_default(self):
        """setUint16() defaults to big-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint16(0, 0x1234)

        assert view.getUint8(0) == 0x12
        assert view.getUint8(1) == 0x34

    def test_set_uint16_little_endian(self):
        """setUint16(offset, value, true) writes little-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint16(0, 0x1234, True)

        assert view.getUint8(0) == 0x34
        assert view.getUint8(1) == 0x12

    def test_set_uint16_max_value(self):
        """setUint16 writes maximum value 65535"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint16(0, 65535)

        assert view.getUint16(0) == 65535

    def test_set_uint16_zero(self):
        """setUint16 writes zero"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint16(0, 0)

        assert view.getUint16(0) == 0

    def test_set_uint16_wrapping(self):
        """setUint16 wraps values > 65535"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        view.setUint16(0, 65536)  # Should wrap to 0

        assert view.getUint16(0) == 0

    def test_set_uint16_endianness_different_bytes(self):
        """Different endianness produces different byte patterns"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        view.setUint16(0, 0x1234, False)  # Big-endian
        view.setUint16(2, 0x1234, True)   # Little-endian

        assert view.getUint8(0) == 0x12
        assert view.getUint8(1) == 0x34
        assert view.getUint8(2) == 0x34
        assert view.getUint8(3) == 0x12

    def test_set_uint16_boundary_throws(self):
        """setUint16 past boundary throws"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.setUint16(3, 0x1234)

    def test_set_uint16_detached_throws(self):
        """setUint16 on detached buffer throws"""
        buf = ArrayBuffer(4)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform setUint16 on a detached ArrayBuffer"):
            view.setUint16(0, 42)


class TestDataViewSetInt32:
    """Test setInt32 method with endianness (FR-ES24-B-022, FR-ES24-B-023)"""

    def test_set_int32_big_endian_default(self):
        """setInt32() defaults to big-endian"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setInt32(0, 0x12345678)

        assert view.getUint8(0) == 0x12
        assert view.getUint8(1) == 0x34
        assert view.getUint8(2) == 0x56
        assert view.getUint8(3) == 0x78

    def test_set_int32_little_endian(self):
        """setInt32(offset, value, true) writes little-endian"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setInt32(0, 0x12345678, True)

        assert view.getUint8(0) == 0x78
        assert view.getUint8(1) == 0x56
        assert view.getUint8(2) == 0x34
        assert view.getUint8(3) == 0x12

    def test_set_int32_max_positive(self):
        """setInt32 writes maximum positive value 2147483647"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setInt32(0, 2147483647)

        assert view.getInt32(0) == 2147483647

    def test_set_int32_negative(self):
        """setInt32 writes negative value"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setInt32(0, -1)

        assert view.getInt32(0) == -1

    def test_set_int32_min_negative(self):
        """setInt32 writes minimum negative value -2147483648"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setInt32(0, -2147483648)

        assert view.getInt32(0) == -2147483648

    def test_set_int32_wrapping(self):
        """setInt32 wraps values > 2147483647"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setInt32(0, 2147483648)  # Should wrap to -2147483648

        assert view.getInt32(0) == -2147483648

    def test_set_int32_boundary_throws(self):
        """setInt32 past boundary throws (needs 4 bytes)"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.setInt32(5, 0x12345678)

    def test_set_int32_detached_throws(self):
        """setInt32 on detached buffer throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform setInt32 on a detached ArrayBuffer"):
            view.setInt32(0, 42)


class TestDataViewSetUint32:
    """Test setUint32 method with endianness (FR-ES24-B-022, FR-ES24-B-023)"""

    def test_set_uint32_big_endian_default(self):
        """setUint32() defaults to big-endian"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setUint32(0, 0x12345678)

        assert view.getUint8(0) == 0x12
        assert view.getUint8(1) == 0x34
        assert view.getUint8(2) == 0x56
        assert view.getUint8(3) == 0x78

    def test_set_uint32_little_endian(self):
        """setUint32(offset, value, true) writes little-endian"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setUint32(0, 0x12345678, True)

        assert view.getUint8(0) == 0x78
        assert view.getUint8(1) == 0x56
        assert view.getUint8(2) == 0x34
        assert view.getUint8(3) == 0x12

    def test_set_uint32_max_value(self):
        """setUint32 writes maximum value 4294967295"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setUint32(0, 4294967295)

        assert view.getUint32(0) == 4294967295

    def test_set_uint32_zero(self):
        """setUint32 writes zero"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setUint32(0, 0)

        assert view.getUint32(0) == 0

    def test_set_uint32_wrapping(self):
        """setUint32 wraps values > 4294967295"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setUint32(0, 4294967296)  # Should wrap to 0

        assert view.getUint32(0) == 0

    def test_set_uint32_endianness_different_bytes(self):
        """Different endianness produces different byte patterns"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setUint32(0, 0x12345678, False)  # Big-endian
        view.setUint32(4, 0x12345678, True)   # Little-endian

        assert view.getUint8(0) == 0x12
        assert view.getUint8(4) == 0x78

    def test_set_uint32_boundary_throws(self):
        """setUint32 past boundary throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.setUint32(5, 0x12345678)

    def test_set_uint32_detached_throws(self):
        """setUint32 on detached buffer throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform setUint32 on a detached ArrayBuffer"):
            view.setUint32(0, 42)


class TestDataViewSetFloat32:
    """Test setFloat32 method with endianness (FR-ES24-B-022, FR-ES24-B-023)"""

    def test_set_float32_positive(self):
        """setFloat32 writes positive value"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setFloat32(0, 3.14)

        result = view.getFloat32(0)
        assert abs(result - 3.14) < 0.001

    def test_set_float32_negative(self):
        """setFloat32 writes negative value"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setFloat32(0, -123.456)

        result = view.getFloat32(0)
        assert abs(result - (-123.456)) < 0.001

    def test_set_float32_zero(self):
        """setFloat32 writes zero"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setFloat32(0, 0.0)

        assert view.getFloat32(0) == 0.0

    def test_set_float32_nan(self):
        """setFloat32 writes NaN"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setFloat32(0, float('nan'))

        result = view.getFloat32(0)
        assert math.isnan(result)

    def test_set_float32_infinity(self):
        """setFloat32 writes infinity"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setFloat32(0, float('inf'))

        assert view.getFloat32(0) == float('inf')

    def test_set_float32_negative_infinity(self):
        """setFloat32 writes negative infinity"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        view.setFloat32(0, float('-inf'))

        assert view.getFloat32(0) == float('-inf')

    def test_set_float32_endianness(self):
        """setFloat32 respects endianness"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setFloat32(0, 3.14, False)  # Big-endian
        view.setFloat32(4, 3.14, True)   # Little-endian

        # Bytes should be in different order
        assert view.getUint8(0) != view.getUint8(4) or view.getUint8(1) != view.getUint8(5)

    def test_set_float32_boundary_throws(self):
        """setFloat32 past boundary throws (needs 4 bytes)"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.setFloat32(5, 3.14)

    def test_set_float32_detached_throws(self):
        """setFloat32 on detached buffer throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform setFloat32 on a detached ArrayBuffer"):
            view.setFloat32(0, 3.14)


class TestDataViewSetFloat64:
    """Test setFloat64 method with endianness (FR-ES24-B-022, FR-ES24-B-023)"""

    def test_set_float64_pi(self):
        """setFloat64 writes PI with full precision"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        view.setFloat64(0, math.pi)

        result = view.getFloat64(0)
        assert abs(result - math.pi) < 1e-15

    def test_set_float64_negative(self):
        """setFloat64 writes negative value"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        view.setFloat64(0, -123.456789012345)

        result = view.getFloat64(0)
        assert abs(result - (-123.456789012345)) < 1e-15

    def test_set_float64_zero(self):
        """setFloat64 writes zero"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        view.setFloat64(0, 0.0)

        assert view.getFloat64(0) == 0.0

    def test_set_float64_nan(self):
        """setFloat64 writes NaN"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        view.setFloat64(0, float('nan'))

        result = view.getFloat64(0)
        assert math.isnan(result)

    def test_set_float64_infinity(self):
        """setFloat64 writes infinity"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        view.setFloat64(0, float('inf'))

        assert view.getFloat64(0) == float('inf')

    def test_set_float64_negative_infinity(self):
        """setFloat64 writes negative infinity"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        view.setFloat64(0, float('-inf'))

        assert view.getFloat64(0) == float('-inf')

    def test_set_float64_endianness(self):
        """setFloat64 respects endianness"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        view.setFloat64(0, math.pi, False)  # Big-endian
        view.setFloat64(8, math.pi, True)   # Little-endian

        # Bytes should be in different order
        assert view.getUint8(0) != view.getUint8(8) or view.getUint8(1) != view.getUint8(9)

    def test_set_float64_boundary_throws(self):
        """setFloat64 past boundary throws (needs 8 bytes)"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        with pytest.raises(RangeError, match="Offset is outside the bounds of the DataView"):
            view.setFloat64(9, math.pi)

    def test_set_float64_detached_throws(self):
        """setFloat64 on detached buffer throws"""
        buf = ArrayBuffer(16)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(JSTypeError, match="Cannot perform setFloat64 on a detached ArrayBuffer"):
            view.setFloat64(0, math.pi)
