"""
Unit tests for Proxy set trap.

Tests property write interception with invariant enforcement.
Covers requirements FR-P3-023 (set trap).
"""

import pytest


class TestProxySetTrap:
    """Test Proxy set trap functionality and invariants."""

    def setup_method(self):
        """Set up test fixtures."""
        from components.memory_gc.src import GarbageCollector

        self.gc = GarbageCollector()

    def test_set_trap_intercepts_property_assignment(self):
        """
        Given a proxy with set trap
        When assigning to a property
        Then trap is called with target, property, value, and receiver
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        trap_calls = []

        handler = JSObject(self.gc)

        def set_trap(tgt, prop, value, receiver):
            trap_calls.append((tgt, prop, value, receiver))
            return True  # Success

        handler._set_trap = set_trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_set
        result = proxy_set(proxy, "name", Value.from_smi(42))

        # Then
        assert len(trap_calls) == 1
        assert trap_calls[0][0] is target
        assert trap_calls[0][1] == "name"
        assert trap_calls[0][2].to_smi() == 42
        assert result is True

    def test_set_trap_returns_false_on_failure(self):
        """
        Given a proxy with set trap that rejects assignment
        When trap returns false
        Then set operation returns false
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        def set_trap(tgt, prop, value, receiver):
            # Reject assignment
            return False

        handler._set_trap = set_trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_set
        result = proxy_set(proxy, "rejected", Value.from_smi(100))

        # Then
        assert result is False

    def test_set_trap_uses_target_when_no_trap(self):
        """
        Given a proxy without set trap
        When assigning to a property
        Then assignment happens on target
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        handler = JSObject(self.gc)  # No trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_set
        result = proxy_set(proxy, "x", Value.from_smi(42))

        # Then
        assert result is True
        assert target.get_property("x").to_smi() == 42

    def test_set_trap_receives_proxy_as_receiver(self):
        """
        Given a proxy with set trap
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

        def set_trap(tgt, prop, value, receiver):
            received_receiver.append(receiver)
            return True

        handler._set_trap = set_trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_set
        proxy_set(proxy, "test", Value.from_smi(1))

        # Then
        assert len(received_receiver) == 1
        assert received_receiver[0] is proxy

    def test_set_trap_invariant_non_writable_non_configurable_property(self):
        """
        Given target has non-writable, non-configurable property
        When set trap returns true
        Then TypeError is raised if value differs from target's value
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        # Create non-writable, non-configurable property
        target._properties["const"] = {
            "value": Value.from_smi(42),
            "writable": False,
            "configurable": False,
        }

        handler = JSObject(self.gc)

        def set_trap(tgt, prop, value, receiver):
            # Try to set different value
            return True

        handler._set_trap = set_trap
        proxy = Proxy(target, handler)

        # When/Then
        from proxy_traps import proxy_set

        with pytest.raises(
            TypeError,
            match="Cannot set non-writable, non-configurable property",
        ):
            proxy_set(proxy, "const", Value.from_smi(100))

    def test_set_trap_invariant_accessor_with_undefined_setter(self):
        """
        Given target has non-configurable accessor without setter
        When set trap returns true
        Then TypeError is raised (cannot set)
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        # Non-configurable accessor with no setter
        target._properties["accessor"] = {
            "get": lambda: Value.from_smi(42),
            "set": None,  # No setter
            "configurable": False,
        }

        handler = JSObject(self.gc)

        def set_trap(tgt, prop, value, receiver):
            return True

        handler._set_trap = set_trap
        proxy = Proxy(target, handler)

        # When/Then
        from proxy_traps import proxy_set

        with pytest.raises(
            TypeError,
            match="Cannot set non-configurable accessor without setter",
        ):
            proxy_set(proxy, "accessor", Value.from_smi(100))

    def test_set_trap_on_revoked_proxy_throws(self):
        """
        Given a revoked proxy
        When attempting to use set trap
        Then TypeError is raised
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        # Revoke proxy
        proxy._revoke()

        # When/Then
        from proxy_traps import proxy_set

        with pytest.raises(TypeError, match="revoked proxy"):
            proxy_set(proxy, "any", Value.from_smi(1))

    def test_set_trap_allows_setting_writable_property(self):
        """
        Given target has writable property
        When set trap returns true with different value
        Then no error is raised (writable property can change)
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target._properties["writable"] = {
            "value": Value.from_smi(10),
            "writable": True,
            "configurable": True,
        }

        handler = JSObject(self.gc)

        def set_trap(tgt, prop, value, receiver):
            return True

        handler._set_trap = set_trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_set
        result = proxy_set(proxy, "writable", Value.from_smi(99))

        # Then
        assert result is True  # No error

    def test_set_trap_can_validate_values(self):
        """
        Given a proxy with validating set trap
        When trap validates and accepts value
        Then value is set
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        def set_trap(tgt, prop, value, receiver):
            # Validate: only allow positive numbers
            if value.to_smi() > 0:
                tgt.set_property(prop, value)
                return True
            return False

        handler._set_trap = set_trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_set
        result_valid = proxy_set(proxy, "positive", Value.from_smi(42))
        result_invalid = proxy_set(proxy, "negative", Value.from_smi(-5))

        # Then
        assert result_valid is True
        assert result_invalid is False
        assert target.get_property("positive").to_smi() == 42

    def test_set_trap_with_undefined_value(self):
        """
        Given a proxy with set trap
        When setting undefined value
        Then trap handles undefined correctly
        """
        # Given
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        trap_calls = []

        def set_trap(tgt, prop, value, receiver):
            trap_calls.append(value)
            return True

        handler._set_trap = set_trap
        proxy = Proxy(target, handler)

        # When
        from proxy_traps import proxy_set
        # undefined is represented by None
        proxy_set(proxy, "undef", None)

        # Then
        assert len(trap_calls) == 1
        assert trap_calls[0] is None  # undefined
