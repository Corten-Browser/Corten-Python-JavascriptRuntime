"""
EvaluationResult - result container for bytecode execution.

This module provides the EvaluationResult class which represents the outcome
of bytecode execution, containing either a successful value or an exception.
"""

from typing import Optional
from components.value_system.src import Value


class EvaluationResult:
    """
    Result of bytecode execution.

    Contains either a successful value or an exception from execution.
    Used to propagate results and errors through the interpreter.

    Attributes:
        value: Return value if execution succeeded (None if exception occurred)
        exception: Exception if execution failed (None if successful)
    """

    def __init__(
        self, value: Optional[Value] = None, exception: Optional[Exception] = None
    ):
        """
        Create an EvaluationResult.

        Args:
            value: Successful result value (optional)
            exception: Exception if execution failed (optional)

        Note:
            If neither value nor exception is provided, this represents
            a successful execution with undefined result.
        """
        self.value = value
        self.exception = exception

    def is_success(self) -> bool:
        """
        Check if execution was successful.

        Returns:
            True if no exception occurred, False otherwise
        """
        return self.exception is None

    def is_exception(self) -> bool:
        """
        Check if execution resulted in an exception.

        Returns:
            True if exception occurred, False otherwise
        """
        return self.exception is not None
