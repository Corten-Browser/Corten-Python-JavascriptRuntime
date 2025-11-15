"""
Integration tests for Symbol component.

Tests end-to-end symbol functionality and integration scenarios.

TDD Phase: RED - These tests should fail initially.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from symbol_value import Symbol, symbol_for, symbol_key_for
from well_known_symbols import SYMBOL_ITERATOR, SYMBOL_TO_STRING_TAG
from symbol_ops import symbol_typeof, symbol_to_string, symbol_strict_equals
from symbol_properties import set_symbol_property, get_symbol_property, get_own_property_symbols


class TestSymbolEndToEnd:
    """Test complete symbol workflows."""

    def test_create_and_use_symbol_as_property_key(self):
        """Complete workflow: create symbol and use as property key."""
        # Create symbol
        sym = Symbol("myProperty")
        assert symbol_typeof(sym) == "symbol"

        # Use as property key
        obj = {}
        set_symbol_property(obj, sym, "secret value")

        # Retrieve value
        value = get_symbol_property(obj, sym)
        assert value == "secret value"

        # Verify not enumerable
        assert sym not in obj

    def test_registry_symbol_reuse(self):
        """Test global registry symbol reuse across different parts."""
        # Component A creates registry symbol
        sym1 = symbol_for("shared.config")
        obj1 = {}
        set_symbol_property(obj1, sym1, {"setting": "value"})

        # Component B retrieves same symbol
        sym2 = symbol_for("shared.config")
        assert sym1 is sym2

        # Component B can access same property
        value = get_symbol_property(obj1, sym2)
        assert value == {"setting": "value"}

    def test_well_known_symbol_protocol(self):
        """Test using well-known symbols for protocol implementation."""
        # Create object with custom iterator
        obj = {}
        iterator_called = []

        def custom_iterator():
            iterator_called.append(True)
            return iter([1, 2, 3])

        set_symbol_property(obj, SYMBOL_ITERATOR, custom_iterator)

        # Retrieve iterator
        iterator = get_symbol_property(obj, SYMBOL_ITERATOR)
        assert iterator is not None
        result = iterator()
        assert iterator_called == [True]

    def test_multiple_well_known_symbols_on_object(self):
        """Test object with multiple well-known symbol properties."""
        obj = {}
        set_symbol_property(obj, SYMBOL_ITERATOR, "iterator")
        set_symbol_property(obj, SYMBOL_TO_STRING_TAG, "CustomObject")

        assert get_symbol_property(obj, SYMBOL_ITERATOR) == "iterator"
        assert get_symbol_property(obj, SYMBOL_TO_STRING_TAG) == "CustomObject"

        symbols = get_own_property_symbols(obj)
        assert len(symbols) == 2

    def test_symbol_coercion_workflow(self):
        """Test symbol type coercion in workflow."""
        sym = Symbol("test")

        # typeof should work
        assert symbol_typeof(sym) == "symbol"

        # String conversion should work
        str_repr = symbol_to_string(sym)
        assert str_repr == "Symbol(test)"

        # Symbol should be truthy
        from symbol_ops import symbol_to_boolean
        assert symbol_to_boolean(sym) is True

    def test_mixed_symbol_and_string_properties(self):
        """Test object with both symbol and string properties."""
        obj = {
            "name": "John",
            "age": 30
        }
        sym1 = Symbol("id")
        sym2 = Symbol("metadata")

        set_symbol_property(obj, sym1, "secret-id-123")
        set_symbol_property(obj, sym2, {"created": "2024-01-01"})

        # Regular properties accessible
        assert obj["name"] == "John"
        assert obj["age"] == 30

        # Symbol properties accessible
        assert get_symbol_property(obj, sym1) == "secret-id-123"
        assert get_symbol_property(obj, sym2) == {"created": "2024-01-01"}

        # Symbol properties not enumerable
        regular_keys = list(obj.keys())
        assert "name" in regular_keys
        assert "age" in regular_keys
        assert sym1 not in regular_keys
        assert sym2 not in regular_keys

        # Can get symbol properties separately
        symbol_keys = get_own_property_symbols(obj)
        assert sym1 in symbol_keys
        assert sym2 in symbol_keys

    def test_symbol_uniqueness_guarantees(self):
        """Test that symbol uniqueness is maintained across operations."""
        # Create many symbols
        symbols = [Symbol(f"sym{i}") for i in range(100)]

        # All should be unique
        unique_ids = set(id(s) for s in symbols)
        assert len(unique_ids) == 100

        # All should have different internal IDs
        internal_ids = set(s._id for s in symbols)
        assert len(internal_ids) == 100

    def test_registry_vs_local_symbols(self):
        """Test interaction between registry and local symbols."""
        # Create local symbol
        local_sym = Symbol("test")

        # Create registry symbol
        registry_sym = symbol_for("test")

        # They should be different
        assert local_sym is not registry_sym
        assert not symbol_strict_equals(local_sym, registry_sym)

        # Registry symbol lookup works
        assert symbol_key_for(registry_sym) == "test"

        # Local symbol lookup returns None
        assert symbol_key_for(local_sym) is None

    def test_symbol_property_deletion(self):
        """Test deleting symbol properties doesn't affect others."""
        obj = {}
        sym1 = Symbol("key1")
        sym2 = Symbol("key2")
        sym3 = Symbol("key3")

        set_symbol_property(obj, sym1, "value1")
        set_symbol_property(obj, sym2, "value2")
        set_symbol_property(obj, sym3, "value3")

        # Delete one symbol property
        from symbol_properties import delete_symbol_property
        delete_symbol_property(obj, sym2)

        # Others should remain
        assert get_symbol_property(obj, sym1) == "value1"
        assert get_symbol_property(obj, sym3) == "value3"

        # Deleted one should be gone
        from symbol_properties import has_symbol_property
        assert not has_symbol_property(obj, sym2)

    def test_well_known_symbols_immutable_across_usage(self):
        """Test that well-known symbols remain constant."""
        from well_known_symbols import (
            SYMBOL_ITERATOR,
            SYMBOL_HAS_INSTANCE,
            SYMBOL_TO_PRIMITIVE
        )

        # Store references
        iter1 = SYMBOL_ITERATOR
        iter2 = SYMBOL_ITERATOR

        # Should be same reference
        assert iter1 is iter2

        # Use in properties shouldn't change it
        obj = {}
        set_symbol_property(obj, SYMBOL_ITERATOR, "test")
        assert SYMBOL_ITERATOR is iter1

        # All well-known symbols should be unique
        assert SYMBOL_ITERATOR is not SYMBOL_HAS_INSTANCE
        assert SYMBOL_ITERATOR is not SYMBOL_TO_PRIMITIVE
        assert SYMBOL_HAS_INSTANCE is not SYMBOL_TO_PRIMITIVE
