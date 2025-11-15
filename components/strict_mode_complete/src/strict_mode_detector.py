"""
Strict Mode Detector

Detects and processes "use strict" directives in JavaScript code.
Implements FR-ES24-B-047: "use strict" directive detection and propagation.
"""

from dataclasses import dataclass
from typing import List, Any


@dataclass
class DirectivePrologueInfo:
    """Information about directives found in a directive prologue"""
    has_use_strict: bool
    directive_count: int
    first_non_directive_index: int


class StrictModeDetector:
    """
    Detects and validates "use strict" directives in JavaScript code.

    The "use strict" directive must:
    1. Be a string literal expression statement
    2. Contain exactly "use strict" (case-sensitive, no escapes)
    3. Appear in the directive prologue (before any non-directive statements)

    Specification: ECMA-262 §14.1.1 - Directive Prologues and the Use Strict Directive
    """

    def __init__(self):
        """Initialize strict mode detector"""
        pass

    def detect_directive(self, statement: Any) -> bool:
        """
        Detect if a statement is a "use strict" directive.

        Args:
            statement: Statement to check (must be AST node)

        Returns:
            True if statement is "use strict" directive, False otherwise

        Notes:
            - Must be an ExpressionStatement with a string Literal
            - String value must be exactly "use strict" (no escapes, case-sensitive)
            - Does NOT check position in prologue (use is_directive_prologue for that)
        """
        # Must be an ExpressionStatement
        if not hasattr(statement, 'type') or statement.type != 'ExpressionStatement':
            return False

        # Must have an expression
        if not hasattr(statement, 'expression'):
            return False

        expression = statement.expression

        # Expression must be a Literal
        if not hasattr(expression, 'type') or expression.type != 'Literal':
            return False

        # Literal must have a value
        if not hasattr(expression, 'value'):
            return False

        # Value must be exactly "use strict" (case-sensitive, no escapes)
        # Note: Escapes like "use\x20strict" are not directives
        return expression.value == "use strict"

    def is_directive_prologue(self, statements: List[Any], index: int) -> bool:
        """
        Check if a statement at given index is in the directive prologue position.

        A directive prologue is a sequence of ExpressionStatement nodes containing
        string literals that appear at the beginning of a Program or FunctionBody.

        Args:
            statements: List of statements in the body
            index: Index of statement to check

        Returns:
            True if the statement is in a directive prologue position

        Notes:
            - Directive prologue ends at the first non-directive statement
            - A statement is a directive if it's an ExpressionStatement with a Literal
        """
        # Check all statements before this one
        for i in range(index):
            stmt = statements[i]

            # If we encounter a non-directive, prologue has ended
            if not self._is_directive_statement(stmt):
                return False

        # All previous statements are directives, so this is in prologue
        return True

    def scan_for_directives(self, body: List[Any]) -> DirectivePrologueInfo:
        """
        Scan a function or program body for all directives.

        Args:
            body: Function or program body (list of statements)

        Returns:
            DirectivePrologueInfo with directive scan results

        Notes:
            - Scans from the beginning until first non-directive
            - Checks for "use strict" among the directives
            - Returns count and index information
        """
        has_use_strict = False
        directive_count = 0
        first_non_directive_index = 0

        for i, stmt in enumerate(body):
            # Check if this is a directive statement
            if not self._is_directive_statement(stmt):
                # Found first non-directive
                first_non_directive_index = i
                break

            # It's a directive - count it
            directive_count += 1

            # Check if it's "use strict"
            if self.detect_directive(stmt):
                has_use_strict = True
        else:
            # All statements are directives (or empty body)
            first_non_directive_index = len(body)

        return DirectivePrologueInfo(
            has_use_strict=has_use_strict,
            directive_count=directive_count,
            first_non_directive_index=first_non_directive_index
        )

    def _is_directive_statement(self, statement: Any) -> bool:
        """
        Check if a statement could be a directive.

        A directive is an ExpressionStatement containing a string Literal.
        It doesn't have to be "use strict" - any string literal counts.

        Args:
            statement: Statement to check

        Returns:
            True if statement is a directive (string literal expression)
        """
        # Must be ExpressionStatement
        if not hasattr(statement, 'type') or statement.type != 'ExpressionStatement':
            return False

        # Must have expression
        if not hasattr(statement, 'expression'):
            return False

        expression = statement.expression

        # Expression must be a Literal
        if not hasattr(expression, 'type') or expression.type != 'Literal':
            return False

        # Must have a value
        if not hasattr(expression, 'value'):
            return False

        # Value must be a string (any string is a directive)
        return isinstance(expression.value, str)
