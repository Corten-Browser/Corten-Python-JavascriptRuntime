"""
Unit tests for TypedArray base class and all 11 variants.
Tests FR-P3-052, FR-P3-053, FR-P3-054, FR-P3-055, FR-P3-059 to FR-P3-064, FR-P3-067, FR-P3-068, FR-P3-070
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from array_buffer import ArrayBuffer
from typed_array import (
    TypedArray,
    Int8Array, Uint8Array, Uint8ClampedArray,
    Int16Array, Uint16Array,
    Int32Array, Uint32Array,
    Float32Array, Float64Array,
    BigInt64Array, BigUint64Array
)
from exceptions import RangeError, TypeError


class TestTypedArrayVariants:
    """Test all 11 TypedArray types exist (FR-P3-052)"""

    def test_all_variants_constructible(self):
        """All 11 TypedArray variants should be constructible"""
        variants = [
            (Int8Array, 1),
            (Uint8Array, 1),
            (Uint8ClampedArray, 1),
            (Int16Array, 2),
            (Uint16Array, 2),
            (Int32Array, 4),
            (Uint32Array, 4),
            (Float32Array, 4),
            (Float64Array, 8),
            (BigInt64Array, 8),
            (BigUint64Array, 8)
        ]

        for ArrayType, expected_bytes in variants:
            arr = ArrayType(10)
            assert arr.length == 10
            assert arr.BYTES_PER_ELEMENT == expected_bytes
            assert ArrayType.BYTES_PER_ELEMENT == expected_bytes


class TestTypedArrayConstructors:
    """Test TypedArray construction patterns (FR-P3-053)"""

    def test_construct_from_length(self):
        """new TypedArray(length) creates array of given length"""
        arr = Uint8Array(10)
        assert arr.length == 10
        assert arr.byteLength == 10
        # All elements should be 0
        for i in range(10):
            assert arr[i] == 0

    def test_construct_from_typed_array(self):
        """new TypedArray(typedArray) copies from another typed array"""
        arr1 = Uint8Array(5)
        arr1[0] = 10
        arr1[1] = 20

        arr2 = Uint8Array(arr1)
        assert arr2.length == 5
        assert arr2[0] == 10
        assert arr2[1] == 20

        # Different buffer
        assert arr2.buffer is not arr1.buffer

    def test_construct_from_array_like(self):
        """new TypedArray(arrayLike) creates from array-like"""
        arr = Uint8Array([1, 2, 3, 4, 5])
        assert arr.length == 5
        assert arr[0] == 1
        assert arr[4] == 5

    def test_construct_from_buffer(self):
        """new TypedArray(buffer) creates view of ArrayBuffer"""
        buf = ArrayBuffer(16)
        arr = Uint8Array(buf)
        assert arr.length == 16
        assert arr.buffer is buf

    def test_construct_from_buffer_with_offset(self):
        """new TypedArray(buffer, byteOffset)"""
        buf = ArrayBuffer(16)
        arr = Uint8Array(buf, 8)
        assert arr.length == 8
        assert arr.byteOffset == 8

    def test_construct_from_buffer_with_offset_and_length(self):
        """new TypedArray(buffer, byteOffset, length)"""
        buf = ArrayBuffer(16)
        arr = Uint8Array(buf, 4, 8)
        assert arr.length == 8
        assert arr.byteOffset == 4
        assert arr.byteLength == 8

    def test_construct_misaligned_offset_throws(self):
        """Offset not aligned to element size throws"""
        buf = ArrayBuffer(16)
        # Int32Array needs 4-byte alignment
        with pytest.raises(RangeError):
            Int32Array(buf, 3)

    def test_construct_invalid_length_throws(self):
        """Invalid length throws"""
        buf = ArrayBuffer(16)
        # Can't fit 10 4-byte elements in 16-byte buffer at offset 8
        with pytest.raises(RangeError):
            Int32Array(buf, 8, 10)


class TestTypedArrayProperties:
    """Test TypedArray properties (FR-P3-054)"""

    def test_buffer_property(self):
        """buffer property returns underlying ArrayBuffer"""
        buf = ArrayBuffer(16)
        arr = Uint8Array(buf)
        assert arr.buffer is buf

    def test_byte_length_property(self):
        """byteLength property"""
        arr = Uint32Array(10)
        assert arr.byteLength == 40  # 10 * 4 bytes

    def test_byte_offset_property(self):
        """byteOffset property"""
        buf = ArrayBuffer(16)
        arr1 = Uint8Array(buf, 0)
        arr2 = Uint8Array(buf, 8)

        assert arr1.byteOffset == 0
        assert arr2.byteOffset == 8

    def test_length_property(self):
        """length property"""
        arr = Int16Array(20)
        assert arr.length == 20

    def test_bytes_per_element_static(self):
        """BYTES_PER_ELEMENT static property"""
        assert Int8Array.BYTES_PER_ELEMENT == 1
        assert Int16Array.BYTES_PER_ELEMENT == 2
        assert Int32Array.BYTES_PER_ELEMENT == 4
        assert Float64Array.BYTES_PER_ELEMENT == 8

    def test_bytes_per_element_instance(self):
        """BYTES_PER_ELEMENT instance property"""
        arr = Int32Array(10)
        assert arr.BYTES_PER_ELEMENT == 4


class TestTypedArrayStaticMethods:
    """Test TypedArray.from() and .of() (FR-P3-059, FR-P3-060)"""

    def test_from_array(self):
        """TypedArray.from(array) creates from array"""
        arr = Uint8Array.from_array([1, 2, 3, 4, 5])
        assert arr.length == 5
        assert list(arr) == [1, 2, 3, 4, 5]

    def test_from_with_map_function(self):
        """TypedArray.from(source, mapFn)"""
        arr = Uint8Array.from_array([1, 2, 3], lambda x, *args: x * 2)
        assert list(arr) == [2, 4, 6]

    def test_from_iterable(self):
        """TypedArray.from() works with iterables"""
        # Generator expression
        arr = Uint8Array.from_array(x for x in range(5))
        assert list(arr) == [0, 1, 2, 3, 4]

    def test_of_method(self):
        """TypedArray.of(...values) creates from arguments"""
        arr = Uint8Array.of(10, 20, 30, 40)
        assert arr.length == 4
        assert list(arr) == [10, 20, 30, 40]

    def test_of_empty(self):
        """TypedArray.of() with no args creates empty array"""
        arr = Uint8Array.of()
        assert arr.length == 0


class TestTypedArrayIndexing:
    """Test array indexing and access"""

    def test_get_index(self):
        """Should get element by index"""
        arr = Uint8Array([10, 20, 30])
        assert arr[0] == 10
        assert arr[1] == 20
        assert arr[2] == 30

    def test_set_index(self):
        """Should set element by index"""
        arr = Uint8Array(3)
        arr[0] = 10
        arr[1] = 20
        arr[2] = 30

        assert arr[0] == 10
        assert arr[1] == 20
        assert arr[2] == 30

    def test_out_of_bounds_get(self):
        """Out of bounds get returns undefined"""
        arr = Uint8Array(3)
        assert arr[10] is None  # undefined

    def test_out_of_bounds_set_ignored(self):
        """Out of bounds set is ignored"""
        arr = Uint8Array(3)
        arr[10] = 99
        # Should not throw, just ignored


class TestTypedArrayAt:
    """Test at() method"""

    def test_at_positive_index(self):
        """at(index) returns element"""
        arr = Uint8Array([10, 20, 30])
        assert arr.at(0) == 10
        assert arr.at(1) == 20

    def test_at_negative_index(self):
        """at(-index) counts from end"""
        arr = Uint8Array([10, 20, 30])
        assert arr.at(-1) == 30
        assert arr.at(-2) == 20

    def test_at_out_of_bounds(self):
        """at() returns undefined for out of bounds"""
        arr = Uint8Array([10, 20, 30])
        assert arr.at(10) is None
        assert arr.at(-10) is None


class TestTypedArraySlice:
    """Test slice() method (FR-P3-061)"""

    def test_slice_no_args(self):
        """slice() copies entire array"""
        arr1 = Uint8Array([1, 2, 3, 4, 5])
        arr2 = arr1.slice()

        assert list(arr2) == [1, 2, 3, 4, 5]
        assert arr2.buffer is not arr1.buffer

    def test_slice_with_start(self):
        """slice(start)"""
        arr1 = Uint8Array([1, 2, 3, 4, 5])
        arr2 = arr1.slice(2)

        assert list(arr2) == [3, 4, 5]

    def test_slice_with_start_and_end(self):
        """slice(start, end)"""
        arr1 = Uint8Array([1, 2, 3, 4, 5])
        arr2 = arr1.slice(1, 4)

        assert list(arr2) == [2, 3, 4]

    def test_slice_negative_indices(self):
        """slice() with negative indices"""
        arr1 = Uint8Array([1, 2, 3, 4, 5])
        arr2 = arr1.slice(-3, -1)

        assert list(arr2) == [3, 4]


class TestTypedArraySubarray:
    """Test subarray() method (FR-P3-062)"""

    def test_subarray_shares_buffer(self):
        """subarray() creates new view of same buffer"""
        arr1 = Uint8Array([1, 2, 3, 4, 5])
        arr2 = arr1.subarray(1, 4)

        assert list(arr2) == [2, 3, 4]
        assert arr2.buffer is arr1.buffer

        # Modifying arr2 affects arr1
        arr2[0] = 99
        assert arr1[1] == 99

    def test_subarray_with_start(self):
        """subarray(start)"""
        arr1 = Uint8Array([1, 2, 3, 4, 5])
        arr2 = arr1.subarray(2)

        assert list(arr2) == [3, 4, 5]


class TestTypedArraySet:
    """Test set() method (FR-P3-063)"""

    def test_set_from_array(self):
        """set(array) copies values"""
        arr = Uint8Array(10)
        arr.set([1, 2, 3, 4, 5])

        assert arr[0] == 1
        assert arr[4] == 5

    def test_set_with_offset(self):
        """set(array, offset) copies at offset"""
        arr = Uint8Array(10)
        arr.set([1, 2, 3], 5)

        assert arr[4] == 0
        assert arr[5] == 1
        assert arr[6] == 2
        assert arr[7] == 3

    def test_set_from_typed_array(self):
        """set(typedArray) copies from TypedArray"""
        arr1 = Uint8Array([1, 2, 3])
        arr2 = Uint8Array(5)
        arr2.set(arr1, 2)

        assert arr2[2] == 1
        assert arr2[3] == 2
        assert arr2[4] == 3

    def test_set_overflow_throws(self):
        """set() throws if source doesn't fit"""
        arr = Uint8Array(5)
        with pytest.raises(RangeError):
            arr.set([1, 2, 3, 4, 5, 6], 1)


