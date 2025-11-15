"""
Strict Mode Errors

Custom error types for strict mode violations.
"""

from enum import Enum


class StrictModeErrorType(Enum):
    """Categories of strict mode errors"""
    UNDECLARED_ASSIGNMENT = "undeclared_assignment"
    UNQUALIFIED_DELETE = "unqualified_delete"
    DUPLICATE_PARAMETER = "duplicate_parameter"
    OCTAL_LITERAL = "octal_literal"
    EVAL_ARGUMENTS_USAGE = "eval_arguments_usage"
    WITH_STATEMENT = "with_statement"
    RESERVED_WORD = "reserved_word"
    READONLY_WRITE = "readonly_write"
    ARGUMENTS_CALLER_CALLEE = "arguments_caller_callee"
    FUNCTION_IN_BLOCK = "function_in_block"


class StrictModeReferenceError(ReferenceError):
    """Assignment to undeclared variable in strict mode"""

    def __init__(self, variable_name: str, message: str = None):
        self.variable_name = variable_name
        if message is None:
            message = f"Assignment to undeclared variable '{variable_name}' in strict mode"
        super().__init__(message)


class StrictModeSyntaxError(SyntaxError):
    """Syntax error specific to strict mode"""

    def __init__(self, violation_type: StrictModeErrorType, message: str):
        self.violation_type = violation_type
        super().__init__(message)


class StrictModeTypeError(TypeError):
    """Type error specific to strict mode"""

    def __init__(self, property_name: str = None, message: str = None):
        self.property_name = property_name
        super().__init__(message)
