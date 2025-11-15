"""Basic JSON functionality tests for coverage"""

import pytest


class TestJSONBasicFunctionality:
    """Test basic JSON operations"""

    def test_stringify_primitives(self):
        """Test stringifying primitive values"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        assert stringifier.stringify(42) == '42'
        assert stringifier.stringify("hello") == '"hello"'
        assert stringifier.stringify(True) == 'true'
        assert stringifier.stringify(False) == 'false'
        assert stringifier.stringify(None) == 'null'

    def test_stringify_simple_object(self):
        """Test stringifying simple object"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()
        result = stringifier.stringify({"a": 1})

        assert '"a"' in result
        assert '1' in result

    def test_stringify_simple_array(self):
        """Test stringifying simple array"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()
        result = stringifier.stringify([1, 2, 3])

        assert '[1' in result or '[1,' in result

    def test_parse_primitives(self):
        """Test parsing primitive values"""
        from json_extensions import JSONParser

        parser = JSONParser()

        assert parser.parse('42') == 42
        assert parser.parse('"hello"') == "hello"
        assert parser.parse('true') is True
        assert parser.parse('false') is False
        assert parser.parse('null') is None

    def test_unicode_escape_valid_pair_chars(self):
        """Test escaping valid surrogate pair"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()

        # Valid high and low surrogates
        result = handler.escape_surrogate_pair(0xD83D, 0xDE00)

        # Should produce valid character or escape
        assert result is not None
        assert len(result) > 0

    def test_unicode_validate_normal_text(self):
        """Validate normal text"""
        from json_extensions import JSONUnicode

        handler = JSONUnicode()

        assert handler.validate_unicode("Hello, World!") is True
        assert handler.validate_unicode("") is True
        assert handler.validate_unicode("测试") is True
