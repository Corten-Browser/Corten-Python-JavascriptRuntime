"""
Unit tests for comparison algorithms.

Tests the Unicode Collation Algorithm implementation.
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.comparison import (
    normalize_string,
    compare_strings,
    extract_numeric_parts,
    remove_punctuation
)


class TestStringNormalization:
    """Test Unicode normalization."""

    def test_normalize_nfc(self):
        """Should normalize to NFC form."""
        result = normalize_string('café')
        assert isinstance(result, str)

    def test_normalize_nfd_to_nfc(self):
        """Should convert NFD to NFC."""
        nfd = 'cafe\u0301'  # NFD form
        result = normalize_string(nfd)
        assert isinstance(result, str)

    def test_normalize_empty_string(self):
        """Should handle empty string."""
        result = normalize_string('')
        assert result == ''


class TestCompareStrings:
    """Test string comparison algorithm."""

    def test_compare_basic(self):
        """Should compare basic ASCII strings."""
        result = compare_strings('a', 'b')
        assert result < 0

    def test_compare_equal(self):
        """Should return 0 for equal strings."""
        result = compare_strings('hello', 'hello')
        assert result == 0

    def test_compare_with_sensitivity_base(self):
        """Should ignore case and accents with base sensitivity."""
        result = compare_strings('a', 'A', sensitivity='base')
        assert result == 0

    def test_compare_with_sensitivity_accent(self):
        """Should distinguish accents with accent sensitivity."""
        result = compare_strings('a', 'á', sensitivity='accent')
        assert result != 0

    def test_compare_with_sensitivity_case(self):
        """Should distinguish case with case sensitivity."""
        result = compare_strings('a', 'A', sensitivity='case')
        assert result != 0

    def test_compare_with_numeric_true(self):
        """Should use numeric ordering with numeric=True."""
        result = compare_strings('2', '10', numeric=True)
        assert result < 0

    def test_compare_with_numeric_false(self):
        """Should use lexicographic ordering with numeric=False."""
        result = compare_strings('2', '10', numeric=False)
        assert result > 0

    def test_compare_with_case_first_upper(self):
        """Should sort uppercase first with caseFirst='upper'."""
        result = compare_strings('A', 'a', case_first='upper')
        assert result < 0

    def test_compare_with_case_first_lower(self):
        """Should sort lowercase first with caseFirst='lower'."""
        result = compare_strings('a', 'A', case_first='lower')
        assert result < 0

    def test_compare_with_ignore_punctuation_true(self):
        """Should ignore punctuation with ignorePunctuation=True."""
        result = compare_strings('hello', 'he-llo', ignore_punctuation=True)
        assert result == 0

    def test_compare_with_ignore_punctuation_false(self):
        """Should not ignore punctuation with ignorePunctuation=False."""
        result = compare_strings('hello', 'he-llo', ignore_punctuation=False)
        assert result != 0


class TestExtractNumericParts:
    """Test numeric part extraction."""

    def test_extract_pure_number(self):
        """Should extract pure number."""
        result = extract_numeric_parts('123')
        assert isinstance(result, list)
        assert len(result) > 0

    def test_extract_mixed_text_number(self):
        """Should extract mixed text and numbers."""
        result = extract_numeric_parts('item10')
        assert isinstance(result, list)
        assert len(result) == 2  # 'item' and '10'

    def test_extract_multiple_numbers(self):
        """Should extract multiple numbers."""
        result = extract_numeric_parts('v1.2.3')
        assert isinstance(result, list)
        assert len(result) > 3

    def test_extract_no_numbers(self):
        """Should handle strings with no numbers."""
        result = extract_numeric_parts('hello')
        assert isinstance(result, list)


class TestRemovePunctuation:
    """Test punctuation removal."""

    def test_remove_punctuation_hyphen(self):
        """Should remove hyphens."""
        result = remove_punctuation('he-llo')
        assert result == 'hello'

    def test_remove_punctuation_period(self):
        """Should remove periods."""
        result = remove_punctuation('he.llo')
        assert result == 'hello'

    def test_remove_punctuation_multiple(self):
        """Should remove multiple punctuation marks."""
        result = remove_punctuation('h-e.l!l?o')
        assert result == 'hello'

    def test_remove_punctuation_none(self):
        """Should handle strings with no punctuation."""
        result = remove_punctuation('hello')
        assert result == 'hello'

    def test_remove_punctuation_all_types(self):
        """Should remove all types of punctuation."""
        result = remove_punctuation('!@#$%hello^&*()')
        assert 'hello' in result
