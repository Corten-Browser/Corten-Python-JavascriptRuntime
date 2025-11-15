"""
object_runtime - JavaScript object model, property storage, and built-in objects.

This module provides:
- JSObject: JavaScript object with property storage and prototype chain
- JSArray: JavaScript array extending JSObject
- JSFunction: JavaScript function extending JSObject
- JSString: JavaScript string extending JSObject
- Built-in prototype factory functions

Public API:
    Classes:
        - JSObject: Base JavaScript object class
        - JSArray: JavaScript array class
        - JSFunction: JavaScript function class
        - JSString: JavaScript string class

    Functions:
        - CreateObjectPrototype: Create Object.prototype
        - CreateArrayPrototype: Create Array.prototype
        - CreateFunctionPrototype: Create Function.prototype

    Constants:
        - UNDEFINED_VALUE: Sentinel value for undefined

Example:
    >>> from components.object_runtime.src import JSObject, JSArray
    >>> from components.memory_gc.src import GarbageCollector
    >>> from components.value_system.src import Value
    >>>
    >>> gc = GarbageCollector()
    >>> obj = JSObject(gc)
    >>> obj.set_property("name", Value.from_smi(42))
    >>> obj.get_property("name").to_smi()
    42
    >>>
    >>> arr = JSArray(gc)
    >>> arr.push(Value.from_smi(10))
    1
    >>> arr.get_element(0).to_smi()
    10
"""

# Export public classes
from .js_object import JSObject, UNDEFINED_VALUE
from .js_array import JSArray
from .js_function import JSFunction
from .js_string import JSString
from .object_constructor import ObjectConstructor, Object

# Export prototype factory functions
from .prototypes import (
    CreateObjectPrototype,
    CreateArrayPrototype,
    CreateFunctionPrototype,
)

__all__ = [
    # Classes
    "JSObject",
    "JSArray",
    "JSFunction",
    "JSString",
    "ObjectConstructor",
    "Object",
    # Constants
    "UNDEFINED_VALUE",
    # Factory functions
    "CreateObjectPrototype",
    "CreateArrayPrototype",
    "CreateFunctionPrototype",
]

__version__ = "0.1.0"
