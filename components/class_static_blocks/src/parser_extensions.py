"""
Parser extensions for static blocks.

Implements FR-ES24-B-011: Parsing of static { ... } syntax.
"""

from typing import List
from components.parser.src.ast_nodes import Statement, SourceLocation
from components.parser.src.token import Token
from components.class_static_blocks.src.ast_nodes import StaticBlock


class StaticBlockParser:
    """Parser extension for static initialization blocks."""

    def is_static_block(self, parser) -> bool:
        """
        Check if current position is start of a static block.

        A static block starts with 'static' keyword followed by '{'.
        This distinguishes it from static fields and static methods.

        Args:
            parser: Parser instance

        Returns:
            True if current position is start of static block

        Example:
            static { }        -> True  (static block)
            static x = 1;     -> False (static field)
            static foo() { }  -> False (static method)
        """
        if not parser.current_token or parser.current_token.value != 'static':
            return False

        # Peek at next token
        next_token = parser.peek()
        if not next_token:
            return False

        # Static block if 'static' followed by '{'
        return next_token.value == '{'

    def parse_class_static_block(self, parser) -> StaticBlock:
        """
        Parse static { ... } block inside class body.

        Syntax:
            static {
                <statements>
            }

        Args:
            parser: Parser instance

        Returns:
            StaticBlock AST node

        Raises:
            SyntaxError: If static block syntax is invalid

        Restrictions:
            - No parameters: static(x) { } is invalid
            - No name: static foo { } is invalid
            - No async: async static { } is invalid
            - No generator: static* { } is invalid
            - Only valid inside class bodies
        """
        start_location = parser.current_token.location

        # Expect 'static' keyword
        if not parser.current_token or parser.current_token.value != 'static':
            raise SyntaxError(
                f"Expected 'static' keyword at {start_location}"
            )

        # Consume 'static'
        parser.advance()

        # Expect '{' (no parameters, no name)
        if not parser.current_token or parser.current_token.value != '{':
            # Check for common errors
            if parser.current_token.value == '(':
                raise SyntaxError(
                    f"Static blocks cannot have parameters at {parser.current_token.location}"
                )
            elif parser.current_token.type == 'IDENTIFIER':
                raise SyntaxError(
                    f"Static blocks cannot be named at {parser.current_token.location}"
                )
            elif parser.current_token.value == '*':
                raise SyntaxError(
                    f"Static blocks cannot be generators at {parser.current_token.location}"
                )
            else:
                raise SyntaxError(
                    f"Expected '{{' after 'static' at {parser.current_token.location}"
                )

        # Parse block statement body
        body = self._parse_block_body(parser)

        end_location = parser.current_token.location if parser.current_token else start_location

        return StaticBlock(
            body=body,
            location=SourceLocation(
                start=start_location.start,
                end=end_location.end,
                source=start_location.source
            )
        )

    def _parse_block_body(self, parser) -> List[Statement]:
        """
        Parse the body of a static block.

        Args:
            parser: Parser instance

        Returns:
            List of statements in the block

        Raises:
            SyntaxError: If block syntax is invalid
        """
        # Consume '{'
        parser.advance()

        statements = []

        # Parse statements until '}'
        while parser.current_token and parser.current_token.value != '}':
            # Parse statement (delegate to parser's statement parsing)
            stmt = parser.parse_statement()
            statements.append(stmt)

        # Expect '}'
        if not parser.current_token or parser.current_token.value != '}':
            raise SyntaxError(
                f"Expected '}}' to close static block"
            )

        # Consume '}'
        parser.advance()

        return statements


def parse_class_static_block(parser) -> StaticBlock:
    """
    Standalone function to parse static block.

    This is the main entry point for parsing static blocks.

    Args:
        parser: Parser instance

    Returns:
        StaticBlock AST node

    Raises:
        SyntaxError: If static block syntax is invalid
    """
    parser_ext = StaticBlockParser()
    return parser_ext.parse_class_static_block(parser)


def is_static_block(parser) -> bool:
    """
    Check if current position is start of static block.

    Args:
        parser: Parser instance

    Returns:
        True if static block follows

    Example:
        >>> parser.current_token.value == 'static'
        >>> parser.peek().value == '{'
        >>> is_static_block(parser)
        True
    """
    parser_ext = StaticBlockParser()
    return parser_ext.is_static_block(parser)
