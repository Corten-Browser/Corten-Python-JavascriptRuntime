"""
Built-in prototype factory functions.

This module provides factory functions to create standard JavaScript
prototypes (Object.prototype, Array.prototype, Function.prototype).
"""

from typing import Optional
from components.memory_gc.src import GarbageCollector
from components.value_system.src import Value
from .js_object import JSObject
from .js_array import JSArray
from .js_function import JSFunction


def CreateObjectPrototype(gc: GarbageCollector) -> JSObject:
    """
    Create Object.prototype.

    The Object prototype is the root of the prototype chain.
    All objects ultimately inherit from Object.prototype.

    Args:
        gc: Garbage collector managing objects

    Returns:
        JSObject representing Object.prototype with standard methods

    Example:
        >>> gc = GarbageCollector()
        >>> obj_proto = CreateObjectPrototype(gc)
        >>> obj = JSObject(gc, prototype=obj_proto)
        >>> obj.has_property("toString")
        True
    """
    # Create base object prototype with no prototype (root of chain)
    obj_proto = JSObject(gc, prototype=None)

    # Add toString method
    def toString(this):
        """toString implementation."""
        return Value.from_smi(hash("[object Object]") % 1000)

    toString_func = JSFunction(gc, toString, name="toString")
    obj_proto.set_property("toString", Value.from_object(toString_func))

    # Add hasOwnProperty method
    def hasOwnProperty(this, key):
        """hasOwnProperty implementation."""
        # Check if property exists directly on object (not inherited)
        has = key in this._properties if hasattr(this, "_properties") else False
        return Value.from_smi(1 if has else 0)

    hasOwn_func = JSFunction(gc, hasOwnProperty, name="hasOwnProperty")
    obj_proto.set_property("hasOwnProperty", Value.from_object(hasOwn_func))

    return obj_proto


def CreateArrayPrototype(
    gc: GarbageCollector, object_proto: Optional[JSObject] = None
) -> JSArray:
    """
    Create Array.prototype.

    Array prototype provides array-specific methods and inherits
    from Object.prototype.

    Args:
        gc: Garbage collector managing objects
        object_proto: Object.prototype to inherit from (optional)

    Returns:
        JSArray representing Array.prototype with standard array methods

    Example:
        >>> gc = GarbageCollector()
        >>> obj_proto = CreateObjectPrototype(gc)
        >>> arr_proto = CreateArrayPrototype(gc, obj_proto)
        >>> arr = JSArray(gc, prototype=arr_proto)
        >>> arr.has_property("push")
        True
    """
    # Array.prototype is itself an array with Object.prototype as its prototype
    arr_proto = JSArray(gc, length=0)

    # Set prototype chain
    if object_proto is not None:
        arr_proto.set_prototype(object_proto)

    # Add push method (wraps the built-in push)
    def push_method(this, *values):
        """push method implementation."""
        if isinstance(this, JSArray):
            for val in values:
                this.push(val)
            return Value.from_smi(this._length)
        return Value.from_smi(-1)

    push_func = JSFunction(gc, push_method, name="push")
    arr_proto.set_property("push", Value.from_object(push_func))

    # Add pop method (wraps the built-in pop)
    def pop_method(this):
        """pop method implementation."""
        if isinstance(this, JSArray):
            return this.pop()
        return Value.from_smi(-1)

    pop_func = JSFunction(gc, pop_method, name="pop")
    arr_proto.set_property("pop", Value.from_object(pop_func))

    return arr_proto


def CreateFunctionPrototype(
    gc: GarbageCollector, object_proto: Optional[JSObject] = None
) -> JSFunction:
    """
    Create Function.prototype.

    Function prototype provides function-specific methods and inherits
    from Object.prototype.

    Args:
        gc: Garbage collector managing objects
        object_proto: Object.prototype to inherit from (optional)

    Returns:
        JSFunction representing Function.prototype with standard function methods

    Example:
        >>> gc = GarbageCollector()
        >>> obj_proto = CreateObjectPrototype(gc)
        >>> func_proto = CreateFunctionPrototype(gc, obj_proto)
        >>> func = JSFunction(gc, lambda: None, prototype=func_proto)
        >>> func.has_property("call")
        True
    """

    # Function.prototype is itself a function that does nothing
    def noop():
        """No-op function."""
        return Value.from_smi(-1)

    func_proto = JSFunction(gc, noop, name="")

    # Set prototype chain
    if object_proto is not None:
        func_proto.set_prototype(object_proto)

    # Add call method
    def call_method(this, this_arg, *args):
        """call method implementation."""
        if isinstance(this, JSFunction):
            return this.call(list(args), this_context=this_arg)
        return Value.from_smi(-1)

    call_func = JSFunction(gc, call_method, name="call")
    func_proto.set_property("call", Value.from_object(call_func))

    # Add apply method
    def apply_method(this, this_arg, args_array):
        """apply method implementation."""
        if isinstance(this, JSFunction):
            args = []
            if isinstance(args_array, JSArray):
                # Extract elements from array
                for i in range(args_array._length):
                    args.append(args_array.get_element(i))
            return this.call(args, this_context=this_arg)
        return Value.from_smi(-1)

    apply_func = JSFunction(gc, apply_method, name="apply")
    func_proto.set_property("apply", Value.from_object(apply_func))

    return func_proto