class TestTypedArrayCopyWithin:
    """Test copyWithin() method (FR-P3-064)"""

    def test_copy_within_basic(self):
        """copyWithin(target, start) copies within array"""
        arr = Uint8Array([1, 2, 3, 4, 5])
        arr.copyWithin(0, 3)

        assert list(arr) == [4, 5, 3, 4, 5]

    def test_copy_within_with_end(self):
        """copyWithin(target, start, end)"""
        arr = Uint8Array([1, 2, 3, 4, 5])
        arr.copyWithin(2, 0, 2)

        assert list(arr) == [1, 2, 1, 2, 5]


class TestTypedArrayIterationMethods:
    """Test array-like iteration methods (FR-P3-055)"""

    def test_forEach(self):
        """forEach() iterates over elements"""
        arr = Uint8Array([1, 2, 3])
        result = []
        arr.forEach(lambda val, idx, *args: result.append((val, idx)))

        assert result == [(1, 0), (2, 1), (3, 2)]

    def test_map(self):
        """map() creates new array with mapped values"""
        arr1 = Uint8Array([1, 2, 3])
        arr2 = arr1.map(lambda x, *args: x * 2)

        assert list(arr2) == [2, 4, 6]
        assert isinstance(arr2, Uint8Array)

    def test_filter(self):
        """filter() creates new array with filtered values"""
        arr1 = Uint8Array([1, 2, 3, 4, 5])
        arr2 = arr1.filter(lambda x, *args: x > 2)

        assert list(arr2) == [3, 4, 5]

    def test_reduce(self):
        """reduce() reduces to single value"""
        arr = Uint8Array([1, 2, 3, 4, 5])
        result = arr.reduce(lambda acc, val, *args: acc + val, 0)

        assert result == 15

    def test_every(self):
        """every() checks all elements"""
        arr = Uint8Array([2, 4, 6, 8])
        assert arr.every(lambda x, *args: x % 2 == 0)
        assert not arr.every(lambda x, *args: x > 5)

    def test_some(self):
        """some() checks any element"""
        arr = Uint8Array([1, 3, 5, 6])
        assert arr.some(lambda x, *args: x % 2 == 0)
        assert not arr.some(lambda x, *args: x > 10)

    def test_find(self):
        """find() returns first matching element"""
        arr = Uint8Array([1, 2, 3, 4, 5])
        assert arr.find(lambda x, *args: x > 2) == 3
        assert arr.find(lambda x, *args: x > 10) is None

    def test_find_index(self):
        """findIndex() returns index of first match"""
        arr = Uint8Array([1, 2, 3, 4, 5])
        assert arr.findIndex(lambda x, *args: x > 2) == 2
        assert arr.findIndex(lambda x, *args: x > 10) == -1


