"""
Token types and token dataclass for lexical analysis.

Provides TokenType enum with all ES5 token types and Token dataclass
for storing lexical tokens with their type, value, and source location.
"""

from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional

from components.shared_types.src import SourceLocation


class TokenType(Enum):
    """
    Enumeration of all token types for ES5 JavaScript.

    Includes keywords, literals, operators, and punctuation tokens
    required for parsing ES5 core JavaScript syntax.
    """

    # Keywords
    VAR = auto()
    LET = auto()
    CONST = auto()
    FUNCTION = auto()
    CLASS = auto()
    EXTENDS = auto()
    STATIC = auto()
    SUPER = auto()
    GET = auto()
    SET = auto()
    IF = auto()
    ELSE = auto()
    WHILE = auto()
    FOR = auto()
    IN = auto()
    OF = auto()
    RETURN = auto()
    BREAK = auto()
    CONTINUE = auto()
    NEW = auto()
    ASYNC = auto()
    AWAIT = auto()
    DEFAULT = auto()

    # ES Modules keywords
    IMPORT = auto()
    EXPORT = auto()
    FROM = auto()
    AS = auto()

    # Literals
    IDENTIFIER = auto()
    NUMBER = auto()
    STRING = auto()
    TEMPLATE_LITERAL = auto()
    REGEXP = auto()
    TRUE = auto()
    FALSE = auto()
    NULL = auto()
    UNDEFINED = auto()

    # Operators
    PLUS = auto()
    MINUS = auto()
    MULTIPLY = auto()
    DIVIDE = auto()
    ASSIGN = auto()
    EQUAL = auto()
    NOT_EQUAL = auto()
    LESS_THAN = auto()
    GREATER_THAN = auto()

    # Punctuation
    LPAREN = auto()
    RPAREN = auto()
    LBRACE = auto()
    RBRACE = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    SEMICOLON = auto()
    COMMA = auto()
    DOT = auto()
    COLON = auto()
    ARROW = auto()  # => for arrow functions
    SPREAD = auto()  # ... for spread/rest operators

    # Special
    EOF = auto()


@dataclass
class Token:
    """
    Lexical token with type, value, and source location.

    Attributes:
        type: The type of the token (from TokenType enum)
        value: The value of the token (for literals and identifiers), None for keywords/operators
        location: Source location where the token was found

    Example:
        >>> loc = SourceLocation(filename="test.js", line=1, column=5, offset=4)
        >>> token = Token(type=TokenType.NUMBER, value=42, location=loc)
        >>> token.type
        <TokenType.NUMBER: 11>
        >>> token.value
        42
    """

    type: TokenType
    value: Optional[Any]
    location: SourceLocation
