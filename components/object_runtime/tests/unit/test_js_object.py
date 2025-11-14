"""
Unit tests for JSObject class.

Tests JavaScript object representation with property storage
and prototype chain implementation.
"""

import pytest


class TestJSObjectCreation:
    """Test JSObject instantiation."""

    def test_create_object_without_prototype(self):
        """Test creating JSObject without prototype."""
        from components.memory_gc.src import GarbageCollector, HeapObject
        from components.value_system.src import Value
        from js_object import JSObject

        gc = GarbageCollector()
        obj = JSObject(gc)

        assert isinstance(obj, JSObject)
        assert isinstance(obj, HeapObject)
        assert obj.get_prototype() is None

    def test_create_object_with_prototype(self):
        """Test creating JSObject with prototype."""
        from components.memory_gc.src import GarbageCollector
        from js_object import JSObject

        gc = GarbageCollector()
        prototype = JSObject(gc)
        obj = JSObject(gc, prototype=prototype)

        assert obj.get_prototype() is prototype


class TestJSObjectPropertyAccess:
    """Test property get/set operations."""

    def test_set_and_get_property(self):
        """Test setting and getting a property."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_object import JSObject

        gc = GarbageCollector()
        obj = JSObject(gc)
        value = Value.from_smi(42)

        obj.set_property("answer", value)
        result = obj.get_property("answer")

        assert result.is_smi()
        assert result.to_smi() == 42

    def test_get_nonexistent_property_returns_undefined(self):
        """Test getting nonexistent property returns undefined."""
        from components.memory_gc.src import GarbageCollector
        from js_object import JSObject

        gc = GarbageCollector()
        obj = JSObject(gc)

        result = obj.get_property("nonexistent")

        # Should return some form of undefined value
        assert result is not None

    def test_overwrite_existing_property(self):
        """Test overwriting existing property."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_object import JSObject

        gc = GarbageCollector()
        obj = JSObject(gc)

        obj.set_property("key", Value.from_smi(1))
        obj.set_property("key", Value.from_smi(2))
        result = obj.get_property("key")

        assert result.to_smi() == 2


class TestJSObjectPrototypeChain:
    """Test prototype chain property lookup."""

    def test_get_property_from_prototype(self):
        """Test getting property from prototype."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_object import JSObject

        gc = GarbageCollector()
        prototype = JSObject(gc)
        obj = JSObject(gc, prototype=prototype)

        prototype.set_property("inherited", Value.from_smi(100))
        result = obj.get_property("inherited")

        assert result.is_smi()
        assert result.to_smi() == 100

    def test_own_property_shadows_prototype_property(self):
        """Test own property shadows prototype property."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_object import JSObject

        gc = GarbageCollector()
        prototype = JSObject(gc)
        obj = JSObject(gc, prototype=prototype)

        prototype.set_property("key", Value.from_smi(1))
        obj.set_property("key", Value.from_smi(2))
        result = obj.get_property("key")

        assert result.to_smi() == 2

    def test_set_prototype(self):
        """Test setting prototype."""
        from components.memory_gc.src import GarbageCollector
        from js_object import JSObject

        gc = GarbageCollector()
        obj = JSObject(gc)
        prototype = JSObject(gc)

        obj.set_prototype(prototype)

        assert obj.get_prototype() is prototype


class TestJSObjectPropertyChecks:
    """Test has_property and delete_property operations."""

    def test_has_property_for_own_property(self):
        """Test has_property for own property."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_object import JSObject

        gc = GarbageCollector()
        obj = JSObject(gc)
        obj.set_property("key", Value.from_smi(1))

        assert obj.has_property("key") is True

    def test_has_property_for_inherited_property(self):
        """Test has_property for inherited property."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_object import JSObject

        gc = GarbageCollector()
        prototype = JSObject(gc)
        obj = JSObject(gc, prototype=prototype)

        prototype.set_property("inherited", Value.from_smi(1))

        assert obj.has_property("inherited") is True

    def test_has_property_for_nonexistent_property(self):
        """Test has_property for nonexistent property."""
        from components.memory_gc.src import GarbageCollector
        from js_object import JSObject

        gc = GarbageCollector()
        obj = JSObject(gc)

        assert obj.has_property("nonexistent") is False

    def test_delete_existing_property(self):
        """Test deleting existing property."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_object import JSObject

        gc = GarbageCollector()
        obj = JSObject(gc)
        obj.set_property("key", Value.from_smi(1))

        result = obj.delete_property("key")

        assert result is True
        assert obj.has_property("key") is False

    def test_delete_nonexistent_property(self):
        """Test deleting nonexistent property."""
        from components.memory_gc.src import GarbageCollector
        from js_object import JSObject

        gc = GarbageCollector()
        obj = JSObject(gc)

        result = obj.delete_property("nonexistent")

        assert result is False

    def test_delete_does_not_affect_prototype(self):
        """Test delete does not affect prototype."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_object import JSObject

        gc = GarbageCollector()
        prototype = JSObject(gc)
        obj = JSObject(gc, prototype=prototype)

        prototype.set_property("inherited", Value.from_smi(1))
        result = obj.delete_property("inherited")

        assert result is False
        assert prototype.has_property("inherited") is True


class TestJSObjectGCIntegration:
    """Test garbage collection integration."""

    def test_get_references_returns_prototype(self):
        """Test get_references returns prototype."""
        from components.memory_gc.src import GarbageCollector
        from js_object import JSObject

        gc = GarbageCollector()
        prototype = JSObject(gc)
        obj = JSObject(gc, prototype=prototype)

        references = obj.get_references()

        assert prototype in references

    def test_get_references_returns_object_values(self):
        """Test get_references returns object values."""
        from components.memory_gc.src import GarbageCollector
        from components.value_system.src import Value
        from js_object import JSObject

        gc = GarbageCollector()
        obj = JSObject(gc)
        ref_obj = JSObject(gc)

        obj.set_property("ref", Value.from_object(ref_obj))
        references = obj.get_references()

        assert ref_obj in references
