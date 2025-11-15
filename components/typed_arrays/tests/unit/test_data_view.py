"""
Unit tests for DataView class.
Tests FR-P3-056, FR-P3-065
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from array_buffer import ArrayBuffer
from data_view import DataView
from exceptions import RangeError, TypeError


class TestDataViewConstructor:
    """Test DataView construction (FR-P3-056)"""

    def test_create_from_buffer(self):
        """DataView(buffer) creates view of entire buffer"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        assert view.buffer is buf
        assert view.byteLength == 16
        assert view.byteOffset == 0

    def test_create_with_offset(self):
        """DataView(buffer, byteOffset)"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 8)

        assert view.byteLength == 8
        assert view.byteOffset == 8

    def test_create_with_offset_and_length(self):
        """DataView(buffer, byteOffset, byteLength)"""
        buf = ArrayBuffer(16)
        view = DataView(buf, 4, 8)

        assert view.byteLength == 8
        assert view.byteOffset == 4

    def test_offset_out_of_bounds_throws(self):
        """Offset beyond buffer throws"""
        buf = ArrayBuffer(16)
        with pytest.raises(RangeError):
            DataView(buf, 20)

    def test_length_out_of_bounds_throws(self):
        """Length extending beyond buffer throws"""
        buf = ArrayBuffer(16)
        with pytest.raises(RangeError):
            DataView(buf, 8, 10)


class TestDataViewInt8:
    """Test Int8 getter/setter"""

    def test_get_int8(self):
        """getInt8() reads signed 8-bit integer"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        # Manually set bytes (we'll use setUint8 once it's tested)
        view.setUint8(0, 127)
        view.setUint8(1, 128)  # -128 as signed

        assert view.getInt8(0) == 127
        assert view.getInt8(1) == -128

    def test_set_int8(self):
        """setInt8() writes signed 8-bit integer"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        view.setInt8(0, 127)
        view.setInt8(1, -128)
        view.setInt8(2, -1)

        assert view.getInt8(0) == 127
        assert view.getInt8(1) == -128
        assert view.getInt8(2) == -1


class TestDataViewUint8:
    """Test Uint8 getter/setter"""

    def test_get_uint8(self):
        """getUint8() reads unsigned 8-bit integer"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        view.setUint8(0, 255)
        view.setUint8(1, 0)

        assert view.getUint8(0) == 255
        assert view.getUint8(1) == 0

    def test_set_uint8(self):
        """setUint8() writes unsigned 8-bit integer"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        view.setUint8(0, 255)
        view.setUint8(1, 128)

        assert view.getUint8(0) == 255
        assert view.getUint8(1) == 128


class TestDataViewInt16:
    """Test Int16 getter/setter with endianness (FR-P3-065)"""

    def test_get_int16_big_endian(self):
        """getInt16() reads big-endian by default"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        # Write bytes manually: 0x7FFF (32767) in big-endian
        view.setUint8(0, 0x7F)
        view.setUint8(1, 0xFF)

        assert view.getInt16(0) == 32767
        assert view.getInt16(0, False) == 32767  # Explicit big-endian

    def test_get_int16_little_endian(self):
        """getInt16(offset, true) reads little-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        # Write bytes: 0xFF 0x7F (little-endian 32767)
        view.setUint8(0, 0xFF)
        view.setUint8(1, 0x7F)

        assert view.getInt16(0, True) == 32767

    def test_set_int16_big_endian(self):
        """setInt16() writes big-endian by default"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        view.setInt16(0, 32767)

        assert view.getUint8(0) == 0x7F
        assert view.getUint8(1) == 0xFF

    def test_set_int16_little_endian(self):
        """setInt16(offset, value, true) writes little-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        view.setInt16(0, 32767, True)

        assert view.getUint8(0) == 0xFF
        assert view.getUint8(1) == 0x7F


class TestDataViewUint16:
    """Test Uint16 getter/setter with endianness"""

    def test_get_uint16_big_endian(self):
        """getUint16() reads big-endian by default"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        view.setUint8(0, 0xFF)
        view.setUint8(1, 0xFF)

        assert view.getUint16(0) == 65535

    def test_get_uint16_little_endian(self):
        """getUint16(offset, true) reads little-endian"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        # 0x1234 in little-endian: 0x34 0x12
        view.setUint8(0, 0x34)
        view.setUint8(1, 0x12)

        assert view.getUint16(0, True) == 0x1234

    def test_set_uint16_endianness(self):
        """setUint16() respects endianness"""
        buf = ArrayBuffer(4)
        view = DataView(buf)

        view.setUint16(0, 0x1234, False)  # Big-endian
        assert view.getUint8(0) == 0x12
        assert view.getUint8(1) == 0x34

        view.setUint16(2, 0x1234, True)   # Little-endian
        assert view.getUint8(2) == 0x34
        assert view.getUint8(3) == 0x12


class TestDataViewInt32:
    """Test Int32 getter/setter with endianness"""

    def test_get_int32_big_endian(self):
        """getInt32() reads big-endian by default"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        # 0x7FFFFFFF (2147483647) big-endian
        view.setUint8(0, 0x7F)
        view.setUint8(1, 0xFF)
        view.setUint8(2, 0xFF)
        view.setUint8(3, 0xFF)

        assert view.getInt32(0) == 2147483647

    def test_get_int32_little_endian(self):
        """getInt32(offset, true) reads little-endian"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        # 0x12345678 little-endian: 0x78 0x56 0x34 0x12
        view.setUint8(0, 0x78)
        view.setUint8(1, 0x56)
        view.setUint8(2, 0x34)
        view.setUint8(3, 0x12)

        assert view.getInt32(0, True) == 0x12345678

    def test_set_int32_endianness(self):
        """setInt32() respects endianness"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setInt32(0, 0x12345678, False)  # Big-endian
        assert view.getUint8(0) == 0x12

        view.setInt32(4, 0x12345678, True)   # Little-endian
        assert view.getUint8(4) == 0x78


