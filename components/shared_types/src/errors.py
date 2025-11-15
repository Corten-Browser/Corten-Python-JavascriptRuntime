"""
JavaScript Error classes with ES2024 cause support.

Implements:
- FR-P3.5-046: Error constructor accepts options.cause parameter
- FR-P3.5-047: Error.prototype.cause property
- FR-P3.5-048: Error cause with all Error subclasses

This module provides JavaScript Error classes that support error chaining
via the cause property, as specified in ECMAScript 2024.
"""


class JSError(Exception):
    """
    JavaScript Error class with cause support.

    Represents the base Error constructor from JavaScript, extended to support
    error chaining via the options.cause parameter (ES2024).

    Args:
        message: Error message string
        options: Optional dictionary with 'cause' key for error chaining

    Example:
        >>> original = JSError("Network timeout")
        >>> wrapped = JSError("Failed to fetch", options={"cause": original})
        >>> wrapped.cause
        JSError('Network timeout')
    """

    def __init__(self, message="", options=None):
        """
        Create a JavaScript Error with optional cause.

        Args:
            message: Error message (default: empty string)
            options: Optional dict with 'cause' key (any value accepted)
        """
        super().__init__(message)
        self.message = message

        # FR-P3.5-046: Accept options.cause parameter
        # FR-P3.5-047: Set cause property only if provided
        if options and isinstance(options, dict) and "cause" in options:
            # Cause can be any value (Error, string, object, number, None, etc.)
            self._cause = options["cause"]

    @property
    def cause(self):
        """
        Get the cause of this error.

        Returns:
            The cause value if it was provided, otherwise raises AttributeError.

        Raises:
            AttributeError: If no cause was provided in options
        """
        if hasattr(self, '_cause'):
            return self._cause
        raise AttributeError("'JSError' object has no attribute 'cause'")

    def __repr__(self):
        """String representation for debugging."""
        if hasattr(self, '_cause'):
            return f"JSError('{self.message}', cause={repr(self._cause)})"
        return f"JSError('{self.message}')"


class JSTypeError(JSError):
    """
    JavaScript TypeError with cause support.

    Represents TypeError from JavaScript, supporting error chaining.

    Example:
        >>> original = JSError("Invalid input")
        >>> type_error = JSTypeError("Expected string", options={"cause": original})
        >>> type_error.cause
        JSError('Invalid input')
    """

    def __repr__(self):
        """String representation for debugging."""
        if hasattr(self, '_cause'):
            return f"JSTypeError('{self.message}', cause={repr(self._cause)})"
        return f"JSTypeError('{self.message}')"


class JSRangeError(JSError):
    """
    JavaScript RangeError with cause support.

    Represents RangeError from JavaScript, supporting error chaining.

    Example:
        >>> range_error = JSRangeError("Value out of bounds", options={"cause": "negative index"})
        >>> range_error.cause
        'negative index'
    """

    def __repr__(self):
        """String representation for debugging."""
        if hasattr(self, '_cause'):
            return f"JSRangeError('{self.message}', cause={repr(self._cause)})"
        return f"JSRangeError('{self.message}')"


class JSSyntaxError(JSError):
    """
    JavaScript SyntaxError with cause support.

    Represents SyntaxError from JavaScript, supporting error chaining.

    Example:
        >>> syntax_error = JSSyntaxError("Unexpected token", options={"cause": {"line": 10, "col": 5}})
        >>> syntax_error.cause
        {'line': 10, 'col': 5}
    """

    def __repr__(self):
        """String representation for debugging."""
        if hasattr(self, '_cause'):
            return f"JSSyntaxError('{self.message}', cause={repr(self._cause)})"
        return f"JSSyntaxError('{self.message}')"


class JSReferenceError(JSError):
    """
    JavaScript ReferenceError with cause support.

    Represents ReferenceError from JavaScript, supporting error chaining.

    Example:
        >>> ref_error = JSReferenceError("Undefined variable", options={"cause": 42})
        >>> ref_error.cause
        42
    """

    def __repr__(self):
        """String representation for debugging."""
        if hasattr(self, '_cause'):
            return f"JSReferenceError('{self.message}', cause={repr(self._cause)})"
        return f"JSReferenceError('{self.message}')"
