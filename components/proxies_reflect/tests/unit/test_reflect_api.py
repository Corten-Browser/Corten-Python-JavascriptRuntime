"""
Unit tests for Reflect API (all 13 methods).

Tests the Reflect API that mirrors Proxy traps.
Covers requirement FR-P3-035.
"""

import pytest


class TestReflectAPI:
    """Test all 13 Reflect API methods."""

    def setup_method(self):
        from components.memory_gc.src import GarbageCollector
        self.gc = GarbageCollector()

    # Reflect.get tests
    def test_reflect_get_returns_property_value(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(42))

        result = Reflect.get(target, "x")
        assert result.to_smi() == 42

    def test_reflect_get_throws_on_non_object(self):
        from reflect_api import Reflect

        with pytest.raises(TypeError, match="must be an object"):
            Reflect.get(42, "x")

    # Reflect.set tests
    def test_reflect_set_sets_property(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        result = Reflect.set(target, "x", Value.from_smi(42))

        assert result is True
        assert target.get_property("x").to_smi() == 42

    def test_reflect_set_throws_on_non_object(self):
        from reflect_api import Reflect
        from components.value_system.src import Value

        with pytest.raises(TypeError, match="must be an object"):
            Reflect.set(42, "x", Value.from_smi(1))

    # Reflect.has tests
    def test_reflect_has_checks_property_existence(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(42))

        assert Reflect.has(target, "x") is True
        assert Reflect.has(target, "missing") is False

    def test_reflect_has_throws_on_non_object(self):
        from reflect_api import Reflect

        with pytest.raises(TypeError, match="must be an object"):
            Reflect.has("not an object", "x")

    # Reflect.deleteProperty tests
    def test_reflect_delete_property_deletes_property(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(42))

        result = Reflect.deleteProperty(target, "x")

        assert result is True
        assert "x" not in target._properties

    def test_reflect_delete_property_throws_on_non_object(self):
        from reflect_api import Reflect

        with pytest.raises(TypeError, match="must be an object"):
            Reflect.deleteProperty(123, "x")

    # Reflect.getOwnPropertyDescriptor tests
    def test_reflect_get_own_property_descriptor_returns_descriptor(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target._properties["x"] = {"value": Value.from_smi(42), "writable": True}

        desc = Reflect.getOwnPropertyDescriptor(target, "x")

        assert desc is not None
        assert desc["value"].to_smi() == 42

    def test_reflect_get_own_property_descriptor_returns_none_for_missing(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        desc = Reflect.getOwnPropertyDescriptor(target, "missing")

        assert desc is None

    def test_reflect_get_own_property_descriptor_throws_on_non_object(self):
        from reflect_api import Reflect

        with pytest.raises(TypeError, match="must be an object"):
            Reflect.getOwnPropertyDescriptor([], "x")

    # Reflect.defineProperty tests
    def test_reflect_define_property_defines_property(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        descriptor = {"value": Value.from_smi(42), "writable": True}

        result = Reflect.defineProperty(target, "x", descriptor)

        assert result is True
        assert "x" in target._properties

    def test_reflect_define_property_throws_on_non_object(self):
        from reflect_api import Reflect

        with pytest.raises(TypeError, match="must be an object"):
            Reflect.defineProperty("not object", "x", {})

    # Reflect.ownKeys tests
    def test_reflect_own_keys_returns_property_keys(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("a", Value.from_smi(1))
        target.set_property("b", Value.from_smi(2))

        keys = Reflect.ownKeys(target)

        assert set(keys) == {"a", "b"}

    def test_reflect_own_keys_returns_empty_for_no_properties(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        keys = Reflect.ownKeys(target)

        assert keys == []

    def test_reflect_own_keys_throws_on_non_object(self):
        from reflect_api import Reflect

        with pytest.raises(TypeError, match="must be an object"):
            Reflect.ownKeys(42)

    # Reflect.getPrototypeOf tests
    def test_reflect_get_prototype_of_returns_prototype(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        proto = JSObject(self.gc)
        target._prototype = proto

        result = Reflect.getPrototypeOf(target)

        assert result is proto

    def test_reflect_get_prototype_of_throws_on_non_object(self):
        from reflect_api import Reflect

        with pytest.raises(TypeError, match="must be an object"):
            Reflect.getPrototypeOf("string")

    # Reflect.setPrototypeOf tests
    def test_reflect_set_prototype_of_sets_prototype(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        proto = JSObject(self.gc)

        result = Reflect.setPrototypeOf(target, proto)

        assert result is True
        assert target._prototype is proto

    def test_reflect_set_prototype_of_throws_on_non_object(self):
        from reflect_api import Reflect

        with pytest.raises(TypeError, match="must be an object"):
            Reflect.setPrototypeOf([], None)

    # Reflect.isExtensible tests
    def test_reflect_is_extensible_returns_true_for_extensible(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)

        result = Reflect.isExtensible(target)

        assert result is True

    def test_reflect_is_extensible_throws_on_non_object(self):
        from reflect_api import Reflect

        with pytest.raises(TypeError, match="must be an object"):
            Reflect.isExtensible(123)

    # Reflect.preventExtensions tests
    def test_reflect_prevent_extensions_makes_non_extensible(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)

        result = Reflect.preventExtensions(target)

        assert result is True
        assert target._extensible is False

    def test_reflect_prevent_extensions_throws_on_non_object(self):
        from reflect_api import Reflect

        with pytest.raises(TypeError, match="must be an object"):
            Reflect.preventExtensions("string")

    # Reflect.apply tests
    def test_reflect_apply_calls_function(self):
        from reflect_api import Reflect

        def test_func(a, b):
            return a + b

        result = Reflect.apply(test_func, None, [2, 3])

        assert result == 5

    def test_reflect_apply_throws_on_non_callable(self):
        from reflect_api import Reflect

        with pytest.raises(TypeError, match="must be callable"):
            Reflect.apply("not callable", None, [])

    # Reflect.construct tests
    def test_reflect_construct_creates_object(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject

        def Constructor():
            obj = JSObject(self.gc)
            obj.name = "test"
            return obj

        result = Reflect.construct(Constructor, [])

        assert hasattr(result, "name")
        assert result.name == "test"

    def test_reflect_construct_throws_on_non_constructor(self):
        from reflect_api import Reflect

        with pytest.raises(TypeError, match="must be constructor"):
            Reflect.construct("not a constructor", [])
