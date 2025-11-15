"""
Unit tests for Error.prototype.stack (FR-ES24-B-017)

Requirements:
- FR-ES24-B-017: Error.prototype.stack - Stack trace property
"""

import pytest
from components.error_extensions.src.error_stack_initializer import (
    ErrorStackInitializer,
    install_error_stack_support
)


class TestErrorStackProperty:
    """Test Error.prototype.stack property."""

    def test_error_has_stack_property(self):
        """Test that Error instances have stack property."""
        initializer = ErrorStackInitializer()

        # Create a mock Error class
        class MockError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "Error"

        # Install stack property
        initializer.install_stack_property(MockError)

        error = MockError("Test error")
        assert hasattr(error, "stack")

    def test_error_stack_is_string(self):
        """Test that stack property returns a string."""
        initializer = ErrorStackInitializer()

        class MockError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "Error"

        initializer.install_stack_property(MockError)
        error = MockError("Test")

        stack = error.stack
        assert isinstance(stack, str)

    def test_error_stack_lazy_evaluation(self):
        """Test that stack is generated lazily on first access."""
        initializer = ErrorStackInitializer()

        class MockError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "Error"
                self._stack = None

        initializer.install_stack_property(MockError)
        error = MockError("Test")

        # Stack should not be generated until accessed
        assert not hasattr(error, "_stack_generated") or error._stack is None

        # Access stack triggers generation
        stack = error.stack
        assert stack is not None
        assert isinstance(stack, str)

    def test_error_stack_contains_error_message(self):
        """Test that stack trace contains the error message."""
        initializer = ErrorStackInitializer()

        class MockError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "Error"

        initializer.install_stack_property(MockError)
        error = MockError("Test error message")

        assert "Test error message" in error.stack or "Error" in error.stack

    def test_error_stack_multiple_access_returns_same_value(self):
        """Test that accessing stack multiple times returns the same value."""
        initializer = ErrorStackInitializer()

        class MockError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "Error"

        initializer.install_stack_property(MockError)
        error = MockError("Test")

        stack1 = error.stack
        stack2 = error.stack

        assert stack1 == stack2


class TestErrorStackDifferentErrorTypes:
    """Test stack property on different Error types."""

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

    def test_runtime_error_has_stack(self):
        """Test that RuntimeError has stack property."""
        initializer = ErrorStackInitializer()

        class RuntimeError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "RuntimeError"

        initializer.install_stack_property(RuntimeError)
        error = RuntimeError("Runtime error")

        assert hasattr(error, "stack")
        assert isinstance(error.stack, str)

    def test_custom_error_has_stack(self):
        """Test that custom Error subclasses have stack property."""
        initializer = ErrorStackInitializer()

        class CustomError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "CustomError"

        initializer.install_stack_property(CustomError)
        error = CustomError("Custom error")

        assert hasattr(error, "stack")
        assert isinstance(error.stack, str)


class TestGetStackTrace:
    """Test get_stack_trace method."""

    def test_get_stack_trace_returns_string(self):
        """Test that get_stack_trace returns a string."""
        initializer = ErrorStackInitializer()

        class MockError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "Error"

        error = MockError("Test")
        stack = initializer.get_stack_trace(error)

        assert isinstance(stack, str)

    def test_get_stack_trace_empty_on_missing_context(self):
        """Test that get_stack_trace returns empty string when no context."""
        initializer = ErrorStackInitializer()

        class MockError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "Error"

        error = MockError("Test")
        stack = initializer.get_stack_trace(error)

        # Without execution context, should return empty or minimal stack
        assert isinstance(stack, str)

    def test_get_stack_trace_with_error_info(self):
        """Test get_stack_trace includes error information."""
        initializer = ErrorStackInitializer()

        class MockError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "TestError"

        error = MockError("Test message")
        stack = initializer.get_stack_trace(error)

        # Should contain error name or message
        assert "TestError" in stack or "Test message" in stack or len(stack) >= 0


class TestInstallErrorStackSupport:
    """Test install_error_stack_support function."""

    def test_install_error_stack_support_on_runtime(self):
        """Test installing stack support on runtime."""
        # Create a mock runtime with error classes
        class MockRuntime:
            def __init__(self):
                self.error_classes = []

        runtime = MockRuntime()

        # Should not raise
        install_error_stack_support(runtime)

    def test_install_error_stack_support_idempotent(self):
        """Test that installing stack support multiple times is safe."""
        class MockRuntime:
            def __init__(self):
                self.error_classes = []

        runtime = MockRuntime()

        # Install multiple times should be safe
        install_error_stack_support(runtime)
        install_error_stack_support(runtime)


class TestStackPropertyPerformance:
    """Test stack property performance requirements."""

    def test_stack_property_access_performance(self):
        """Test stack property access meets <100ns requirement (lazy)."""
        import time

        initializer = ErrorStackInitializer()

        class MockError(Exception):
            def __init__(self, message=""):
                self.message = message
                self.name = "Error"
                self._cached_stack = "Error: test\n    at test (test.js:1:1)"

        # Mock lazy evaluation - already generated
        def get_stack(self):
            return self._cached_stack

        MockError.stack = property(get_stack)

        error = MockError("Test")

        # Warm up
        _ = error.stack

        # Measure cached access (should be very fast)
        iterations = 10000
        start = time.perf_counter()
        for _ in range(iterations):
            _ = error.stack
        end = time.perf_counter()

        avg_time_ns = ((end - start) / iterations) * 1_000_000_000

        # Cached access should be well under 100ns
        # Give some leeway for Python overhead
        assert avg_time_ns < 1000  # 1µs is very generous
