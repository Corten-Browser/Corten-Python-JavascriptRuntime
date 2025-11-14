"""
Unit tests for let/const declarations with block scope support.

Tests verify parsing of ES6-style let/const variable declarations,
including syntax validation (const requires initializer) and proper
AST generation with kind field.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src.lexer import Lexer
from components.parser.src.parser import Parser
from components.parser.src.ast_nodes import *


def parse(source: str) -> Program:
    """Helper to parse source code into AST."""
    lexer = Lexer(source, "test.js")
    parser = Parser(lexer)
    return parser.parse()


# ============================================================================
# LET DECLARATIONS
# ============================================================================


def test_parse_let_declaration_with_init():
    """
    Given a let declaration with initializer
    When parsing
    Then correct AST should be produced with kind='let'
    """
    program = parse("let x = 1;")

    assert isinstance(program, Program)
    assert len(program.body) == 1
    assert isinstance(program.body[0], VariableDeclaration)

    var_decl = program.body[0]
    assert var_decl.kind == "let"
    assert len(var_decl.declarations) == 1
    assert var_decl.declarations[0].name == "x"
    assert isinstance(var_decl.declarations[0].init, Literal)
    assert var_decl.declarations[0].init.value == 1


def test_parse_let_declaration_without_init():
    """
    Given a let declaration without initializer
    When parsing
    Then init should be None and kind='let'
    """
    program = parse("let x;")

    var_decl = program.body[0]
    assert var_decl.kind == "let"
    assert var_decl.declarations[0].name == "x"
    assert var_decl.declarations[0].init is None


def test_parse_let_multiple_declarations():
    """
    Given multiple let declarations
    When parsing
    Then all declarations should be in AST with kind='let'
    """
    program = parse("let x = 1, y = 2, z;")

    var_decl = program.body[0]
    assert var_decl.kind == "let"
    assert len(var_decl.declarations) == 3
    assert var_decl.declarations[0].name == "x"
    assert var_decl.declarations[0].init.value == 1
    assert var_decl.declarations[1].name == "y"
    assert var_decl.declarations[1].init.value == 2
    assert var_decl.declarations[2].name == "z"
    assert var_decl.declarations[2].init is None


def test_parse_let_in_block_scope():
    """
    Given a let declaration inside a block
    When parsing
    Then it should parse correctly within BlockStatement
    """
    program = parse("{ let x = 1; }")

    assert isinstance(program.body[0], BlockStatement)
    block = program.body[0]
    assert len(block.body) == 1
    assert isinstance(block.body[0], VariableDeclaration)
    assert block.body[0].kind == "let"
    assert block.body[0].declarations[0].name == "x"


# ============================================================================
# CONST DECLARATIONS
# ============================================================================


def test_parse_const_declaration_with_init():
    """
    Given a const declaration with initializer
    When parsing
    Then correct AST should be produced with kind='const'
    """
    program = parse("const y = 2;")

    assert isinstance(program, Program)
    assert len(program.body) == 1
    assert isinstance(program.body[0], VariableDeclaration)

    var_decl = program.body[0]
    assert var_decl.kind == "const"
    assert len(var_decl.declarations) == 1
    assert var_decl.declarations[0].name == "y"
    assert isinstance(var_decl.declarations[0].init, Literal)
    assert var_decl.declarations[0].init.value == 2


def test_parse_const_declaration_without_init_error():
    """
    Given a const declaration without initializer
    When parsing
    Then SyntaxError should be raised
    """
    with pytest.raises(SyntaxError, match="Missing initializer in const declaration"):
        parse("const x;")


def test_parse_const_multiple_declarations_mixed_init():
    """
    Given const declarations with mixed initializers
    When parsing const with missing init
    Then SyntaxError should be raised for missing init
    """
    # Valid: all have initializers
    program = parse("const x = 1, y = 2;")
    var_decl = program.body[0]
    assert var_decl.kind == "const"
    assert len(var_decl.declarations) == 2
    assert var_decl.declarations[0].init.value == 1
    assert var_decl.declarations[1].init.value == 2

    # Invalid: second declarator missing init
    with pytest.raises(SyntaxError, match="Missing initializer in const declaration"):
        parse("const x = 1, y;")


def test_parse_const_in_block_scope():
    """
    Given a const declaration inside a block
    When parsing
    Then it should parse correctly within BlockStatement
    """
    program = parse("{ const x = 1; }")

    assert isinstance(program.body[0], BlockStatement)
    block = program.body[0]
    assert len(block.body) == 1
    assert isinstance(block.body[0], VariableDeclaration)
    assert block.body[0].kind == "const"
    assert block.body[0].declarations[0].name == "x"


# ============================================================================
# MIXED VAR/LET/CONST
# ============================================================================


def test_parse_var_let_const_mixed():
    """
    Given a program with var, let, and const declarations
    When parsing
    Then all should parse correctly with proper kind values
    """
    program = parse(
        """
        var a = 1;
        let b = 2;
        const c = 3;
    """
    )

    assert len(program.body) == 3

    # var declaration
    assert isinstance(program.body[0], VariableDeclaration)
    assert program.body[0].kind == "var"
    assert program.body[0].declarations[0].name == "a"

    # let declaration
    assert isinstance(program.body[1], VariableDeclaration)
    assert program.body[1].kind == "let"
    assert program.body[1].declarations[0].name == "b"

    # const declaration
    assert isinstance(program.body[2], VariableDeclaration)
    assert program.body[2].kind == "const"
    assert program.body[2].declarations[0].name == "c"


def test_let_const_in_nested_blocks():
    """
    Given nested blocks with let/const declarations
    When parsing
    Then all should parse correctly at different nesting levels
    """
    program = parse(
        """
        {
            let x = 1;
            {
                const y = 2;
                let z = 3;
            }
        }
    """
    )

    outer_block = program.body[0]
    assert isinstance(outer_block, BlockStatement)
    assert len(outer_block.body) == 2

    # First statement: let x = 1
    assert outer_block.body[0].kind == "let"
    assert outer_block.body[0].declarations[0].name == "x"

    # Second statement: nested block
    inner_block = outer_block.body[1]
    assert isinstance(inner_block, BlockStatement)
    assert len(inner_block.body) == 2

    # const y = 2
    assert inner_block.body[0].kind == "const"
    assert inner_block.body[0].declarations[0].name == "y"

    # let z = 3
    assert inner_block.body[1].kind == "let"
    assert inner_block.body[1].declarations[0].name == "z"


# ============================================================================
# BACKWARD COMPATIBILITY
# ============================================================================


def test_var_declaration_still_works():
    """
    Given existing var declarations
    When parsing with new let/const support
    Then var should still parse correctly with kind='var'
    """
    program = parse("var x = 5;")

    var_decl = program.body[0]
    assert var_decl.kind == "var"
    assert var_decl.declarations[0].name == "x"
    assert var_decl.declarations[0].init.value == 5


def test_var_without_init_still_works():
    """
    Given var declaration without initializer
    When parsing
    Then it should still work with kind='var'
    """
    program = parse("var x;")

    var_decl = program.body[0]
    assert var_decl.kind == "var"
    assert var_decl.declarations[0].name == "x"
    assert var_decl.declarations[0].init is None


# ============================================================================
# COMPLEX EXPRESSIONS WITH LET/CONST
# ============================================================================


def test_let_with_complex_expression():
    """
    Given let declaration with complex expression
    When parsing
    Then expression should be parsed correctly
    """
    program = parse("let x = 1 + 2 * 3;")

    var_decl = program.body[0]
    assert var_decl.kind == "let"
    init = var_decl.declarations[0].init
    assert isinstance(init, BinaryExpression)
    # Should be: 1 + (2 * 3) due to precedence
    assert init.operator == "+"


def test_const_with_object_literal():
    """
    Given const declaration with object literal
    When parsing
    Then object should be parsed correctly
    """
    program = parse("const obj = {x: 1, y: 2};")

    var_decl = program.body[0]
    assert var_decl.kind == "const"
    init = var_decl.declarations[0].init
    assert isinstance(init, ObjectExpression)
    assert len(init.properties) == 2


def test_let_with_array_literal():
    """
    Given let declaration with array literal
    When parsing
    Then array should be parsed correctly
    """
    program = parse("let arr = [1, 2, 3];")

    var_decl = program.body[0]
    assert var_decl.kind == "let"
    init = var_decl.declarations[0].init
    assert isinstance(init, ArrayExpression)
    assert len(init.elements) == 3
