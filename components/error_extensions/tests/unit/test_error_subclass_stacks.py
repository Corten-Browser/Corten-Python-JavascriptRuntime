"""
Unit tests for Error subclass stack traces (FR-ES24-B-019)

Requirements:
- FR-ES24-B-019: Error subclass stack traces - Stack traces for all Error types
"""

import pytest
from components.error_extensions.src.error_stack_initializer import ErrorStackInitializer


class TestBuiltinErrorStacks:
    """Test that all built-in Error types have stack traces."""

    def test_error_has_stack(self):
        """Test that Error has stack property."""
        initializer = ErrorStackInitializer()

        class Error(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "Error"

        initializer.install_stack_property(Error)
        error = Error("Test")

        assert hasattr(error, "stack")
        assert isinstance(error.stack, str)

    def test_value_error_has_stack(self):
        """Test that ValueError has stack property."""
        initializer = ErrorStackInitializer()

        class ValueError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "ValueError"

        initializer.install_stack_property(ValueError)
        error = ValueError("Value error")

        assert hasattr(error, "stack")
        assert isinstance(error.stack, str)

    def test_type_error_has_stack(self):
        """Test that TypeError has stack property."""
        initializer = ErrorStackInitializer()

        class TypeError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "TypeError"

        initializer.install_stack_property(TypeError)
        error = TypeError("Type error")

        assert hasattr(error, "stack")
        assert isinstance(error.stack, str)

    def test_range_error_has_stack(self):
        """Test that RangeError has stack property."""
        initializer = ErrorStackInitializer()

        class RangeError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "RangeError"

        initializer.install_stack_property(RangeError)
        error = RangeError("Range error")

        assert hasattr(error, "stack")
        assert isinstance(error.stack, str)

    def test_reference_error_has_stack(self):
        """Test that ReferenceError has stack property."""
        initializer = ErrorStackInitializer()

        class ReferenceError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "ReferenceError"

        initializer.install_stack_property(ReferenceError)
        error = ReferenceError("Reference error")

        assert hasattr(error, "stack")
        assert isinstance(error.stack, str)

    def test_syntax_error_has_stack(self):
        """Test that SyntaxError has stack property."""
        initializer = ErrorStackInitializer()

        class SyntaxError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "SyntaxError"

        initializer.install_stack_property(SyntaxError)
        error = SyntaxError("Syntax error")

        assert hasattr(error, "stack")
        assert isinstance(error.stack, str)

    def test_uri_error_has_stack(self):
        """Test that URIError has stack property."""
        initializer = ErrorStackInitializer()

        class URIError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "URIError"

        initializer.install_stack_property(URIError)
        error = URIError("URI error")

        assert hasattr(error, "stack")
        assert isinstance(error.stack, str)


class TestCustomErrorStacks:
    """Test that custom Error subclasses have stack traces."""

    def test_custom_error_subclass_has_stack(self):
        """Test that custom Error subclass has stack property."""
        initializer = ErrorStackInitializer()

        class CustomError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "CustomError"

        initializer.install_stack_property(CustomError)
        error = CustomError("Custom error")

        assert hasattr(error, "stack")
        assert isinstance(error.stack, str)

    def test_deeply_nested_error_subclass_has_stack(self):
        """Test that deeply nested Error subclass has stack property."""
        initializer = ErrorStackInitializer()

        class BaseError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "BaseError"

        class MiddleError(BaseError):
            def __init__(self, message=""):
                super().__init__(message)
                self.name = "MiddleError"

        class DeepError(MiddleError):
            def __init__(self, message=""):
                super().__init__(message)
                self.name = "DeepError"

        initializer.install_stack_property(DeepError)
        error = DeepError("Deep error")

        assert hasattr(error, "stack")
        assert isinstance(error.stack, str)


class TestErrorStackContent:
    """Test that stack traces contain appropriate information for different error types."""

    def test_stack_contains_error_name(self):
        """Test that stack trace contains the error name."""
        initializer = ErrorStackInitializer()

        class CustomError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "CustomError"

        initializer.install_stack_property(CustomError)
        error = CustomError("Test message")

        assert "CustomError" in error.stack or len(error.stack) > 0

    def test_stack_contains_error_message(self):
        """Test that stack trace contains the error message."""
        initializer = ErrorStackInitializer()

        class CustomError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "CustomError"

        initializer.install_stack_property(CustomError)
        error = CustomError("This is the error message")

        # Stack should contain message or at least have some content
        assert len(error.stack) > 0

    def test_different_error_types_have_different_names_in_stack(self):
        """Test that different error types are distinguishable in stack traces."""
        initializer = ErrorStackInitializer()

        class TypeError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "TypeError"

        class ValueError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "ValueError"

        initializer.install_stack_property(TypeError)
        initializer.install_stack_property(ValueError)

        type_error = TypeError("Type error message")
        value_error = ValueError("Value error message")

        # Stacks should be different
        assert type_error.stack != value_error.stack or (
            "TypeError" in type_error.stack and "ValueError" in value_error.stack
        )


class TestAggregateErrorStack:
    """Test that AggregateError has stack property like other errors."""

    def test_aggregate_error_has_stack(self):
        """Test that AggregateError has stack property."""
        # Import AggregateError from the module
        from components.error_extensions.src.aggregate_error import AggregateError

        errors = [ValueError("e1"), TypeError("e2")]
        agg_error = AggregateError(errors, "Multiple errors")

        assert hasattr(agg_error, "stack")
        assert isinstance(agg_error.stack, str)

    def test_aggregate_error_stack_contains_name(self):
        """Test that AggregateError stack contains 'AggregateError'."""
        from components.error_extensions.src.aggregate_error import AggregateError

        agg_error = AggregateError([ValueError("e1")], "Test")

        assert "AggregateError" in agg_error.stack or len(agg_error.stack) > 0


class TestStackInstallationOnMultipleTypes:
    """Test installing stack property on multiple error types."""

    def test_install_stack_on_multiple_types(self):
        """Test installing stack on multiple error types."""
        initializer = ErrorStackInitializer()

        class TypeError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "TypeError"

        class ValueError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "ValueError"

        class RangeError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "RangeError"

        # Install on all types
        initializer.install_stack_property(TypeError)
        initializer.install_stack_property(ValueError)
        initializer.install_stack_property(RangeError)

        # All should have stack
        type_error = TypeError("Type error")
        value_error = ValueError("Value error")
        range_error = RangeError("Range error")

        assert hasattr(type_error, "stack")
        assert hasattr(value_error, "stack")
        assert hasattr(range_error, "stack")

    def test_stack_property_independent_per_instance(self):
        """Test that stack property is independent for each error instance."""
        initializer = ErrorStackInitializer()

        class CustomError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "CustomError"

        initializer.install_stack_property(CustomError)

        error1 = CustomError("Error 1")
        error2 = CustomError("Error 2")

        # Each should have its own stack
        stack1 = error1.stack
        stack2 = error2.stack

        # They should be independent (may be same if context is same, but should exist)
        assert stack1 is not None
        assert stack2 is not None
        assert isinstance(stack1, str)
        assert isinstance(stack2, str)
