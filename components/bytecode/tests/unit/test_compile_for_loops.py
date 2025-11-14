"""
Tests for compiling for-loop statements.

These tests verify compilation of:
- ForStatement (traditional for loops)
- ForInStatement (for-in loops over object properties)
- ForOfStatement (for-of loops over array elements)
"""

import pytest
from components.bytecode.src.compiler import BytecodeCompiler
from components.bytecode.src.opcode import Opcode
from components.parser.src.ast_nodes import (
    Program,
    ExpressionStatement,
    ForStatement,
    ForInStatement,
    ForOfStatement,
    VariableDeclaration,
    VariableDeclarator,
    Identifier,
    Literal,
    BinaryExpression,
    BlockStatement,
    CallExpression,
)
from components.shared_types.src.location import SourceLocation


def create_loc():
    """Helper to create a dummy source location."""
    return SourceLocation(filename="test.js", line=1, column=1, offset=0)


# ============================================================================
# Traditional For Loop Tests
# ============================================================================


def test_compile_traditional_for_loop():
    """
    Test traditional for loop: for (var i = 0; i < 10; i++) { ... }

    Given a traditional for loop with init, test, and update
    When compiled to bytecode
    Then it should generate proper loop structure with jumps
    """
    # Given: for (var i = 0; i < 10; i++) { i; }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            ForStatement(
                location=loc,
                init=VariableDeclaration(
                    location=loc,
                    kind="var",
                    declarations=[
                        VariableDeclarator(
                            name="i",
                            init=Literal(value=0, location=loc),
                        )
                    ],
                ),
                test=BinaryExpression(
                    location=loc,
                    operator="<",
                    left=Identifier(name="i", location=loc),
                    right=Literal(value=10, location=loc),
                ),
                update=BinaryExpression(
                    location=loc,
                    operator="=",
                    left=Identifier(name="i", location=loc),
                    right=BinaryExpression(
                        location=loc,
                        operator="+",
                        left=Identifier(name="i", location=loc),
                        right=Literal(value=1, location=loc),
                    ),
                ),
                body=BlockStatement(
                    location=loc,
                    body=[
                        ExpressionStatement(
                            location=loc,
                            expression=Identifier(name="i", location=loc),
                        )
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions

    # Expected structure:
    # 1. Init: LOAD_CONSTANT 0, STORE_LOCAL 0
    # 2. Loop start (test): LOAD_LOCAL 0, LOAD_CONSTANT 10, LESS_THAN
    # 3. JUMP_IF_FALSE to loop end
    # 4. Body: LOAD_LOCAL 0, POP
    # 5. Update: i = i + 1 (LOAD_LOCAL 0, LOAD_CONSTANT 1, ADD, DUP, STORE_LOCAL 0)
    # 6. JUMP to loop start
    # 7. Loop end: LOAD_UNDEFINED, RETURN

    # Verify we have a loop structure (at least 10+ instructions)
    assert len(instructions) >= 10

    # Verify init (LOAD_CONSTANT 0, STORE_LOCAL)
    assert instructions[0].opcode == Opcode.LOAD_CONSTANT
    assert bytecode.constant_pool[instructions[0].operand1] == 0
    assert instructions[1].opcode == Opcode.STORE_LOCAL

    # Find JUMP_IF_FALSE (conditional exit)
    jump_if_false_found = False
    for instr in instructions:
        if instr.opcode == Opcode.JUMP_IF_FALSE:
            jump_if_false_found = True
            break
    assert jump_if_false_found, "Loop should have JUMP_IF_FALSE for test"

    # Find backward JUMP (loop back)
    jump_found = False
    for instr in instructions:
        if instr.opcode == Opcode.JUMP:
            jump_found = True
            break
    assert jump_found, "Loop should have JUMP to loop start"


def test_compile_for_loop_without_init():
    """
    Test for loop without initialization: for (; i < 10; i++) { ... }

    Given a for loop with no init clause
    When compiled to bytecode
    Then it should compile without initialization
    """
    # Given: for (; i < 10; i++) { }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            ForStatement(
                location=loc,
                init=None,  # No initialization
                test=BinaryExpression(
                    location=loc,
                    operator="<",
                    left=Identifier(name="i", location=loc),
                    right=Literal(value=10, location=loc),
                ),
                update=BinaryExpression(
                    location=loc,
                    operator="=",
                    left=Identifier(name="i", location=loc),
                    right=BinaryExpression(
                        location=loc,
                        operator="+",
                        left=Identifier(name="i", location=loc),
                        right=Literal(value=1, location=loc),
                    ),
                ),
                body=BlockStatement(location=loc, body=[]),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    # Should compile successfully without init
    assert len(bytecode.instructions) > 0
    assert any(instr.opcode == Opcode.LESS_THAN for instr in bytecode.instructions)


def test_compile_for_loop_infinite():
    """
    Test infinite for loop: for (;;) { }

    Given a for loop with no clauses
    When compiled to bytecode
    Then it should generate an infinite loop structure
    """
    # Given: for (;;) { }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            ForStatement(
                location=loc,
                init=None,
                test=None,  # No test = infinite loop
                update=None,
                body=BlockStatement(location=loc, body=[]),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    # Should have at least JUMP instruction for infinite loop
    assert any(instr.opcode == Opcode.JUMP for instr in bytecode.instructions)


def test_compile_nested_for_loops():
    """
    Test nested for loops.

    Given nested for loops
    When compiled to bytecode
    Then both loops should be properly compiled with separate jump targets
    """
    # Given: for (var i = 0; i < 3; i++) { for (var j = 0; j < 2; j++) { } }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            ForStatement(
                location=loc,
                init=VariableDeclaration(
                    location=loc,
                    kind="var",
                    declarations=[
                        VariableDeclarator(
                            name="i", init=Literal(value=0, location=loc)
                        )
                    ],
                ),
                test=BinaryExpression(
                    location=loc,
                    operator="<",
                    left=Identifier(name="i", location=loc),
                    right=Literal(value=3, location=loc),
                ),
                update=BinaryExpression(
                    location=loc,
                    operator="=",
                    left=Identifier(name="i", location=loc),
                    right=BinaryExpression(
                        location=loc,
                        operator="+",
                        left=Identifier(name="i", location=loc),
                        right=Literal(value=1, location=loc),
                    ),
                ),
                body=BlockStatement(
                    location=loc,
                    body=[
                        ForStatement(
                            location=loc,
                            init=VariableDeclaration(
                                location=loc,
                                kind="var",
                                declarations=[
                                    VariableDeclarator(
                                        name="j", init=Literal(value=0, location=loc)
                                    )
                                ],
                            ),
                            test=BinaryExpression(
                                location=loc,
                                operator="<",
                                left=Identifier(name="j", location=loc),
                                right=Literal(value=2, location=loc),
                            ),
                            update=BinaryExpression(
                                location=loc,
                                operator="=",
                                left=Identifier(name="j", location=loc),
                                right=BinaryExpression(
                                    location=loc,
                                    operator="+",
                                    left=Identifier(name="j", location=loc),
                                    right=Literal(value=1, location=loc),
                                ),
                            ),
                            body=BlockStatement(location=loc, body=[]),
                        )
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    # Should have multiple JUMP_IF_FALSE and JUMP instructions for both loops
    jump_if_false_count = sum(
        1 for instr in bytecode.instructions if instr.opcode == Opcode.JUMP_IF_FALSE
    )
    jump_count = sum(
        1 for instr in bytecode.instructions if instr.opcode == Opcode.JUMP
    )

    assert (
        jump_if_false_count >= 2
    ), "Should have at least 2 conditional jumps for nested loops"
    assert jump_count >= 2, "Should have at least 2 backward jumps for nested loops"


# ============================================================================
# For-In Loop Tests
# ============================================================================


def test_compile_for_in_loop():
    """
    Test for-in loop: for (var key in obj) { ... }

    Given a for-in loop over object properties
    When compiled to bytecode
    Then it should iterate over object keys
    """
    # Given: for (var key in obj) { key; }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            ForInStatement(
                location=loc,
                left=VariableDeclaration(
                    location=loc,
                    kind="var",
                    declarations=[VariableDeclarator(name="key", init=None)],
                ),
                right=Identifier(name="obj", location=loc),
                body=BlockStatement(
                    location=loc,
                    body=[
                        ExpressionStatement(
                            location=loc,
                            expression=Identifier(name="key", location=loc),
                        )
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    # Should compile successfully
    assert len(bytecode.instructions) > 0

    # Should have loop structure with JUMP and JUMP_IF_FALSE
    jump_if_false_found = any(
        instr.opcode == Opcode.JUMP_IF_FALSE for instr in bytecode.instructions
    )
    jump_found = any(instr.opcode == Opcode.JUMP for instr in bytecode.instructions)

    assert jump_if_false_found, "For-in loop should have conditional jump"
    assert jump_found, "For-in loop should have backward jump"


def test_compile_for_in_with_identifier_left():
    """
    Test for-in loop with identifier (not declaration): for (key in obj) { ... }

    Given a for-in loop with identifier on left
    When compiled to bytecode
    Then it should use existing variable
    """
    # Given: for (key in obj) { }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            ForInStatement(
                location=loc,
                left=Identifier(name="key", location=loc),
                right=Identifier(name="obj", location=loc),
                body=BlockStatement(location=loc, body=[]),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    assert len(bytecode.instructions) > 0


# ============================================================================
# For-Of Loop Tests
# ============================================================================


def test_compile_for_of_loop():
    """
    Test for-of loop: for (var value of array) { ... }

    Given a for-of loop over array elements
    When compiled to bytecode
    Then it should iterate over array values
    """
    # Given: for (var value of arr) { value; }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            ForOfStatement(
                location=loc,
                left=VariableDeclaration(
                    location=loc,
                    kind="var",
                    declarations=[VariableDeclarator(name="value", init=None)],
                ),
                right=Identifier(name="arr", location=loc),
                body=BlockStatement(
                    location=loc,
                    body=[
                        ExpressionStatement(
                            location=loc,
                            expression=Identifier(name="value", location=loc),
                        )
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    # Should compile successfully
    assert len(bytecode.instructions) > 0

    # Should have loop structure
    jump_if_false_found = any(
        instr.opcode == Opcode.JUMP_IF_FALSE for instr in bytecode.instructions
    )
    jump_found = any(instr.opcode == Opcode.JUMP for instr in bytecode.instructions)

    assert jump_if_false_found, "For-of loop should have conditional jump"
    assert jump_found, "For-of loop should have backward jump"


def test_compile_for_of_with_identifier_left():
    """
    Test for-of loop with identifier: for (value of array) { ... }

    Given a for-of loop with identifier on left
    When compiled to bytecode
    Then it should use existing variable
    """
    # Given: for (value of arr) { }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            ForOfStatement(
                location=loc,
                left=Identifier(name="value", location=loc),
                right=Identifier(name="arr", location=loc),
                body=BlockStatement(location=loc, body=[]),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    assert len(bytecode.instructions) > 0


def test_compile_nested_for_in_and_for_of():
    """
    Test nested for-in and for-of loops.

    Given nested for-in and for-of loops
    When compiled to bytecode
    Then both loops should be properly compiled
    """
    # Given: for (var key in obj) { for (var val of arr) { } }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            ForInStatement(
                location=loc,
                left=VariableDeclaration(
                    location=loc,
                    kind="var",
                    declarations=[VariableDeclarator(name="key", init=None)],
                ),
                right=Identifier(name="obj", location=loc),
                body=BlockStatement(
                    location=loc,
                    body=[
                        ForOfStatement(
                            location=loc,
                            left=VariableDeclaration(
                                location=loc,
                                kind="var",
                                declarations=[
                                    VariableDeclarator(name="val", init=None)
                                ],
                            ),
                            right=Identifier(name="arr", location=loc),
                            body=BlockStatement(location=loc, body=[]),
                        )
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    # Should compile successfully with nested loops
    assert len(bytecode.instructions) > 0

    # Should have multiple jumps for both loops
    jump_count = sum(
        1 for instr in bytecode.instructions if instr.opcode == Opcode.JUMP
    )
    assert jump_count >= 2, "Should have backward jumps for both loops"
