"""
Unit tests for template literal parsing.

Tests parsing of template literals including basic templates,
templates with expressions, and templates with multiple expressions.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src.lexer import Lexer
from components.parser.src.parser import Parser
from components.parser.src.ast_nodes import (
    TemplateLiteral,
    Literal,
    BinaryExpression,
    Identifier,
    ExpressionStatement,
)
from components.parser.src.token import TokenType


class TestTemplateLiteralLexer:
    """Test lexer tokenization of template literals."""

    def test_lexer_tokenizes_simple_template_literal(self):
        """Test that lexer recognizes backtick-delimited template literals."""
        lexer = Lexer("`Hello World`", "test.js")
        token = lexer.next_token()

        assert token.type == TokenType.TEMPLATE_LITERAL
        assert token.value == "Hello World"

    def test_lexer_tokenizes_empty_template_literal(self):
        """Test that lexer handles empty template literals."""
        lexer = Lexer("``", "test.js")
        token = lexer.next_token()

        assert token.type == TokenType.TEMPLATE_LITERAL
        assert token.value == ""

    def test_lexer_tokenizes_template_with_newlines(self):
        """Test that template literals can contain newlines."""
        lexer = Lexer("`Line 1\nLine 2\nLine 3`", "test.js")
        token = lexer.next_token()

        assert token.type == TokenType.TEMPLATE_LITERAL
        assert token.value == "Line 1\nLine 2\nLine 3"


class TestTemplateLiteralParser:
    """Test parser handling of template literals."""

    def test_parse_simple_template_literal(self):
        """
        Given a simple template literal with only static text
        When the parser processes it
        Then it creates a TemplateLiteral AST node with one quasi and no expressions
        """
        # Given
        source = "`Hello World`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        assert len(ast.body) == 1
        stmt = ast.body[0]
        assert isinstance(stmt, ExpressionStatement)
        expr = stmt.expression
        assert isinstance(expr, TemplateLiteral)
        assert len(expr.quasis) == 1
        assert expr.quasis[0] == "Hello World"
        assert len(expr.expressions) == 0

    def test_parse_template_with_single_expression(self):
        """
        Given a template literal with one expression
        When the parser processes it
        Then it creates a TemplateLiteral with quasis and one expression
        """
        # Given
        source = "`Value: ${x}`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        assert len(ast.body) == 1
        stmt = ast.body[0]
        assert isinstance(stmt, ExpressionStatement)
        expr = stmt.expression
        assert isinstance(expr, TemplateLiteral)
        assert len(expr.quasis) == 2  # "Value: " and ""
        assert expr.quasis[0] == "Value: "
        assert expr.quasis[1] == ""
        assert len(expr.expressions) == 1
        assert isinstance(expr.expressions[0], Identifier)
        assert expr.expressions[0].name == "x"

    def test_parse_template_with_multiple_expressions(self):
        """
        Given a template literal with multiple expressions
        When the parser processes it
        Then it creates a TemplateLiteral with all quasis and expressions
        """
        # Given
        source = "`${a} + ${b} = ${a + b}`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        assert len(ast.body) == 1
        stmt = ast.body[0]
        assert isinstance(stmt, ExpressionStatement)
        expr = stmt.expression
        assert isinstance(expr, TemplateLiteral)
        assert len(expr.quasis) == 4  # "", " + ", " = ", ""
        assert expr.quasis[0] == ""
        assert expr.quasis[1] == " + "
        assert expr.quasis[2] == " = "
        assert expr.quasis[3] == ""
        assert len(expr.expressions) == 3

    def test_parse_template_with_expression_operators(self):
        """
        Given a template with complex expressions
        When the parser processes it
        Then expressions are correctly parsed
        """
        # Given
        source = "`Sum: ${x + 1}`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        stmt = ast.body[0]
        assert isinstance(stmt, ExpressionStatement)
        expr = stmt.expression
        assert isinstance(expr, TemplateLiteral)
        assert len(expr.expressions) == 1
        assert isinstance(expr.expressions[0], BinaryExpression)
        assert expr.expressions[0].operator == "+"

    def test_parse_template_only_expressions(self):
        """
        Given a template with only expressions (no static text)
        When the parser processes it
        Then quasis are empty strings
        """
        # Given
        source = "`${x}${y}`"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        stmt = ast.body[0]
        assert isinstance(stmt, ExpressionStatement)
        expr = stmt.expression
        assert isinstance(expr, TemplateLiteral)
        assert len(expr.quasis) == 3  # "", "", ""
        assert all(q == "" for q in expr.quasis)
        assert len(expr.expressions) == 2

    def test_parse_empty_template_literal(self):
        """
        Given an empty template literal
        When the parser processes it
        Then it creates a TemplateLiteral with one empty quasi
        """
        # Given
        source = "``"
        lexer = Lexer(source, "test.js")
        parser = Parser(lexer)

        # When
        ast = parser.parse()

        # Then
        stmt = ast.body[0]
        assert isinstance(stmt, ExpressionStatement)
        expr = stmt.expression
        assert isinstance(expr, TemplateLiteral)
        assert len(expr.quasis) == 1
        assert expr.quasis[0] == ""
        assert len(expr.expressions) == 0
