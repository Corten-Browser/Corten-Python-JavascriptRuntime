"""
Integration tests for Unicode normalization
Tests end-to-end normalization workflows
"""
import pytest
from components.unicode_edge_cases.src.normalizer import UnicodeNormalizer


class TestNormalizationRoundTrip:
    """Test normalization round-trip properties"""

    def test_nfc_nfd_round_trip(self):
        """NFC(NFD(s)) should equal NFC(s)"""
        text = "café"
        nfd = UnicodeNormalizer.normalize_nfd(text)
        nfc_from_nfd = UnicodeNormalizer.normalize_nfc(nfd)
        nfc_direct = UnicodeNormalizer.normalize_nfc(text)
        assert nfc_from_nfd == nfc_direct

    def test_nfd_nfc_round_trip(self):
        """NFD(NFC(s)) should equal NFD(s)"""
        text = "e\u0301"  # Decomposed
        nfc = UnicodeNormalizer.normalize_nfc(text)
        nfd_from_nfc = UnicodeNormalizer.normalize_nfd(nfc)
        nfd_direct = UnicodeNormalizer.normalize_nfd(text)
        assert nfd_from_nfc == nfd_direct

    def test_nfkc_stability(self):
        """NFKC(NFKC(s)) = NFKC(s)"""
        text = "ﬁle"
        nfkc1 = UnicodeNormalizer.normalize_nfkc(text)
        nfkc2 = UnicodeNormalizer.normalize_nfkc(nfkc1)
        assert nfkc1 == nfkc2

    def test_nfkd_stability(self):
        """NFKD(NFKD(s)) = NFKD(s)"""
        text = "\uFF21"  # Full-width A
        nfkd1 = UnicodeNormalizer.normalize_nfkd(text)
        nfkd2 = UnicodeNormalizer.normalize_nfkd(nfkd1)
        assert nfkd1 == nfkd2


class TestComplexNormalization:
    """Test complex normalization scenarios"""

    def test_mixed_scripts(self):
        """Mixed scripts should normalize correctly"""
        text = "Hello café 가나다"
        nfc = UnicodeNormalizer.normalize_nfc(text)
        nfd = UnicodeNormalizer.normalize_nfd(text)
        assert len(nfc) <= len(nfd)

    def test_emoji_in_text(self):
        """Text with emoji should normalize correctly"""
        text = "Hello 👋🏽 World"
        nfc = UnicodeNormalizer.normalize_nfc(text)
        assert "Hello" in nfc
        assert "World" in nfc

    def test_compatibility_normalization(self):
        """Compatibility normalization should be lossy"""
        text = "ﬁle"  # fi ligature
        nfkc = UnicodeNormalizer.normalize_nfkc(text)
        assert nfkc == "file"

    def test_hangul_full_workflow(self):
        """Complete Hangul normalization workflow"""
        # Start with Jamo
        jamo = "\u1100\u1161\u11A8"
        # Compose to syllable
        nfc = UnicodeNormalizer.normalize_nfc(jamo)
        assert len(nfc) == 1
        # Decompose back
        nfd = UnicodeNormalizer.normalize_nfd(nfc)
        assert nfd == jamo

    def test_combining_marks_with_emoji(self):
        """Combining marks and emoji should coexist"""
        text = "é👋"
        nfc = UnicodeNormalizer.normalize_nfc(text)
        nfd = UnicodeNormalizer.normalize_nfd(text)
        assert len(nfc) <= len(nfd)


class TestIsNormalizedIntegration:
    """Test is_normalized integration with normalization"""

    def test_normalized_string_is_detected(self):
        """Normalized string should be detected as normalized"""
        text = "café"
        nfc = UnicodeNormalizer.normalize_nfc(text)
        assert UnicodeNormalizer.is_normalized(nfc, "NFC") is True

    def test_non_normalized_is_detected(self):
        """Non-normalized string should be detected"""
        text = "e\u0301"  # Decomposed
        assert UnicodeNormalizer.is_normalized(text, "NFC") is False

    def test_normalize_only_if_needed(self):
        """Only normalize if is_normalized returns False"""
        text = "Hello World"
        if not UnicodeNormalizer.is_normalized(text, "NFC"):
            result = UnicodeNormalizer.normalize_nfc(text)
        else:
            result = text
        assert result == "Hello World"


class TestPerformanceIntegration:
    """Test performance with realistic data"""

    def test_small_string_performance(self):
        """Small string normalization < 1ms"""
        import time
        text = "café" * 50  # ~200 bytes

        start = time.perf_counter()
        result = UnicodeNormalizer.normalize_nfc(text)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.001  # < 1ms

    def test_medium_string_performance(self):
        """Medium string normalization < 10ms"""
        import time
        text = "Hello World café 가나다 " * 500  # ~10KB

        start = time.perf_counter()
        result = UnicodeNormalizer.normalize_nfc(text)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.01  # < 10ms

    def test_is_normalized_fast_path(self):
        """is_normalized fast path < 500µs"""
        import time
        text = "Hello World" * 50  # ASCII only, ~550 bytes

        start = time.perf_counter()
        result = UnicodeNormalizer.is_normalized(text, "NFC")
        elapsed = time.perf_counter() - start

        assert result is True
        assert elapsed < 0.0005  # < 500µs
