"""
This Binding Handler

Handles 'this' binding in strict mode.
Implements FR-ES24-B-053: This binding in strict mode.
"""

from enum import Enum
from typing import Any, Optional


class CallType(Enum):
    """Type of function call"""
    PLAIN = "plain"  # f()
    METHOD = "method"  # obj.f()
    CONSTRUCTOR = "constructor"  # new f()
    APPLY_CALL = "apply_call"  # f.apply() / f.call()


class ThisBindingHandler:
    """
    Handles 'this' binding in strict mode.

    In strict mode:
    - Plain function calls have undefined this (not global object)
    - Primitive this values are NOT boxed to objects
    - Explicit this values are preserved as-is

    In non-strict mode:
    - Plain function calls have global object as this
    - Primitive this values are boxed to objects
    - null/undefined this becomes global object

    Specification: ECMA-262 §9.2.1.2 - OrdinaryCallBindThis
    """

    def __init__(self, is_strict: bool):
        """
        Initialize this binding handler.

        Args:
            is_strict: Strict mode flag
        """
        self.is_strict = is_strict

    def get_this_value(
        self,
        call_type: CallType,
        explicit_this: Optional[Any]
    ) -> Any:
        """
        Get this value for function call.

        Args:
            call_type: Type of function call
            explicit_this: Explicitly provided this value

        Returns:
            Actual this value for function

        Notes:
            - PLAIN call in strict: undefined (None)
            - PLAIN call in non-strict: global object
            - METHOD/CONSTRUCTOR/APPLY_CALL: preserve explicit this
        """
        if call_type == CallType.PLAIN:
            # Plain function call
            if self.is_strict:
                # In strict mode, this is undefined
                return None  # undefined represented as None
            else:
                # In non-strict mode, this would be global object
                # For testing, we return a marker or accept explicit_this
                return explicit_this  # Could be global object in real implementation

        # For method, constructor, and apply/call, preserve explicit this
        return explicit_this

    def validate_this_binding(
        self,
        this_value: Any,
        is_strict: bool
    ) -> Any:
        """
        Validate and normalize this value.

        Args:
            this_value: This value to validate
            is_strict: Strict mode flag

        Returns:
            Validated this value (no boxing in strict mode)

        Notes:
            - Strict mode: Return this value as-is (no boxing)
            - Non-strict mode: Box primitives to objects (not implemented here)
        """
        if is_strict:
            # In strict mode, do not box primitives
            return this_value
        else:
            # In non-strict mode, would box primitives
            # For testing, we just return the value
            return this_value
