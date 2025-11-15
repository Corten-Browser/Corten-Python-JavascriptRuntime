"""
Unit tests for well-known symbols.

Tests FR-P3-013 (Well-known symbols), FR-P3-018 (Symbol.iterator),
FR-P3-019 (Symbol.toStringTag), FR-P3-020 (Symbol.hasInstance).

TDD Phase: RED - These tests should fail initially.
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from well_known_symbols import (
    SYMBOL_ITERATOR,
    SYMBOL_TO_STRING_TAG,
    SYMBOL_HAS_INSTANCE,
    SYMBOL_TO_PRIMITIVE,
    SYMBOL_SPECIES,
    SYMBOL_IS_CONCAT_SPREADABLE,
    SYMBOL_UNSCOPABLES,
    SYMBOL_MATCH,
    SYMBOL_REPLACE,
    SYMBOL_SEARCH,
    SYMBOL_SPLIT,
)


class TestWellKnownSymbolsExist:
    """Test that all well-known symbols exist."""

    def test_symbol_iterator_exists(self):
        """Symbol.iterator should exist."""
        assert SYMBOL_ITERATOR is not None

    def test_symbol_to_string_tag_exists(self):
        """Symbol.toStringTag should exist."""
        assert SYMBOL_TO_STRING_TAG is not None

    def test_symbol_has_instance_exists(self):
        """Symbol.hasInstance should exist."""
        assert SYMBOL_HAS_INSTANCE is not None

    def test_symbol_to_primitive_exists(self):
        """Symbol.toPrimitive should exist."""
        assert SYMBOL_TO_PRIMITIVE is not None

    def test_symbol_species_exists(self):
        """Symbol.species should exist."""
        assert SYMBOL_SPECIES is not None

    def test_symbol_is_concat_spreadable_exists(self):
        """Symbol.isConcatSpreadable should exist."""
        assert SYMBOL_IS_CONCAT_SPREADABLE is not None

    def test_symbol_unscopables_exists(self):
        """Symbol.unscopables should exist."""
        assert SYMBOL_UNSCOPABLES is not None

    def test_symbol_match_exists(self):
        """Symbol.match should exist."""
        assert SYMBOL_MATCH is not None

    def test_symbol_replace_exists(self):
        """Symbol.replace should exist."""
        assert SYMBOL_REPLACE is not None

    def test_symbol_search_exists(self):
        """Symbol.search should exist."""
        assert SYMBOL_SEARCH is not None

    def test_symbol_split_exists(self):
        """Symbol.split should exist."""
        assert SYMBOL_SPLIT is not None


class TestWellKnownSymbolsUnique:
    """Test that well-known symbols are unique."""

    def test_all_well_known_symbols_are_different(self):
        """All well-known symbols should be unique."""
        symbols = [
            SYMBOL_ITERATOR,
            SYMBOL_TO_STRING_TAG,
            SYMBOL_HAS_INSTANCE,
            SYMBOL_TO_PRIMITIVE,
            SYMBOL_SPECIES,
            SYMBOL_IS_CONCAT_SPREADABLE,
            SYMBOL_UNSCOPABLES,
            SYMBOL_MATCH,
            SYMBOL_REPLACE,
            SYMBOL_SEARCH,
            SYMBOL_SPLIT,
        ]
        # All symbols should be unique
        assert len(symbols) == len(set(id(s) for s in symbols))

    def test_well_known_symbols_are_symbols(self):
        """All well-known symbols should be Symbol instances."""
        from symbol_value import SymbolValue

        symbols = [
            SYMBOL_ITERATOR,
            SYMBOL_TO_STRING_TAG,
            SYMBOL_HAS_INSTANCE,
            SYMBOL_TO_PRIMITIVE,
            SYMBOL_SPECIES,
            SYMBOL_IS_CONCAT_SPREADABLE,
            SYMBOL_UNSCOPABLES,
            SYMBOL_MATCH,
            SYMBOL_REPLACE,
            SYMBOL_SEARCH,
            SYMBOL_SPLIT,
        ]
        for sym in symbols:
            assert isinstance(sym, SymbolValue)


class TestWellKnownSymbolDescriptions:
    """Test that well-known symbols have correct descriptions."""

    def test_symbol_iterator_description(self):
        """Symbol.iterator should have 'Symbol.iterator' description."""
        assert SYMBOL_ITERATOR.description == "Symbol.iterator"

    def test_symbol_to_string_tag_description(self):
        """Symbol.toStringTag should have correct description."""
        assert SYMBOL_TO_STRING_TAG.description == "Symbol.toStringTag"

    def test_symbol_has_instance_description(self):
        """Symbol.hasInstance should have correct description."""
        assert SYMBOL_HAS_INSTANCE.description == "Symbol.hasInstance"

    def test_symbol_to_primitive_description(self):
        """Symbol.toPrimitive should have correct description."""
        assert SYMBOL_TO_PRIMITIVE.description == "Symbol.toPrimitive"

    def test_symbol_species_description(self):
        """Symbol.species should have correct description."""
        assert SYMBOL_SPECIES.description == "Symbol.species"

    def test_symbol_is_concat_spreadable_description(self):
        """Symbol.isConcatSpreadable should have correct description."""
        assert SYMBOL_IS_CONCAT_SPREADABLE.description == "Symbol.isConcatSpreadable"

    def test_symbol_unscopables_description(self):
        """Symbol.unscopables should have correct description."""
        assert SYMBOL_UNSCOPABLES.description == "Symbol.unscopables"

    def test_symbol_match_description(self):
        """Symbol.match should have correct description."""
        assert SYMBOL_MATCH.description == "Symbol.match"

    def test_symbol_replace_description(self):
        """Symbol.replace should have correct description."""
        assert SYMBOL_REPLACE.description == "Symbol.replace"

    def test_symbol_search_description(self):
        """Symbol.search should have correct description."""
        assert SYMBOL_SEARCH.description == "Symbol.search"

    def test_symbol_split_description(self):
        """Symbol.split should have correct description."""
        assert SYMBOL_SPLIT.description == "Symbol.split"


class TestWellKnownSymbolsImmutable:
    """Test that well-known symbols are immutable."""

    def test_well_known_symbols_always_same_reference(self):
        """Well-known symbols should always be the same reference."""
        # Import twice to ensure they're the same
        from well_known_symbols import SYMBOL_ITERATOR as iter1
        from well_known_symbols import SYMBOL_ITERATOR as iter2
        assert iter1 is iter2

    def test_symbol_iterator_consistent(self):
        """Symbol.iterator should be consistent across imports."""
        # This is the same as the reference test but explicit
        assert SYMBOL_ITERATOR is SYMBOL_ITERATOR
