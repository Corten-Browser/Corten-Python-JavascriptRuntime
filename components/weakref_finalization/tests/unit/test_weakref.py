"""
Unit tests for WeakRef class.

Tests follow TDD RED phase - these tests will fail until implementation is complete.
Covers:
- FR-ES24-B-028: WeakRef constructor
- FR-ES24-B-029: WeakRef.prototype.deref()
- FR-ES24-B-030: WeakRef GC behavior (unit-level)
"""

import pytest
from weakref_finalization import WeakRef


class TestWeakRefConstructor:
    """Test WeakRef constructor (FR-ES24-B-028)."""

    def test_create_weakref_with_object(self):
        """
        Given an object
        When creating a WeakRef to it
        Then WeakRef instance is created successfully
        """
        target = {"name": "test"}
        ref = WeakRef(target)

        assert ref is not None
        assert isinstance(ref, WeakRef)

    def test_create_weakref_with_symbol(self):
        """
        Given a symbol
        When creating a WeakRef to it
        Then WeakRef instance is created successfully

        Note: Symbols are allowed as WeakRef targets.
        """
        # For now, we'll use a special object to represent a symbol
        # In real implementation, this would be a JSSymbol
        symbol_target = type('Symbol', (), {'__name__': 'test_symbol'})()
        ref = WeakRef(symbol_target)

        assert ref is not None
        assert isinstance(ref, WeakRef)

    def test_weakref_rejects_null(self):
        """
        Given null value
        When creating a WeakRef to it
        Then TypeError is raised
        """
        with pytest.raises(TypeError, match="WeakRef target must be an object"):
            WeakRef(None)

    def test_weakref_rejects_undefined(self):
        """
        Given undefined value (represented as special object)
        When creating a WeakRef to it
        Then TypeError is raised
        """
        # In Python, we'll use a sentinel value for undefined
        undefined = type('Undefined', (), {})()

        with pytest.raises(TypeError, match="WeakRef target must be an object"):
            WeakRef(undefined)

    def test_weakref_rejects_number(self):
        """
        Given a number primitive
        When creating a WeakRef to it
        Then TypeError is raised
        """
        with pytest.raises(TypeError, match="WeakRef target must be an object"):
            WeakRef(42)

    def test_weakref_rejects_string(self):
        """
        Given a string primitive
        When creating a WeakRef to it
        Then TypeError is raised
        """
        with pytest.raises(TypeError, match="WeakRef target must be an object"):
            WeakRef("test string")

    def test_weakref_rejects_boolean(self):
        """
        Given a boolean primitive
        When creating a WeakRef to it
        Then TypeError is raised
        """
        with pytest.raises(TypeError, match="WeakRef target must be an object"):
            WeakRef(True)


class TestWeakRefDeref:
    """Test WeakRef.deref() method (FR-ES24-B-029)."""

    def test_deref_returns_target_when_alive(self):
        """
        Given a WeakRef to an alive object
        When calling deref()
        Then the original target object is returned
        """
        target = {"name": "test", "value": 123}
        ref = WeakRef(target)

        result = ref.deref()

        assert result is target
        assert result["name"] == "test"
        assert result["value"] == 123

    def test_deref_returns_none_when_collected(self):
        """
        Given a WeakRef to a collected object
        When calling deref()
        Then undefined (None in Python) is returned
        """
        # Create weak ref
        ref = WeakRef({"name": "test"})

        # Simulate GC by manually marking as collected
        ref._mark_collected()

        result = ref.deref()

        assert result is None

    def test_deref_stability_within_turn(self):
        """
        Given a WeakRef
        When calling deref() multiple times in same turn
        Then same value is returned each time

        Note: This tests turn stability guarantee.
        """
        target = {"name": "test"}
        ref = WeakRef(target)

        # Multiple deref calls in same turn
        result1 = ref.deref()
        result2 = ref.deref()
        result3 = ref.deref()

        assert result1 is result2
        assert result2 is result3
        assert result1 is target

    def test_deref_after_target_goes_out_of_scope(self):
        """
        Given a WeakRef created in a scope
        When target goes out of scope and is collected
        Then deref() returns None
        """
        def create_target_and_ref():
            target = {"name": "temp"}
            ref = WeakRef(target)
            return ref

        ref = create_target_and_ref()
        # Target is out of scope now, simulate GC
        ref._mark_collected()

        result = ref.deref()
        assert result is None

    def test_multiple_weakrefs_to_same_target(self):
        """
        Given multiple WeakRefs to the same target
        When dereferencing each
        Then all return the same target object
        """
        target = {"shared": "object"}
        ref1 = WeakRef(target)
        ref2 = WeakRef(target)
        ref3 = WeakRef(target)

        assert ref1.deref() is target
        assert ref2.deref() is target
        assert ref3.deref() is target
        assert ref1.deref() is ref2.deref()


