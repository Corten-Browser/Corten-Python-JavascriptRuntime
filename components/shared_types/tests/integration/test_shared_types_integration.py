"""
Integration tests for shared_types component.

These tests verify that all components work together correctly
and that the public API is properly exposed.
"""

import pytest


def test_public_api_imports():
    """
    Given the shared_types package
    When importing from the package root
    Then all public API components are accessible
    """
    from src import TypeTag, ErrorType, SourceLocation, assert_type, format_error

    # Verify all exports are accessible
    assert TypeTag is not None
    assert ErrorType is not None
    assert SourceLocation is not None
    assert callable(assert_type)
    assert callable(format_error)


def test_end_to_end_error_formatting_workflow():
    """
    Given a complete error scenario with location
    When using all components together
    Then error is properly formatted with location
    """
    from src import ErrorType, SourceLocation, format_error

    # Create a source location
    location = SourceLocation(filename="app.js", line=42, column=10, offset=1024)

    # Format an error with location
    result = format_error(ErrorType.SYNTAX_ERROR, "Unexpected token ';'", location)

    # Verify complete formatted error
    assert "SyntaxError" in result
    assert "Unexpected token ';'" in result
    assert "app.js" in result
    assert "42" in result
    assert "10" in result


def test_end_to_end_type_assertion_workflow():
    """
    Given a value with type tag
    When using TypeTag and assert_type together
    Then type assertion works correctly
    """
    from src import TypeTag, assert_type

    # Create mock value with tag
    class MockValue:
        def __init__(self, tag):
            self.tag = tag

    # Test successful assertion
    string_value = MockValue(TypeTag.STRING)
    assert_type(string_value, TypeTag.STRING)

    # Test failed assertion
    number_value = MockValue(TypeTag.NUMBER)
    with pytest.raises(TypeError):
        assert_type(number_value, TypeTag.STRING)


def test_error_formatting_without_location():
    """
    Given an error without location
    When formatting the error
    Then basic error message is returned
    """
    from src import ErrorType, format_error

    result = format_error(ErrorType.TYPE_ERROR, "Cannot read property 'x' of undefined")

    assert "TypeError" in result
    assert "Cannot read property 'x' of undefined" in result


def test_multiple_source_locations():
    """
    Given multiple source locations
    When creating SourceLocation instances
    Then each maintains independent state
    """
    from src import SourceLocation

    loc1 = SourceLocation("file1.js", 10, 5, 100)
    loc2 = SourceLocation("file2.js", 20, 10, 200)
    loc3 = SourceLocation("file1.js", 30, 15, 300)

    assert loc1.filename == "file1.js"
    assert loc2.filename == "file2.js"
    assert loc3.filename == "file1.js"
    assert loc1.line != loc3.line


def test_all_type_tags_with_assert_type():
    """
    Given values for all TypeTag values
    When asserting types
    Then all tags work correctly
    """
    from src import TypeTag, assert_type

    class MockValue:
        def __init__(self, tag):
            self.tag = tag

    # Test all TypeTag values
    for tag in TypeTag:
        value = MockValue(tag)
        assert_type(value, tag)  # Should not raise


def test_all_error_types_formatting():
    """
    Given all ErrorType values
    When formatting errors
    Then all error types format correctly
    """
    from src import ErrorType, format_error

    error_messages = {
        ErrorType.SYNTAX_ERROR: "Invalid syntax",
        ErrorType.TYPE_ERROR: "Invalid type",
        ErrorType.REFERENCE_ERROR: "Undefined reference",
        ErrorType.RANGE_ERROR: "Out of range",
        ErrorType.ERROR: "Generic error",
    }

    for error_type, message in error_messages.items():
        result = format_error(error_type, message)
        assert isinstance(result, str)
        assert message in result


def test_immutable_source_location_integration():
    """
    Given a SourceLocation instance
    When attempting to modify it
    Then modification is prevented (immutability)
    """
    from src import SourceLocation

    location = SourceLocation("test.js", 1, 1, 0)

    # Verify immutability
    with pytest.raises(Exception):
        location.line = 999

    # Original values unchanged
    assert location.line == 1


def test_package_version_available():
    """
    Given the shared_types package
    When checking for version
    Then version is available
    """
    import src

    assert hasattr(src, "__version__")
    assert isinstance(src.__version__, str)


def test_package_exports_match_all():
    """
    Given the shared_types package __all__
    When checking exports
    Then all declared exports are importable
    """
    import src

    assert hasattr(src, "__all__")
    assert isinstance(src.__all__, list)

    # Verify all declared exports exist
    for name in src.__all__:
        assert hasattr(src, name), f"Missing export: {name}"
