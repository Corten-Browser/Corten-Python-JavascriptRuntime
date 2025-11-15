"""
Unit tests for ES2024 String methods: isWellFormed() and toWellFormed().

Tests Unicode surrogate pair handling according to ECMAScript 2024 specification.
"""

import pytest
from components.memory_gc.src import GarbageCollector
from components.object_runtime.src import JSString


class TestIsWellFormed:
    """Test String.prototype.isWellFormed() (FR-P3.5-030)."""

    def test_well_formed_ascii_string(self):
        """
        Given a string containing only ASCII characters
        When isWellFormed() is called
        Then it returns True (well-formed)
        """
        # Given
        gc = GarbageCollector()
        s = JSString(gc, "hello world")

        # When
        result = s.is_well_formed()

        # Then
        assert result is True

    def test_well_formed_unicode_string(self):
        """
        Given a string containing regular Unicode characters (no surrogates)
        When isWellFormed() is called
        Then it returns True (well-formed)
        """
        # Given
        gc = GarbageCollector()
        s = JSString(gc, "Hello 世界 🌍")

        # When
        result = s.is_well_formed()

        # Then
        assert result is True

    def test_well_formed_with_valid_surrogate_pair(self):
        """
        Given a string containing valid surrogate pairs
        When isWellFormed() is called
        Then it returns True (well-formed)
        """
        # Given
        gc = GarbageCollector()
        # Valid surrogate pair: high (0xD800) + low (0xDC00)
        s = JSString(gc, "test\ud800\udc00end")

        # When
        result = s.is_well_formed()

        # Then
        assert result is True

    def test_unpaired_high_surrogate_at_end(self):
        """
        Given a string with unpaired high surrogate at the end
        When isWellFormed() is called
        Then it returns False (not well-formed)
        """
        # Given
        gc = GarbageCollector()
        # Unpaired high surrogate (0xD800) at end
        s = JSString(gc, "test\ud800")

        # When
        result = s.is_well_formed()

        # Then
        assert result is False

    def test_unpaired_high_surrogate_in_middle(self):
        """
        Given a string with unpaired high surrogate in the middle
        When isWellFormed() is called
        Then it returns False (not well-formed)
        """
        # Given
        gc = GarbageCollector()
        # Unpaired high surrogate (0xD800) not followed by low surrogate
        s = JSString(gc, "test\ud800end")

        # When
        result = s.is_well_formed()

        # Then
        assert result is False

    def test_unpaired_low_surrogate(self):
        """
        Given a string with unpaired low surrogate
        When isWellFormed() is called
        Then it returns False (not well-formed)
        """
        # Given
        gc = GarbageCollector()
        # Unpaired low surrogate (0xDC00) without preceding high
        s = JSString(gc, "test\udc00end")

        # When
        result = s.is_well_formed()

        # Then
        assert result is False

    def test_multiple_unpaired_surrogates(self):
        """
        Given a string with multiple unpaired surrogates
        When isWellFormed() is called
        Then it returns False (not well-formed)
        """
        # Given
        gc = GarbageCollector()
        # Multiple unpaired surrogates
        s = JSString(gc, "\ud800test\udc00end\ud800")

        # When
        result = s.is_well_formed()

        # Then
        assert result is False

    def test_empty_string_is_well_formed(self):
        """
        Given an empty string
        When isWellFormed() is called
        Then it returns True (well-formed)
        """
        # Given
        gc = GarbageCollector()
        s = JSString(gc, "")

        # When
        result = s.is_well_formed()

        # Then
        assert result is True


