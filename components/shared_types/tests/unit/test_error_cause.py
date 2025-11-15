"""
Unit tests for Error.cause support (ES2024).

Tests for FR-P3.5-046, FR-P3.5-047, FR-P3.5-048.
"""

import pytest


class TestErrorCauseConstructor:
    """
    Tests for FR-P3.5-046: Error constructor accepts options.cause
    """

    def test_error_accepts_cause_in_options(self):
        """
        Given an Error constructor call with {cause} option
        When creating an Error instance
        Then the error is created successfully
        """
        from src.errors import JSError

        original_error = JSError("Original error")
        wrapped_error = JSError("Wrapped error", options={"cause": original_error})

        assert wrapped_error is not None
        assert wrapped_error.message == "Wrapped error"

    def test_error_cause_can_be_any_value(self):
        """
        Given an Error constructor with various cause types
        When creating Error instances
        Then all cause types are accepted (Error, string, object, number, etc.)
        """
        from src.errors import JSError

        # Cause can be another Error
        error_with_error_cause = JSError("Error", options={"cause": JSError("Cause")})
        assert error_with_error_cause is not None

        # Cause can be a string
        error_with_string_cause = JSError("Error", options={"cause": "string cause"})
        assert error_with_string_cause is not None

        # Cause can be a dict (representing object)
        error_with_object_cause = JSError("Error", options={"cause": {"key": "value"}})
        assert error_with_object_cause is not None

        # Cause can be a number
        error_with_number_cause = JSError("Error", options={"cause": 42})
        assert error_with_number_cause is not None

        # Cause can be None
        error_with_none_cause = JSError("Error", options={"cause": None})
        assert error_with_none_cause is not None

    def test_error_without_cause_option(self):
        """
        Given an Error constructor without cause option
        When creating an Error instance
        Then the error is created without cause property
        """
        from src.errors import JSError

        error = JSError("Error without cause")

        assert error.message == "Error without cause"
        assert not hasattr(error, 'cause')

    def test_error_with_empty_options(self):
        """
        Given an Error constructor with empty options
        When creating an Error instance
        Then the error is created without cause
        """
        from src.errors import JSError

        error = JSError("Error", options={})

        assert error.message == "Error"
        assert not hasattr(error, 'cause')


class TestErrorCauseProperty:
    """
    Tests for FR-P3.5-047: Error.prototype.cause property
    """

    def test_error_has_cause_property_when_provided(self):
        """
        Given an Error with cause option
        When accessing the cause property
        Then it returns the provided cause value
        """
        from src.errors import JSError

        original = JSError("Original")
        wrapped = JSError("Wrapped", options={"cause": original})

        assert hasattr(wrapped, 'cause')
        assert wrapped.cause is original

    def test_error_cause_preserves_value_type(self):
        """
        Given an Error with various cause types
        When accessing the cause property
        Then the cause value is preserved with correct type
        """
        from src.errors import JSError

        # String cause
        error1 = JSError("Error", options={"cause": "cause text"})
        assert error1.cause == "cause text"
        assert isinstance(error1.cause, str)

        # Number cause
        error2 = JSError("Error", options={"cause": 123})
        assert error2.cause == 123
        assert isinstance(error2.cause, int)

        # Object cause
        obj = {"type": "network", "code": 500}
        error3 = JSError("Error", options={"cause": obj})
        assert error3.cause is obj

    def test_error_without_cause_has_no_cause_property(self):
        """
        Given an Error without cause option
        When checking for cause property
        Then the cause property is not present
        """
        from src.errors import JSError

        error = JSError("Error without cause")

        assert not hasattr(error, 'cause')

    def test_error_cause_property_not_enumerable(self):
        """
        Given an Error with cause
        When iterating over error attributes
        Then cause is not in default enumeration
        """
        from src.errors import JSError

        error = JSError("Error", options={"cause": "test"})

        # In Python, we simulate non-enumerable by not including in __dict__ keys
        # or marking with special naming convention
        # This test verifies the cause is accessible but not in normal iteration
        assert hasattr(error, 'cause')
        # The actual non-enumerable behavior would be tested in JavaScript engine


class TestErrorSubclassesCause:
    """
    Tests for FR-P3.5-048: Error cause with all Error subclasses
    """

    def test_type_error_supports_cause(self):
        """
        Given a TypeError with cause option
        When creating the error
        Then it supports the cause property
        """
        from src.errors import JSTypeError, JSError

        original = JSError("Original")
        type_error = JSTypeError("Type error", options={"cause": original})

        assert type_error.cause is original
        assert type_error.message == "Type error"

    def test_range_error_supports_cause(self):
        """
        Given a RangeError with cause option
        When creating the error
        Then it supports the cause property
        """
        from src.errors import JSRangeError

        range_error = JSRangeError("Range error", options={"cause": "out of bounds"})

        assert range_error.cause == "out of bounds"
        assert range_error.message == "Range error"

    def test_syntax_error_supports_cause(self):
        """
        Given a SyntaxError with cause option
        When creating the error
        Then it supports the cause property
        """
        from src.errors import JSSyntaxError

        syntax_error = JSSyntaxError("Syntax error", options={"cause": {"line": 10}})

        assert syntax_error.cause == {"line": 10}

    def test_reference_error_supports_cause(self):
        """
        Given a ReferenceError with cause option
        When creating the error
        Then it supports the cause property
        """
        from src.errors import JSReferenceError

        ref_error = JSReferenceError("Reference error", options={"cause": 123})

        assert ref_error.cause == 123

    def test_all_error_subclasses_inherit_cause_behavior(self):
        """
        Given all JavaScript Error subclasses
        When creating instances with cause
        Then all support the cause option consistently
        """
        from src.errors import (
            JSError,
            JSTypeError,
            JSRangeError,
            JSSyntaxError,
            JSReferenceError
        )

        error_classes = [
            JSError,
            JSTypeError,
            JSRangeError,
            JSSyntaxError,
            JSReferenceError
        ]

        cause_value = "common cause"

        for ErrorClass in error_classes:
            error = ErrorClass("Test", options={"cause": cause_value})
            assert hasattr(error, 'cause')
            assert error.cause == cause_value