class TestWeakRefGCBehavior:
    """Test WeakRef GC behavior (FR-ES24-B-030 - unit level)."""

    def test_weakref_does_not_prevent_collection(self):
        """
        Given a WeakRef to an object
        When the object has no other strong references
        Then the object can be garbage collected

        Note: We simulate this by verifying WeakRef doesn't keep strong ref.
        """
        target = {"name": "collectable"}
        ref = WeakRef(target)

        # WeakRef should not prevent collection
        # We verify this by checking internal state
        assert not ref._has_strong_reference()

    def test_weakref_target_collected_when_no_strong_refs(self):
        """
        Given a WeakRef where target has no strong references
        When GC runs
        Then target is collected and deref() returns None
        """
        ref = WeakRef({"temp": "data"})

        # Simulate GC collection
        ref._mark_collected()

        assert ref.deref() is None

    def test_weakref_target_alive_with_strong_refs(self):
        """
        Given a WeakRef where target has strong references
        When GC runs
        Then target is NOT collected and deref() returns target
        """
        target = {"persistent": "data"}
        ref = WeakRef(target)

        # Target has strong reference (variable 'target')
        # Simulate GC - target should NOT be collected
        # (GC would see strong ref and not collect)

        result = ref.deref()
        assert result is target

    def test_collection_state_tracked_correctly(self):
        """
        Given a WeakRef
        When target is collected
        Then internal state correctly reflects collection
        """
        ref = WeakRef({"name": "test"})

        # Initially not collected
        assert not ref._is_collected()

        # Mark as collected
        ref._mark_collected()

        # Now collected
        assert ref._is_collected()


class TestWeakRefEdgeCases:
    """Test WeakRef edge cases."""

    def test_weakref_to_empty_object(self):
        """
        Given an empty object
        When creating a WeakRef to it
        Then WeakRef works correctly
        """
        target = {}
        ref = WeakRef(target)

        assert ref.deref() is target

    def test_weakref_to_nested_object(self):
        """
        Given a nested object structure
        When creating a WeakRef to it
        Then WeakRef correctly references the object
        """
        target = {
            "outer": {
                "inner": {
                    "value": 42
                }
            }
        }
        ref = WeakRef(target)

        result = ref.deref()
        assert result is target
        assert result["outer"]["inner"]["value"] == 42

    def test_weakref_to_object_with_methods(self):
        """
        Given an object with methods
        When creating a WeakRef to it
        Then WeakRef correctly references the object
        """
        class TestClass:
            def method(self):
                return "called"

        target = TestClass()
        ref = WeakRef(target)

        result = ref.deref()
        assert result is target
        assert result.method() == "called"

    def test_weakref_comparison(self):
        """
        Given two WeakRefs
        When comparing them
        Then they are equal if they reference the same target
        """
        target = {"name": "shared"}
        ref1 = WeakRef(target)
        ref2 = WeakRef(target)
        ref3 = WeakRef({"name": "different"})

        # Different WeakRef instances
        assert ref1 is not ref2
        assert ref1 is not ref3

        # But deref returns same target
        assert ref1.deref() is ref2.deref()
        assert ref1.deref() is not ref3.deref()


class TestWeakRefPerformance:
    """Performance tests for WeakRef."""

    def test_weakref_creation_performance(self):
        """
        Given performance requirement of <1µs creation
        When creating many WeakRefs
        Then average creation time is within limit
        """
        import time

        targets = [{"id": i} for i in range(1000)]

        start = time.perf_counter()
        refs = [WeakRef(target) for target in targets]
        end = time.perf_counter()

        avg_time_us = (end - start) / len(targets) * 1_000_000

        # Should be < 1µs per creation
        assert avg_time_us < 1.0, f"Creation took {avg_time_us}µs, should be <1µs"

    def test_deref_performance_when_alive(self):
        """
        Given performance requirement of <100ns for deref when alive
        When dereferencing many times
        Then average deref time is within limit
        """
        import time

        target = {"name": "test"}
        ref = WeakRef(target)

        iterations = 100000
        start = time.perf_counter()
        for _ in range(iterations):
            result = ref.deref()
        end = time.perf_counter()

        avg_time_ns = (end - start) / iterations * 1_000_000_000

        # Should be < 100ns per deref
        assert avg_time_ns < 100.0, f"Deref took {avg_time_ns}ns, should be <100ns"

    def test_deref_performance_when_collected(self):
        """
        Given performance requirement of <50ns for deref when collected
        When dereferencing collected WeakRef many times
        Then average deref time is within limit
        """
        import time

        ref = WeakRef({"name": "test"})
        ref._mark_collected()

        iterations = 100000
        start = time.perf_counter()
        for _ in range(iterations):
            result = ref.deref()
        end = time.perf_counter()

        avg_time_ns = (end - start) / iterations * 1_000_000_000

        # Should be < 50ns per deref when collected
        assert avg_time_ns < 50.0, f"Deref (collected) took {avg_time_ns}ns, should be <50ns"
