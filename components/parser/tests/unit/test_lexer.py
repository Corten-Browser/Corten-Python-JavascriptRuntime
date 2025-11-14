"""
Unit tests for Lexer class.

Tests verify lexical analysis (tokenization) of JavaScript source code,
including handling of keywords, identifiers, literals, operators, and punctuation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.shared_types.src import SourceLocation
from components.parser.src.token import Token, TokenType
from components.parser.src.lexer import Lexer


def test_lexer_creation():
    """
    Given JavaScript source code
    When creating a Lexer
    Then it should initialize successfully
    """
    lexer = Lexer("var x = 5;", "test.js")
    assert lexer is not None


def test_lexer_tokenize_simple_var_declaration():
    """
    Given a simple var declaration
    When tokenizing
    Then correct tokens should be produced
    """
    lexer = Lexer("var x = 5;", "test.js")

    tokens = []
    while True:
        token = lexer.next_token()
        tokens.append(token)
        if token.type == TokenType.EOF:
            break

    assert len(tokens) == 6
    assert tokens[0].type == TokenType.VAR
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "x"
    assert tokens[2].type == TokenType.ASSIGN
    assert tokens[3].type == TokenType.NUMBER
    assert tokens[3].value == 5
    assert tokens[4].type == TokenType.SEMICOLON
    assert tokens[5].type == TokenType.EOF


def test_lexer_keywords():
    """
    Given JavaScript keywords
    When tokenizing
    Then keywords should be recognized
    """
    source = "var function if else while for return break continue"
    lexer = Lexer(source, "test.js")

    expected_types = [
        TokenType.VAR,
        TokenType.FUNCTION,
        TokenType.IF,
        TokenType.ELSE,
        TokenType.WHILE,
        TokenType.FOR,
        TokenType.RETURN,
        TokenType.BREAK,
        TokenType.CONTINUE,
        TokenType.EOF,
    ]

    for expected_type in expected_types:
        token = lexer.next_token()
        assert token.type == expected_type


def test_lexer_identifiers():
    """
    Given various identifiers
    When tokenizing
    Then identifiers should be recognized with correct names
    """
    lexer = Lexer("myVar _private $jquery x123", "test.js")

    expected = ["myVar", "_private", "$jquery", "x123"]
    for expected_name in expected:
        token = lexer.next_token()
        assert token.type == TokenType.IDENTIFIER
        assert token.value == expected_name


def test_lexer_numbers():
    """
    Given numeric literals
    When tokenizing
    Then numbers should be parsed correctly
    """
    lexer = Lexer("42 3.14 0 100", "test.js")

    expected_values = [42, 3.14, 0, 100]
    for expected_value in expected_values:
        token = lexer.next_token()
        assert token.type == TokenType.NUMBER
        assert token.value == expected_value


def test_lexer_strings():
    """
    Given string literals
    When tokenizing
    Then strings should be parsed correctly
    """
    lexer = Lexer('"hello" "world" "test 123"', "test.js")

    expected_values = ["hello", "world", "test 123"]
    for expected_value in expected_values:
        token = lexer.next_token()
        assert token.type == TokenType.STRING
        assert token.value == expected_value


def test_lexer_boolean_literals():
    """
    Given boolean literals
    When tokenizing
    Then true and false should be recognized
    """
    lexer = Lexer("true false", "test.js")

    token = lexer.next_token()
    assert token.type == TokenType.TRUE

    token = lexer.next_token()
    assert token.type == TokenType.FALSE


def test_lexer_null_and_undefined():
    """
    Given null and undefined keywords
    When tokenizing
    Then they should be recognized as literals
    """
    lexer = Lexer("null undefined", "test.js")

    token = lexer.next_token()
    assert token.type == TokenType.NULL

    token = lexer.next_token()
    assert token.type == TokenType.UNDEFINED


def test_lexer_operators():
    """
    Given various operators
    When tokenizing
    Then operators should be recognized
    """
    lexer = Lexer("+ - * / = == !=", "test.js")

    expected_types = [
        TokenType.PLUS,
        TokenType.MINUS,
        TokenType.MULTIPLY,
        TokenType.DIVIDE,
        TokenType.ASSIGN,
        TokenType.EQUAL,
        TokenType.NOT_EQUAL,
    ]

    for expected_type in expected_types:
        token = lexer.next_token()
        assert token.type == expected_type


def test_lexer_comparison_operators():
    """
    Given comparison operators
    When tokenizing
    Then they should be recognized
    """
    lexer = Lexer("< >", "test.js")

    token = lexer.next_token()
    assert token.type == TokenType.LESS_THAN

    token = lexer.next_token()
    assert token.type == TokenType.GREATER_THAN


def test_lexer_punctuation():
    """
    Given punctuation characters
    When tokenizing
    Then they should be recognized
    """
    lexer = Lexer("( ) { } [ ] ; , .", "test.js")

    expected_types = [
        TokenType.LPAREN,
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RBRACE,
        TokenType.LBRACKET,
        TokenType.RBRACKET,
        TokenType.SEMICOLON,
        TokenType.COMMA,
        TokenType.DOT,
    ]

    for expected_type in expected_types:
        token = lexer.next_token()
        assert token.type == expected_type


def test_lexer_whitespace_handling():
    """
    Given source with various whitespace
    When tokenizing
    Then whitespace should be skipped
    """
    lexer = Lexer("  var   x  =  5  ;  ", "test.js")

    tokens = []
    while True:
        token = lexer.next_token()
        tokens.append(token)
        if token.type == TokenType.EOF:
            break

    # Should produce same tokens as without extra whitespace
    assert len(tokens) == 6
    assert tokens[0].type == TokenType.VAR
    assert tokens[1].type == TokenType.IDENTIFIER


def test_lexer_peek_token():
    """
    Given a lexer with tokens
    When using peek_token
    Then it should look ahead without consuming
    """
    lexer = Lexer("var x = 5;", "test.js")

    # Peek at first token
    peeked = lexer.peek_token(0)
    assert peeked.type == TokenType.VAR

    # Peek should not consume - next token should still be VAR
    token = lexer.next_token()
    assert token.type == TokenType.VAR

    # Peek ahead by 1
    peeked = lexer.peek_token(1)
    assert peeked.type == TokenType.ASSIGN

    # Next token should be IDENTIFIER (not ASSIGN)
    token = lexer.next_token()
    assert token.type == TokenType.IDENTIFIER


def test_lexer_source_location_tracking():
    """
    Given source code with multiple lines
    When tokenizing
    Then source locations should be tracked correctly
    """
    source = "var x = 5;\nvar y = 10;"
    lexer = Lexer(source, "test.js")

    # First token (var) on line 1
    token = lexer.next_token()
    assert token.location.line == 1
    assert token.location.filename == "test.js"

    # Skip to second line
    lexer.next_token()  # x
    lexer.next_token()  # =
    lexer.next_token()  # 5
    lexer.next_token()  # ;

    # var on line 2
    token = lexer.next_token()
    assert token.type == TokenType.VAR
    assert token.location.line == 2


def test_lexer_function_declaration():
    """
    Given a function declaration
    When tokenizing
    Then all tokens should be recognized correctly
    """
    source = "function add(a, b) { return a + b; }"
    lexer = Lexer(source, "test.js")

    expected_types = [
        TokenType.FUNCTION,
        TokenType.IDENTIFIER,  # add
        TokenType.LPAREN,
        TokenType.IDENTIFIER,  # a
        TokenType.COMMA,
        TokenType.IDENTIFIER,  # b
        TokenType.RPAREN,
        TokenType.LBRACE,
        TokenType.RETURN,
        TokenType.IDENTIFIER,  # a
        TokenType.PLUS,
        TokenType.IDENTIFIER,  # b
        TokenType.SEMICOLON,
        TokenType.RBRACE,
        TokenType.EOF,
    ]

    for expected_type in expected_types:
        token = lexer.next_token()
        assert token.type == expected_type


def test_lexer_empty_source():
    """
    Given empty source code
    When tokenizing
    Then only EOF should be produced
    """
    lexer = Lexer("", "test.js")

    token = lexer.next_token()
    assert token.type == TokenType.EOF

    # Multiple calls should still return EOF
    token = lexer.next_token()
    assert token.type == TokenType.EOF


def test_lexer_single_line_comment():
    """
    Given source with single-line comments
    When tokenizing
    Then comments should be skipped
    """
    source = "var x = 5; // this is a comment\nvar y = 10;"
    lexer = Lexer(source, "test.js")

    tokens = []
    while True:
        token = lexer.next_token()
        if token.type == TokenType.EOF:
            break
        tokens.append(token)

    # Should not include comment content
    # Just: var x = 5 ; var y = 10 ;
    assert all(
        t.type != TokenType.IDENTIFIER or t.value not in ["this", "is", "a", "comment"]
        for t in tokens
    )
