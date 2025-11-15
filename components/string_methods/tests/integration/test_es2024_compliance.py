"""
Integration tests for ES2024 String compliance

Tests realistic usage scenarios combining multiple string methods
and Unicode operations together.
"""

import pytest
from components.string_methods.src.string_methods import StringMethods
from components.string_methods.src.unicode_support import UnicodeSupport


class TestRealWorldScenarios:
    """Integration tests for real-world usage scenarios"""

    def test_user_input_processing(self):
        """Test processing user input with trim and normalize"""
        # Simulate user input with extra whitespace and mixed normalization
        user_input = "  cafe\u0301  "  # Extra spaces, e with combining accent

        # Process: trim, normalize
        trimmed = StringMethods.trim_start(user_input)
        trimmed = StringMethods.trim_end(trimmed)
        normalized = UnicodeSupport.normalize(trimmed, "NFC")

        # Should normalize to composed form
        assert "café" in normalized or "café" == normalized

    def test_format_credit_card_display(self):
        """Test formatting credit card number for display"""
        # Last 4 digits, padded
        last_four = "1234"
        formatted = StringMethods.pad_start(last_four, 16, "*")

        assert formatted == "************1234"
        assert len(formatted) == 16

    def test_search_and_replace_text(self):
        """Test searching and replacing in text content"""
        text = "Hello world! World is beautiful. WORLD peace."

        # Replace all occurrences (case-sensitive)
        result = StringMethods.replace_all(text, "world", "universe")
        assert result == "Hello universe! World is beautiful. WORLD peace."

        # Match all occurrences with regex
        matches = list(StringMethods.match_all(result, r"[Uu]niverse"))
        assert len(matches) == 1

    def test_emoji_and_unicode_handling(self):
        """Test handling emoji in strings"""
        text = "Hello 😀 World 🌍"

        # Get Unicode-aware length
        length = UnicodeSupport.get_unicode_length(text)
        assert length == 15  # "Hello " (6) + "😀" (1) + " World " (7) + "🌍" (1)

        # Split into characters
        chars = UnicodeSupport.handle_surrogate_pairs(text)
        assert "😀" in chars
        assert "🌍" in chars

        # Access emoji by index
        emoji1 = StringMethods.at(text, 6)
        assert emoji1 == "😀"

    def test_template_string_processing(self):
        """Test template string with String.raw()"""
        # Simulate template literal: `C:\Users\${user}\file.txt`
        template = ["C:\\Users\\", "\\file.txt"]
        substitutions = ["john"]

        result = StringMethods.raw(template, substitutions)
        assert result == "C:\\Users\\john\\file.txt"
        assert "\\" in result  # Backslashes preserved

    def test_international_text_normalization(self):
        """Test normalizing international text"""
        # German text with umlauts
        german = "Müller"  # Could be M + ü or M + u + combining diaeresis
        normalized = UnicodeSupport.normalize(german, "NFC")

        # French text with accents
        french = "café"
        normalized_french = UnicodeSupport.normalize(french, "NFC")

        assert "ü" in normalized
        assert "é" in normalized_french

    def test_code_point_conversion(self):
        """Test converting between strings and code points"""
        # Convert emoji to code point
        emoji = "😀"
        code = StringMethods.code_point_at(emoji, 0)
        assert code == 0x1F600

        # Convert back
        reconstructed = StringMethods.from_code_point([code])
        assert reconstructed == emoji

    def test_padding_for_alignment(self):
        """Test padding strings for text alignment"""
        names = ["Alice", "Bob", "Charlie"]

        # Pad to align right
        aligned = [StringMethods.pad_start(name, 10) for name in names]
        assert all(len(name) == 10 for name in aligned)
        assert aligned[0] == "     Alice"
        assert aligned[2] == "   Charlie"

        # Pad to align left
        aligned_left = [StringMethods.pad_end(name, 10) for name in names]
        assert all(len(name) == 10 for name in aligned_left)
        assert aligned_left[0] == "Alice     "

    def test_parsing_unicode_literals(self):
        """Test parsing Unicode escape sequences"""
        # Parse JavaScript-style Unicode escapes
        escaped = "Hello \\u{1F600} World"
        parsed = UnicodeSupport.parse_unicode_escape(escaped)
        assert "😀" in parsed

        # Parse traditional \\uXXXX format
        escaped_traditional = "\\u0048\\u0065\\u006C\\u006C\\u006F"
        parsed_traditional = UnicodeSupport.parse_unicode_escape(escaped_traditional)
        assert parsed_traditional == "Hello"

    def test_extract_urls_from_text(self):
        """Test extracting URLs using matchAll"""
        text = "Visit https://example.com or http://test.org for more info"

        # Find all URLs
        url_pattern = r"https?://[^\s]+"
        urls = list(StringMethods.match_all(text, url_pattern))

        assert len(urls) == 2
        assert "example.com" in urls[0][0]
        assert "test.org" in urls[1][0]

    def test_multilingual_string_comparison(self):
        """Test normalizing strings for comparison"""
        # Same string in different normalization forms
        nfc = "\u00e9"  # é as single character
        nfd = "e\u0301"  # é as e + combining accent

        # Before normalization, they're different
        assert nfc != nfd

        # After normalization, they're the same
        nfc_normalized = UnicodeSupport.normalize(nfc, "NFC")
        nfd_normalized = UnicodeSupport.normalize(nfd, "NFC")
        assert nfc_normalized == nfd_normalized


