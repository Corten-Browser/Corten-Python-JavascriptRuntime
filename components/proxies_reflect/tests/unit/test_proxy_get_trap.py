"""
Unit tests for Proxy get trap.

Tests property read interception with invariant enforcement.
Covers requirements FR-P3-022.
"""

import pytest


class TestProxyGetTrap:
    """Test Proxy get trap functionality and invariants."""

    def setup_method(self):
        """Set up test fixtures."""
        from components.memory_gc.src import GarbageCollector

        self.gc = GarbageCollector()

    def test_get_trap_intercepts_property_access(self):
        """
        Given a proxy with get trap
        When accessing a property
        Then trap is called with target, property, and receiver
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("name", Value.from_smi(42))

        # Track trap calls
        trap_calls = []

        handler = JSObject(self.gc)
        # Simulate trap function
        def get_trap(tgt, prop, receiver):
            trap_calls.append((tgt, prop, receiver))
            return Value.from_smi(100)

        # Manually set trap (in real impl, this would be a method)
        handler._get_trap = get_trap

        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_get
        result = proxy_get(proxy, "name")

        # Then
        assert len(trap_calls) == 1
        assert trap_calls[0][0] is target
        assert trap_calls[0][1] == "name"
        # receiver is the proxy itself
        assert result.to_smi() == 100

    def test_get_trap_returns_target_value_when_no_trap(self):
        """
        Given a proxy without get trap
        When accessing a property
        Then target's property value is returned
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(42))

        handler = JSObject(self.gc)  # No trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_get
        result = proxy_get(proxy, "x")

        # Then
        assert result.to_smi() == 42

    def test_get_trap_can_return_different_value(self):
        """
        Given a proxy with custom get trap
        When trap returns different value
        Then custom value is returned (not target's value)
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("age", Value.from_smi(25))

        handler = JSObject(self.gc)

        def get_trap(tgt, prop, receiver):
            # Return different value
            return Value.from_smi(30)

        handler._get_trap = get_trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_get
        result = proxy_get(proxy, "age")

        # Then
        assert result.to_smi() == 30  # Trap's value, not target's 25

    def test_get_trap_receives_proxy_as_receiver(self):
        """
        Given a proxy with get trap
        When trap is called
        Then receiver parameter is the proxy itself
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        received_receiver = []

        def get_trap(tgt, prop, receiver):
            received_receiver.append(receiver)
            return Value.from_smi(0)

        handler._get_trap = get_trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_get
        proxy_get(proxy, "test")

        # Then
        assert len(received_receiver) == 1
        assert received_receiver[0] is proxy

    def test_get_trap_invariant_non_writable_non_configurable_property(self):
        """
        Given target has non-writable, non-configurable property with value X
        When get trap returns different value Y
        Then TypeError is raised (invariant violation)
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        # Create non-writable, non-configurable property
        # (This would normally use Object.defineProperty)
        target.set_property("const", Value.from_smi(42))
        # Mark as non-writable and non-configurable (simulated)
        target._properties["const"] = {
            "value": Value.from_smi(42),
            "writable": False,
            "configurable": False,
        }

        handler = JSObject(self.gc)

        def get_trap(tgt, prop, receiver):
            # Try to return different value
            return Value.from_smi(100)

        handler._get_trap = get_trap
        proxy = Proxy(target, handler)

        # When/Then
        from proxy_traps import proxy_get

        with pytest.raises(
            TypeError,
            match="Cannot return different value for non-writable, non-configurable property",
        ):
            proxy_get(proxy, "const")

    def test_get_trap_allows_same_value_for_non_writable_property(self):
        """
        Given target has non-writable, non-configurable property with value X
        When get trap returns same value X
        Then no error is raised (invariant satisfied)
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target._properties["const"] = {
            "value": Value.from_smi(42),
            "writable": False,
            "configurable": False,
        }

        handler = JSObject(self.gc)

        def get_trap(tgt, prop, receiver):
            # Return same value
            return Value.from_smi(42)

        handler._get_trap = get_trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_get
        result = proxy_get(proxy, "const")

        # Then
        assert result.to_smi() == 42  # No error

    def test_get_trap_invariant_accessor_with_undefined_getter(self):
        """
        Given target has non-configurable accessor with undefined getter
        When get trap is called
        Then trap must return undefined (invariant)
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        # Non-configurable accessor with undefined get
        target._properties["accessor"] = {
            "get": None,  # undefined
            "set": lambda v: None,
            "configurable": False,
        }

        handler = JSObject(self.gc)

        def get_trap(tgt, prop, receiver):
            # Try to return non-undefined value
            return Value.from_smi(100)

        handler._get_trap = get_trap
        proxy = Proxy(target, handler)

        # When/Then
        from proxy_traps import proxy_get

        with pytest.raises(
            TypeError,
            match="Must return undefined for non-configurable accessor with undefined getter",
        ):
            proxy_get(proxy, "accessor")

    def test_get_trap_works_with_symbol_properties(self):
        """
        Given a property with symbol key
        When get trap is called
        Then trap works correctly with symbol
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        # This test will be relevant when symbols are implemented
        # For now, just verify string properties work
        target = JSObject(self.gc)
        target.set_property("symbolProp", Value.from_smi(42))

        handler = JSObject(self.gc)

        def get_trap(tgt, prop, receiver):
            return Value.from_smi(99)

        handler._get_trap = get_trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_get
        result = proxy_get(proxy, "symbolProp")

        # Then
        assert result.to_smi() == 99

    def test_get_trap_on_revoked_proxy_throws(self):
        """
        Given a revoked proxy
        When attempting to use get trap
        Then TypeError is raised
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        # Revoke proxy
        proxy._revoke()

        # When/Then
        from proxy_traps import proxy_get

        with pytest.raises(TypeError, match="revoked proxy"):
            proxy_get(proxy, "any")

    def test_get_trap_with_undefined_property(self):
        """
        Given target doesn't have the property
        When get trap is called
        Then trap receives undefined from target and can return custom value
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        # No property "missing" on target

        handler = JSObject(self.gc)

        received_value = []

        def get_trap(tgt, prop, receiver):
            # Check what target has
            val = tgt.get_property(prop)
            received_value.append(val)
            # Return custom value
            return Value.from_smi(42)

        handler._get_trap = get_trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_get
        result = proxy_get(proxy, "missing")

        # Then
        # Trap was called and received value from target
        assert len(received_value) == 1
        # Trap's custom value is returned
        assert result.to_smi() == 42
