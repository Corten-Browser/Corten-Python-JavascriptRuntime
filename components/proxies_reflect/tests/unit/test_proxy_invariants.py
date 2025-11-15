"""
Comprehensive tests for Proxy invariants enforcement.

Tests all invariant violations per ECMAScript 2024 specification.
"""

import pytest


class TestProxyInvariants:
    """Test all proxy invariants."""

    def setup_method(self):
        from components.memory_gc.src import GarbageCollector
        self.gc = GarbageCollector()

    # Get trap invariants
    def test_get_invariant_non_writable_data_property(self):
        """Non-writable data property must return same value."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_get

        target = JSObject(self.gc)
        target._properties["x"] = {
            "value": Value.from_smi(42),
            "writable": False,
            "configurable": False,
        }

        handler = JSObject(self.gc)
        handler._get_trap = lambda t, p, r: Value.from_smi(99)

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="different value"):
            proxy_get(proxy, "x")

    def test_get_invariant_accessor_no_getter(self):
        """Accessor without getter must return undefined."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_get

        target = JSObject(self.gc)
        target._properties["x"] = {
            "get": None,
            "set": lambda v: None,
            "configurable": False,
        }

        handler = JSObject(self.gc)
        handler._get_trap = lambda t, p, r: Value.from_smi(42)

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="undefined getter"):
            proxy_get(proxy, "x")

    # Set trap invariants
    def test_set_invariant_non_writable_property(self):
        """Cannot set non-writable property."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_set

        target = JSObject(self.gc)
        target._properties["x"] = {
            "value": Value.from_smi(42),
            "writable": False,
            "configurable": False,
        }

        handler = JSObject(self.gc)
        handler._set_trap = lambda t, p, v, r: True

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="non-writable"):
            proxy_set(proxy, "x", Value.from_smi(99))

    def test_set_invariant_accessor_no_setter(self):
        """Cannot set accessor without setter."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_set

        target = JSObject(self.gc)
        target._properties["x"] = {
            "get": lambda: Value.from_smi(42),
            "set": None,
            "configurable": False,
        }

        handler = JSObject(self.gc)
        handler._set_trap = lambda t, p, v, r: True

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="without setter"):
            proxy_set(proxy, "x", Value.from_smi(99))

    # Has trap invariants
    def test_has_invariant_non_configurable(self):
        """Cannot hide non-configurable property."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_has

        target = JSObject(self.gc)
        target._properties["x"] = {
            "value": Value.from_smi(42),
            "configurable": False,
        }

        handler = JSObject(self.gc)
        handler._has_trap = lambda t, p: False

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="non-configurable"):
            proxy_has(proxy, "x")

    def test_has_invariant_non_extensible_target(self):
        """Cannot hide property of non-extensible target."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_has

        target = JSObject(self.gc)
        target._extensible = False
        target._properties["x"] = {"value": Value.from_smi(42)}

        handler = JSObject(self.gc)
        handler._has_trap = lambda t, p: False

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="non-extensible"):
            proxy_has(proxy, "x")

    # DeleteProperty trap invariants
    def test_delete_invariant_non_configurable(self):
        """Cannot delete non-configurable property."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_delete_property

        target = JSObject(self.gc)
        target._properties["x"] = {
            "value": Value.from_smi(42),
            "configurable": False,
        }

        handler = JSObject(self.gc)
        handler._delete_property_trap = lambda t, p: True

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="non-configurable"):
            proxy_delete_property(proxy, "x")

    # OwnKeys trap invariants
    def test_own_keys_invariant_must_return_array(self):
        """ownKeys must return array."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_own_keys

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        handler._own_keys_trap = lambda t: "not an array"

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="must return an array"):
            proxy_own_keys(proxy)

    def test_own_keys_invariant_must_include_non_configurable(self):
        """ownKeys must include all non-configurable properties."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_own_keys

        target = JSObject(self.gc)
        target._properties["x"] = {
            "value": Value.from_smi(42),
            "configurable": False,
        }

        handler = JSObject(self.gc)
        handler._own_keys_trap = lambda t: []

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="non-configurable properties"):
            proxy_own_keys(proxy)

    def test_own_keys_invariant_non_extensible_target(self):
        """ownKeys must match target keys for non-extensible target."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_own_keys

        target = JSObject(self.gc)
        target._extensible = False
        target._properties["x"] = {"value": Value.from_smi(42)}
        target._properties["y"] = {"value": Value.from_smi(10)}

        handler = JSObject(self.gc)
        handler._own_keys_trap = lambda t: ["x"]  # Missing "y"

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="must match target keys"):
            proxy_own_keys(proxy)

    # DefineProperty trap invariants
    def test_define_property_invariant_non_extensible(self):
        """Cannot add property to non-extensible target."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value
        from proxy_traps import proxy_define_property

        target = JSObject(self.gc)
        target._extensible = False

        handler = JSObject(self.gc)
        handler._define_property_trap = lambda t, p, d: True

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="non-extensible"):
            proxy_define_property(proxy, "new_prop", {"value": Value.from_smi(42)})

    # GetPrototypeOf trap invariants
    def test_get_prototype_invariant_non_extensible(self):
        """getPrototypeOf must return target's prototype for non-extensible."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_get_prototype_of

        target = JSObject(self.gc)
        target._extensible = False
        target._prototype = None

        fake_proto = JSObject(self.gc)

        handler = JSObject(self.gc)
        handler._get_prototype_of_trap = lambda t: fake_proto

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="target's prototype"):
            proxy_get_prototype_of(proxy)

    # SetPrototypeOf trap invariants
    def test_set_prototype_invariant_non_extensible(self):
        """Cannot change prototype of non-extensible target."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_set_prototype_of

        target = JSObject(self.gc)
        target._extensible = False
        target._prototype = None

        new_proto = JSObject(self.gc)

        handler = JSObject(self.gc)
        handler._set_prototype_of_trap = lambda t, p: True

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="non-extensible"):
            proxy_set_prototype_of(proxy, new_proto)

    # IsExtensible trap invariants
    def test_is_extensible_invariant_must_match_target(self):
        """isExtensible must return same as target."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_is_extensible

        target = JSObject(self.gc)
        target._extensible = False

        handler = JSObject(self.gc)
        handler._is_extensible_trap = lambda t: True  # Wrong!

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="must match"):
            proxy_is_extensible(proxy)

    # PreventExtensions trap invariants
    def test_prevent_extensions_invariant(self):
        """preventExtensions can only return true if target is non-extensible."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_prevent_extensions

        target = JSObject(self.gc)
        target._extensible = True  # Still extensible

        handler = JSObject(self.gc)
        # Trap returns true but doesn't actually prevent extensions
        handler._prevent_extensions_trap = lambda t: True

        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="only return true if target"):
            proxy_prevent_extensions(proxy)

    # Construct trap invariants
    def test_construct_invariant_must_return_object(self):
        """construct must return object."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_construct

        def constructor():
            return 42  # Not an object!

        handler = JSObject(self.gc)
        handler._construct_trap = lambda t, a, nt: 42

        proxy = Proxy(constructor, handler)

        with pytest.raises(TypeError, match="must return an object"):
            proxy_construct(proxy, [])

    # Apply trap - target must be callable
    def test_apply_requires_callable_target(self):
        """apply trap requires callable target."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from proxy_traps import proxy_apply

        target = JSObject(self.gc)  # Not callable

        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        with pytest.raises(TypeError, match="must be callable"):
            proxy_apply(proxy, None, [])
