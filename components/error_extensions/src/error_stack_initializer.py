"""
Error Stack Initializer implementation

Implements FR-ES24-B-017 and FR-ES24-B-019:
- Error.prototype.stack: Stack trace property on all errors
- Error subclass stack traces: Stack traces for all Error types

Installs the stack property getter on Error.prototype and all Error subclasses.
"""

from typing import Any, Optional
from components.error_extensions.src.stack_trace_generator import (
    StackTraceGenerator,
    format_error_stack
)


class ErrorStackInitializer:
    """
    Initializes stack property on all Error types.

    Installs a lazy-evaluated stack property getter on Error classes,
    ensuring that all Error instances have access to stack traces.
    """

    def __init__(self):
        """Initialize the error stack initializer."""
        self.generator = StackTraceGenerator()

    def install_stack_property(self, error_class: type) -> None:
        """
        Install stack property getter on Error.prototype.

        Adds a 'stack' property to the error class that lazily generates
        stack traces on first access.

        Args:
            error_class: Error class to install stack property on

        Example:
            >>> class CustomError(Exception):
            ...     pass
            >>> initializer = ErrorStackInitializer()
            >>> initializer.install_stack_property(CustomError)
            >>> error = CustomError("test")
            >>> hasattr(error, "stack")
            True
        """
        # Check if stack property already exists
        if hasattr(error_class, "stack") and isinstance(
            getattr(error_class, "stack", None), property
        ):
            # Already installed
            return

        # Create stack property with lazy evaluation
        def get_stack(self) -> str:
            """
            Get stack trace for this error instance.

            Stack trace is generated lazily on first access and cached.

            Returns:
                Stack trace string
            """
            # Check if stack was already generated
            if hasattr(self, "_cached_stack") and self._cached_stack is not None:
                return self._cached_stack

            # Generate stack trace
            generator = StackTraceGenerator()
            frames = generator._capture_python_stack()

            # Format the stack trace
            from components.error_extensions.src.stack_trace_generator import format_error_stack
            stack = format_error_stack(self, frames)

            # Cache it
            self._cached_stack = stack

            return stack

        # Install as property on the class
        error_class.stack = property(get_stack)

        # Ensure instances will have the property
        # We need to make sure hasattr works
        if not hasattr(error_class, '_has_stack_installed'):
            error_class._has_stack_installed = True

    @staticmethod
    def _static_get_stack_trace(error: Any) -> str:
        """
        Static method to get stack trace for an error.

        This is separated from the instance to allow easy mocking and testing.

        Args:
            error: Error instance

        Returns:
            Stack trace string
        """
        generator = StackTraceGenerator()
        return generator.capture_stack_trace(error)

    def get_stack_trace(self, error: Any) -> str:
        """
        Get stack trace for error (lazy generation).

        Generates a stack trace for the given error object.
        If the error already has a cached stack, returns it.

        Args:
            error: Error object

        Returns:
            Stack trace string or empty string if no context available

        Example:
            >>> class Error:
            ...     name = "Error"
            ...     message = "test"
            >>> initializer = ErrorStackInitializer()
            >>> stack = initializer.get_stack_trace(Error())
            >>> isinstance(stack, str)
            True
        """
        # Check for cached stack
        if hasattr(error, "_cached_stack") and error._cached_stack is not None:
            return error._cached_stack

        # Generate new stack trace
        stack = self.generator.capture_stack_trace(error)

        return stack


def install_error_stack_support(runtime: Any) -> None:
    """
    Install stack trace support on all Error types in the runtime.

    This function should be called during runtime initialization to ensure
    all Error types have the stack property.

    Args:
        runtime: JavaScript runtime object

    Example:
        >>> class Runtime:
        ...     error_classes = []
        >>> runtime = Runtime()
        >>> install_error_stack_support(runtime)
    """
    initializer = ErrorStackInitializer()

    # Get all error classes from runtime
    error_classes = getattr(runtime, "error_classes", [])

    # Install stack property on each error class
    for error_class in error_classes:
        initializer.install_stack_property(error_class)

    # Also install on common built-in error types if they exist
    builtin_errors = [
        "Error",
        "TypeError",
        "ValueError",
        "RangeError",
        "ReferenceError",
        "SyntaxError",
        "URIError"
    ]

    for error_name in builtin_errors:
        if hasattr(runtime, error_name):
            error_class = getattr(runtime, error_name)
            initializer.install_stack_property(error_class)
