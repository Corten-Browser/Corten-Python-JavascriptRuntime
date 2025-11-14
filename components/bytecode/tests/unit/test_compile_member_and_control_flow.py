"""
Tests for compiling MemberExpression and control flow statements.

These tests verify compilation of:
- MemberExpression (obj.property)
- IfStatement (if/else)
- WhileStatement (while loops)
"""

import pytest
from components.bytecode.src.compiler import BytecodeCompiler
from components.bytecode.src.opcode import Opcode
from components.parser.src.ast_nodes import (
    Program,
    ExpressionStatement,
    MemberExpression,
    Identifier,
    Literal,
    IfStatement,
    WhileStatement,
    BlockStatement,
    BinaryExpression,
    VariableDeclaration,
    VariableDeclarator,
)
from components.shared_types.src.location import SourceLocation


def create_loc():
    """Helper to create a dummy source location."""
    return SourceLocation(filename="test.js", line=1, column=1, offset=0)


# ============================================================================
# MemberExpression Tests
# ============================================================================


def test_compile_member_expression_direct():
    """
    Test obj.property compilation (non-computed).

    Given a member expression with dot notation
    When compiled to bytecode
    Then it should load the object and property
    """
    # Given: obj.name
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=MemberExpression(
                    location=loc,
                    object=Identifier(name="obj", location=loc),
                    property=Identifier(name="name", location=loc),
                    computed=False,
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    # Should have: LOAD_GLOBAL "obj", LOAD_PROPERTY "name", RETURN
    # Note: Last expression value is preserved (no POP) for REPL/eval mode
    instructions = bytecode.instructions
    assert len(instructions) >= 3

    # Load object
    assert instructions[0].opcode == Opcode.LOAD_GLOBAL
    assert bytecode.constant_pool[instructions[0].operand1] == "obj"

    # Load property
    assert instructions[1].opcode == Opcode.LOAD_PROPERTY
    assert bytecode.constant_pool[instructions[1].operand1] == "name"

    # Return (expression value preserved)
    assert instructions[2].opcode == Opcode.RETURN


def test_compile_member_expression_computed():
    """
    Test obj[expr] compilation (computed).

    Given a member expression with bracket notation
    When compiled to bytecode
    Then it should load the object, evaluate expression, and get property
    """
    # Given: obj[0]
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=MemberExpression(
                    location=loc,
                    object=Identifier(name="obj", location=loc),
                    property=Literal(value=0, location=loc),
                    computed=True,
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    # Should have: LOAD_GLOBAL "obj", LOAD_CONSTANT 0, LOAD_ELEMENT, RETURN
    # Note: Last expression value is preserved (no POP) for REPL/eval mode
    instructions = bytecode.instructions
    assert len(instructions) >= 4

    # Load object
    assert instructions[0].opcode == Opcode.LOAD_GLOBAL
    assert bytecode.constant_pool[instructions[0].operand1] == "obj"

    # Load index
    assert instructions[1].opcode == Opcode.LOAD_CONSTANT
    assert bytecode.constant_pool[instructions[1].operand1] == 0

    # Load element
    assert instructions[2].opcode == Opcode.LOAD_ELEMENT

    # Return (expression value preserved)
    assert instructions[3].opcode == Opcode.RETURN


# ============================================================================
# IfStatement Tests
# ============================================================================


def test_compile_if_statement_without_else():
    """
    Test if statement compilation without else branch.

    Given an if statement without else
    When compiled to bytecode
    Then it should jump over consequent if condition is false
    """
    # Given: if (x > 0) { var y = 1; }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            IfStatement(
                location=loc,
                test=BinaryExpression(
                    location=loc,
                    operator=">",
                    left=Identifier(name="x", location=loc),
                    right=Literal(value=0, location=loc),
                ),
                consequent=BlockStatement(
                    location=loc,
                    body=[
                        VariableDeclaration(
                            location=loc,
                            kind="var",
                            declarations=[
                                VariableDeclarator(
                                    name="y",
                                    init=Literal(value=1, location=loc),
                                )
                            ],
                        )
                    ],
                ),
                alternate=None,
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions

    # Should have test, JUMP_IF_FALSE, consequent, end
    # Test: LOAD_GLOBAL "x", LOAD_CONSTANT 0, GREATER_THAN
    assert instructions[0].opcode == Opcode.LOAD_GLOBAL
    assert instructions[1].opcode == Opcode.LOAD_CONSTANT
    assert instructions[2].opcode == Opcode.GREATER_THAN

    # JUMP_IF_FALSE (should point past consequent)
    assert instructions[3].opcode == Opcode.JUMP_IF_FALSE
    jump_target = instructions[3].operand1

    # Consequent: LOAD_CONSTANT 1, STORE_LOCAL
    consequent_start = 4
    assert instructions[consequent_start].opcode == Opcode.LOAD_CONSTANT

    # Jump target should point to end (past consequent)
    assert jump_target > consequent_start


def test_compile_if_statement_with_else():
    """
    Test if statement compilation with else branch.

    Given an if-else statement
    When compiled to bytecode
    Then it should jump correctly between branches
    """
    # Given: if (x > 0) { var y = 1; } else { var y = 2; }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            IfStatement(
                location=loc,
                test=BinaryExpression(
                    location=loc,
                    operator=">",
                    left=Identifier(name="x", location=loc),
                    right=Literal(value=0, location=loc),
                ),
                consequent=BlockStatement(
                    location=loc,
                    body=[
                        VariableDeclaration(
                            location=loc,
                            kind="var",
                            declarations=[
                                VariableDeclarator(
                                    name="y",
                                    init=Literal(value=1, location=loc),
                                )
                            ],
                        )
                    ],
                ),
                alternate=BlockStatement(
                    location=loc,
                    body=[
                        VariableDeclaration(
                            location=loc,
                            kind="var",
                            declarations=[
                                VariableDeclarator(
                                    name="z",
                                    init=Literal(value=2, location=loc),
                                )
                            ],
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

    # Test condition
    assert instructions[0].opcode == Opcode.LOAD_GLOBAL
    assert instructions[1].opcode == Opcode.LOAD_CONSTANT
    assert instructions[2].opcode == Opcode.GREATER_THAN

    # JUMP_IF_FALSE (should point to else branch)
    assert instructions[3].opcode == Opcode.JUMP_IF_FALSE
    jump_to_else = instructions[3].operand1

    # There should be a JUMP at end of consequent (to skip else)
    # Find it by scanning forward
    found_jump = False
    for i in range(4, len(instructions)):
        if instructions[i].opcode == Opcode.JUMP:
            found_jump = True
            break
    assert found_jump, "Should have JUMP at end of consequent"


# ============================================================================
# WhileStatement Tests
# ============================================================================


def test_compile_while_statement():
    """
    Test while loop compilation.

    Given a while statement
    When compiled to bytecode
    Then it should create a loop with condition check and jump back
    """
    # Given: while (i < 10) { i = i + 1; }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            WhileStatement(
                location=loc,
                test=BinaryExpression(
                    location=loc,
                    operator="<",
                    left=Identifier(name="i", location=loc),
                    right=Literal(value=10, location=loc),
                ),
                body=BlockStatement(
                    location=loc,
                    body=[
                        ExpressionStatement(
                            location=loc,
                            expression=BinaryExpression(
                                location=loc,
                                operator="+",
                                left=Identifier(name="i", location=loc),
                                right=Literal(value=1, location=loc),
                            ),
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

    # Loop should start at beginning (index 0)
    loop_start = 0

    # Test condition: LOAD_GLOBAL "i", LOAD_CONSTANT 10, LESS_THAN
    assert instructions[0].opcode == Opcode.LOAD_GLOBAL
    assert instructions[1].opcode == Opcode.LOAD_CONSTANT
    assert instructions[2].opcode == Opcode.LESS_THAN

    # JUMP_IF_FALSE (should point past loop body)
    assert instructions[3].opcode == Opcode.JUMP_IF_FALSE
    jump_to_end = instructions[3].operand1

    # Should have JUMP back to loop start at end of body
    # Scan backward from jump_to_end to find it
    found_jump_back = False
    for i in range(4, jump_to_end):
        if (
            instructions[i].opcode == Opcode.JUMP
            and instructions[i].operand1 == loop_start
        ):
            found_jump_back = True
            break
    assert found_jump_back, "Should have JUMP back to loop start"


def test_compile_nested_control_flow():
    """
    Test nested if inside while.

    Given nested control flow structures
    When compiled to bytecode
    Then both should compile correctly
    """
    # Given: while (i < 10) { if (i > 5) { i = 0; } }
    loc = create_loc()
    ast = Program(
        location=loc,
        body=[
            WhileStatement(
                location=loc,
                test=BinaryExpression(
                    location=loc,
                    operator="<",
                    left=Identifier(name="i", location=loc),
                    right=Literal(value=10, location=loc),
                ),
                body=BlockStatement(
                    location=loc,
                    body=[
                        IfStatement(
                            location=loc,
                            test=BinaryExpression(
                                location=loc,
                                operator=">",
                                left=Identifier(name="i", location=loc),
                                right=Literal(value=5, location=loc),
                            ),
                            consequent=BlockStatement(
                                location=loc,
                                body=[
                                    ExpressionStatement(
                                        location=loc,
                                        expression=Literal(value=0, location=loc),
                                    )
                                ],
                            ),
                            alternate=None,
                        )
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then - should compile without errors
    assert len(bytecode.instructions) > 0

    # Should have both JUMP (for while) and JUMP_IF_FALSE (for if and while)
    jump_count = sum(1 for i in bytecode.instructions if i.opcode == Opcode.JUMP)
    jump_if_false_count = sum(
        1 for i in bytecode.instructions if i.opcode == Opcode.JUMP_IF_FALSE
    )

    assert jump_count >= 1, "Should have at least one JUMP (back to loop start)"
    assert jump_if_false_count >= 2, "Should have JUMP_IF_FALSE for both while and if"
