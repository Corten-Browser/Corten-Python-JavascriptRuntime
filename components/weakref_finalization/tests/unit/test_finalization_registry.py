"""
Unit tests for FinalizationRegistry class.

Tests follow TDD RED phase - these tests will fail until implementation is complete.
Covers:
- FR-ES24-B-031: FinalizationRegistry constructor
- FR-ES24-B-032: FinalizationRegistry.register()
- FR-ES24-B-033: FinalizationRegistry cleanup (unit-level)
"""

import pytest
from weakref_finalization import FinalizationRegistry


class TestFinalizationRegistryConstructor:
    """Test FinalizationRegistry constructor (FR-ES24-B-031)."""

    def test_create_registry_with_callable(self):
        """
        Given a callable cleanup function
        When creating a FinalizationRegistry
        Then registry instance is created successfully
        """
        cleanup_called = []

        def cleanup_callback(held_value):
            cleanup_called.append(held_value)

        registry = FinalizationRegistry(cleanup_callback)

        assert registry is not None
        assert isinstance(registry, FinalizationRegistry)

    def test_create_registry_with_lambda(self):
        """
        Given a lambda function
        When creating a FinalizationRegistry
        Then registry instance is created successfully
        """
        registry = FinalizationRegistry(lambda held: None)

        assert registry is not None
        assert isinstance(registry, FinalizationRegistry)

    def test_registry_rejects_non_callable(self):
        """
        Given a non-callable value
        When creating a FinalizationRegistry
        Then TypeError is raised
        """
        with pytest.raises(TypeError, match="cleanup callback must be callable"):
            FinalizationRegistry(42)

    def test_registry_rejects_none(self):
        """
        Given None as cleanup callback
        When creating a FinalizationRegistry
        Then TypeError is raised
        """
        with pytest.raises(TypeError, match="cleanup callback must be callable"):
            FinalizationRegistry(None)

    def test_registry_rejects_string(self):
        """
        Given a string as cleanup callback
        When creating a FinalizationRegistry
        Then TypeError is raised
        """
        with pytest.raises(TypeError, match="cleanup callback must be callable"):
            FinalizationRegistry("not a function")


