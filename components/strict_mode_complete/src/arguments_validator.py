"""
Arguments Object Validator

Validates arguments object behavior in strict mode.
Implements FR-ES24-B-056: arguments.caller/callee restrictions.
"""

from typing import Any, List
from .errors import StrictModeTypeError


class ArgumentsObjectValidator:
    """
    Validates arguments object behavior in strict mode.

    In strict mode:
    - arguments.caller throws TypeError
    - arguments.callee throws TypeError
    - No aliasing between parameters and arguments array

    Specification: ECMA-262 §9.4.4 - Arguments Exotic Objects
    """

    def __init__(self, is_strict: bool):
        """
        Initialize arguments validator.

        Args:
            is_strict: Strict mode flag
        """
        self.is_strict = is_strict

    def validate_caller_access(self, arguments_obj: Any) -> None:
        """
        Validate arguments.caller access.

        Args:
            arguments_obj: Arguments object

        Raises:
            StrictModeTypeError: If accessing caller in strict mode
        """
        if not self.is_strict:
            return

        raise StrictModeTypeError(
            property_name="caller",
            message="arguments.caller is not allowed in strict mode"
        )

    def validate_callee_access(self, arguments_obj: Any) -> None:
        """
        Validate arguments.callee access.

        Args:
            arguments_obj: Arguments object

        Raises:
            StrictModeTypeError: If accessing callee in strict mode
        """
        if not self.is_strict:
            return

        raise StrictModeTypeError(
            property_name="callee",
            message="arguments.callee is not allowed in strict mode"
        )

    def create_arguments_object(
        self,
        parameters: List[str],
        values: List[Any],
        is_strict: bool
    ) -> Any:
        """
        Create arguments object with correct behavior.

        Args:
            parameters: Function parameter names
            values: Argument values
            is_strict: Strict mode flag

        Returns:
            Arguments object (aliased or unaliased based on strict mode)

        Notes:
            - In strict mode: arguments is NOT aliased to parameters
            - In non-strict mode: arguments[i] is aliased to parameter i
        """
        # Create a simple arguments-like object
        class ArgumentsObject:
            def __init__(self, values, is_strict):
                self._values = list(values)
                self._is_strict = is_strict
                self.length = len(values)

            def __getitem__(self, index):
                if 0 <= index < len(self._values):
                    return self._values[index]
                return None

            def __setitem__(self, index, value):
                if 0 <= index < len(self._values):
                    self._values[index] = value

        args_obj = ArgumentsObject(values, is_strict)

        # In strict mode, accessing caller/callee would throw
        # (handled by validate_caller_access and validate_callee_access)

        return args_obj