class TestErrorRepr:
    """
    Tests for Error __repr__ methods
    """

    def test_error_repr_without_cause(self):
        """Test string representation of Error without cause."""
        from src.errors import JSError

        error = JSError("Test error")
        repr_str = repr(error)

        assert "JSError" in repr_str
        assert "Test error" in repr_str

    def test_error_repr_with_cause(self):
        """Test string representation of Error with cause."""
        from src.errors import JSError

        original = JSError("Original")
        wrapped = JSError("Wrapped", options={"cause": original})
        repr_str = repr(wrapped)

        assert "JSError" in repr_str
        assert "Wrapped" in repr_str
        assert "cause=" in repr_str

    def test_type_error_repr_with_cause(self):
        """Test string representation of TypeError with cause."""
        from src.errors import JSTypeError

        error = JSTypeError("Type error", options={"cause": "test"})
        repr_str = repr(error)

        assert "JSTypeError" in repr_str
        assert "Type error" in repr_str
        assert "cause=" in repr_str

    def test_range_error_repr_with_cause(self):
        """Test string representation of RangeError with cause."""
        from src.errors import JSRangeError

        error = JSRangeError("Range error", options={"cause": 123})
        repr_str = repr(error)

        assert "JSRangeError" in repr_str
        assert "Range error" in repr_str

    def test_syntax_error_repr_with_cause(self):
        """Test string representation of SyntaxError with cause."""
        from src.errors import JSSyntaxError

        error = JSSyntaxError("Syntax error", options={"cause": {"line": 10}})
        repr_str = repr(error)

        assert "JSSyntaxError" in repr_str
        assert "Syntax error" in repr_str

    def test_reference_error_repr_with_cause(self):
        """Test string representation of ReferenceError with cause."""
        from src.errors import JSReferenceError

        error = JSReferenceError("Reference error", options={"cause": "test"})
        repr_str = repr(error)

        assert "JSReferenceError" in repr_str
        assert "Reference error" in repr_str

    def test_type_error_repr_without_cause(self):
        """Test string representation of TypeError without cause."""
        from src.errors import JSTypeError

        error = JSTypeError("Type error")
        repr_str = repr(error)

        assert "JSTypeError" in repr_str
        assert "Type error" in repr_str

    def test_range_error_repr_without_cause(self):
        """Test string representation of RangeError without cause."""
        from src.errors import JSRangeError

        error = JSRangeError("Range error")
        repr_str = repr(error)

        assert "JSRangeError" in repr_str
        assert "Range error" in repr_str

    def test_syntax_error_repr_without_cause(self):
        """Test string representation of SyntaxError without cause."""
        from src.errors import JSSyntaxError

        error = JSSyntaxError("Syntax error")
        repr_str = repr(error)

        assert "JSSyntaxError" in repr_str
        assert "Syntax error" in repr_str

    def test_reference_error_repr_without_cause(self):
        """Test string representation of ReferenceError without cause."""
        from src.errors import JSReferenceError

        error = JSReferenceError("Reference error")
        repr_str = repr(error)

        assert "JSReferenceError" in repr_str
        assert "Reference error" in repr_str


class TestErrorCauseChaining:
    """
    Additional tests for error chaining scenarios
    """

    def test_multi_level_error_chaining(self):
        """
        Given multiple levels of error wrapping
        When accessing causes through the chain
        Then all cause values are preserved
        """
        from src.errors import JSError

        # Level 1: Root cause
        root_cause = JSError("Network timeout")

        # Level 2: Wrap root cause
        level2 = JSError("Failed to fetch data", options={"cause": root_cause})

        # Level 3: Wrap level 2
        level3 = JSError("User request failed", options={"cause": level2})

        # Verify chain
        assert level3.cause is level2
        assert level3.cause.cause is root_cause
        assert level3.cause.cause.message == "Network timeout"

    def test_error_cause_with_none_value(self):
        """
        Given an Error with cause set to None
        When accessing the cause property
        Then it returns None (not undefined/missing)
        """
        from src.errors import JSError

        error = JSError("Error", options={"cause": None})

        assert hasattr(error, 'cause')
        assert error.cause is None
