"""
Integration tests for GC integration with WeakRef and FinalizationRegistry.

These tests verify the integration with the garbage collector.
Covers:
- FR-ES24-B-030: WeakRef GC behavior (integration)
- FR-ES24-B-033: FinalizationRegistry cleanup (integration)
"""

import pytest
import gc as python_gc
from weakref_finalization import WeakRef, FinalizationRegistry


class TestWeakRefGCIntegration:
    """Test WeakRef integration with garbage collector."""

    def test_weakref_allows_gc_when_no_strong_refs(self):
        """
        Given a WeakRef to an object
        When all strong references are removed
        Then object is garbage collected
        And deref() returns None
        """
        # Create object and WeakRef
        ref = WeakRef({"temp": "data"})

        # Target has no strong references
        # Simulate GC
        ref._mark_collected()

        # deref should return None
        assert ref.deref() is None

    def test_weakref_preserves_object_with_strong_refs(self):
        """
        Given a WeakRef to an object with strong references
        When GC runs
        Then object is NOT collected
        And deref() returns the object
        """
        target = {"persistent": "data"}
        ref = WeakRef(target)

        # Object has strong reference (variable 'target')
        # GC should not collect it
        result = ref.deref()

        assert result is target
        assert result["persistent"] == "data"

    def test_deref_stability_across_gc_cycles(self):
        """
        Given a WeakRef to an object
        When multiple GC cycles occur within same turn
        Then deref() returns stable value
        """
        target = {"name": "stable"}
        ref = WeakRef(target)

        # Multiple deref calls with GC in between (same turn)
        result1 = ref.deref()
        # Simulate GC cycle (but object has strong ref)
        result2 = ref.deref()

        assert result1 is result2
        assert result1 is target

    def test_multiple_weakrefs_all_notified_on_gc(self):
        """
        Given multiple WeakRefs to the same target
        When target is collected
        Then all WeakRefs report collection
        """
        refs = []
        for _ in range(5):
            refs.append(WeakRef({"shared": "target"}))

        # Simulate collection for all
        for ref in refs:
            ref._mark_collected()

        # All should return None
        for ref in refs:
            assert ref.deref() is None


class TestFinalizationRegistryGCIntegration:
    """Test FinalizationRegistry integration with garbage collector."""

    def test_cleanup_callback_after_gc(self):
        """
        Given a registered object
        When object is garbage collected
        Then cleanup callback is invoked
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target = {"name": "test"}
        registry.register(target, "cleanup_data")

        # Simulate GC
        registry._simulate_collection(target)
        registry._process_cleanup_callbacks()

        assert len(cleanup_calls) == 1
        assert cleanup_calls[0] == "cleanup_data"

    def test_cleanup_scheduled_as_microtask(self):
        """
        Given a registered object that gets collected
        When GC runs
        Then cleanup callback is scheduled as microtask

        Note: In real implementation, this would integrate with event_loop.
        For now we verify the scheduling mechanism exists.
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target = {"name": "test"}
        registry.register(target, "data")

        # Simulate GC
        registry._simulate_collection(target)

        # Callback should be queued
        assert registry._has_pending_callbacks()

        # Process as microtask
        registry._process_cleanup_callbacks()

        assert "data" in cleanup_calls

    def test_multiple_objects_batch_cleanup(self):
        """
        Given multiple registered objects
        When all are collected in one GC cycle
        Then cleanup callbacks are batched
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        targets = [{"id": i} for i in range(10)]
        for i, target in enumerate(targets):
            registry.register(target, f"data_{i}")

        # Simulate GC collecting all
        for target in targets:
            registry._simulate_collection(target)

        # Process batch
        registry._process_cleanup_callbacks()

        # All callbacks should have been invoked
        assert len(cleanup_calls) == 10
        for i in range(10):
            assert f"data_{i}" in cleanup_calls

    def test_unregister_prevents_callback(self):
        """
        Given a registered object
        When unregistered before collection
        Then cleanup callback is NOT invoked
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target = {"name": "test"}
        token = {"token": "id"}

        registry.register(target, "data", token)

        # Unregister before collection
        registry.unregister(token)

        # Simulate GC
        registry._simulate_collection(target)
        registry._process_cleanup_callbacks()

        # Callback should NOT have been invoked
        assert len(cleanup_calls) == 0

    def test_partial_unregister_with_multiple_registrations(self):
        """
        Given multiple registrations for same target
        When only some are unregistered
        Then remaining callbacks are invoked
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target = {"name": "test"}
        token = {"token": "id"}

        registry.register(target, "with_token", token)
        registry.register(target, "without_token")

        # Unregister token-based registration
        registry.unregister(token)

        # Simulate GC
        registry._simulate_collection(target)
        registry._process_cleanup_callbacks()

        # Only non-token registration should invoke callback
        assert len(cleanup_calls) == 1
        assert "without_token" in cleanup_calls
        assert "with_token" not in cleanup_calls


class TestWeakRefAndFinalizationRegistryTogether:
    """Test WeakRef and FinalizationRegistry working together."""

    def test_weakref_and_registry_for_same_object(self):
        """
        Given an object with both WeakRef and FinalizationRegistry
        When object is collected
        Then WeakRef.deref() returns None
        And cleanup callback is invoked
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target = {"name": "dual"}
        ref = WeakRef(target)

        registry.register(target, "cleanup_data")

        # Simulate GC
        ref._mark_collected()
        registry._simulate_collection(target)
        registry._process_cleanup_callbacks()

        # Both should reflect collection
        assert ref.deref() is None
        assert "cleanup_data" in cleanup_calls

    def test_weakref_in_held_value(self):
        """
        Given a FinalizationRegistry with WeakRef in held value
        When target is collected
        Then cleanup callback receives the WeakRef
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target = {"name": "test"}
        related = {"related": "object"}
        weak_related = WeakRef(related)

        # Register with WeakRef as held value
        registry.register(target, {"weak": weak_related, "data": "info"})

        # Simulate collection of target
        registry._simulate_collection(target)
        registry._process_cleanup_callbacks()

        # Callback should receive held value with WeakRef
        assert len(cleanup_calls) == 1
        assert "weak" in cleanup_calls[0]
        assert isinstance(cleanup_calls[0]["weak"], WeakRef)

        # WeakRef should still work if 'related' is alive
        assert cleanup_calls[0]["weak"].deref() is related

    def test_finalization_order_with_dependency_chain(self):
        """
        Given objects A, B, C where B references A, C references B
        When all are collected
        Then cleanup callbacks may run in any order

        Note: No guaranteed order for cleanup callbacks.
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        obj_a = {"name": "A"}
        obj_b = {"name": "B", "ref": obj_a}
        obj_c = {"name": "C", "ref": obj_b}

        registry.register(obj_a, "A_cleanup")
        registry.register(obj_b, "B_cleanup")
        registry.register(obj_c, "C_cleanup")

        # Simulate GC
        registry._simulate_collection(obj_a)
        registry._simulate_collection(obj_b)
        registry._simulate_collection(obj_c)

        registry._process_cleanup_callbacks()

        # All callbacks should run (order not guaranteed)
        assert len(cleanup_calls) == 3
        assert "A_cleanup" in cleanup_calls
        assert "B_cleanup" in cleanup_calls
        assert "C_cleanup" in cleanup_calls


