"""
SameValueZero equality algorithm for Map and Set.

Per ECMAScript 2024 spec:
- +0 === -0: true (unlike SameValue)
- NaN === NaN: true (unlike strict equality)
- Objects compared by reference

Requirements: FR-P3-037, FR-P3-039
"""

import math


def same_value_zero(x, y):
    """
    Compare two values using SameValueZero algorithm.

    SameValueZero is used by Map and Set for key/value equality.

    Rules:
    1. +0 and -0 are considered equal
    2. NaN is considered equal to NaN
    3. All other values compared with strict equality (no type coercion)
    4. Objects compared by reference only

    Args:
        x: First value
        y: Second value

    Returns:
        bool: True if values are equal per SameValueZero
    """
    # Fast path: same object/reference
    if x is y:
        return True

    # Different types are never equal (strict equality, no coercion)
    if type(x) != type(y):
        return False

    # Handle NaN special case (NaN === NaN in SameValueZero)
    if isinstance(x, float) and math.isnan(x) and math.isnan(y):
        return True

    # For primitive types (numbers, strings, booleans, None), use value equality
    # For objects (dict, list, etc.), only same reference is equal (handled by x is y above)
    if isinstance(x, (int, float, str, bool, type(None))):
        return x == y

    # For all other types (objects, lists, etc.), only reference equality
    # This is already handled by the x is y check at the top
    return False
