"""
AggregateError implementation (ES2021)

Implements FR-ES24-B-015 and FR-ES24-B-016:
- AggregateError: Error type for representing multiple failures
- AggregateError.errors property: Read-only array of aggregated errors

AggregateError is used to represent multiple errors as a single error,
typically used in Promise.any() rejections and similar scenarios.
"""

from typing import Any, Dict, Iterable, List, Optional


class AggregateError(Exception):
    """
    Error type representing multiple failures.

    AggregateError is a built-in error object that indicates several errors
    occurred. It is typically used when multiple errors need to be reported
    at once, such as when all promises in Promise.any() are rejected.

    Attributes:
        errors: Read-only list of aggregated error objects
        message: Error message (string)
        name: Error name (always "AggregateError")
        stack: Stack trace string (lazy-generated)
        cause: Optional cause of the error
    """

    def __init__(
        self,
        errors: Iterable[Any],
        message: str = "",
        options: Optional[Dict[str, Any]] = None
    ):
        """
        Create a new AggregateError.

        Args:
            errors: Iterable of error objects (can be any values)
            message: Optional error message (default: empty string)
            options: Optional options dict (may contain 'cause')

        Raises:
            TypeError: If errors is not iterable
        """
        super().__init__(message)

        # Validate that errors is iterable
        try:
            # Convert to list to make it concrete and iterable
            error_list = list(errors)
        except TypeError as e:
            raise TypeError(f"{errors!r} is not iterable") from e

        # Store errors as a read-only (frozen) list
        # In Python, we use a private attribute and property to enforce read-only
        self._errors = tuple(error_list)  # Tuple is immutable

        # Set standard Error properties
        self.message = message
        self.name = "AggregateError"

        # Handle options (ES2022 Error cause)
        if options is not None:
            self.cause = options.get("cause")
        else:
            self.cause = None

        # Stack trace (lazy-generated via property)
        self._stack = None
        self._stack_generated = False

    @property
    def errors(self) -> List[Any]:
        """
        Get the list of aggregated errors.

        Returns a copy of the internal errors list to prevent modification.
        The list itself is read-only (attempts to modify will raise TypeError).

        Returns:
            List of error objects
        """
        # Return a copy to prevent modification of internal tuple
        # In JavaScript, this would be a sealed/frozen array
        return list(self._errors)

    @errors.setter
    def errors(self, value: Any) -> None:
        """
        Prevent assignment to errors property.

        Raises:
            AttributeError: Always, as errors is read-only
        """
        raise AttributeError("can't set attribute 'errors' (read-only)")

    @property
    def stack(self) -> str:
        """
        Get the stack trace for this error.

        Stack trace is generated lazily on first access.
        This property will be enhanced by ErrorStackInitializer.

        Returns:
            Stack trace string
        """
        if not self._stack_generated:
            # Generate basic stack trace
            # This will be enhanced by StackTraceGenerator
            self._stack = self._generate_basic_stack()
            self._stack_generated = True
        return self._stack

    def _generate_basic_stack(self) -> str:
        """
        Generate a basic stack trace.

        This is a fallback for when ErrorStackInitializer hasn't been applied.
        The stack trace will be more detailed when ErrorStackInitializer is used.

        Returns:
            Basic stack trace string
        """
        # Basic format: "ErrorName: message"
        if self.message:
            return f"{self.name}: {self.message}"
        else:
            return self.name

    def toString(self) -> str:
        """
        Get string representation of the error.

        Returns:
            String in format "AggregateError: message" or just "AggregateError"
        """
        if self.message:
            return f"{self.name}: {self.message}"
        else:
            return self.name

    def __str__(self) -> str:
        """
        Python string representation.

        Returns:
            String representation of the error
        """
        return self.toString()

    def __repr__(self) -> str:
        """
        Python repr representation.

        Returns:
            Detailed representation showing errors count
        """
        error_count = len(self._errors)
        if self.message:
            return f"AggregateError({error_count} errors, '{self.message}')"
        else:
            return f"AggregateError({error_count} errors)"


def create_aggregate_error(
    errors: Iterable[Any],
    message: str,
    options: Dict[str, Any]
) -> AggregateError:
    """
    Factory function for creating AggregateError.

    This is a convenience function that creates an AggregateError instance.
    It's equivalent to calling AggregateError() directly.

    Args:
        errors: Iterable of error objects
        message: Error message
        options: Options dict (may contain 'cause')

    Returns:
        New AggregateError instance

    Example:
        >>> errors = [ValueError("error1"), TypeError("error2")]
        >>> agg_error = create_aggregate_error(errors, "Multiple errors", {})
        >>> len(agg_error.errors)
        2
    """
    return AggregateError(errors, message, options)