class TestDataViewUint32:
    """Test Uint32 getter/setter"""

    def test_get_uint32(self):
        """getUint32() reads unsigned 32-bit"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setUint8(0, 0xFF)
        view.setUint8(1, 0xFF)
        view.setUint8(2, 0xFF)
        view.setUint8(3, 0xFF)

        assert view.getUint32(0) == 4294967295

    def test_set_uint32(self):
        """setUint32() writes unsigned 32-bit"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setUint32(0, 4294967295, False)

        assert view.getUint8(0) == 0xFF
        assert view.getUint8(3) == 0xFF


class TestDataViewFloat32:
    """Test Float32 getter/setter"""

    def test_get_float32(self):
        """getFloat32() reads 32-bit float"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setFloat32(0, 3.14, False)
        result = view.getFloat32(0, False)

        assert abs(result - 3.14) < 0.001

    def test_set_float32(self):
        """setFloat32() writes 32-bit float"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setFloat32(0, -123.456, False)
        result = view.getFloat32(0, False)

        assert abs(result - (-123.456)) < 0.001

    def test_float32_endianness(self):
        """Float32 respects endianness"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setFloat32(0, 3.14, False)  # Big-endian
        view.setFloat32(4, 3.14, True)   # Little-endian

        # Bytes should be different
        assert view.getUint8(0) != view.getUint8(4)


class TestDataViewFloat64:
    """Test Float64 getter/setter"""

    def test_get_float64(self):
        """getFloat64() reads 64-bit float"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        view.setFloat64(0, 3.141592653589793, False)
        result = view.getFloat64(0, False)

        assert abs(result - 3.141592653589793) < 1e-15

    def test_set_float64(self):
        """setFloat64() writes 64-bit float"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        view.setFloat64(0, -123.456789012345, False)
        result = view.getFloat64(0, False)

        assert abs(result - (-123.456789012345)) < 1e-15

    def test_float64_endianness(self):
        """Float64 respects endianness"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        view.setFloat64(0, 3.141592653589793, False)  # Big-endian
        view.setFloat64(8, 3.141592653589793, True)   # Little-endian

        # Bytes should be different
        assert view.getUint8(0) != view.getUint8(8)


