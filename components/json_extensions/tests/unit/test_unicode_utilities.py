"""Additional tests for Unicode utility methods to improve coverage"""

import pytest


class TestJSONUnicodeUtilities:
    """Test standalone Unicode utility methods"""

    def test_has_unpaired_surrogates_detects_high(self):
        """Detect unpaired high surrogate"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()
        text = "\uD800test"  # Unpaired high surrogate
        assert handler.has_unpaired_surrogates(text) is True

    def test_has_unpaired_surrogates_detects_low(self):
        """Detect unpaired low surrogate"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()
        text = "test\uDC00"  # Unpaired low surrogate
        assert handler.has_unpaired_surrogates(text) is True

    def test_has_unpaired_surrogates_valid_pair(self):
        """Valid pair should not be detected as unpaired"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()
        text = "\U0001F600"  # Valid emoji (surrogate pair)
        assert handler.has_unpaired_surrogates(text) is False

    def test_has_unpaired_surrogates_normal_text(self):
        """Normal text should not have unpaired surrogates"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()
        assert handler.has_unpaired_surrogates("hello world") is False

    def test_fix_unpaired_surrogates(self):
        """Fix unpaired surrogates by escaping"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()
        text = "\uD800test"
        fixed = handler.fix_unpaired_surrogates(text)

        # Should escape the unpaired surrogate
        assert "\\u" in fixed.lower()

    def test_fix_unpaired_surrogates_preserves_valid_pairs(self):
        """Fix should preserve valid surrogate pairs"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()
        text = "\U0001F600test"  # Valid emoji
        fixed = handler.fix_unpaired_surrogates(text)

        # Should preserve the valid pair
        assert "\U0001F600" in fixed or "\\ud83d" in fixed.lower()

    def test_fix_unpaired_surrogates_multiple(self):
        """Fix multiple unpaired surrogates"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()
        text = "\uD800\uDC00\uD801"  # Valid pair + unpaired high
        fixed = handler.fix_unpaired_surrogates(text)

        # Should have at least one escape sequence for the unpaired one
        assert "\\u" in fixed.lower()
