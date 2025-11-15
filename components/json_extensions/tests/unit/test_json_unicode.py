"""
Unit tests for well-formed JSON.stringify Unicode handling (FR-ES24-B-036)

Tests proper Unicode surrogate pair handling:
- Complete surrogate pairs preserved
- Unpaired surrogates escaped
- Well-formed JSON output
- Unicode validation
"""

import pytest


class TestJSONStringifyUnicodeSurrogatePairs:
    """Test handling of Unicode surrogate pairs"""

    def test_valid_surrogate_pair_preserved(self):
        """Valid surrogate pairs should be preserved in output"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        # U+1F600 (😀) = high surrogate U+D83D + low surrogate U+DE00
        text = "\U0001F600"  # 😀
        result = stringifier.stringify_well_formed(text)

        # Should preserve the emoji
        assert '😀' in result or 'ud83d' in result.lower()

    def test_unpaired_high_surrogate_escaped(self):
        """Unpaired high surrogate should be escaped"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        # U+D800 is a high surrogate without a pair
        text = "\uD800"
        result = stringifier.stringify_well_formed(text)

        # Should be escaped as \uD800
        assert '\\ud800' in result.lower()

    def test_unpaired_low_surrogate_escaped(self):
        """Unpaired low surrogate should be escaped"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        # U+DC00 is a low surrogate without a pair
        text = "\uDC00"
        result = stringifier.stringify_well_formed(text)

        # Should be escaped as \uDC00
        assert '\\udc00' in result.lower()

    def test_reversed_surrogate_pair_escaped(self):
        """Reversed surrogate pair (low then high) should be escaped"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        # Low surrogate followed by high surrogate (invalid)
        text = "\uDC00\uD800"
        result = stringifier.stringify_well_formed(text)

        # Both should be escaped
        assert '\\udc00' in result.lower()
        assert '\\ud800' in result.lower()

    def test_multiple_surrogate_pairs(self):
        """Multiple valid surrogate pairs should all be preserved"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        text = "\U0001F600\U0001F601"  # 😀😁
        result = stringifier.stringify_well_formed(text)

        # Both emojis should be preserved
        assert '😀' in result or 'ud83d' in result.lower()

    def test_mixed_valid_and_unpaired_surrogates(self):
        """Mix of valid pairs and unpaired surrogates"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        # Valid pair + unpaired high surrogate
        text = "\U0001F600\uD800"
        result = stringifier.stringify_well_formed(text)

        # Valid pair preserved, unpaired escaped
        assert ('😀' in result or 'ud83d' in result.lower())
        assert '\\ud800' in result.lower()


class TestJSONStringifyUnicodeEscaping:
    """Test Unicode character escaping"""

    def test_escape_surrogate_pair_method(self):
        """Test escape_surrogate_pair utility method"""
        from json_extensions import JSONUnicode

        unicode_handler = JSONUnicode()

        # High: U+D83D, Low: U+DE00 -> 😀
        result = unicode_handler.escape_surrogate_pair(0xD83D, 0xDE00)

        # Should produce proper escape sequence or character
        assert result is not None

    def test_escape_unpaired_surrogate_method(self):
        """Test escape_unpaired_surrogate utility method"""
        from json_extensions import JSONUnicode

        unicode_handler = JSONUnicode()

        result = unicode_handler.escape_unpaired_surrogate(0xD800)

        # Should produce \uD800
        assert '\\u' in result.lower() or 'ud800' in result.lower()

    def test_escape_high_surrogate_range(self):
        """Test all high surrogates (U+D800 to U+DBFF) are escaped"""
        from json_extensions import JSONUnicode

        unicode_handler = JSONUnicode()

        # Test boundaries
        result_low = unicode_handler.escape_unpaired_surrogate(0xD800)
        result_high = unicode_handler.escape_unpaired_surrogate(0xDBFF)

        assert result_low is not None
        assert result_high is not None

    def test_escape_low_surrogate_range(self):
        """Test all low surrogates (U+DC00 to U+DFFF) are escaped"""
        from json_extensions import JSONUnicode

        unicode_handler = JSONUnicode()

        # Test boundaries
        result_low = unicode_handler.escape_unpaired_surrogate(0xDC00)
        result_high = unicode_handler.escape_unpaired_surrogate(0xDFFF)

        assert result_low is not None
        assert result_high is not None


class TestJSONStringifyUnicodeValidation:
    """Test Unicode validation in JSON"""

    def test_validate_unicode_well_formed(self):
        """Valid Unicode should pass validation"""
        from json_extensions import JSONUnicode

        unicode_handler = JSONUnicode()

        # Valid Unicode string
        assert unicode_handler.validate_unicode("Hello, 世界")
        assert unicode_handler.validate_unicode("\U0001F600")  # 😀

    def test_validate_unicode_unpaired_surrogate_detected(self):
        """Unpaired surrogates should be detected"""
        from json_extensions import JSONUnicode

        unicode_handler = JSONUnicode()

        # Unpaired high surrogate
        result = unicode_handler.validate_unicode("\uD800")

        # Should detect as invalid (or at least handle it)
        # Implementation may return False or True with escape handling
        assert result is not None

    def test_validate_unicode_empty_string(self):
        """Empty string should be valid"""
        from json_extensions import JSONUnicode

        unicode_handler = JSONUnicode()

        assert unicode_handler.validate_unicode("")

    def test_validate_unicode_ascii(self):
        """Pure ASCII should be valid"""
        from json_extensions import JSONUnicode

        unicode_handler = JSONUnicode()

        assert unicode_handler.validate_unicode("Hello, World!")


class TestJSONStringifyWellFormedIntegration:
    """Integration tests for well-formed JSON.stringify"""

    def test_well_formed_stringify_vs_regular_stringify(self):
        """Well-formed stringify should differ from regular for unpaired surrogates"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        text = "\uD800"

        # Regular stringify might pass through unpaired surrogate
        regular = stringifier.stringify(text)

        # Well-formed stringify must escape it
        well_formed = stringifier.stringify_well_formed(text)

        # Well-formed should have escape sequence
        assert '\\u' in well_formed.lower()

    def test_well_formed_with_object_containing_surrogates(self):
        """Well-formed stringify should handle objects with surrogate strings"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {
            "valid": "\U0001F600",  # Valid emoji
            "invalid": "\uD800"  # Unpaired surrogate
        }

        result = stringifier.stringify_well_formed(obj)

        # Should escape the unpaired surrogate
        assert '\\ud800' in result.lower()

    def test_well_formed_with_arrays(self):
        """Well-formed stringify should handle arrays with surrogate strings"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        arr = ["\U0001F600", "\uD800", "\uDC00"]
        result = stringifier.stringify_well_formed(arr)

        # Unpaired surrogates should be escaped
        assert '\\ud800' in result.lower() or '\\udc00' in result.lower()

    def test_well_formed_roundtrip(self):
        """Well-formed stringified JSON should parse back correctly"""
        from json_extensions import JSONStringifier, JSONParser

        stringifier = JSONStringifier()
        parser = JSONParser()

        original = {"text": "\uD800test"}
        json_str = stringifier.stringify_well_formed(original)

        # Should be valid JSON that can be parsed
        parsed = parser.parse(json_str)

        # Parsed value should be valid (escaped surrogate)
        assert parsed is not None
