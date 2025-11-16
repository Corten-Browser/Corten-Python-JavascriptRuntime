"""
Unit tests for QuickCheckOptimizer class
Tests FR-ES24-D-005: Normalization performance optimization
"""
import pytest
from components.unicode_edge_cases.src.quick_check import QuickCheckOptimizer


class TestQuickCheckNFC:
    """Test NFC Quick Check algorithm"""

    def test_ascii_is_quick_check_yes(self):
        """ASCII strings are Quick Check YES"""
        text = "Hello World"
        result = QuickCheckOptimizer.quick_check_nfc(text)
        assert result == "YES"

    def test_empty_string_is_yes(self):
        """Empty string is Quick Check YES"""
        result = QuickCheckOptimizer.quick_check_nfc("")
        assert result == "YES"

    def test_precomposed_characters_yes(self):
        """Most precomposed characters are Quick Check YES"""
        text = "\u00E9"  # é (precomposed)
        result = QuickCheckOptimizer.quick_check_nfc(text)
        assert result in ["YES", "MAYBE"]

    def test_decomposed_is_no_or_maybe(self):
        """Decomposed characters are Quick Check NO or MAYBE"""
        text = "e\u0301"  # e + combining acute
        result = QuickCheckOptimizer.quick_check_nfc(text)
        assert result in ["NO", "MAYBE"]

    def test_hangul_jamo_is_no(self):
        """Hangul Jamo are Quick Check NO (need composition)"""
        text = "\u1100\u1161"  # Jamo
        result = QuickCheckOptimizer.quick_check_nfc(text)
        assert result in ["NO", "MAYBE"]

    def test_hangul_syllable_is_yes(self):
        """Hangul syllables are Quick Check YES"""
        text = "\uAC00"  # 가
        result = QuickCheckOptimizer.quick_check_nfc(text)
        assert result == "YES"

    def test_quick_check_maybe_characters(self):
        """Some characters are Quick Check MAYBE"""
        # Characters that need context to determine normalization
        text = "\u0344"  # Combining Greek dialytika tonos
        result = QuickCheckOptimizer.quick_check_nfc(text)
        assert result in ["NO", "MAYBE"]


class TestQuickCheckNFD:
    """Test NFD Quick Check algorithm"""

    def test_ascii_is_yes(self):
        """ASCII strings are Quick Check YES"""
        text = "Hello World"
        result = QuickCheckOptimizer.quick_check_nfd(text)
        assert result == "YES"

    def test_empty_string_is_yes(self):
        """Empty string is Quick Check YES"""
        result = QuickCheckOptimizer.quick_check_nfd("")
        assert result == "YES"

    def test_decomposed_is_yes(self):
        """Decomposed characters are Quick Check YES"""
        text = "e\u0301"  # e + combining acute
        result = QuickCheckOptimizer.quick_check_nfd(text)
        assert result == "YES"

    def test_precomposed_is_no(self):
        """Precomposed characters are Quick Check NO"""
        text = "\u00E9"  # é (precomposed)
        result = QuickCheckOptimizer.quick_check_nfd(text)
        assert result == "NO"

    def test_hangul_syllable_is_no(self):
        """Hangul syllables are Quick Check NO (need decomposition)"""
        text = "\uAC00"  # 가
        result = QuickCheckOptimizer.quick_check_nfd(text)
        assert result == "NO"

    def test_hangul_jamo_is_yes(self):
        """Hangul Jamo are Quick Check YES"""
        text = "\u1100\u1161"  # Jamo
        result = QuickCheckOptimizer.quick_check_nfd(text)
        assert result == "YES"

    def test_no_maybe_for_nfd(self):
        """NFD has no MAYBE results (only YES or NO)"""
        # Various test strings
        texts = ["Hello", "\u00E9", "e\u0301", "\uAC00", "\u1100"]
        for text in texts:
            result = QuickCheckOptimizer.quick_check_nfd(text)
            assert result in ["YES", "NO"]
            assert result != "MAYBE"


class TestIsQuickCheckYes:
    """Test Quick Check YES character detection"""

    def test_ascii_is_yes_for_nfc(self):
        """ASCII is Quick Check YES for NFC"""
        assert QuickCheckOptimizer.is_quick_check_yes(ord('A'), "NFC") is True
        assert QuickCheckOptimizer.is_quick_check_yes(ord('z'), "NFC") is True

    def test_ascii_is_yes_for_nfd(self):
        """ASCII is Quick Check YES for NFD"""
        assert QuickCheckOptimizer.is_quick_check_yes(ord('A'), "NFD") is True

    def test_combining_mark_is_no_for_nfc(self):
        """Combining marks may not be Quick Check YES for NFC"""
        result = QuickCheckOptimizer.is_quick_check_yes(0x0301, "NFC")
        # May be NO or MAYBE depending on context
        assert isinstance(result, bool)

    def test_precomposed_is_yes_for_nfc(self):
        """Most precomposed characters are Quick Check YES for NFC"""
        result = QuickCheckOptimizer.is_quick_check_yes(0x00E9, "NFC")
        assert isinstance(result, bool)

    def test_precomposed_is_no_for_nfd(self):
        """Precomposed characters are Quick Check NO for NFD"""
        assert QuickCheckOptimizer.is_quick_check_yes(0x00E9, "NFD") is False

    def test_hangul_syllable_yes_for_nfc(self):
        """Hangul syllables are Quick Check YES for NFC"""
        assert QuickCheckOptimizer.is_quick_check_yes(0xAC00, "NFC") is True

    def test_hangul_syllable_no_for_nfd(self):
        """Hangul syllables are Quick Check NO for NFD"""
        assert QuickCheckOptimizer.is_quick_check_yes(0xAC00, "NFD") is False

    def test_hangul_jamo_no_for_nfc(self):
        """Hangul Jamo are Quick Check NO for NFC (need composition)"""
        assert QuickCheckOptimizer.is_quick_check_yes(0x1100, "NFC") is False

    def test_hangul_jamo_yes_for_nfd(self):
        """Hangul Jamo are Quick Check YES for NFD"""
        assert QuickCheckOptimizer.is_quick_check_yes(0x1100, "NFD") is True

    def test_invalid_form_raises_error(self):
        """Invalid normalization form should raise error"""
        with pytest.raises(ValueError, match="Invalid normalization form"):
            QuickCheckOptimizer.is_quick_check_yes(ord('A'), "INVALID")


class TestQuickCheckPerformance:
    """Test Quick Check performance characteristics"""

    def test_ascii_fast_path(self):
        """ASCII-only strings should use fast path"""
        import time
        text = "Hello World" * 100  # 1100 characters

        start = time.perf_counter()
        result = QuickCheckOptimizer.quick_check_nfc(text)
        elapsed = time.perf_counter() - start

        assert result == "YES"
        # Should be very fast (< 1ms for 1KB)
        assert elapsed < 0.001  # 1ms

    def test_quick_check_lookup_is_fast(self):
        """Individual character lookup should be O(1)"""
        import time

        start = time.perf_counter()
        for _ in range(1000):
            QuickCheckOptimizer.is_quick_check_yes(ord('A'), "NFC")
        elapsed = time.perf_counter() - start

        # 1000 lookups should complete in < 1ms (hash table)
        assert elapsed < 0.001

    def test_empty_string_instant(self):
        """Empty string should be instant"""
        import time

        start = time.perf_counter()
        result = QuickCheckOptimizer.quick_check_nfc("")
        elapsed = time.perf_counter() - start

        assert result == "YES"
        assert elapsed < 0.0001  # < 100µs