class TestPerformance:
    """Performance tests for string operations"""

    def test_large_string_replace_all(self):
        """Test replaceAll performance on large strings"""
        import time

        # Create large string (~500KB)
        large_text = "test " * 100000

        start = time.time()
        result = StringMethods.replace_all(large_text, "test", "pass")
        elapsed = time.time() - start

        # Should complete reasonably fast (< 10ms for ~500KB)
        assert elapsed < 0.01
        assert "pass" in result
        assert "test" not in result

    def test_unicode_normalization_performance(self):
        """Test Unicode normalization performance"""
        import time

        # Create string with mixed normalization (~10KB)
        text = "café" * 2000

        start = time.time()
        result = UnicodeSupport.normalize(text, "NFC")
        elapsed = time.time() - start

        # Should complete in < 5ms (per requirements)
        assert elapsed < 0.005
        assert len(result) == len(text)

    def test_pad_performance(self):
        """Test padding performance"""
        import time

        start = time.time()
        # Pad many strings
        for i in range(10000):
            StringMethods.pad_start("test", 100, "x")
        elapsed = time.time() - start

        # Should be very fast
        assert elapsed < 0.1  # 10,000 operations in < 100ms


class TestEdgeCases:
    """Integration tests for edge cases"""

    def test_empty_string_operations(self):
        """Test operations on empty strings"""
        empty = ""

        assert StringMethods.at(empty, 0) is None
        assert StringMethods.trim_start(empty) == ""
        assert StringMethods.trim_end(empty) == ""
        assert StringMethods.pad_start(empty, 5) == "     "
        assert StringMethods.replace_all(empty, "x", "y") == ""
        # .* matches empty string once (valid behavior)
        matches = list(StringMethods.match_all(empty, r"x"))
        assert matches == []

    def test_very_long_strings(self):
        """Test operations on very long strings"""
        # Create 1MB string
        long_text = "a" * 1_000_000

        # Should handle without errors
        assert StringMethods.at(long_text, -1) == "a"
        assert len(StringMethods.trim_start(long_text)) == 1_000_000

        # Pad (shouldn't add padding if already long enough)
        padded = StringMethods.pad_start(long_text, 100)
        assert len(padded) == 1_000_000

    def test_special_characters(self):
        """Test handling special characters"""
        special = "Line1\\nLine2\\tTab\\r\\nWindows"

        # String.raw should preserve escapes
        result = StringMethods.raw([special], [])
        assert "\\n" in result
        assert "\\t" in result

    def test_mixed_unicode_operations(self):
        """Test combining multiple Unicode operations"""
        text = "  \\u{1F600} café\\u0301  "

        # Parse escapes
        parsed = UnicodeSupport.parse_unicode_escape(text)

        # Trim
        trimmed = StringMethods.trim_start(parsed)
        trimmed = StringMethods.trim_end(trimmed)

        # Normalize
        normalized = UnicodeSupport.normalize(trimmed, "NFC")

        # Should have emoji and normalized text
        assert "😀" in normalized
        assert "café" in normalized
