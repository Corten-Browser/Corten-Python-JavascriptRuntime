"""
Custom exceptions for TypedArrays.
"""


class RangeError(Exception):
    """Raised for out-of-range values or indices"""
    pass


class TypeError(Exception):
    """Raised for type mismatches or invalid operations"""
    pass
