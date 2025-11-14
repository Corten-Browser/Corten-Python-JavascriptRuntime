"""
Tests for let/const compilation support.

Phase 1: let/const compiled as function-scoped (like var).
Phase 2 TODO: Implement full block scope, TDZ, and const enforcement.

Following TDD methodology - these tests written BEFORE implementation.
"""

import pytest
from components.bytecode.src.compiler import BytecodeCompiler
from components.parser.src.ast_nodes import (
    Program,
    VariableDeclaration,
    VariableDeclarator,
    Identifier,
    Literal,
    ExpressionStatement,
    BinaryExpression,
    ObjectExpression,
    Property,
)
from components.bytecode.src.opcode import Opcode
from components.shared_types.src.location import SourceLocation


def test_compile_let_declaration():
    """
    Given a let declaration with initializer
    When bytecode is compiled
    Then it should generate LOAD_CONSTANT and STORE_LOCAL instructions
    """
    # Given: let x = 42;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="let",
                declarations=[
                    VariableDeclarator(
                        name="x",
                        init=Literal(location=loc, value=42),
                    )
                ],
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.LOAD_CONSTANT in opcodes
    assert Opcode.STORE_LOCAL in opcodes
    assert bytecode.local_count == 1


def test_compile_let_without_init():
    """
    Given a let declaration without initializer
    When bytecode is compiled
    Then it should initialize to undefined
    """
    # Given: let x;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="let",
                declarations=[
                    VariableDeclarator(
                        name="x",
                        init=None,
                    )
                ],
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.LOAD_UNDEFINED in opcodes
    assert Opcode.STORE_LOCAL in opcodes


def test_compile_let_multiple():
    """
    Given multiple let declarations
    When bytecode is compiled
    Then each variable should get a unique local slot
    """
    # Given: let x = 1, y = 2, z = 3;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="let",
                declarations=[
                    VariableDeclarator(name="x", init=Literal(location=loc, value=1)),
                    VariableDeclarator(name="y", init=Literal(location=loc, value=2)),
                    VariableDeclarator(name="z", init=Literal(location=loc, value=3)),
                ],
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    assert bytecode.local_count == 3
    # Should have 3 STORE_LOCAL instructions
    store_local_count = sum(
        1 for instr in bytecode.instructions if instr.opcode == Opcode.STORE_LOCAL
    )
    assert store_local_count == 3


def test_compile_const_declaration():
    """
    Given a const declaration with initializer
    When bytecode is compiled
    Then it should generate LOAD_CONSTANT and STORE_LOCAL instructions
    """
    # Given: const x = 42;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="const",
                declarations=[
                    VariableDeclarator(
                        name="x",
                        init=Literal(location=loc, value=42),
                    )
                ],
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.LOAD_CONSTANT in opcodes
    assert Opcode.STORE_LOCAL in opcodes
    assert bytecode.local_count == 1


def test_compile_const_multiple():
    """
    Given multiple const declarations
    When bytecode is compiled
    Then each variable should get a unique local slot
    """
    # Given: const x = 1, y = 2;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="const",
                declarations=[
                    VariableDeclarator(name="x", init=Literal(location=loc, value=1)),
                    VariableDeclarator(name="y", init=Literal(location=loc, value=2)),
                ],
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    assert bytecode.local_count == 2
    store_local_count = sum(
        1 for instr in bytecode.instructions if instr.opcode == Opcode.STORE_LOCAL
    )
    assert store_local_count == 2


def test_compile_mixed_var_let_const():
    """
    Given mixed var, let, and const declarations
    When bytecode is compiled
    Then all should be compiled correctly with unique local slots
    """
    # Given:
    # var a = 1;
    # let b = 2;
    # const c = 3;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="var",
                declarations=[
                    VariableDeclarator(name="a", init=Literal(location=loc, value=1))
                ],
            ),
            VariableDeclaration(
                location=loc,
                kind="let",
                declarations=[
                    VariableDeclarator(name="b", init=Literal(location=loc, value=2))
                ],
            ),
            VariableDeclaration(
                location=loc,
                kind="const",
                declarations=[
                    VariableDeclarator(name="c", init=Literal(location=loc, value=3))
                ],
            ),
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    assert bytecode.local_count == 3
    store_local_count = sum(
        1 for instr in bytecode.instructions if instr.opcode == Opcode.STORE_LOCAL
    )
    assert store_local_count == 3