class TestToWellFormed:
    """Test String.prototype.toWellFormed() (FR-P3.5-031)."""

    def test_already_well_formed_string_unchanged(self):
        """
        Given a well-formed string
        When toWellFormed() is called
        Then it returns a new string with the same value
        """
        # Given
        gc = GarbageCollector()
        s = JSString(gc, "hello world")

        # When
        result = s.to_well_formed()

        # Then
        assert result.get_value() == "hello world"
        assert result is not s  # New object

    def test_unpaired_high_surrogate_replaced(self):
        """
        Given a string with unpaired high surrogate
        When toWellFormed() is called
        Then unpaired surrogate is replaced with U+FFFD
        """
        # Given
        gc = GarbageCollector()
        # Unpaired high surrogate (0xD800)
        s = JSString(gc, "test\ud800end")

        # When
        result = s.to_well_formed()

        # Then
        assert result.get_value() == "test\ufffdend"

    def test_unpaired_low_surrogate_replaced(self):
        """
        Given a string with unpaired low surrogate
        When toWellFormed() is called
        Then unpaired surrogate is replaced with U+FFFD
        """
        # Given
        gc = GarbageCollector()
        # Unpaired low surrogate (0xDC00)
        s = JSString(gc, "test\udc00end")

        # When
        result = s.to_well_formed()

        # Then
        assert result.get_value() == "test\ufffdend"

    def test_multiple_unpaired_surrogates_all_replaced(self):
        """
        Given a string with multiple unpaired surrogates
        When toWellFormed() is called
        Then all unpaired surrogates are replaced with U+FFFD
        """
        # Given
        gc = GarbageCollector()
        # Multiple unpaired surrogates: low, high, high
        s = JSString(gc, "\udc00test\ud800end\ud800")

        # When
        result = s.to_well_formed()

        # Then
        assert result.get_value() == "\ufffdtest\ufffdend\ufffd"

    def test_valid_surrogate_pairs_preserved(self):
        """
        Given a string with valid surrogate pairs
        When toWellFormed() is called
        Then valid pairs are preserved unchanged
        """
        # Given
        gc = GarbageCollector()
        # Valid surrogate pair: high (0xD800) + low (0xDC00)
        original_value = "test\ud800\udc00end"
        s = JSString(gc, original_value)

        # When
        result = s.to_well_formed()

        # Then
        assert result.get_value() == original_value

    def test_original_string_not_mutated(self):
        """
        Given a string with unpaired surrogates
        When toWellFormed() is called
        Then original string is NOT mutated
        """
        # Given
        gc = GarbageCollector()
        original_value = "test\ud800end"
        s = JSString(gc, original_value)

        # When
        result = s.to_well_formed()

        # Then
        assert s.get_value() == original_value  # Original unchanged
        assert result.get_value() == "test\ufffdend"  # Result has replacement

    def test_empty_string_returns_empty_string(self):
        """
        Given an empty string
        When toWellFormed() is called
        Then it returns a new empty string
        """
        # Given
        gc = GarbageCollector()
        s = JSString(gc, "")

        # When
        result = s.to_well_formed()

        # Then
        assert result.get_value() == ""
        assert result is not s  # New object

    def test_high_surrogate_at_end_replaced(self):
        """
        Given a string with unpaired high surrogate at the end
        When toWellFormed() is called
        Then the high surrogate is replaced with U+FFFD
        """
        # Given
        gc = GarbageCollector()
        # High surrogate at end
        s = JSString(gc, "test\ud800")

        # When
        result = s.to_well_formed()

        # Then
        assert result.get_value() == "test\ufffd"

    def test_mixed_valid_and_invalid_surrogates(self):
        """
        Given a string with both valid pairs and unpaired surrogates
        When toWellFormed() is called
        Then only unpaired surrogates are replaced, valid pairs preserved
        """
        # Given
        gc = GarbageCollector()
        # Valid pair (D800 DC00) + unpaired high (D800) + valid pair (D801 DC01)
        s = JSString(gc, "\ud800\udc00test\ud800end\ud801\udc01")

        # When
        result = s.to_well_formed()

        # Then
        # Valid pairs preserved, unpaired high replaced
        assert result.get_value() == "\ud800\udc00test\ufffdend\ud801\udc01"


class TestES2024StringMethodsIntegration:
    """Integration tests for ES2024 String methods."""

    def test_is_well_formed_and_to_well_formed_consistency(self):
        """
        Given any string
        When toWellFormed() is called
        Then the result should always be well-formed
        """
        # Given
        gc = GarbageCollector()
        test_strings = [
            "hello",
            "test\ud800",
            "\udc00test",
            "\ud800\udc00",
            "\ud800test\udc00",
            "",
        ]

        for test_str in test_strings:
            # When
            s = JSString(gc, test_str)
            well_formed = s.to_well_formed()

            # Then
            assert well_formed.is_well_formed() is True

    def test_multiple_valid_surrogate_pairs(self):
        """
        Given a string with multiple valid surrogate pairs
        When isWellFormed() is called
        Then it returns True
        """
        # Given
        gc = GarbageCollector()
        # Multiple valid pairs
        s = JSString(gc, "\ud800\udc00\ud801\udc01\ud802\udc02")

        # When
        result = s.is_well_formed()

        # Then
        assert result is True

    def test_boundary_surrogate_values(self):
        """
        Given strings with boundary surrogate values
        When isWellFormed() is called
        Then it correctly identifies well-formed and malformed strings
        """
        # Given
        gc = GarbageCollector()

        # Test high surrogate boundaries
        # 0xD800 (first high) + 0xDC00 (first low) - VALID
        s1 = JSString(gc, "\ud800\udc00")
        assert s1.is_well_formed() is True

        # 0xDBFF (last high) + 0xDFFF (last low) - VALID
        s2 = JSString(gc, "\udbff\udfff")
        assert s2.is_well_formed() is True

        # 0xD800 (first high) alone - INVALID
        s3 = JSString(gc, "\ud800")
        assert s3.is_well_formed() is False

        # 0xDC00 (first low) alone - INVALID
        s4 = JSString(gc, "\udc00")
        assert s4.is_well_formed() is False
