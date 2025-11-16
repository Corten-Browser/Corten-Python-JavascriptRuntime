"""
Unit tests for CombiningCharacterHandler class
Tests combining mark reordering and canonical ordering
"""
import pytest
from components.unicode_edge_cases.src.combining_chars import CombiningCharacterHandler


class TestCombiningMarkReordering:
    """Test combining mark reordering functionality"""

    def test_single_combining_mark(self):
        """Single combining mark should be unchanged"""
        text = "e\u0301"  # e + acute
        result = CombiningCharacterHandler.reorder_combining_marks(text)
        assert result == "e\u0301"

    def test_multiple_marks_same_ccc(self):
        """Marks with same CCC should preserve order (stable sort)"""
        # e + acute (CCC=230) + grave (CCC=230)
        text = "e\u0301\u0300"
        result = CombiningCharacterHandler.reorder_combining_marks(text)
        # Order should be preserved (stable sort)
        assert result == "e\u0301\u0300"

    def test_multiple_marks_different_ccc(self):
        """Marks with different CCC should be sorted"""
        # e + cedilla (CCC=202) + acute (CCC=230)
        # Should reorder to acute + cedilla
        text = "e\u0327\u0301"
        result = CombiningCharacterHandler.reorder_combining_marks(text)
        # Lower CCC comes first
        assert result == "e\u0327\u0301" or result == "e\u0301\u0327"

    def test_blocked_combining_marks(self):
        """Starter character should block reordering"""
        # e + acute, then a (starter), then grave
        # acute and grave should NOT reorder across 'a'
        text = "e\u0301a\u0300"
        result = CombiningCharacterHandler.reorder_combining_marks(text)
        assert result[1] == "\u0301"  # Acute stays with 'e'
        assert result[3] == "\u0300"  # Grave stays with 'a'

    def test_complex_sequence(self):
        """Complex combining mark sequence"""
        # Multiple marks with different CCC values
        text = "e\u0301\u0327\u0300"
        result = CombiningCharacterHandler.reorder_combining_marks(text)
        # Should be ordered by CCC
        assert result[0] == "e"
        assert len(result) == 4

    def test_empty_string(self):
        """Empty string should be unchanged"""
        result = CombiningCharacterHandler.reorder_combining_marks("")
        assert result == ""


class TestIsStarter:
    """Test starter character detection"""

    def test_ascii_is_starter(self):
        """ASCII characters are starters"""
        assert CombiningCharacterHandler.is_starter(ord('A')) is True
        assert CombiningCharacterHandler.is_starter(ord('e')) is True

    def test_combining_mark_not_starter(self):
        """Combining marks are not starters"""
        assert CombiningCharacterHandler.is_starter(0x0301) is False  # Acute
        assert CombiningCharacterHandler.is_starter(0x0300) is False  # Grave

    def test_hangul_is_starter(self):
        """Hangul syllables are starters"""
        assert CombiningCharacterHandler.is_starter(0xAC00) is True  # 가

    def test_emoji_is_starter(self):
        """Emoji are starters"""
        assert CombiningCharacterHandler.is_starter(0x1F44B) is True  # 👋


class TestGetCombiningClass:
    """Test Canonical Combining Class retrieval"""

    def test_starter_has_ccc_zero(self):
        """Starters have CCC=0"""
        assert CombiningCharacterHandler.get_combining_class(ord('A')) == 0
        assert CombiningCharacterHandler.get_combining_class(0xAC00) == 0

    def test_combining_acute_ccc(self):
        """Combining acute has CCC=230"""
        assert CombiningCharacterHandler.get_combining_class(0x0301) == 230

    def test_combining_grave_ccc(self):
        """Combining grave has CCC=230"""
        assert CombiningCharacterHandler.get_combining_class(0x0300) == 230

    def test_combining_cedilla_ccc(self):
        """Combining cedilla has CCC=202"""
        assert CombiningCharacterHandler.get_combining_class(0x0327) == 202

    def test_combining_tilde_below_ccc(self):
        """Combining tilde below has CCC=220"""
        assert CombiningCharacterHandler.get_combining_class(0x0330) == 220
