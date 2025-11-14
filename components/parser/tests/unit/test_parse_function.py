"""
Unit tests for Parse() main entry point function.

Tests verify the Parse() function correctly parses JavaScript source
into AST trees through the public API.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src import (
    Parse,
    Program,
    VariableDeclaration,
    FunctionDeclaration,
)


def test_parse_function_exists():
    """
    Given the Parse function
    When checking it exists
    Then it should be callable
    """
    assert callable(Parse)


def test_parse_simple_var():
    """
    Given simple JavaScript code
    When using Parse function
    Then correct AST should be returned
    """
    ast = Parse("var x = 5;", "test.js")

    assert isinstance(ast, Program)
    assert len(ast.body) == 1
    assert isinstance(ast.body[0], VariableDeclaration)


def test_parse_with_default_filename():
    """
    Given JavaScript code with no filename
    When using Parse function
    Then it should use default filename
    """
    ast = Parse("var x = 5;")

    assert isinstance(ast, Program)
    assert ast.location.filename == "<stdin>"


def test_parse_complete_program():
    """
    Given a complete JavaScript program
    When using Parse function
    Then entire program should be parsed
    """
    source = """
        var x = 5;
        var y = 10;

        function add(a, b) {
            return a + b;
        }

        var result = add(x, y);
    """

    ast = Parse(source, "test.js")

    assert isinstance(ast, Program)
    assert len(ast.body) == 4

    # var x = 5;
    assert isinstance(ast.body[0], VariableDeclaration)

    # var y = 10;
    assert isinstance(ast.body[1], VariableDeclaration)

    # function add(a, b) { return a + b; }
    assert isinstance(ast.body[2], FunctionDeclaration)
    assert ast.body[2].name == "add"

    # var result = add(x, y);
    assert isinstance(ast.body[3], VariableDeclaration)


def test_parse_empty_source():
    """
    Given empty source code
    When using Parse function
    Then empty Program should be returned
    """
    ast = Parse("", "test.js")

    assert isinstance(ast, Program)
    assert len(ast.body) == 0


def test_parse_syntax_error():
    """
    Given invalid JavaScript syntax
    When using Parse function
    Then SyntaxError should be raised
    """
    with pytest.raises(SyntaxError):
        Parse("var x =", "test.js")  # Incomplete statement


def test_parse_function_location():
    """
    Given JavaScript code
    When using Parse function
    Then source locations should be tracked
    """
    ast = Parse("var x = 5;", "myfile.js")

    assert ast.location.filename == "myfile.js"
    assert ast.body[0].location.filename == "myfile.js"
