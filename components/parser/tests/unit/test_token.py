"""
Unit tests for Token dataclass and TokenType enum.

Tests verify that Token correctly stores type, value, and location information,
and that TokenType enum includes all necessary token types for ES5 parsing.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.shared_types.src import SourceLocation


def test_token_type_enum_has_all_required_types():
    """
    Given the TokenType enum is defined
    When checking for required token types
    Then all ES5 token types should be present
    """
    from components.parser.src.token import TokenType

    # Keywords
    assert hasattr(TokenType, "VAR")
    assert hasattr(TokenType, "FUNCTION")
    assert hasattr(TokenType, "IF")
    assert hasattr(TokenType, "ELSE")
    assert hasattr(TokenType, "WHILE")
    assert hasattr(TokenType, "FOR")
    assert hasattr(TokenType, "RETURN")
    assert hasattr(TokenType, "BREAK")
    assert hasattr(TokenType, "CONTINUE")

    # Literals
    assert hasattr(TokenType, "IDENTIFIER")
    assert hasattr(TokenType, "NUMBER")
    assert hasattr(TokenType, "STRING")
    assert hasattr(TokenType, "TRUE")
    assert hasattr(TokenType, "FALSE")
    assert hasattr(TokenType, "NULL")
    assert hasattr(TokenType, "UNDEFINED")

    # Operators
    assert hasattr(TokenType, "PLUS")
    assert hasattr(TokenType, "MINUS")
    assert hasattr(TokenType, "MULTIPLY")
    assert hasattr(TokenType, "DIVIDE")
    assert hasattr(TokenType, "ASSIGN")
    assert hasattr(TokenType, "EQUAL")
    assert hasattr(TokenType, "NOT_EQUAL")
    assert hasattr(TokenType, "LESS_THAN")
    assert hasattr(TokenType, "GREATER_THAN")

    # Punctuation
    assert hasattr(TokenType, "LPAREN")
    assert hasattr(TokenType, "RPAREN")
    assert hasattr(TokenType, "LBRACE")
    assert hasattr(TokenType, "RBRACE")
    assert hasattr(TokenType, "LBRACKET")
    assert hasattr(TokenType, "RBRACKET")
    assert hasattr(TokenType, "SEMICOLON")
    assert hasattr(TokenType, "COMMA")
    assert hasattr(TokenType, "DOT")
    assert hasattr(TokenType, "EOF")


def test_token_creation_with_all_fields():
    """
    Given a TokenType, value, and SourceLocation
    When creating a Token
    Then the Token should store all fields correctly
    """
    from components.parser.src.token import Token, TokenType

    location = SourceLocation(filename="test.js", line=1, column=5, offset=4)
    token = Token(type=TokenType.NUMBER, value=42, location=location)

    assert token.type == TokenType.NUMBER
    assert token.value == 42
    assert token.location == location
    assert token.location.filename == "test.js"
    assert token.location.line == 1
    assert token.location.column == 5


def test_token_creation_with_identifier():
    """
    Given an identifier token
    When creating a Token
    Then the value should be the identifier name
    """
    from components.parser.src.token import Token, TokenType

    location = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    token = Token(type=TokenType.IDENTIFIER, value="myVariable", location=location)

    assert token.type == TokenType.IDENTIFIER
    assert token.value == "myVariable"


def test_token_creation_with_string_literal():
    """
    Given a string literal token
    When creating a Token
    Then the value should be the string content
    """
    from components.parser.src.token import Token, TokenType

    location = SourceLocation(filename="test.js", line=2, column=10, offset=20)
    token = Token(type=TokenType.STRING, value="hello world", location=location)

    assert token.type == TokenType.STRING
    assert token.value == "hello world"


def test_token_creation_with_keyword():
    """
    Given a keyword token
    When creating a Token
    Then the token type should be the keyword type
    """
    from components.parser.src.token import Token, TokenType

    location = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    token = Token(type=TokenType.VAR, value=None, location=location)

    assert token.type == TokenType.VAR
    assert token.value is None


def test_token_creation_with_operator():
    """
    Given an operator token
    When creating a Token
    Then the token should represent the operator
    """
    from components.parser.src.token import Token, TokenType

    location = SourceLocation(filename="test.js", line=1, column=15, offset=14)
    token = Token(type=TokenType.PLUS, value=None, location=location)

    assert token.type == TokenType.PLUS


def test_token_eof():
    """
    Given an EOF token
    When creating a Token
    Then it should mark end of file
    """
    from components.parser.src.token import Token, TokenType

    location = SourceLocation(filename="test.js", line=10, column=1, offset=200)
    token = Token(type=TokenType.EOF, value=None, location=location)

    assert token.type == TokenType.EOF
    assert token.value is None