class TestFinalizationRegistryRegister:
    """Test FinalizationRegistry.register() method (FR-ES24-B-032)."""

    def test_register_object_with_held_value(self):
        """
        Given a FinalizationRegistry
        When registering an object with a held value
        Then registration succeeds without error
        """
        registry = FinalizationRegistry(lambda held: None)
        target = {"name": "test"}
        held_value = "cleanup data"

        # Should not raise
        registry.register(target, held_value)

    def test_register_object_with_unregister_token(self):
        """
        Given a FinalizationRegistry
        When registering an object with unregister token
        Then registration succeeds
        """
        registry = FinalizationRegistry(lambda held: None)
        target = {"name": "test"}
        held_value = "cleanup data"
        token = {"token": "id"}

        # Should not raise
        registry.register(target, held_value, token)

    def test_register_with_primitive_held_value(self):
        """
        Given a FinalizationRegistry
        When registering with primitive held value
        Then registration succeeds

        Note: held_value can be any value including primitives.
        """
        registry = FinalizationRegistry(lambda held: None)
        target = {"name": "test"}

        # All these should work
        registry.register(target, 42)
        registry.register(target, "string")
        registry.register(target, True)
        registry.register(target, None)

    def test_register_rejects_primitive_target(self):
        """
        Given a FinalizationRegistry
        When registering a primitive as target
        Then TypeError is raised
        """
        registry = FinalizationRegistry(lambda held: None)

        with pytest.raises(TypeError, match="target must be an object"):
            registry.register(42, "held")

    def test_register_rejects_null_target(self):
        """
        Given a FinalizationRegistry
        When registering null as target
        Then TypeError is raised
        """
        registry = FinalizationRegistry(lambda held: None)

        with pytest.raises(TypeError, match="target must be an object"):
            registry.register(None, "held")

    def test_register_rejects_target_as_unregister_token(self):
        """
        Given a FinalizationRegistry
        When registering with target same as unregister token
        Then TypeError is raised

        Note: This prevents keeping target alive through token.
        """
        registry = FinalizationRegistry(lambda held: None)
        target = {"name": "test"}

        with pytest.raises(TypeError, match="target and unregister token cannot be the same"):
            registry.register(target, "held", target)

    def test_register_multiple_times_same_target(self):
        """
        Given a FinalizationRegistry
        When registering the same target multiple times
        Then all registrations are recorded

        Note: Multiple registrations for same target are allowed.
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target = {"name": "multi"}
        registry.register(target, "first")
        registry.register(target, "second")
        registry.register(target, "third")

        # Should not raise, multiple registrations allowed

    def test_register_different_targets(self):
        """
        Given a FinalizationRegistry
        When registering different targets
        Then all registrations are recorded
        """
        registry = FinalizationRegistry(lambda held: None)

        target1 = {"name": "first"}
        target2 = {"name": "second"}
        target3 = {"name": "third"}

        registry.register(target1, "data1")
        registry.register(target2, "data2")
        registry.register(target3, "data3")

        # Should not raise


class TestFinalizationRegistryUnregister:
    """Test FinalizationRegistry.unregister() method."""

    def test_unregister_removes_registration(self):
        """
        Given a registration with an unregister token
        When calling unregister with that token
        Then registration is removed and True is returned
        """
        registry = FinalizationRegistry(lambda held: None)
        target = {"name": "test"}
        token = {"token": "id"}

        registry.register(target, "held", token)
        result = registry.unregister(token)

        assert result is True

    def test_unregister_with_nonexistent_token(self):
        """
        Given a FinalizationRegistry with no matching registrations
        When calling unregister
        Then False is returned
        """
        registry = FinalizationRegistry(lambda held: None)
        token = {"token": "nonexistent"}

        result = registry.unregister(token)

        assert result is False

    def test_unregister_removes_all_matching_registrations(self):
        """
        Given multiple registrations with the same token
        When calling unregister with that token
        Then all matching registrations are removed
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target1 = {"name": "first"}
        target2 = {"name": "second"}
        token = {"shared": "token"}

        registry.register(target1, "data1", token)
        registry.register(target2, "data2", token)

        result = registry.unregister(token)

        assert result is True

    def test_unregister_does_not_affect_queued_callbacks(self):
        """
        Given a cleanup callback already queued
        When calling unregister
        Then already-queued callback still runs

        Note: unregister only affects pending registrations, not queued callbacks.
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target = {"name": "test"}
        token = {"token": "id"}

        registry.register(target, "data", token)

        # Simulate target collection (callback queued)
        registry._simulate_collection(target)

        # Unregister should not prevent queued callback
        registry.unregister(token)

        # Process callbacks
        registry._process_cleanup_callbacks()

        # Callback should still have run
        assert "data" in cleanup_calls

    def test_unregister_without_token_registration(self):
        """
        Given a registration without unregister token
        When another registration with token is unregistered
        Then first registration is unaffected
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target1 = {"name": "no_token"}
        target2 = {"name": "with_token"}
        token = {"token": "id"}

        registry.register(target1, "data1")  # No token
        registry.register(target2, "data2", token)  # With token

        # Unregister token-based registration
        result = registry.unregister(token)
        assert result is True

        # First registration should still be active
        # (This would be verified in integration tests when GC runs)


class TestFinalizationRegistryCleanup:
    """Test FinalizationRegistry cleanup callbacks (FR-ES24-B-033 - unit level)."""

    def test_cleanup_callback_invoked_on_collection(self):
        """
        Given a registered object
        When the object is garbage collected
        Then cleanup callback is invoked with held value
        """
        cleanup_calls = []

        def cleanup(held_value):
            cleanup_calls.append(held_value)

        registry = FinalizationRegistry(cleanup)
        target = {"name": "test"}

        registry.register(target, "cleanup_data")

        # Simulate GC collection
        registry._simulate_collection(target)

        # Process cleanup callbacks
        registry._process_cleanup_callbacks()

        assert len(cleanup_calls) == 1
        assert cleanup_calls[0] == "cleanup_data"

    def test_cleanup_callback_receives_correct_held_value(self):
        """
        Given multiple registrations with different held values
        When objects are collected
        Then callback receives correct held values
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target1 = {"name": "first"}
        target2 = {"name": "second"}

        registry.register(target1, "data1")
        registry.register(target2, "data2")

        # Simulate collection
        registry._simulate_collection(target1)
        registry._simulate_collection(target2)

        # Process callbacks
        registry._process_cleanup_callbacks()

        assert len(cleanup_calls) == 2
        assert "data1" in cleanup_calls
        assert "data2" in cleanup_calls

    def test_cleanup_callback_exception_handled(self):
        """
        Given a cleanup callback that throws
        When callback is invoked
        Then exception is caught and other callbacks continue

        Note: Callback exceptions must not break cleanup processing.
        """
        cleanup_calls = []

        def cleanup_with_error(held):
            if held == "error":
                raise ValueError("Intentional error")
            cleanup_calls.append(held)

        registry = FinalizationRegistry(cleanup_with_error)

        target1 = {"name": "error_target"}
        target2 = {"name": "normal_target"}

        registry.register(target1, "error")
        registry.register(target2, "normal")

        # Simulate collection
        registry._simulate_collection(target1)
        registry._simulate_collection(target2)

        # Process callbacks - should not raise
        registry._process_cleanup_callbacks()

        # Normal callback should have run
        assert "normal" in cleanup_calls

    def test_multiple_registrations_same_target_all_invoke(self):
        """
        Given multiple registrations for the same target
        When target is collected
        Then all callbacks are invoked
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target = {"name": "multi"}

        registry.register(target, "first")
        registry.register(target, "second")
        registry.register(target, "third")

        # Simulate collection
        registry._simulate_collection(target)

        # Process callbacks
        registry._process_cleanup_callbacks()

        assert len(cleanup_calls) == 3
        assert "first" in cleanup_calls
        assert "second" in cleanup_calls
        assert "third" in cleanup_calls

    def test_cleanup_runs_even_if_registry_collected(self):
        """
        Given a registration
        When registry itself is collected but callback is queued
        Then callback still runs

        Note: Pending callbacks must run even if registry is GC'd.
        """
        cleanup_calls = []

        # Create registry and register
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))
        target = {"name": "test"}
        registry.register(target, "data")

        # Simulate target collection
        registry._simulate_collection(target)

        # Even if registry is "collected", queued callbacks should run
        # (In real implementation, cleanup jobs are independent of registry lifetime)
        registry._process_cleanup_callbacks()

        assert "data" in cleanup_calls


