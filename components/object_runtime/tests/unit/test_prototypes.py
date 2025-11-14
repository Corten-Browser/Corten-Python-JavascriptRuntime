"""
Unit tests for built-in prototype factory functions.

Tests creation of standard JavaScript prototypes
(Object.prototype, Array.prototype, Function.prototype).
"""

import pytest


class TestObjectPrototype:
    """Test CreateObjectPrototype factory function."""

    def test_create_object_prototype_returns_jsobject(self):
        """Test that CreateObjectPrototype returns a JSObject."""
        from components.memory_gc.src import GarbageCollector
        from js_object import JSObject
        from prototypes import CreateObjectPrototype

        gc = GarbageCollector()
        obj_proto = CreateObjectPrototype(gc)

        assert isinstance(obj_proto, JSObject)

    def test_object_prototype_has_tostring_method(self):
        """Test that Object.prototype has toString method."""
        from components.memory_gc.src import GarbageCollector
        from prototypes import CreateObjectPrototype

        gc = GarbageCollector()
        obj_proto = CreateObjectPrototype(gc)

        # Check for toString property (it will be a JSFunction)
        toString = obj_proto.get_property("toString")
        assert toString is not None
        # In real implementation, this would be a JSFunction
        # For now, just verify it exists and is not undefined


class TestArrayPrototype:
    """Test CreateArrayPrototype factory function."""

    def test_create_array_prototype_returns_jsarray(self):
        """Test that CreateArrayPrototype returns a JSArray."""
        from components.memory_gc.src import GarbageCollector
        from js_array import JSArray
        from prototypes import CreateArrayPrototype

        gc = GarbageCollector()
        arr_proto = CreateArrayPrototype(gc)

        # Array prototype is actually a JSArray (special case)
        assert isinstance(arr_proto, JSArray)

    def test_array_prototype_has_push_method(self):
        """Test that Array.prototype has push method."""
        from components.memory_gc.src import GarbageCollector
        from prototypes import CreateArrayPrototype

        gc = GarbageCollector()
        arr_proto = CreateArrayPrototype(gc)

        # Check for push property
        push = arr_proto.get_property("push")
        assert push is not None

    def test_array_prototype_has_pop_method(self):
        """Test that Array.prototype has pop method."""
        from components.memory_gc.src import GarbageCollector
        from prototypes import CreateArrayPrototype

        gc = GarbageCollector()
        arr_proto = CreateArrayPrototype(gc)

        # Check for pop property
        pop = arr_proto.get_property("pop")
        assert pop is not None


class TestFunctionPrototype:
    """Test CreateFunctionPrototype factory function."""

    def test_create_function_prototype_returns_jsfunction(self):
        """Test that CreateFunctionPrototype returns a JSFunction."""
        from components.memory_gc.src import GarbageCollector
        from js_function import JSFunction
        from prototypes import CreateFunctionPrototype

        gc = GarbageCollector()
        func_proto = CreateFunctionPrototype(gc)

        # Function prototype is actually a JSFunction
        assert isinstance(func_proto, JSFunction)

    def test_function_prototype_has_call_method(self):
        """Test that Function.prototype has call method."""
        from components.memory_gc.src import GarbageCollector
        from prototypes import CreateFunctionPrototype

        gc = GarbageCollector()
        func_proto = CreateFunctionPrototype(gc)

        # Check for call property
        call = func_proto.get_property("call")
        assert call is not None


class TestPrototypeChain:
    """Test prototype chain setup."""

    def test_array_prototype_inherits_from_object_prototype(self):
        """Test that Array.prototype's prototype is Object.prototype."""
        from components.memory_gc.src import GarbageCollector
        from prototypes import CreateObjectPrototype, CreateArrayPrototype

        gc = GarbageCollector()
        obj_proto = CreateObjectPrototype(gc)
        arr_proto = CreateArrayPrototype(gc, obj_proto)

        # Array prototype should have Object prototype as its prototype
        assert arr_proto.get_prototype() is obj_proto

    def test_function_prototype_inherits_from_object_prototype(self):
        """Test that Function.prototype's prototype is Object.prototype."""
        from components.memory_gc.src import GarbageCollector
        from prototypes import CreateObjectPrototype, CreateFunctionPrototype

        gc = GarbageCollector()
        obj_proto = CreateObjectPrototype(gc)
        func_proto = CreateFunctionPrototype(gc, obj_proto)

        # Function prototype should have Object prototype as its prototype
        assert func_proto.get_prototype() is obj_proto
