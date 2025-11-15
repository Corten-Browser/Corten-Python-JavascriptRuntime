"""
Strict Mode Validator

Validates strict mode constraints and raises errors.
Implements FR-ES24-B-048 to FR-ES24-B-058.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, List
from .errors import (
    StrictModeReferenceError,
    StrictModeSyntaxError,
    StrictModeTypeError,
    StrictModeErrorType,
)


class ScopeType(Enum):
    """Type of scope"""
    GLOBAL = "global"
    FUNCTION = "function"
    BLOCK = "block"
    EVAL = "eval"
    MODULE = "module"


@dataclass
class StrictModeContext:
    """Context for strict mode execution"""
    is_strict: bool
    scope_type: ScopeType
    has_local_directive: bool
    inherited_strict: bool


class StrictModeValidator:
    """
    Validates strict mode constraints and raises errors.

    Handles both parse-time (syntax) and runtime (execution) validation.
    Many strict mode violations are syntax errors that should be caught during parsing.

    Specification: ECMA-262 §13.2.1 - Strict Mode Restrictions
    """

    # Future reserved words in strict mode
    FUTURE_RESERVED_WORDS = {
        "implements", "interface", "let", "package",
        "private", "protected", "public", "static", "yield"
    }

    def __init__(self, is_strict: bool):
        """
        Initialize validator with strict mode flag.

        Args:
            is_strict: Whether strict mode is active
        """
        self.is_strict = is_strict

    def validate_assignment(self, target: Any, scope: Any) -> None:
        """
        Validate assignment (throws if undeclared in strict mode).

        FR-ES24-B-048: Assignment to undeclared variable throws ReferenceError

        Args:
            target: Assignment target expression
            scope: Current scope

        Raises:
            StrictModeReferenceError: If assigning to undeclared variable in strict mode
        """
        if not self.is_strict:
            return

        # Only validate for simple identifiers
        if not hasattr(target, 'type') or target.type != 'Identifier':
            return

        # Check if variable is declared in scope
        if not hasattr(target, 'name'):
            return

        var_name = target.name

        # Check if binding exists in scope
        if scope and hasattr(scope, 'has_binding'):
            if not scope.has_binding(var_name):
                raise StrictModeReferenceError(
                    variable_name=var_name,
                    message=f"Assignment to undeclared variable '{var_name}' in strict mode"
                )

    def validate_deletion(self, target: Any) -> None:
        """
        Validate deletion (throws on unqualified identifier).

        FR-ES24-B-049: Delete of unqualified identifier throws SyntaxError

        Args:
            target: Deletion target

        Raises:
            StrictModeSyntaxError: If deleting unqualified identifier
        """
        if not self.is_strict:
            return

        # Only simple identifiers (unqualified) are forbidden
        if hasattr(target, 'type') and target.type == 'Identifier':
            raise StrictModeSyntaxError(
                violation_type=StrictModeErrorType.UNQUALIFIED_DELETE,
                message="Delete of an unqualified identifier in strict mode"
            )

        # Member expressions (obj.prop, obj[prop]) are allowed

    def validate_parameters(self, parameters: List[str]) -> None:
        """
        Validate function parameters (throws on duplicates).

        FR-ES24-B-050: Duplicate parameter names throw SyntaxError

        Args:
            parameters: Function parameter names

        Raises:
            StrictModeSyntaxError: If duplicate parameter names found
        """
        if not self.is_strict:
            return

        # Check for duplicates
        seen = set()
        for param in parameters:
            if param in seen:
                raise StrictModeSyntaxError(
                    violation_type=StrictModeErrorType.DUPLICATE_PARAMETER,
                    message=f"Duplicate parameter name '{param}' in strict mode"
                )
            seen.add(param)

    def validate_octal_literal(self, literal: str) -> None:
        """
        Validate numeric literal (throws on legacy octal).

        FR-ES24-B-051: Octal literals (0777) throw SyntaxError

        Args:
            literal: Numeric literal string

        Raises:
            StrictModeSyntaxError: If legacy octal literal found

        Notes:
            - Legacy octal: 0777 (starts with 0, contains only 0-7)
            - ES6 octal: 0o777 (starts with 0o or 0O) - ALLOWED
            - Hex: 0xFF - ALLOWED
            - Binary: 0b1010 - ALLOWED
        """
        if not self.is_strict:
            return

        # Check if it's a legacy octal literal
        if len(literal) > 1 and literal[0] == '0':
            # Check for ES6 prefixes (allowed)
            if len(literal) > 2 and literal[1] in 'oObBxX':
                return  # ES6 octal, binary, or hex - allowed

            # Check if it's all octal digits (0-7)
            # If so, it's a legacy octal literal
            if all(c in '01234567' for c in literal[1:]):
                raise StrictModeSyntaxError(
                    violation_type=StrictModeErrorType.OCTAL_LITERAL,
                    message="Octal literals are not allowed in strict mode"
                )

    def validate_identifier_name(self, name: str, context: str) -> None:
        """
        Validate identifier usage (eval, arguments restrictions).

        FR-ES24-B-052: Cannot use eval or arguments as identifiers

        Args:
            name: Identifier name
            context: Usage context (variable, parameter, etc.)

        Raises:
            StrictModeSyntaxError: If using eval or arguments as identifier
        """
        if not self.is_strict:
            return

        if name in ('eval', 'arguments'):
            raise StrictModeSyntaxError(
                violation_type=StrictModeErrorType.EVAL_ARGUMENTS_USAGE,
                message=f"Cannot use '{name}' as identifier in strict mode"
            )

    def validate_with_statement(self, with_stmt: Any) -> None:
        """
        Validate with statement (always throws in strict mode).

        FR-ES24-B-054: with statement throws SyntaxError

        Args:
            with_stmt: With statement node

        Raises:
            StrictModeSyntaxError: Always in strict mode
        """
        if not self.is_strict:
            return

        raise StrictModeSyntaxError(
            violation_type=StrictModeErrorType.WITH_STATEMENT,
            message="Strict mode code may not include a with statement"
        )

    def validate_reserved_word(self, word: str, context: str) -> None:
        """
        Validate future reserved words.

        FR-ES24-B-055: Future reserved words cannot be used as identifiers

        Args:
            word: Word to check
            context: Usage context

        Raises:
            StrictModeSyntaxError: If using future reserved word
        """
        if not self.is_strict:
            return

        if word in self.FUTURE_RESERVED_WORDS:
            raise StrictModeSyntaxError(
                violation_type=StrictModeErrorType.RESERVED_WORD,
                message=f"Use of future reserved word '{word}' in strict mode"
            )

    def validate_property_write(self, obj: Any, property: str, value: Any) -> None:
        """
        Validate property assignment (throws on readonly).

        FR-ES24-B-057: Assignment to readonly property throws TypeError

        Args:
            obj: Object to modify
            property: Property name
            value: Value to set

        Raises:
            StrictModeTypeError: If property is readonly
        """
        if not self.is_strict:
            return

        # Get property descriptor
        if hasattr(obj, 'get_property_descriptor'):
            descriptor = obj.get_property_descriptor(property)

            if descriptor is not None:
                # Check if property is writable
                if 'writable' in descriptor and not descriptor['writable']:
                    raise StrictModeTypeError(
                        property_name=property,
                        message=f"Cannot assign to read-only property '{property}' in strict mode"
                    )

    def validate_function_declaration(self, func_decl: Any, parent: Any) -> None:
        """
        Validate function declaration in blocks.

        FR-ES24-B-058: Function declarations in blocks have block scope

        Args:
            func_decl: Function declaration
            parent: Parent statement

        Notes:
            In strict mode, function declarations in blocks are block-scoped
            (ES2015+ semantics). This is not an error, just different scoping.
        """
        # In strict mode, function declarations in blocks are allowed
        # but have block scope instead of function scope.
        # This is not a validation error, just a semantic difference.
        pass
