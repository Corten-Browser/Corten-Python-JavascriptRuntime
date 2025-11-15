"""
Tests for advanced Proxy traps: descriptors, prototypes, extensibility, functions.

Covers requirements FR-P3-027 to FR-P3-032.
"""

import pytest


class TestDescriptorTraps:
    """Tests for getOwnPropertyDescriptor and defineProperty traps."""

    def setup_method(self):
        from components.memory_gc.src import GarbageCollector
        self.gc = GarbageCollector()

    def test_get_own_property_descriptor_trap(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_get_own_property_descriptor

        target = JSObject(self.gc)
        target._properties["x"] = {"value": Value.from_smi(42), "writable": True}

        handler = JSObject(self.gc)
        handler._get_own_property_descriptor_trap = lambda tgt, prop: {"value": Value.from_smi(99)}

        proxy = Proxy(target, handler)
        desc = proxy_get_own_property_descriptor(proxy, "x")

        assert desc["value"].to_smi() == 99

    def test_define_property_trap(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_define_property

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        calls = []
        def define_trap(tgt, prop, desc):
            calls.append((prop, desc))
            return True

        handler._define_property_trap = define_trap
        proxy = Proxy(target, handler)

        result = proxy_define_property(proxy, "x", {"value": Value.from_smi(42)})

        assert result is True
        assert len(calls) == 1


class TestPrototypeTraps:
    """Tests for getPrototypeOf and setPrototypeOf traps."""

    def setup_method(self):
        from components.memory_gc.src import GarbageCollector
        self.gc = GarbageCollector()

    def test_get_prototype_of_trap(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_get_prototype_of

        target = JSObject(self.gc)
        proto = JSObject(self.gc)
        target._prototype = proto

        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        result = proxy_get_prototype_of(proxy)
        assert result is proto

    def test_set_prototype_of_trap(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_set_prototype_of

        target = JSObject(self.gc)
        new_proto = JSObject(self.gc)

        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        result = proxy_set_prototype_of(proxy, new_proto)

        assert result is True
        assert target._prototype is new_proto


class TestExtensibilityTraps:
    """Tests for isExtensible and preventExtensions traps."""

    def setup_method(self):
        from components.memory_gc.src import GarbageCollector
        self.gc = GarbageCollector()

    def test_is_extensible_trap(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_is_extensible

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        assert proxy_is_extensible(proxy) is True

    def test_prevent_extensions_trap(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_prevent_extensions

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        result = proxy_prevent_extensions(proxy)

        assert result is True
        assert target._extensible is False


class TestFunctionTraps:
    """Tests for apply and construct traps."""

    def setup_method(self):
        from components.memory_gc.src import GarbageCollector
        self.gc = GarbageCollector()

    def test_apply_trap(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_apply

        def target_func(a, b):
            return a + b

        handler = JSObject(self.gc)
        proxy = Proxy(target_func, handler)

        result = proxy_apply(proxy, None, [2, 3])
        assert result == 5

    def test_construct_trap(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_construct

        def target_constructor():
            obj = JSObject(self.gc)
            obj.name = "test"
            return obj

        handler = JSObject(self.gc)
        proxy = Proxy(target_constructor, handler)

        result = proxy_construct(proxy, [])
        assert hasattr(result, "name")


class TestRevocableProxy:
    """Tests for Proxy.revocable."""

    def setup_method(self):
        from components.memory_gc.src import GarbageCollector
        self.gc = GarbageCollector()

    def test_revocable_creates_proxy_and_revoke_function(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        result = Proxy.revocable(target, handler)

        assert 'proxy' in result
        assert 'revoke' in result
        assert isinstance(result['proxy'], Proxy)
        assert callable(result['revoke'])

    def test_revoke_function_revokes_proxy(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_get

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(42))

        handler = JSObject(self.gc)

        result = Proxy.revocable(target, handler)
        proxy = result['proxy']
        revoke = result['revoke']

        # Before revocation - should work
        value = proxy_get(proxy, "x")
        assert value.to_smi() == 42

        # Revoke
        revoke()

        # After revocation - should throw
        with pytest.raises(TypeError, match="revoked proxy"):
            proxy_get(proxy, "x")

    def test_revoke_is_idempotent(self):
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        result = Proxy.revocable(target, handler)
        revoke = result['revoke']

        # Call revoke multiple times - should not error
        revoke()
        revoke()
        revoke()
