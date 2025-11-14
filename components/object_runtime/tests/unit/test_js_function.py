"""
Unit tests for JSFunction class.

Tests JavaScript function representation.
"""

import pytest


class TestJSFunctionCreation:
    """Test JSFunction instantiation."""

    def test_create_function_with_callable(self):
        """Test creating JSFunction with a Python callable."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_function import JSFunction

        gc = GarbageCollector()

        def add(a, b):
            return Value.from_smi(a.to_smi() + b.to_smi())

        func = JSFunction(gc, add)

        assert func is not None
        assert callable(func._callable)

    def test_create_function_with_name(self):
        """Test creating JSFunction with a name."""
        from components.memory_gc.src import GarbageCollector
        from js_function import JSFunction

        gc = GarbageCollector()

        def my_func():
            pass

        func = JSFunction(gc, my_func, name="myFunction")

        assert func.get_property("name").to_smi() != -1  # Not undefined


class TestJSFunctionCall:
    """Test function call operations."""

    def test_call_function_with_no_args(self):
        """Test calling function with no arguments."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_function import JSFunction

        gc = GarbageCollector()

        def get_value():
            return Value.from_smi(42)

        func = JSFunction(gc, get_value)
        result = func.call([])

        assert result.is_smi()
        assert result.to_smi() == 42

    def test_call_function_with_args(self):
        """Test calling function with arguments."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_function import JSFunction

        gc = GarbageCollector()

        def add(a, b):
            return Value.from_smi(a.to_smi() + b.to_smi())

        func = JSFunction(gc, add)
        args = [Value.from_smi(10), Value.from_smi(20)]
        result = func.call(args)

        assert result.is_smi()
        assert result.to_smi() == 30

    def test_call_function_with_this_context(self):
        """Test calling function with 'this' context."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_function import JSFunction
        from js_object import JSObject

        gc = GarbageCollector()

        def get_x(this):
            return this.get_property("x")

        func = JSFunction(gc, get_x)
        this_obj = JSObject(gc)
        this_obj.set_property("x", Value.from_smi(100))

        result = func.call([], this_context=this_obj)

        assert result.is_smi()
        assert result.to_smi() == 100


class TestJSFunctionProperties:
    """Test function property operations."""

    def test_function_has_length_property(self):
        """Test that functions have a length property."""
        from components.memory_gc.src import GarbageCollector
        from js_function import JSFunction

        gc = GarbageCollector()

        def my_func(a, b, c):
            pass

        func = JSFunction(gc, my_func)

        # In Python, we can get arg count via inspection
        # For now, just verify it's not undefined
        length = func.get_property("length")
        assert length is not None

    def test_function_has_name_property(self):
        """Test that functions have a name property."""
        from components.memory_gc.src import GarbageCollector
        from js_function import JSFunction

        gc = GarbageCollector()

        def my_function():
            pass

        func = JSFunction(gc, my_function, name="myFunction")

        name = func.get_property("name")
        assert name is not None


class TestJSFunctionGCIntegration:
    """Test garbage collection integration."""

    def test_get_references_returns_prototype(self):
        """Test get_references returns prototype."""
        from components.memory_gc.src import GarbageCollector
        from js_function import JSFunction
        from js_object import JSObject

        gc = GarbageCollector()
        prototype = JSObject(gc)

        def my_func():
            pass

        func = JSFunction(gc, my_func, prototype=prototype)

        references = func.get_references()

        assert prototype in references