class TestFinalizationRegistryEdgeCases:
    """Test FinalizationRegistry edge cases."""

    def test_register_with_complex_held_value(self):
        """
        Given a complex object as held value
        When registration occurs
        Then held value is preserved correctly
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target = {"name": "test"}
        held_value = {"type": "cleanup", "actions": ["delete", "notify"], "count": 42}

        registry.register(target, held_value)

        # Simulate collection
        registry._simulate_collection(target)
        registry._process_cleanup_callbacks()

        assert len(cleanup_calls) == 1
        assert cleanup_calls[0] == held_value
        assert cleanup_calls[0]["type"] == "cleanup"
        assert cleanup_calls[0]["count"] == 42

    def test_same_target_in_multiple_registries(self):
        """
        Given the same target registered in multiple registries
        When target is collected
        Then all registries invoke their callbacks
        """
        calls1 = []
        calls2 = []

        registry1 = FinalizationRegistry(lambda held: calls1.append(held))
        registry2 = FinalizationRegistry(lambda held: calls2.append(held))

        target = {"name": "shared"}

        registry1.register(target, "registry1_data")
        registry2.register(target, "registry2_data")

        # Simulate collection in both registries
        registry1._simulate_collection(target)
        registry2._simulate_collection(target)

        # Process both
        registry1._process_cleanup_callbacks()
        registry2._process_cleanup_callbacks()

        assert "registry1_data" in calls1
        assert "registry2_data" in calls2

    def test_cleanup_with_none_held_value(self):
        """
        Given a registration with None as held value
        When target is collected
        Then callback is invoked with None
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target = {"name": "test"}
        registry.register(target, None)

        registry._simulate_collection(target)
        registry._process_cleanup_callbacks()

        assert len(cleanup_calls) == 1
        assert cleanup_calls[0] is None


class TestFinalizationRegistryPerformance:
    """Performance tests for FinalizationRegistry."""

    def test_registration_performance(self):
        """
        Given performance requirement of <500ns per registration
        When registering many objects
        Then average registration time is within limit
        """
        import time

        registry = FinalizationRegistry(lambda held: None)
        targets = [{"id": i} for i in range(1000)]

        start = time.perf_counter()
        for target in targets:
            registry.register(target, f"data_{id(target)}")
        end = time.perf_counter()

        avg_time_ns = (end - start) / len(targets) * 1_000_000_000

        # Should be < 500ns per registration
        assert avg_time_ns < 500.0, f"Registration took {avg_time_ns}ns, should be <500ns"

    def test_cleanup_scheduling_performance(self):
        """
        Given performance requirement of <10µs per batch
        When scheduling cleanup callbacks
        Then batch processing time is within limit
        """
        import time

        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        # Register many targets
        targets = [{"id": i} for i in range(100)]
        for i, target in enumerate(targets):
            registry.register(target, i)

        # Simulate collection of all
        for target in targets:
            registry._simulate_collection(target)

        # Measure callback processing
        start = time.perf_counter()
        registry._process_cleanup_callbacks()
        end = time.perf_counter()

        time_us = (end - start) * 1_000_000

        # Should be < 10µs per batch
        # (note: this is per batch, not per callback)
        assert time_us < 10.0, f"Cleanup batch took {time_us}µs, should be <10µs"
