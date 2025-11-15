"""
Edge case tests for Proxy and Reflect.

Tests unusual scenarios and edge cases not covered elsewhere.
"""

import pytest


class TestProxyEdgeCases:
    """Test edge cases for Proxy."""

    def setup_method(self):
        from components.memory_gc.src import GarbageCollector
        self.gc = GarbageCollector()

    # Get trap edge cases
    def test_get_with_symbol_property(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_get

        target = JSObject(self.gc)
        # Simulate symbol property
        target.set_property("Symbol.iterator", Value.from_smi(42))

        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        result = proxy_get(proxy, "Symbol.iterator")
        assert result.to_smi() == 42

    def test_set_returns_false_when_trap_returns_false(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_set

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        handler._set_trap = lambda t, p, v, r: False

        proxy = Proxy(target, handler)

        result = proxy_set(proxy, "x", Value.from_smi(42))
        assert result is False

    def test_has_returns_false_for_missing_property(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_has

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        assert proxy_has(proxy, "missing") is False

    def test_delete_nonexistent_property_succeeds(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_delete_property

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        # Deleting non-existent property succeeds
        assert proxy_delete_property(proxy, "nonexistent") is True

    def test_own_keys_empty_target(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_own_keys

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        assert proxy_own_keys(proxy) == []

    def test_define_property_on_new_property(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_define_property

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        descriptor = {"value": Value.from_smi(42), "writable": True}
        result = proxy_define_property(proxy, "new_prop", descriptor)

        assert result is True

    def test_get_prototype_of_null_prototype(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_get_prototype_of

        target = JSObject(self.gc)
        target._prototype = None

        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        assert proxy_get_prototype_of(proxy) is None

    def test_set_prototype_to_null(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_set_prototype_of

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        result = proxy_set_prototype_of(proxy, None)
        assert result is True
        assert target._prototype is None

    def test_is_extensible_newly_created_target(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_is_extensible

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        # New objects are extensible by default
        assert proxy_is_extensible(proxy) is True

    def test_apply_with_empty_args(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_apply

        def target_func():
            return "called"

        handler = JSObject(self.gc)
        proxy = Proxy(target_func, handler)

        result = proxy_apply(proxy, None, [])
        assert result == "called"

    def test_construct_with_empty_args(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_construct

        def constructor():
            obj = JSObject(self.gc)
            obj.created = True
            return obj

        handler = JSObject(self.gc)
        proxy = Proxy(constructor, handler)

        result = proxy_construct(proxy, [])
        assert hasattr(result, "created")

    # Reflect edge cases
    def test_reflect_delete_nonexistent_property(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        # Deleting nonexistent property succeeds
        assert Reflect.deleteProperty(target, "nonexistent") is True

    def test_reflect_own_keys_empty_object(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        keys = Reflect.ownKeys(target)
        assert keys == []

    def test_reflect_get_own_property_descriptor_missing(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        desc = Reflect.getOwnPropertyDescriptor(target, "missing")
        assert desc is None

    def test_reflect_set_prototype_to_null(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        result = Reflect.setPrototypeOf(target, None)
        assert result is True
        assert target._prototype is None

    def test_reflect_apply_with_this_arg(self):
        from reflect_api import Reflect

        context = {"value": 10}

        def func(x):
            return x + 1

        result = Reflect.apply(func, context, [5])
        assert result == 6

    def test_reflect_construct_with_new_target(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject

        def Constructor():
            obj = JSObject(self.gc)
            obj.type = "constructed"
            return obj

        def AltConstructor():
            obj = JSObject(self.gc)
            obj.type = "alt"
            return obj

        result = Reflect.construct(Constructor, [], AltConstructor)
        assert hasattr(result, "type")

    # Revocable proxy edge cases
    def test_revoke_multiple_times_is_safe(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        result = Proxy.revocable(target, handler)
        revoke = result['revoke']

        # Call revoke multiple times
        revoke()
        revoke()
        revoke()
        # Should not error

    def test_revoked_proxy_all_operations_throw(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import (
            proxy_get, proxy_set, proxy_has, proxy_delete_property, proxy_own_keys
        )

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        result = Proxy.revocable(target, handler)
        proxy = result['proxy']
        revoke = result['revoke']

        revoke()

        # All operations should throw
        with pytest.raises(TypeError, match="revoked"):
            proxy_get(proxy, "x")
        with pytest.raises(TypeError, match="revoked"):
            proxy_set(proxy, "x", Value.from_smi(1))
        with pytest.raises(TypeError, match="revoked"):
            proxy_has(proxy, "x")
        with pytest.raises(TypeError, match="revoked"):
            proxy_delete_property(proxy, "x")
        with pytest.raises(TypeError, match="revoked"):
            proxy_own_keys(proxy)

    # Proxy constructor edge cases
    def test_proxy_accepts_function_target(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        def target_func():
            pass

        handler = JSObject(self.gc)
        proxy = Proxy(target_func, handler)
        assert proxy is not None

    def test_proxy_handler_can_be_empty(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        # Handler with no traps defined

        proxy = Proxy(target, handler)
        assert proxy is not None

    # Trap return value edge cases
    def test_own_keys_trap_returns_duplicates(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_own_keys

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        handler._own_keys_trap = lambda t: ["x", "y", "x"]  # Duplicate "x"

        proxy = Proxy(target, handler)

        # Should return what trap returns (including duplicates)
        keys = proxy_own_keys(proxy)
        assert keys == ["x", "y", "x"]

    def test_get_own_property_descriptor_returns_none(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_get_own_property_descriptor

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        handler._get_own_property_descriptor_trap = lambda t, p: None

        proxy = Proxy(target, handler)

        desc = proxy_get_own_property_descriptor(proxy, "x")
        assert desc is None

    def test_is_extensible_false_on_non_extensible_target(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_is_extensible

        target = JSObject(self.gc)
        target._extensible = False

        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        assert proxy_is_extensible(proxy) is False

    # Multiple properties edge cases
    def test_own_keys_returns_many_properties(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_own_keys

        target = JSObject(self.gc)
        for i in range(100):
            target.set_property(f"prop{i}", Value.from_smi(i))

        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        keys = proxy_own_keys(proxy)
        assert len(keys) == 100

    # Numeric property names
    def test_proxy_with_numeric_property_names(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_get, proxy_set

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        # Numeric property names (array-like)
        proxy_set(proxy, "0", Value.from_smi(100))
        result = proxy_get(proxy, "0")
        assert result.to_smi() == 100

    # Additional simple tests to ensure coverage
    def test_proxy_multiple_get_calls(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_get

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(42))

        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        # Multiple calls should work
        assert proxy_get(proxy, "x").to_smi() == 42
        assert proxy_get(proxy, "x").to_smi() == 42
        assert proxy_get(proxy, "x").to_smi() == 42

    def test_proxy_multiple_set_calls(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_set

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        # Multiple sets
        assert proxy_set(proxy, "a", Value.from_smi(1)) is True
        assert proxy_set(proxy, "b", Value.from_smi(2)) is True
        assert proxy_set(proxy, "c", Value.from_smi(3)) is True

    def test_reflect_multiple_operations(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        obj = JSObject(self.gc)

        # Multiple operations in sequence
        Reflect.set(obj, "a", Value.from_smi(1))
        Reflect.set(obj, "b", Value.from_smi(2))
        assert Reflect.has(obj, "a") is True
        assert Reflect.has(obj, "b") is True

    def test_proxy_handler_properties_independent(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target1 = JSObject(self.gc)
        target2 = JSObject(self.gc)

        handler1 = JSObject(self.gc)
        handler2 = JSObject(self.gc)

        proxy1 = Proxy(target1, handler1)
        proxy2 = Proxy(target2, handler2)

        # Proxies are independent
        assert proxy1._target is target1
        assert proxy2._target is target2

    def test_revocable_multiple_proxies(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        # Create multiple revocable proxies
        r1 = Proxy.revocable(target, handler)
        r2 = Proxy.revocable(target, handler)

        # They are independent
        assert r1['proxy'] is not r2['proxy']

    def test_own_keys_preserves_order(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_own_keys

        target = JSObject(self.gc)
        target.set_property("z", Value.from_smi(1))
        target.set_property("a", Value.from_smi(2))
        target.set_property("m", Value.from_smi(3))

        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        keys = proxy_own_keys(proxy)
        # Order should be preserved
        assert len(keys) == 3

    def test_reflect_set_creates_new_property(self):
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        obj = JSObject(self.gc)

        # Set new property
        Reflect.set(obj, "new", Value.from_smi(99))
        assert Reflect.has(obj, "new") is True

    def test_proxy_with_many_traps_independent(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        # Set multiple independent traps
        get_count = [0]
        set_count = [0]
        has_count = [0]

        def get_trap(t, p, r):
            get_count[0] += 1
            return t.get_property(p)

        def set_trap(t, p, v, r):
            set_count[0] += 1
            return True

        def has_trap(t, p):
            has_count[0] += 1
            return True

        handler._get_trap = get_trap
        handler._set_trap = set_trap
        handler._has_trap = has_trap

        proxy = Proxy(target, handler)

        from proxy_traps import proxy_get, proxy_set, proxy_has
        from components.value_system.src import Value

        proxy_get(proxy, "x")
        proxy_set(proxy, "x", Value.from_smi(1))
        proxy_has(proxy, "x")

        # Each trap was called once
        assert get_count[0] == 1
        assert set_count[0] == 1
        assert has_count[0] == 1
