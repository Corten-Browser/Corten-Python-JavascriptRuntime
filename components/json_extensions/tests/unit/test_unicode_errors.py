"""Test Unicode error handling for coverage"""

import pytest


class TestUnicodeErrorHandling:
    """Test error cases in Unicode handling"""

    def test_escape_surrogate_pair_invalid_high(self):
        """Test error when high surrogate is invalid"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()

        # Invalid high surrogate (not in range 0xD800-0xDBFF)
        with pytest.raises(ValueError, match="Invalid high surrogate"):
            handler.escape_surrogate_pair(0xD7FF, 0xDC00)  # Too low

    def test_escape_surrogate_pair_invalid_low(self):
        """Test error when low surrogate is invalid"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()

        # Invalid low surrogate (not in range 0xDC00-0xDFFF)
        with pytest.raises(ValueError, match="Invalid low surrogate"):
            handler.escape_surrogate_pair(0xD800, 0xDBFF)  # Not a low surrogate

    def test_escape_unpaired_surrogate_invalid(self):
        """Test error when code point is not a surrogate"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()

        # Not a surrogate at all
        with pytest.raises(ValueError, match="Not a surrogate"):
            handler.escape_unpaired_surrogate(0x0041)  # 'A'

    def test_validate_unicode_non_string(self):
        """Test validation with non-string input"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()

        # Non-string input
        result = handler.validate_unicode(123)
        assert result is False

    def test_validate_unicode_with_exception(self):
        """Test validation handles exceptions"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()

        # Test with something that might raise an exception
        result = handler.validate_unicode(None)
        assert result is False