class TestTypedArrayOtherMethods:
    """Test other array-like methods (FR-P3-055)"""

    def test_fill(self):
        """fill() fills array with value"""
        arr = Uint8Array(5)
        arr.fill(42)
        assert list(arr) == [42, 42, 42, 42, 42]

    def test_fill_with_range(self):
        """fill(value, start, end)"""
        arr = Uint8Array(5)
        arr.fill(99, 1, 4)
        assert list(arr) == [0, 99, 99, 99, 0]

    def test_reverse(self):
        """reverse() reverses array in place"""
        arr = Uint8Array([1, 2, 3, 4, 5])
        arr.reverse()
        assert list(arr) == [5, 4, 3, 2, 1]

    def test_sort_numeric(self):
        """sort() sorts numerically"""
        arr = Uint8Array([5, 2, 8, 1, 9])
        arr.sort()
        assert list(arr) == [1, 2, 5, 8, 9]

    def test_sort_with_compare_function(self):
        """sort(compareFn) uses custom comparison"""
        arr = Uint8Array([1, 2, 3, 4, 5])
        arr.sort(lambda a, b: b - a)  # Descending
        assert list(arr) == [5, 4, 3, 2, 1]

    def test_includes(self):
        """includes() checks if value exists"""
        arr = Uint8Array([1, 2, 3, 4, 5])
        assert arr.includes(3)
        assert not arr.includes(10)

    def test_indexOf(self):
        """indexOf() returns first index of value"""
        arr = Uint8Array([1, 2, 3, 2, 1])
        assert arr.indexOf(2) == 1
        assert arr.indexOf(10) == -1

    def test_lastIndexOf(self):
        """lastIndexOf() returns last index of value"""
        arr = Uint8Array([1, 2, 3, 2, 1])
        assert arr.lastIndexOf(2) == 3
        assert arr.lastIndexOf(10) == -1

    def test_join(self):
        """join() creates string"""
        arr = Uint8Array([1, 2, 3])
        assert arr.join(',') == '1,2,3'
        assert arr.join('-') == '1-2-3'