class TestDataViewBigInt64:
    """Test BigInt64 getter/setter"""

    def test_get_big_int64(self):
        """getBigInt64() reads signed 64-bit BigInt"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        # Set max positive: 0x7FFFFFFFFFFFFFFF
        for i in range(8):
            view.setUint8(i, 0xFF if i > 0 else 0x7F)

        result = view.getBigInt64(0, False)
        assert result == 9223372036854775807  # 2^63 - 1

    def test_set_big_int64(self):
        """setBigInt64() writes signed 64-bit BigInt"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        view.setBigInt64(0, 9223372036854775807, False)

        assert view.getUint8(0) == 0x7F
        assert view.getUint8(7) == 0xFF

    def test_big_int64_endianness(self):
        """BigInt64 respects endianness"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        value = 0x123456789ABCDEF0

        view.setBigInt64(0, value, False)  # Big-endian
        view.setBigInt64(8, value, True)   # Little-endian

        # First byte should be different
        assert view.getUint8(0) != view.getUint8(8)


class TestDataViewBigUint64:
    """Test BigUint64 getter/setter"""

    def test_get_big_uint64(self):
        """getBigUint64() reads unsigned 64-bit BigInt"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        # Set max value: 0xFFFFFFFFFFFFFFFF
        for i in range(8):
            view.setUint8(i, 0xFF)

        result = view.getBigUint64(0, False)
        assert result == 18446744073709551615  # 2^64 - 1

    def test_set_big_uint64(self):
        """setBigUint64() writes unsigned 64-bit BigInt"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        view.setBigUint64(0, 18446744073709551615, False)

        for i in range(8):
            assert view.getUint8(i) == 0xFF


class TestDataViewBounds:
    """Test bounds checking"""

    def test_read_out_of_bounds_throws(self):
        """Reading beyond buffer throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf, 0, 8)

        with pytest.raises(RangeError):
            view.getInt32(6)  # Would read bytes 6,7,8,9 but buffer ends at 7

    def test_write_out_of_bounds_throws(self):
        """Writing beyond buffer throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf, 0, 8)

        with pytest.raises(RangeError):
            view.setInt32(6, 123)

    def test_negative_offset_throws(self):
        """Negative offset throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        with pytest.raises(RangeError):
            view.getInt8(-1)


class TestDataViewDetachedBuffer:
    """Test DataView with detached buffer"""

    def test_read_from_detached_throws(self):
        """Reading from detached buffer throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(TypeError):
            view.getInt8(0)

    def test_write_to_detached_throws(self):
        """Writing to detached buffer throws"""
        buf = ArrayBuffer(8)
        view = DataView(buf)
        buf.transfer()

        with pytest.raises(TypeError):
            view.setInt8(0, 42)


class TestDataViewEdgeCases:
    """Test edge cases and special values"""

    def test_nan_float32(self):
        """Float32 can store NaN"""
        buf = ArrayBuffer(8)
        view = DataView(buf)

        view.setFloat32(0, float('nan'))
        result = view.getFloat32(0)

        assert result != result  # NaN != NaN

    def test_infinity_float64(self):
        """Float64 can store infinity"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        view.setFloat64(0, float('inf'))
        assert view.getFloat64(0) == float('inf')

        view.setFloat64(8, float('-inf'))
        assert view.getFloat64(8) == float('-inf')

    def test_zero_values(self):
        """All types can store zero"""
        buf = ArrayBuffer(16)
        view = DataView(buf)

        view.setInt8(0, 0)
        view.setInt16(1, 0)
        view.setInt32(3, 0)
        view.setFloat32(7, 0.0)

        assert view.getInt8(0) == 0
        assert view.getInt16(1) == 0
        assert view.getInt32(3) == 0
        assert view.getFloat32(7) == 0.0
