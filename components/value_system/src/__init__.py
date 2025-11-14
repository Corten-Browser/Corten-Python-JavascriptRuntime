"""
Value system - tagged pointer representation for JavaScript values.

This package provides the Value class for efficient representation of
JavaScript values using tagged pointers, along with type checking and
conversion functions per ECMAScript specification.

Public API:
    - Value: Tagged value representation class
    - IsNumber: Check if value is number
    - IsString: Check if value is string
    - IsObject: Check if value is object
    - IsUndefined: Check if value is undefined
    - IsNull: Check if value is null
    - ToNumber: Convert value to number
    - ToString: Convert value to string
    - ToBoolean: Convert value to boolean
    - NULL_VALUE: Sentinel for JavaScript null
"""

from .value import Value
from .type_check import (
    IsNumber,
    IsString,
    IsObject,
    IsUndefined,
    IsNull,
    NULL_VALUE,
)
from .conversions import ToNumber, ToString, ToBoolean

__all__ = [
    "Value",
    "IsNumber",
    "IsString",
    "IsObject",
    "IsUndefined",
    "IsNull",
    "ToNumber",
    "ToString",
    "ToBoolean",
    "NULL_VALUE",
]

__version__ = "0.1.0"