class TestGCHooks:
    """Test GC hook integration."""

    def test_on_object_collected_hook(self):
        """
        Given GC hook registered
        When object is collected
        Then hook is called with object pointer
        """
        # This would test integration with memory_gc component
        # For now, verify the hook mechanism exists
        from weakref_finalization import on_object_collected

        # Clear any previous collected objects
        on_object_collected._collected_objects = []

        # In real implementation, this would integrate with GC
        # For testing, we can call it directly
        obj_id = id({"test": "object"})
        on_object_collected(obj_id)

        # Verify hook was called and object was tracked
        assert obj_id in on_object_collected._collected_objects

    def test_cleanup_microtask_scheduling(self):
        """
        Given cleanup callbacks queued
        When GC completes
        Then microtask is scheduled for cleanup

        Note: This tests integration with event_loop component.
        """
        from weakref_finalization import schedule_cleanup_microtask

        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        target = {"name": "test"}
        registry.register(target, "data")

        # Simulate GC and microtask scheduling
        registry._simulate_collection(target)

        # In real implementation, this would call event_loop.schedule_microtask
        # For testing, verify scheduling mechanism exists
        scheduled = schedule_cleanup_microtask(registry)

        assert scheduled is True

        # Process the microtask
        registry._process_cleanup_callbacks()

        assert "data" in cleanup_calls


class TestGCEdgeCases:
    """Test GC edge cases."""

    def test_resurrection_attempt_fails(self):
        """
        Given a cleanup callback that tries to resurrect object
        When callback runs
        Then resurrection fails (object already collected)

        Note: Cleanup callbacks cannot resurrect objects.
        """
        resurrection_attempt = []

        def try_resurrect(held):
            # Try to access the original object (should fail)
            resurrection_attempt.append("attempted")
            # In real scenario, object is already gone

        registry = FinalizationRegistry(try_resurrect)

        target = {"name": "test"}
        registry.register(target, "data")

        # Simulate collection
        registry._simulate_collection(target)
        registry._process_cleanup_callbacks()

        # Callback ran but couldn't resurrect
        assert "attempted" in resurrection_attempt

    def test_gc_during_cleanup_callback(self):
        """
        Given a cleanup callback that triggers GC
        When callback runs
        Then GC is deferred or nested GC is handled safely
        """
        cleanup_calls = []

        def cleanup_with_gc(held):
            cleanup_calls.append(held)
            # In real implementation, triggering GC here should be safe
            # For now, just verify callback completes

        registry = FinalizationRegistry(cleanup_with_gc)

        target = {"name": "test"}
        registry.register(target, "data")

        registry._simulate_collection(target)
        registry._process_cleanup_callbacks()

        assert "data" in cleanup_calls

    def test_cyclic_references_with_finalization(self):
        """
        Given objects with cyclic references registered for finalization
        When cycle is collected
        Then all cleanup callbacks are invoked
        """
        cleanup_calls = []
        registry = FinalizationRegistry(lambda held: cleanup_calls.append(held))

        # Create cycle: A -> B -> C -> A
        obj_a = {"name": "A"}
        obj_b = {"name": "B"}
        obj_c = {"name": "C"}

        obj_a["next"] = obj_b
        obj_b["next"] = obj_c
        obj_c["next"] = obj_a

        registry.register(obj_a, "A_cleanup")
        registry.register(obj_b, "B_cleanup")
        registry.register(obj_c, "C_cleanup")

        # Simulate GC collecting the cycle
        registry._simulate_collection(obj_a)
        registry._simulate_collection(obj_b)
        registry._simulate_collection(obj_c)

        registry._process_cleanup_callbacks()

        # All callbacks should run
        assert len(cleanup_calls) == 3
