"""
Unit tests for utility functions.

Following TDD: These tests are written FIRST before implementation.
"""

import pytest


def test_assert_type_exists():
    """Test that assert_type function can be imported."""
    from src.utils import assert_type

    assert callable(assert_type)


def test_format_error_exists():
    """Test that format_error function can be imported."""
    from src.utils import format_error

    assert callable(format_error)


class TestAssertType:
    """Test suite for assert_type utility function."""

    def test_assert_type_passes_with_correct_type(self):
        """
        Given a value with correct type tag
        When assert_type is called
        Then no exception is raised
        """
        from src.utils import assert_type
        from src.types import TypeTag

        # Mock value with tag attribute
        class MockValue:
            def __init__(self, tag):
                self.tag = tag

        value = MockValue(TypeTag.STRING)
        # Should not raise
        assert_type(value, TypeTag.STRING)

    def test_assert_type_raises_with_incorrect_type(self):
        """
        Given a value with incorrect type tag
        When assert_type is called
        Then TypeError is raised
        """
        from src.utils import assert_type
        from src.types import TypeTag

        class MockValue:
            def __init__(self, tag):
                self.tag = tag

        value = MockValue(TypeTag.NUMBER)

        with pytest.raises(TypeError):
            assert_type(value, TypeTag.STRING)

    def test_assert_type_uses_custom_message(self):
        """
        Given a value with incorrect type and custom message
        When assert_type is called
        Then TypeError contains the custom message
        """
        from src.utils import assert_type
        from src.types import TypeTag

        class MockValue:
            def __init__(self, tag):
                self.tag = tag

        value = MockValue(TypeTag.NUMBER)
        custom_message = "Expected string value"

        with pytest.raises(TypeError, match=custom_message):
            assert_type(value, TypeTag.STRING, custom_message)

    def test_assert_type_with_default_message(self):
        """
        Given a value with incorrect type and no custom message
        When assert_type is called
        Then TypeError contains a default message
        """
        from src.utils import assert_type
        from src.types import TypeTag

        class MockValue:
            def __init__(self, tag):
                self.tag = tag

        value = MockValue(TypeTag.NUMBER)

        with pytest.raises(TypeError):
            assert_type(value, TypeTag.STRING)

    def test_assert_type_with_all_type_tags(self):
        """Test assert_type works with all TypeTag values."""
        from src.utils import assert_type
        from src.types import TypeTag

        class MockValue:
            def __init__(self, tag):
                self.tag = tag

        for tag in TypeTag:
            value = MockValue(tag)
            # Should not raise when tag matches
            assert_type(value, tag)

    def test_assert_type_with_value_without_tag_attribute(self):
        """
        Given a value without a tag attribute
        When assert_type is called
        Then appropriate error is raised
        """
        from src.utils import assert_type
        from src.types import TypeTag

        value = "plain string"  # No tag attribute

        with pytest.raises((TypeError, AttributeError)):
            assert_type(value, TypeTag.STRING)


class TestFormatError:
    """Test suite for format_error utility function."""

    def test_format_error_returns_string(self):
        """
        Given error type and message
        When format_error is called
        Then a string is returned
        """
        from src.utils import format_error
        from src.types import ErrorType

        result = format_error(ErrorType.SYNTAX_ERROR, "Unexpected token")
        assert isinstance(result, str)

    def test_format_error_includes_error_type(self):
        """
        Given error type and message
        When format_error is called
        Then result includes the error type
        """
        from src.utils import format_error
        from src.types import ErrorType

        result = format_error(ErrorType.SYNTAX_ERROR, "Unexpected token")
        assert "SyntaxError" in result or "SYNTAX_ERROR" in result

    def test_format_error_includes_message(self):
        """
        Given error type and message
        When format_error is called
        Then result includes the message
        """
        from src.utils import format_error
        from src.types import ErrorType

        message = "Unexpected token ';'"
        result = format_error(ErrorType.SYNTAX_ERROR, message)
        assert message in result

    def test_format_error_with_location(self):
        """
        Given error type, message, and location
        When format_error is called
        Then result includes location information
        """
        from src.utils import format_error
        from src.types import ErrorType
        from src.location import SourceLocation

        location = SourceLocation(filename="test.js", line=10, column=5, offset=128)
        result = format_error(ErrorType.SYNTAX_ERROR, "Unexpected token", location)

        assert "test.js" in result
        assert "10" in result
        assert "5" in result

    def test_format_error_without_location(self):
        """
        Given error type and message without location
        When format_error is called
        Then result doesn't require location information
        """
        from src.utils import format_error
        from src.types import ErrorType

        result = format_error(ErrorType.TYPE_ERROR, "Cannot read property")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_format_error_with_all_error_types(self):
        """Test format_error works with all ErrorType values."""
        from src.utils import format_error
        from src.types import ErrorType

        for error_type in ErrorType:
            result = format_error(error_type, "Test message")
            assert isinstance(result, str)
            assert len(result) > 0

    def test_format_error_with_type_error(self):
        """Test format_error with TYPE_ERROR."""
        from src.utils import format_error
        from src.types import ErrorType

        result = format_error(ErrorType.TYPE_ERROR, "Cannot call undefined")
        assert "TypeError" in result or "TYPE_ERROR" in result

    def test_format_error_with_reference_error(self):
        """Test format_error with REFERENCE_ERROR."""
        from src.utils import format_error
        from src.types import ErrorType

        result = format_error(ErrorType.REFERENCE_ERROR, "x is not defined")
        assert "ReferenceError" in result or "REFERENCE_ERROR" in result

    def test_format_error_with_range_error(self):
        """Test format_error with RANGE_ERROR."""
        from src.utils import format_error
        from src.types import ErrorType

        result = format_error(ErrorType.RANGE_ERROR, "Invalid array length")
        assert "RangeError" in result or "RANGE_ERROR" in result

    def test_format_error_with_generic_error(self):
        """Test format_error with generic ERROR."""
        from src.utils import format_error
        from src.types import ErrorType

        result = format_error(ErrorType.ERROR, "Something went wrong")
        assert "Error" in result or "ERROR" in result

    def test_format_error_format_matches_javascript_style(self):
        """
        Given error with location
        When format_error is called
        Then result follows JavaScript error format
        (e.g., "ErrorType: message at filename:line:column")
        """
        from src.utils import format_error
        from src.types import ErrorType
        from src.location import SourceLocation

        location = SourceLocation(filename="app.js", line=25, column=10, offset=500)
        result = format_error(ErrorType.SYNTAX_ERROR, "Unexpected token ';'", location)

        # Should contain error type, message, and location
        assert "app.js" in result
        assert "25" in result
        assert "10" in result
        assert "Unexpected token ';'" in result
