"""
Unit tests for Proxy fundamental traps: has, deleteProperty, ownKeys.

Tests property existence checking, deletion, and enumeration with invariants.
Covers requirements FR-P3-024, FR-P3-025, FR-P3-026.
"""

import pytest


class TestProxyHasTrap:
    """Test Proxy has trap (for 'in' operator)."""

    def setup_method(self):
        """Set up test fixtures."""
        from components.memory_gc.src import GarbageCollector
        self.gc = GarbageCollector()

    def test_has_trap_intercepts_in_operator(self):
        """Test that has trap intercepts property existence checks."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(42))

        trap_calls = []
        handler = JSObject(self.gc)

        def has_trap(tgt, prop):
            trap_calls.append((tgt, prop))
            return True

        handler._has_trap = has_trap
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_has
        result = proxy_has(proxy, "x")

        assert len(trap_calls) == 1
        assert trap_calls[0][0] is target
        assert trap_calls[0][1] == "x"
        assert result is True

    def test_has_trap_can_hide_existing_property(self):
        """Test that has trap can report property as non-existent."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("secret", Value.from_smi(42))

        handler = JSObject(self.gc)

        def has_trap(tgt, prop):
            if prop == "secret":
                return False  # Hide property
            return prop in tgt._properties if hasattr(tgt, "_properties") else False

        handler._has_trap = has_trap
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_has
        assert proxy_has(proxy, "secret") is False

    def test_has_trap_invariant_non_configurable_property(self):
        """Test that non-configurable property cannot be hidden."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target._properties["const"] = {
            "value": Value.from_smi(42),
            "configurable": False,
        }

        handler = JSObject(self.gc)

        def has_trap(tgt, prop):
            return False  # Try to hide

        handler._has_trap = has_trap
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_has
        with pytest.raises(TypeError, match="Cannot report non-configurable property"):
            proxy_has(proxy, "const")

    def test_has_trap_returns_target_value_when_no_trap(self):
        """Test default behavior without trap."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(1))

        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_has
        assert proxy_has(proxy, "x") is True
        assert proxy_has(proxy, "missing") is False

    def test_has_trap_on_revoked_proxy_throws(self):
        """Test that revoked proxy throws TypeError."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)
        proxy._revoke()

        from proxy_traps import proxy_has
        with pytest.raises(TypeError, match="revoked proxy"):
            proxy_has(proxy, "any")


class TestProxyDeletePropertyTrap:
    """Test Proxy deleteProperty trap (for delete operator)."""

    def setup_method(self):
        """Set up test fixtures."""
        from components.memory_gc.src import GarbageCollector
        self.gc = GarbageCollector()

    def test_delete_property_trap_intercepts_deletion(self):
        """Test that trap intercepts property deletion."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(42))

        trap_calls = []
        handler = JSObject(self.gc)

        def delete_trap(tgt, prop):
            trap_calls.append((tgt, prop))
            return True

        handler._delete_property_trap = delete_trap
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_delete_property
        result = proxy_delete_property(proxy, "x")

        assert len(trap_calls) == 1
        assert trap_calls[0][1] == "x"
        assert result is True

    def test_delete_property_trap_can_prevent_deletion(self):
        """Test that trap can return false to prevent deletion."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("protected", Value.from_smi(42))

        handler = JSObject(self.gc)

        def delete_trap(tgt, prop):
            if prop == "protected":
                return False  # Prevent deletion
            return True

        handler._delete_property_trap = delete_trap
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_delete_property
        assert proxy_delete_property(proxy, "protected") is False

    def test_delete_property_trap_invariant_non_configurable(self):
        """Test that non-configurable property cannot be deleted."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target._properties["const"] = {
            "value": Value.from_smi(42),
            "configurable": False,
        }

        handler = JSObject(self.gc)

        def delete_trap(tgt, prop):
            return True  # Try to allow deletion

        handler._delete_property_trap = delete_trap
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_delete_property
        with pytest.raises(TypeError, match="Cannot delete non-configurable property"):
            proxy_delete_property(proxy, "const")

    def test_delete_property_without_trap_deletes_from_target(self):
        """Test default deletion behavior without trap."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(42))

        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_delete_property
        result = proxy_delete_property(proxy, "x")

        assert result is True
        assert "x" not in target._properties

    def test_delete_property_on_revoked_proxy_throws(self):
        """Test that revoked proxy throws TypeError."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)
        proxy._revoke()

        from proxy_traps import proxy_delete_property
        with pytest.raises(TypeError, match="revoked proxy"):
            proxy_delete_property(proxy, "any")


class TestProxyOwnKeysTrap:
    """Test Proxy ownKeys trap (for Object.keys, etc.)."""

    def setup_method(self):
        """Set up test fixtures."""
        from components.memory_gc.src import GarbageCollector
        self.gc = GarbageCollector()

    def test_own_keys_trap_intercepts_enumeration(self):
        """Test that trap intercepts key enumeration."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("a", Value.from_smi(1))
        target.set_property("b", Value.from_smi(2))

        trap_calls = []
        handler = JSObject(self.gc)

        def own_keys_trap(tgt):
            trap_calls.append(tgt)
            return ["a", "b", "c"]

        handler._own_keys_trap = own_keys_trap
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_own_keys
        result = proxy_own_keys(proxy)

        assert len(trap_calls) == 1
        assert result == ["a", "b", "c"]

    def test_own_keys_trap_must_return_list(self):
        """Test invariant: trap must return array."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)

        def own_keys_trap(tgt):
            return "not a list"  # Invalid

        handler._own_keys_trap = own_keys_trap
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_own_keys
        with pytest.raises(TypeError, match="must return an array"):
            proxy_own_keys(proxy)

    def test_own_keys_trap_invariant_must_include_non_configurable(self):
        """Test that result must include non-configurable properties."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target._properties["const"] = {
            "value": Value.from_smi(42),
            "configurable": False,
        }

        handler = JSObject(self.gc)

        def own_keys_trap(tgt):
            return []  # Missing "const"

        handler._own_keys_trap = own_keys_trap
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_own_keys
        with pytest.raises(TypeError, match="must include all non-configurable properties"):
            proxy_own_keys(proxy)

    def test_own_keys_without_trap_returns_target_keys(self):
        """Test default behavior without trap."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject
        from components.value_system.src import Value

        target = JSObject(self.gc)
        target.set_property("x", Value.from_smi(1))
        target.set_property("y", Value.from_smi(2))

        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)

        from proxy_traps import proxy_own_keys
        result = proxy_own_keys(proxy)

        assert set(result) == {"x", "y"}

    def test_own_keys_on_revoked_proxy_throws(self):
        """Test that revoked proxy throws TypeError."""
        from proxy import Proxy
        from components.object_runtime.src import JSObject

        target = JSObject(self.gc)
        handler = JSObject(self.gc)
        proxy = Proxy(target, handler)
        proxy._revoke()

        from proxy_traps import proxy_own_keys
        with pytest.raises(TypeError, match="revoked proxy"):
            proxy_own_keys(proxy)
