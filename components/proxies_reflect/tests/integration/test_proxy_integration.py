"""
Integration tests for Proxy and Reflect.

Tests complex proxy scenarios and integration with Reflect API.
"""

import pytest


class TestProxyReflectIntegration:
    """Test Proxy and Reflect working together."""

    def setup_method(self):
        from components.memory_gc.src import GarbageCollector
        self.gc = GarbageCollector()

    def test_proxy_with_reflect_in_traps(self):
        """Test using Reflect methods inside proxy traps."""
        from proxy import Proxy
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        def get_trap(tgt, prop, receiver):
            # Use Reflect.get as default behavior
            return Reflect.get(tgt, prop)

        handler._get_trap = get_trap
        proxy = Proxy(target, handler)

        Reflect.set(target, "x", Value.from_smi(42))

        from proxy_traps import proxy_get
        result = proxy_get(proxy, "x")
        assert result.to_smi() == 42

    def test_nested_proxies(self):
        """Test proxy of proxy."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(10))

        handler1 = JSObject(self.gc)
        handler1._get_trap = lambda tgt, prop, rcv: Value.from_smi(20)

        proxy1 = Proxy(target, handler1)

        handler2 = JSObject(self.gc)
        handler2._get_trap = lambda tgt, prop, rcv: Value.from_smi(30)

        proxy2 = Proxy(proxy1, handler2)

        from proxy_traps import proxy_get
        # Outer proxy returns 30
        assert proxy_get(proxy2, "x").to_smi() == 30

    def test_property_access_logger(self):
        """Test logging all property accesses with proxy."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("name", Value.from_smi(1))
        target.set_property("age", Value.from_smi(2))

        access_log = []
        handler = JSObject(self.gc)

        def get_trap(tgt, prop, receiver):
            access_log.append(f"GET {prop}")
            return tgt.get_property(prop)

        def set_trap(tgt, prop, value, receiver):
            access_log.append(f"SET {prop}")
            tgt.set_property(prop, value)
            return True

        handler._get_trap = get_trap
        handler._set_trap = set_trap

        proxy = Proxy(target, handler)

        from proxy_traps import proxy_get, proxy_set
        proxy_get(proxy, "name")
        proxy_set(proxy, "age", Value.from_smi(25))
        proxy_get(proxy, "age")

        assert access_log == ["GET name", "SET age", "GET age"]

    def test_validation_proxy(self):
        """Test validation with proxy."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        def set_trap(tgt, prop, value, receiver):
            # Only allow positive numbers
            if value.to_smi() < 0:
                return False
            tgt.set_property(prop, value)
            return True

        handler._set_trap = set_trap
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_set
        assert proxy_set(proxy, "positive", Value.from_smi(10)) is True
        assert proxy_set(proxy, "negative", Value.from_smi(-5)) is False

    def test_default_values_proxy(self):
        """Test proxy providing default values for missing properties."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        def get_trap(tgt, prop, receiver):
            if hasattr(tgt, "_properties") and prop in tgt._properties:
                return tgt.get_property(prop)
            # Return default value
            return Value.from_smi(0)

        handler._get_trap = get_trap
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_get
        # Missing property returns default
        assert proxy_get(proxy, "missing").to_smi() == 0

    def test_read_only_proxy(self):
        """Test making object read-only with proxy."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(42))

        handler = JSObject(self.gc)
        # Reject all sets
        handler._set_trap = lambda tgt, prop, val, rcv: False

        proxy = Proxy(target, handler)

        from proxy_traps import proxy_set
        # Cannot modify
        assert proxy_set(proxy, "x", Value.from_smi(100)) is False
        # Original value unchanged
        assert target.get_property("x").to_smi() == 42

    def test_property_enumeration_filtering(self):
        """Test filtering properties during enumeration."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("public", Value.from_smi(1))
        target.set_property("_private", Value.from_smi(2))
        target.set_property("also_public", Value.from_smi(3))

        handler = JSObject(self.gc)

        def own_keys_trap(tgt):
            # Filter out private properties (starting with _)
            all_keys = list(tgt._properties.keys())
            return [k for k in all_keys if not k.startswith("_")]

        handler._own_keys_trap = own_keys_trap
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_own_keys
        keys = proxy_own_keys(proxy)

        assert "_private" not in keys
        assert "public" in keys

    def test_revocable_proxy_integration(self):
        """Test revocable proxy with multiple operations."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_get, proxy_set

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        result = Proxy.revocable(target, handler)
        proxy = result['proxy']
        revoke = result['revoke']

        # Works before revocation
        proxy_set(proxy, "x", Value.from_smi(42))
        assert proxy_get(proxy, "x").to_smi() == 42

        # Revoke
        revoke()

        # All operations fail after revocation
        with pytest.raises(TypeError, match="revoked"):
            proxy_get(proxy, "x")

        with pytest.raises(TypeError, match="revoked"):
            proxy_set(proxy, "y", Value.from_smi(10))

    def test_proxy_with_all_traps(self):
        """Test proxy with all 13 traps defined."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        # Define all traps
        handler._get_trap = lambda t, p, r: Value.from_smi(1)
        handler._set_trap = lambda t, p, v, r: True
        handler._has_trap = lambda t, p: True
        handler._delete_property_trap = lambda t, p: True
        handler._own_keys_trap = lambda t: []
        handler._get_own_property_descriptor_trap = lambda t, p: None
        handler._define_property_trap = lambda t, p, d: True
        handler._get_prototype_of_trap = lambda t: None
        handler._set_prototype_of_trap = lambda t, p: True
        handler._is_extensible_trap = lambda t: True
        # preventExtensions must actually make target non-extensible
        def prevent_extensions_trap(t):
            t._extensible = False
            return True
        handler._prevent_extensions_trap = prevent_extensions_trap

        proxy = Proxy(target, handler)

        # All traps should work
        from proxy_traps import (
            proxy_get, proxy_set, proxy_has, proxy_delete_property,
            proxy_own_keys, proxy_get_own_property_descriptor,
            proxy_define_property, proxy_get_prototype_of,
            proxy_set_prototype_of, proxy_is_extensible,
            proxy_prevent_extensions
        )

        assert proxy_get(proxy, "x").to_smi() == 1
        assert proxy_set(proxy, "x", Value.from_smi(2)) is True
        assert proxy_has(proxy, "x") is True
        assert proxy_delete_property(proxy, "x") is True
        assert proxy_own_keys(proxy) == []
        assert proxy_get_own_property_descriptor(proxy, "x") is None
        assert proxy_define_property(proxy, "x", {}) is True
        assert proxy_get_prototype_of(proxy) is None
        assert proxy_set_prototype_of(proxy, None) is True
        assert proxy_is_extensible(proxy) is True
        assert proxy_prevent_extensions(proxy) is True

    def test_reflect_all_methods_integration(self):
        """Test all Reflect methods work together."""
        from reflect_api import Reflect
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        obj = JSObject(self.gc)

        # Set property
        Reflect.set(obj, "x", Value.from_smi(42))

        # Get property
        assert Reflect.get(obj, "x").to_smi() == 42

        # Check exists
        assert Reflect.has(obj, "x") is True

        # Get keys
        keys = Reflect.ownKeys(obj)
        assert "x" in keys

        # Define property
        Reflect.defineProperty(obj, "y", {"value": Value.from_smi(10)})

        # Get descriptor
        desc = Reflect.getOwnPropertyDescriptor(obj, "y")
        assert desc is not None

        # Delete property
        Reflect.deleteProperty(obj, "x")
        assert Reflect.has(obj, "x") is False

        # Extensibility
        assert Reflect.isExtensible(obj) is True
        Reflect.preventExtensions(obj)
        assert obj._extensible is False
