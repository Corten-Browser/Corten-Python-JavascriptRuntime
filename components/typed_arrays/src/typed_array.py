"""
TypedArray implementation following ECMAScript 2024 specification.
Implements all 11 TypedArray variants with full array-like API.
"""

import struct
from array_buffer import ArrayBuffer
from exceptions import RangeError, TypeError as JSTypeError
from type_conversions import CONVERTERS


class TypedArray:
    """
    Base class for all TypedArray variants.
    Not directly constructible - use specific subclasses.
    """

    # Subclasses must define these
    _type_name = None  # e.g., 'Int8', 'Uint8', etc.
    BYTES_PER_ELEMENT = None

    def __init__(self, *args):
        """
        TypedArray construction supports multiple patterns:
        - TypedArray(length): Create array of given length
        - TypedArray(typedArray): Copy from another typed array
        - TypedArray(arrayLike): Create from array-like object
        - TypedArray(buffer, byteOffset?, length?): View of ArrayBuffer
        """
        if len(args) == 0:
            raise JSTypeError(f"TypedArray constructor requires at least 1 argument")

        arg0 = args[0]

        # Pattern: TypedArray(buffer, byteOffset?, length?)
        if isinstance(arg0, ArrayBuffer):
            self._init_from_buffer(*args)

        # Pattern: TypedArray(typedArray) - copy constructor
        elif isinstance(arg0, TypedArray):
            self._init_from_typed_array(arg0)

        # Pattern: TypedArray(arrayLike) - from list/iterable
        elif hasattr(arg0, '__iter__') and not isinstance(arg0, (str, bytes)):
            self._init_from_iterable(arg0)

        # Pattern: TypedArray(length) - create new buffer
        else:
            length = int(arg0)
            if length < 0:
                raise RangeError(f"Invalid typed array length: {length}")
            byte_length = length * self.BYTES_PER_ELEMENT
            self._buffer = ArrayBuffer(byte_length)
            self._byteOffset = 0
            self._length = length
            self._byteLength = byte_length

    def _init_from_buffer(self, buffer, byteOffset=0, length=None):
        """Initialize as view of ArrayBuffer"""
        byteOffset = int(byteOffset)

        # Check alignment
        if byteOffset % self.BYTES_PER_ELEMENT != 0:
            raise RangeError(
                f"Byte offset {byteOffset} is not aligned to "
                f"{self.BYTES_PER_ELEMENT}-byte boundary"
            )

        if byteOffset < 0 or byteOffset > buffer.byteLength:
            raise RangeError(f"Byte offset {byteOffset} out of range")

        if length is None:
            # Use remaining buffer
            remaining = buffer.byteLength - byteOffset
            if remaining % self.BYTES_PER_ELEMENT != 0:
                raise RangeError(
                    f"Buffer length {remaining} is not a multiple of "
                    f"{self.BYTES_PER_ELEMENT}"
                )
            length = remaining // self.BYTES_PER_ELEMENT
        else:
            length = int(length)
            if length < 0:
                raise RangeError(f"Invalid length: {length}")

        byte_length = length * self.BYTES_PER_ELEMENT

        if byteOffset + byte_length > buffer.byteLength:
            raise RangeError(
                f"TypedArray extends beyond buffer "
                f"({byteOffset + byte_length} > {buffer.byteLength})"
            )

        self._buffer = buffer
        self._byteOffset = byteOffset
        self._length = length
        self._byteLength = byte_length

    def _init_from_typed_array(self, source):
        """Initialize by copying from another TypedArray"""
        # Create new buffer
        byte_length = source.length * self.BYTES_PER_ELEMENT
        self._buffer = ArrayBuffer(byte_length)
        self._byteOffset = 0
        self._length = source.length
        self._byteLength = byte_length

        # Copy elements (with type conversion)
        for i in range(source.length):
            self[i] = source[i]

    def _init_from_iterable(self, iterable):
        """Initialize from array-like or iterable"""
        # Convert to list first
        items = list(iterable)
        length = len(items)

        # Create buffer
        byte_length = length * self.BYTES_PER_ELEMENT
        self._buffer = ArrayBuffer(byte_length)
        self._byteOffset = 0
        self._length = length
        self._byteLength = byte_length

        # Fill with values
        for i, value in enumerate(items):
            self[i] = value

    # Properties
    @property
    def buffer(self):
        """Underlying ArrayBuffer"""
        return self._buffer

    @property
    def byteLength(self):
        """Length in bytes"""
        if self._buffer.detached:
            return 0
        return self._byteLength

    @property
    def byteOffset(self):
        """Offset in buffer (bytes)"""
        if self._buffer.detached:
            return 0
        return self._byteOffset

    @property
    def length(self):
        """Number of elements"""
        if self._buffer.detached:
            return 0
        return self._length

    # Element access
    def __getitem__(self, index):
        """Get element at index"""
        if isinstance(index, slice):
            raise JSTypeError("Slice access not supported, use slice() method")

        index = int(index)
        if index < 0 or index >= self._length:
            return None  # undefined in JavaScript

        if self._buffer.detached:
            raise JSTypeError("Cannot access detached buffer")

        # Read raw bytes
        byte_index = self._byteOffset + index * self.BYTES_PER_ELEMENT
        raw_bytes = self._buffer._get_bytes(byte_index, self.BYTES_PER_ELEMENT)

        # Decode based on type
        return self._decode_element(raw_bytes)

    def __setitem__(self, index, value):
        """Set element at index"""
        if isinstance(index, slice):
            raise JSTypeError("Slice access not supported, use set() method")

        index = int(index)
        if index < 0 or index >= self._length:
            return  # Out of bounds set is ignored

        if self._buffer.detached:
            raise JSTypeError("Cannot modify detached buffer")

        # Convert value to correct type
        converted = self._convert_value(value)

        # Encode to bytes
        encoded_bytes = self._encode_element(converted)

        # Write to buffer
        byte_index = self._byteOffset + index * self.BYTES_PER_ELEMENT
        self._buffer._set_bytes(byte_index, encoded_bytes)

    def __len__(self):
        """Length for Python len()"""
        return self.length

    def __iter__(self):
        """Iterator protocol"""
        return self.values()

    # Type conversion methods (overridden by subclasses)
    def _convert_value(self, value):
        """Convert value to correct type using converter"""
        converter = CONVERTERS[self._type_name]
        return converter(value)

    def _decode_element(self, raw_bytes):
        """Decode bytes to element value (overridden by subclasses)"""
        raise NotImplementedError("Subclass must implement _decode_element")

    def _encode_element(self, value):
        """Encode value to bytes (overridden by subclasses)"""
        raise NotImplementedError("Subclass must implement _encode_element")

    # Static methods
    @classmethod
    def from_array(cls, source, mapFn=None, thisArg=None):
        """
        Create TypedArray from array-like or iterable.
        Optionally apply mapping function.
        """
        if mapFn is not None:
            items = [mapFn(item, i) for i, item in enumerate(source)]
        else:
            items = list(source)

        return cls(items)

    @classmethod
    def of(cls, *values):
        """Create TypedArray from argument list"""
        return cls(list(values))

    # Array-like methods
    def at(self, index):
        """Get element at index (supports negative indices)"""
        index = int(index)
        if index < 0:
            index = self._length + index

        if index < 0 or index >= self._length:
            return None  # undefined

        return self[index]

    def fill(self, value, start=0, end=None):
        """Fill array with value"""
        if end is None:
            end = self._length

        start = int(start)
        end = int(end)

        if start < 0:
            start = max(0, self._length + start)
        if end < 0:
            end = max(0, self._length + end)

        start = max(0, min(start, self._length))
        end = max(0, min(end, self._length))

        for i in range(start, end):
            self[i] = value

        return self

    def slice(self, start=0, end=None):
        """Copy portion of array to new TypedArray"""
        if self._buffer.detached:
            raise JSTypeError("Cannot slice detached buffer")

        if end is None:
            end = self._length

        start = int(start)
        end = int(end)

        if start < 0:
            start = max(0, self._length + start)
        if end < 0:
            end = max(0, self._length + end)

        start = max(0, min(start, self._length))
        end = max(start, min(end, self._length))

        length = end - start

        # Create new array
        result = type(self)(length)

        # Copy elements
        for i in range(length):
            result[i] = self[start + i]

        return result

    def subarray(self, begin=0, end=None):
        """Create new view of same buffer"""
        if end is None:
            end = self._length

        begin = int(begin)
        end = int(end)

        if begin < 0:
            begin = max(0, self._length + begin)
        if end < 0:
            end = max(0, self._length + end)

        begin = max(0, min(begin, self._length))
        end = max(begin, min(end, self._length))

        length = end - begin
        byteOffset = self._byteOffset + begin * self.BYTES_PER_ELEMENT

        return type(self)(self._buffer, byteOffset, length)

    def set(self, source, offset=0):
        """Copy values from source array"""
        offset = int(offset)
        if offset < 0:
            raise RangeError(f"Invalid offset: {offset}")

        source_list = list(source) if not isinstance(source, TypedArray) else [source[i] for i in range(source.length)]
        source_length = len(source_list)

        if offset + source_length > self._length:
            raise RangeError("Source array too large for target")

        for i, value in enumerate(source_list):
            self[offset + i] = value

    def copyWithin(self, target, start, end=None):
        """Copy portion of array within itself"""
        if end is None:
            end = self._length

        target = int(target)
        start = int(start)
        end = int(end)

        if target < 0:
            target = max(0, self._length + target)
        if start < 0:
            start = max(0, self._length + start)
        if end < 0:
            end = max(0, self._length + end)

        count = min(end - start, self._length - target)
        if count <= 0:
            return self

        # Copy to temp to handle overlapping regions
        temp = [self[start + i] for i in range(count)]
        for i in range(count):
            self[target + i] = temp[i]

        return self

    def forEach(self, callback, thisArg=None):
        """Execute callback for each element"""
        for i in range(self._length):
            callback(self[i], i, self)

    def map(self, callback, thisArg=None):
        """Create new array with mapped values"""
        result = type(self)(self._length)
        for i in range(self._length):
            result[i] = callback(self[i], i, self)
        return result

    def filter(self, callback, thisArg=None):
        """Create new array with filtered values"""
        filtered = []
        for i in range(self._length):
            if callback(self[i], i, self):
                filtered.append(self[i])
        return type(self)(filtered)

    def reduce(self, callback, initialValue=None):
        """Reduce array to single value"""
        if self._length == 0 and initialValue is None:
            raise JSTypeError("Reduce of empty array with no initial value")

        start_index = 0
        if initialValue is None:
            accumulator = self[0]
            start_index = 1
        else:
            accumulator = initialValue

        for i in range(start_index, self._length):
            accumulator = callback(accumulator, self[i], i, self)

        return accumulator

    def reduceRight(self, callback, initialValue=None):
        """Reduce array from right to left"""
        if self._length == 0 and initialValue is None:
            raise JSTypeError("Reduce of empty array with no initial value")

        start_index = self._length - 1
        if initialValue is None:
            accumulator = self[self._length - 1]
            start_index = self._length - 2
        else:
            accumulator = initialValue

        for i in range(start_index, -1, -1):
            accumulator = callback(accumulator, self[i], i, self)

        return accumulator

    def every(self, callback, thisArg=None):
        """Check if all elements satisfy predicate"""
        for i in range(self._length):
            if not callback(self[i], i, self):
                return False
        return True

    def some(self, callback, thisArg=None):
        """Check if any element satisfies predicate"""
        for i in range(self._length):
            if callback(self[i], i, self):
                return True
        return False

    def find(self, callback, thisArg=None):
        """Find first element satisfying predicate"""
        for i in range(self._length):
            if callback(self[i], i, self):
                return self[i]
        return None  # undefined

    def findIndex(self, callback, thisArg=None):
        """Find index of first element satisfying predicate"""
        for i in range(self._length):
            if callback(self[i], i, self):
                return i
        return -1

    def includes(self, value, fromIndex=0):
        """Check if array includes value"""
        fromIndex = int(fromIndex)
        if fromIndex < 0:
            fromIndex = max(0, self._length + fromIndex)

        for i in range(fromIndex, self._length):
            if self[i] == value:
                return True
        return False

    def indexOf(self, value, fromIndex=0):
        """Find first index of value"""
        fromIndex = int(fromIndex)
        if fromIndex < 0:
            fromIndex = max(0, self._length + fromIndex)

        for i in range(fromIndex, self._length):
            if self[i] == value:
                return i
        return -1

    def lastIndexOf(self, value, fromIndex=None):
        """Find last index of value"""
        if fromIndex is None:
            fromIndex = self._length - 1
        else:
            fromIndex = int(fromIndex)
            if fromIndex < 0:
                fromIndex = self._length + fromIndex

        for i in range(min(fromIndex, self._length - 1), -1, -1):
            if self[i] == value:
                return i
        return -1

    def join(self, separator=','):
        """Join elements to string"""
        return separator.join(str(self[i]) for i in range(self._length))

    def reverse(self):
        """Reverse array in place"""
        for i in range(self._length // 2):
            j = self._length - 1 - i
            temp = self[i]
            self[i] = self[j]
            self[j] = temp
        return self

    def sort(self, compareFn=None):
        """Sort array in place"""
        # Extract elements
        elements = [self[i] for i in range(self._length)]

        # Sort
        if compareFn is None:
            elements.sort()
        else:
            # Python's sort expects: negative if a<b, 0 if a==b, positive if a>b
            import functools
            elements.sort(key=functools.cmp_to_key(compareFn))

        # Write back
        for i, value in enumerate(elements):
            self[i] = value

        return self

    def toLocaleString(self):
        """Convert to locale string"""
        return self.join(',')

    def toString(self):
        """Convert to string"""
        return self.join(',')

    # Iterator methods
    def keys(self):
        """Iterator of indices"""
        for i in range(self._length):
            yield i

    def values(self):
        """Iterator of values"""
        for i in range(self._length):
            yield self[i]

    def entries(self):
        """Iterator of [index, value] pairs"""
        for i in range(self._length):
            yield (i, self[i])


# Now define all 11 TypedArray variants with their specific encoding/decoding

class Int8Array(TypedArray):
    """8-bit signed integer array"""
    _type_name = 'Int8'
    BYTES_PER_ELEMENT = 1

    def _decode_element(self, raw_bytes):
        return struct.unpack('b', raw_bytes)[0]

    def _encode_element(self, value):
        return struct.pack('b', value)


class Uint8Array(TypedArray):
    """8-bit unsigned integer array"""
    _type_name = 'Uint8'
    BYTES_PER_ELEMENT = 1

    def _decode_element(self, raw_bytes):
        return struct.unpack('B', raw_bytes)[0]

    def _encode_element(self, value):
        return struct.pack('B', value)


class Uint8ClampedArray(TypedArray):
    """8-bit unsigned integer array with clamping"""
    _type_name = 'Uint8Clamped'
    BYTES_PER_ELEMENT = 1

    def _decode_element(self, raw_bytes):
        return struct.unpack('B', raw_bytes)[0]

    def _encode_element(self, value):
        return struct.pack('B', value)


class Int16Array(TypedArray):
    """16-bit signed integer array"""
    _type_name = 'Int16'
    BYTES_PER_ELEMENT = 2

    def _decode_element(self, raw_bytes):
        return struct.unpack('<h', raw_bytes)[0]  # Little-endian

    def _encode_element(self, value):
        return struct.pack('<h', value)


class Uint16Array(TypedArray):
    """16-bit unsigned integer array"""
    _type_name = 'Uint16'
    BYTES_PER_ELEMENT = 2

    def _decode_element(self, raw_bytes):
        return struct.unpack('<H', raw_bytes)[0]

    def _encode_element(self, value):
        return struct.pack('<H', value)


class Int32Array(TypedArray):
    """32-bit signed integer array"""
    _type_name = 'Int32'
    BYTES_PER_ELEMENT = 4

    def _decode_element(self, raw_bytes):
        return struct.unpack('<i', raw_bytes)[0]

    def _encode_element(self, value):
        return struct.pack('<i', value)


class Uint32Array(TypedArray):
    """32-bit unsigned integer array"""
    _type_name = 'Uint32'
    BYTES_PER_ELEMENT = 4

    def _decode_element(self, raw_bytes):
        return struct.unpack('<I', raw_bytes)[0]

    def _encode_element(self, value):
        return struct.pack('<I', value)


class Float32Array(TypedArray):
    """32-bit floating point array"""
    _type_name = 'Float32'
    BYTES_PER_ELEMENT = 4

    def _decode_element(self, raw_bytes):
        return struct.unpack('<f', raw_bytes)[0]

    def _encode_element(self, value):
        return struct.pack('<f', value)


class Float64Array(TypedArray):
    """64-bit floating point array"""
    _type_name = 'Float64'
    BYTES_PER_ELEMENT = 8

    def _decode_element(self, raw_bytes):
        return struct.unpack('<d', raw_bytes)[0]

    def _encode_element(self, value):
        return struct.pack('<d', value)


class BigInt64Array(TypedArray):
    """64-bit signed BigInt array"""
    _type_name = 'BigInt64'
    BYTES_PER_ELEMENT = 8

    def _decode_element(self, raw_bytes):
        return struct.unpack('<q', raw_bytes)[0]

    def _encode_element(self, value):
        return struct.pack('<q', value)


class BigUint64Array(TypedArray):
    """64-bit unsigned BigInt array"""
    _type_name = 'BigUint64'
    BYTES_PER_ELEMENT = 8

    def _decode_element(self, raw_bytes):
        return struct.unpack('<Q', raw_bytes)[0]

    def _encode_element(self, value):
        return struct.pack('<Q', value)