class TestTypedArrayIterators:
    """Test iterator protocol (FR-P3-070)"""

    def test_keys_iterator(self):
        """keys() returns iterator of indices"""
        arr = Uint8Array([10, 20, 30])
        keys = list(arr.keys())
        assert keys == [0, 1, 2]

    def test_values_iterator(self):
        """values() returns iterator of values"""
        arr = Uint8Array([10, 20, 30])
        values = list(arr.values())
        assert values == [10, 20, 30]

    def test_entries_iterator(self):
        """entries() returns iterator of [index, value] pairs"""
        arr = Uint8Array([10, 20, 30])
        entries = list(arr.entries())
        assert entries == [(0, 10), (1, 20), (2, 30)]

    def test_symbol_iterator(self):
        """[Symbol.iterator]() makes array iterable"""
        arr = Uint8Array([10, 20, 30])
        # Should be iterable in for loop
        result = [x for x in arr]
        assert result == [10, 20, 30]


class TestTypedArrayTypeConversions:
    """Test type conversions for different TypedArray types (FR-P3-067)"""

    def test_int8_wrapping(self):
        """Int8Array wraps to -128..127"""
        arr = Int8Array([127, 128, 255, 256, -129])
        assert arr[0] == 127
        assert arr[1] == -128  # Wraps
        assert arr[2] == -1    # Wraps
        assert arr[3] == 0     # Wraps
        assert arr[4] == 127   # Wraps

    def test_uint8_wrapping(self):
        """Uint8Array wraps to 0..255"""
        arr = Uint8Array([255, 256, -1, -256])
        assert arr[0] == 255
        assert arr[1] == 0     # Wraps
        assert arr[2] == 255   # Wraps
        assert arr[3] == 0     # Wraps

    def test_uint8_clamped(self):
        """Uint8ClampedArray clamps to 0..255 (FR-P3-068)"""
        arr = Uint8ClampedArray([255, 256, -1, -100, 128.5, 128.6])
        assert arr[0] == 255
        assert arr[1] == 255   # Clamped to 255
        assert arr[2] == 0     # Clamped to 0
        assert arr[3] == 0     # Clamped to 0
        assert arr[4] == 128   # Rounded to even
        assert arr[5] == 129   # Rounded to even

    def test_int16_wrapping(self):
        """Int16Array wraps to -32768..32767"""
        arr = Int16Array([32767, 32768, -32769])
        assert arr[0] == 32767
        assert arr[1] == -32768  # Wraps
        assert arr[2] == 32767   # Wraps

    def test_float32_precision(self):
        """Float32Array has reduced precision"""
        arr = Float32Array([1.23456789012345])
        # Should be close but not exact due to single precision
        assert abs(arr[0] - 1.2345679) < 0.0001

    def test_float64_precision(self):
        """Float64Array has full double precision"""
        arr = Float64Array([1.23456789012345])
        assert abs(arr[0] - 1.23456789012345) < 1e-15


class TestTypedArrayDetachedBuffer:
    """Test behavior with detached buffers (FR-P3-069)"""

    def test_access_detached_throws(self):
        """Accessing TypedArray with detached buffer throws"""
        buf = ArrayBuffer(16)
        arr = Uint8Array(buf)
        buf.transfer()  # Detaches buffer

        with pytest.raises(TypeError):
            _ = arr[0]

    def test_set_on_detached_throws(self):
        """Setting value on detached buffer throws"""
        buf = ArrayBuffer(16)
        arr = Uint8Array(buf)
        buf.transfer()

        with pytest.raises(TypeError):
            arr[0] = 42

    def test_slice_detached_throws(self):
        """slice() on detached buffer throws"""
        buf = ArrayBuffer(16)
        arr = Uint8Array(buf)
        buf.transfer()

        with pytest.raises(TypeError):
            arr.slice()
