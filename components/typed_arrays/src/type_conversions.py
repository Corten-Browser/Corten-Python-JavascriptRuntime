"""
Type conversion utilities for TypedArray elements.
Implements wrapping, clamping, and precision conversion per ECMAScript spec.
"""

import struct
import math


def to_int8(value):
    """
    Convert to Int8 (-128 to 127) with wrapping.
    """
    if isinstance(value, bool):
        value = 1 if value else 0
    value = int(value)
    # Wrap to -128..127
    value = value % 256
    if value >= 128:
        value -= 256
    return value


def to_uint8(value):
    """
    Convert to Uint8 (0 to 255) with wrapping.
    """
    if isinstance(value, bool):
        value = 1 if value else 0
    value = int(value)
    # Wrap to 0..255
    return value % 256


def to_uint8_clamped(value):
    """
    Convert to Uint8Clamped (0 to 255) with clamping and special rounding.
    Spec: rounds to even for .5 values (banker's rounding).
    """
    if isinstance(value, bool):
        value = 1 if value else 0

    # Clamp to 0..255
    if value <= 0:
        return 0
    if value >= 255:
        return 255

    # Special rounding for .5 (round to even)
    floor_val = math.floor(value)
    if value - floor_val == 0.5:
        # Round to even
        if floor_val % 2 == 0:
            return floor_val
        else:
            return floor_val + 1
    else:
        return round(value)


def to_int16(value):
    """
    Convert to Int16 (-32768 to 32767) with wrapping.
    """
    if isinstance(value, bool):
        value = 1 if value else 0
    value = int(value)
    # Wrap to -32768..32767
    value = value % 65536
    if value >= 32768:
        value -= 65536
    return value


def to_uint16(value):
    """
    Convert to Uint16 (0 to 65535) with wrapping.
    """
    if isinstance(value, bool):
        value = 1 if value else 0
    value = int(value)
    # Wrap to 0..65535
    return value % 65536


def to_int32(value):
    """
    Convert to Int32 (-2^31 to 2^31-1) with wrapping.
    """
    if isinstance(value, bool):
        value = 1 if value else 0
    value = int(value)
    # Wrap to -2147483648..2147483647
    value = value % 4294967296
    if value >= 2147483648:
        value -= 4294967296
    return value


def to_uint32(value):
    """
    Convert to Uint32 (0 to 2^32-1) with wrapping.
    """
    if isinstance(value, bool):
        value = 1 if value else 0
    value = int(value)
    # Wrap to 0..4294967295
    return value % 4294967296


def to_float32(value):
    """
    Convert to Float32 (IEEE 754 single precision).
    """
    if isinstance(value, bool):
        value = 1.0 if value else 0.0

    # Pack as float32 and unpack to get precision loss
    try:
        packed = struct.pack('f', float(value))
        return struct.unpack('f', packed)[0]
    except (struct.error, OverflowError):
        # Handle infinity, NaN, etc.
        return float(value)


def to_float64(value):
    """
    Convert to Float64 (IEEE 754 double precision).
    """
    if isinstance(value, bool):
        value = 1.0 if value else 0.0
    return float(value)


def to_bigint64(value):
    """
    Convert to BigInt64 (signed 64-bit integer).
    """
    if not isinstance(value, int):
        raise TypeError("BigInt64Array requires BigInt/int values")

    # Wrap to -2^63..2^63-1
    value = value % (2**64)
    if value >= 2**63:
        value -= 2**64
    return value


def to_biguint64(value):
    """
    Convert to BigUint64 (unsigned 64-bit integer).
    """
    if not isinstance(value, int):
        raise TypeError("BigUint64Array requires BigInt/int values")

    # Wrap to 0..2^64-1
    return value % (2**64)


# Converter registry for each TypedArray type
CONVERTERS = {
    'Int8': to_int8,
    'Uint8': to_uint8,
    'Uint8Clamped': to_uint8_clamped,
    'Int16': to_int16,
    'Uint16': to_uint16,
    'Int32': to_int32,
    'Uint32': to_uint32,
    'Float32': to_float32,
    'Float64': to_float64,
    'BigInt64': to_bigint64,
    'BigUint64': to_biguint64,
}