def test_compile_let_with_expression():
    """
    Given a let declaration with complex expression
    When bytecode is compiled
    Then expression should be compiled correctly
    """
    # Given: let x = 10 + 20;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="let",
                declarations=[
                    VariableDeclarator(
                        name="x",
                        init=BinaryExpression(
                            location=loc,
                            operator="+",
                            left=Literal(location=loc, value=10),
                            right=Literal(location=loc, value=20),
                        ),
                    )
                ],
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.ADD in opcodes
    assert Opcode.STORE_LOCAL in opcodes


def test_compile_const_with_object_literal():
    """
    Given a const declaration with object literal
    When bytecode is compiled
    Then object should be compiled correctly
    """
    # Given: const obj = { x: 1, y: 2 };
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="const",
                declarations=[
                    VariableDeclarator(
                        name="obj",
                        init=ObjectExpression(
                            location=loc,
                            properties=[
                                Property(
                                    location=loc,
                                    key=Identifier(location=loc, name="x"),
                                    value=Literal(location=loc, value=1),
                                    kind="init",
                                    computed=False,
                                ),
                                Property(
                                    location=loc,
                                    key=Identifier(location=loc, name="y"),
                                    value=Literal(location=loc, value=2),
                                    kind="init",
                                    computed=False,
                                ),
                            ],
                        ),
                    )
                ],
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.CREATE_OBJECT in opcodes
    assert Opcode.STORE_LOCAL in opcodes


def test_compile_let_in_block():
    """
    Given a let declaration
    When bytecode is compiled
    Then it should compile successfully
    And note: Phase 1 does not enforce block scope boundaries
    """
    # Given: let x = 42;
    # Note: In Phase 1, we don't have block statements yet,
    # but this test documents that let works at statement level
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="let",
                declarations=[
                    VariableDeclarator(name="x", init=Literal(location=loc, value=42))
                ],
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    assert bytecode.local_count == 1
    # Phase 2 TODO: Add block scope tracking


def test_compile_const_in_block():
    """
    Given a const declaration
    When bytecode is compiled
    Then it should compile successfully
    And note: Phase 1 does not enforce block scope boundaries
    """
    # Given: const x = 42;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="const",
                declarations=[
                    VariableDeclarator(name="x", init=Literal(location=loc, value=42))
                ],
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    assert bytecode.local_count == 1
    # Phase 2 TODO: Add block scope tracking


def test_let_reference_after_declaration():
    """
    Given a let declaration followed by reference
    When bytecode is compiled
    Then reference should load from local
    """
    # Given:
    # let x = 42;
    # x;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="let",
                declarations=[
                    VariableDeclarator(name="x", init=Literal(location=loc, value=42))
                ],
            ),
            ExpressionStatement(
                location=loc, expression=Identifier(location=loc, name="x")
            ),
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    # Should have LOAD_LOCAL for the reference (not LOAD_GLOBAL)
    load_local_count = sum(
        1 for instr in bytecode.instructions if instr.opcode == Opcode.LOAD_LOCAL
    )
    assert load_local_count >= 1


def test_const_reference_after_declaration():
    """
    Given a const declaration followed by reference
    When bytecode is compiled
    Then reference should load from local
    """
    # Given:
    # const x = 42;
    # x;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="const",
                declarations=[
                    VariableDeclarator(name="x", init=Literal(location=loc, value=42))
                ],
            ),
            ExpressionStatement(
                location=loc, expression=Identifier(location=loc, name="x")
            ),
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    # Should have LOAD_LOCAL for the reference (not LOAD_GLOBAL)
    load_local_count = sum(
        1 for instr in bytecode.instructions if instr.opcode == Opcode.LOAD_LOCAL
    )
    assert load_local_count >= 1
