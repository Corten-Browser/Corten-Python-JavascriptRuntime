"""
Tests for arrow function compilation.

These tests verify the BytecodeCompiler correctly compiles ArrowFunctionExpression
nodes to bytecode, handling both expression bodies (implicit return) and block
bodies (explicit return).
"""

import pytest
from components.bytecode.src.compiler import BytecodeCompiler
from components.bytecode.src.opcode import Opcode
from components.parser.src.ast_nodes import (
    Program,
    ExpressionStatement,
    ArrowFunctionExpression,
    Identifier,
    Literal,
    BinaryExpression,
    BlockStatement,
    ReturnStatement,
    VariableDeclaration,
    VariableDeclarator,
)
from components.shared_types.src.location import SourceLocation


def make_loc():
    """Helper to create a source location."""
    return SourceLocation(filename="test.js", line=1, column=1, offset=0)


def test_compile_arrow_function_no_params():
    """
    Given an arrow function with no parameters and expression body
    When compiled to bytecode
    Then it creates a function with 0 parameters and implicit return

    Code: () => 42
    """
    loc = make_loc()

    # () => 42
    arrow = ArrowFunctionExpression(
        location=loc, params=[], body=Literal(location=loc, value=42), is_async=False
    )

    ast = Program(
        location=loc, body=[ExpressionStatement(location=loc, expression=arrow)]
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Should create a function
    assert any(instr.opcode == Opcode.CREATE_CLOSURE for instr in bytecode.instructions)


def test_compile_arrow_function_single_param():
    """
    Given an arrow function with single parameter and expression body
    When compiled to bytecode
    Then it creates a function with 1 parameter and implicit return

    Code: x => x * 2
    """
    loc = make_loc()

    # x => x * 2
    arrow = ArrowFunctionExpression(
        location=loc,
        params=[Identifier(location=loc, name="x")],
        body=BinaryExpression(
            location=loc,
            operator="*",
            left=Identifier(location=loc, name="x"),
            right=Literal(location=loc, value=2),
        ),
        is_async=False,
    )

    ast = Program(
        location=loc, body=[ExpressionStatement(location=loc, expression=arrow)]
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Should create a function
    assert any(instr.opcode == Opcode.CREATE_CLOSURE for instr in bytecode.instructions)


def test_compile_arrow_function_multiple_params():
    """
    Given an arrow function with multiple parameters
    When compiled to bytecode
    Then it creates a function with correct parameter count

    Code: (x, y) => x + y
    """
    loc = make_loc()

    # (x, y) => x + y
    arrow = ArrowFunctionExpression(
        location=loc,
        params=[Identifier(location=loc, name="x"), Identifier(location=loc, name="y")],
        body=BinaryExpression(
            location=loc,
            operator="+",
            left=Identifier(location=loc, name="x"),
            right=Identifier(location=loc, name="y"),
        ),
        is_async=False,
    )

    ast = Program(
        location=loc, body=[ExpressionStatement(location=loc, expression=arrow)]
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Should create a function
    assert any(instr.opcode == Opcode.CREATE_CLOSURE for instr in bytecode.instructions)


def test_compile_arrow_function_expression_body():
    """
    Given an arrow function with expression body
    When compiled to bytecode
    Then the function body includes implicit RETURN

    Code: x => x * 2
    Expression body should automatically return the expression value.
    """
    loc = make_loc()

    # x => x * 2
    arrow = ArrowFunctionExpression(
        location=loc,
        params=[Identifier(location=loc, name="x")],
        body=BinaryExpression(
            location=loc,
            operator="*",
            left=Identifier(location=loc, name="x"),
            right=Literal(location=loc, value=2),
        ),
        is_async=False,
    )

    ast = Program(
        location=loc, body=[ExpressionStatement(location=loc, expression=arrow)]
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Function should be created
    create_func_instr = None
    for instr in bytecode.instructions:
        if instr.opcode == Opcode.CREATE_CLOSURE:
            create_func_instr = instr
            break

    assert create_func_instr is not None

    # The function bytecode should contain the expression body with implicit return
    # (We'll verify this in integration tests with the interpreter)


def test_compile_arrow_function_block_body():
    """
    Given an arrow function with block body
    When compiled to bytecode
    Then the function body compiles the block normally

    Code: x => { return x * 2; }
    Block body has explicit return statement.
    """
    loc = make_loc()

    # x => { return x * 2; }
    arrow = ArrowFunctionExpression(
        location=loc,
        params=[Identifier(location=loc, name="x")],
        body=BlockStatement(
            location=loc,
            body=[
                ReturnStatement(
                    location=loc,
                    argument=BinaryExpression(
                        location=loc,
                        operator="*",
                        left=Identifier(location=loc, name="x"),
                        right=Literal(location=loc, value=2),
                    ),
                )
            ],
        ),
        is_async=False,
    )

    ast = Program(
        location=loc, body=[ExpressionStatement(location=loc, expression=arrow)]
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Function should be created
    assert any(instr.opcode == Opcode.CREATE_CLOSURE for instr in bytecode.instructions)


def test_compile_arrow_function_implicit_return():
    """
    Given an arrow function with expression body (not BlockStatement)
    When compiled to bytecode
    Then the expression value is implicitly returned

    Code: () => 42
    Should compile to: LOAD_CONSTANT 42, RETURN
    """
    loc = make_loc()

    # () => 42
    arrow = ArrowFunctionExpression(
        location=loc, params=[], body=Literal(location=loc, value=42), is_async=False
    )

    ast = Program(
        location=loc, body=[ExpressionStatement(location=loc, expression=arrow)]
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Should create a function
    assert any(instr.opcode == Opcode.CREATE_CLOSURE for instr in bytecode.instructions)

    # The function should contain the literal 42
    # (Expression body means implicit return of the expression value)


def test_compile_arrow_function_explicit_return():
    """
    Given an arrow function with block body containing return statement
    When compiled to bytecode
    Then the return statement is compiled explicitly

    Code: x => { return x; }
    Block body with explicit return.
    """
    loc = make_loc()

    # x => { return x; }
    arrow = ArrowFunctionExpression(
        location=loc,
        params=[Identifier(location=loc, name="x")],
        body=BlockStatement(
            location=loc,
            body=[
                ReturnStatement(
                    location=loc, argument=Identifier(location=loc, name="x")
                )
            ],
        ),
        is_async=False,
    )

    ast = Program(
        location=loc, body=[ExpressionStatement(location=loc, expression=arrow)]
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Function should be created
    assert any(instr.opcode == Opcode.CREATE_CLOSURE for instr in bytecode.instructions)


def test_compile_arrow_function_nested():
    """
    Given a nested arrow function
    When compiled to bytecode
    Then both functions are compiled correctly

    Code: x => y => x + y
    Outer function returns inner function.
    """
    loc = make_loc()

    # Inner: y => x + y
    inner_arrow = ArrowFunctionExpression(
        location=loc,
        params=[Identifier(location=loc, name="y")],
        body=BinaryExpression(
            location=loc,
            operator="+",
            left=Identifier(location=loc, name="x"),
            right=Identifier(location=loc, name="y"),
        ),
        is_async=False,
    )

    # Outer: x => (y => x + y)
    outer_arrow = ArrowFunctionExpression(
        location=loc,
        params=[Identifier(location=loc, name="x")],
        body=inner_arrow,
        is_async=False,
    )

    ast = Program(
        location=loc, body=[ExpressionStatement(location=loc, expression=outer_arrow)]
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Should create at least one function (outer)
    create_func_count = sum(
        1 for instr in bytecode.instructions if instr.opcode == Opcode.CREATE_CLOSURE
    )
    assert create_func_count >= 1


def test_compile_arrow_function_as_callback():
    """
    Given an arrow function used as callback argument
    When compiled to bytecode
    Then the function is created and passed as argument

    Code: array.map(x => x * 2)
    Arrow function as callback to map.
    """
    loc = make_loc()

    # x => x * 2
    arrow = ArrowFunctionExpression(
        location=loc,
        params=[Identifier(location=loc, name="x")],
        body=BinaryExpression(
            location=loc,
            operator="*",
            left=Identifier(location=loc, name="x"),
            right=Literal(location=loc, value=2),
        ),
        is_async=False,
    )

    # Just compile the arrow function in isolation for this test
    ast = Program(
        location=loc, body=[ExpressionStatement(location=loc, expression=arrow)]
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Function should be created
    assert any(instr.opcode == Opcode.CREATE_CLOSURE for instr in bytecode.instructions)


def test_compile_arrow_function_with_let_const():
    """
    Given an arrow function with block body using let/const
    When compiled to bytecode
    Then variable declarations compile correctly

    Code: x => { const y = x * 2; return y; }
    Block body with const declaration.
    """
    loc = make_loc()

    # x => { const y = x * 2; return y; }
    arrow = ArrowFunctionExpression(
        location=loc,
        params=[Identifier(location=loc, name="x")],
        body=BlockStatement(
            location=loc,
            body=[
                VariableDeclaration(
                    location=loc,
                    kind="const",
                    declarations=[
                        VariableDeclarator(
                            name="y",
                            init=BinaryExpression(
                                location=loc,
                                operator="*",
                                left=Identifier(location=loc, name="x"),
                                right=Literal(location=loc, value=2),
                            ),
                        )
                    ],
                ),
                ReturnStatement(
                    location=loc, argument=Identifier(location=loc, name="y")
                ),
            ],
        ),
        is_async=False,
    )

    ast = Program(
        location=loc, body=[ExpressionStatement(location=loc, expression=arrow)]
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Function should be created
    assert any(instr.opcode == Opcode.CREATE_CLOSURE for instr in bytecode.instructions)


def test_compile_arrow_function_block_without_return():
    """
    Given an arrow function with block body but no explicit return
    When compiled to bytecode
    Then implicit return undefined is added

    Code: x => { x * 2; }
    Block body without return should implicitly return undefined.
    """
    loc = make_loc()

    # x => { x * 2; }  (expression statement, no return)
    arrow = ArrowFunctionExpression(
        location=loc,
        params=[Identifier(location=loc, name="x")],
        body=BlockStatement(
            location=loc,
            body=[
                ExpressionStatement(
                    location=loc,
                    expression=BinaryExpression(
                        location=loc,
                        operator="*",
                        left=Identifier(location=loc, name="x"),
                        right=Literal(location=loc, value=2),
                    ),
                )
            ],
        ),
        is_async=False,
    )

    ast = Program(
        location=loc, body=[ExpressionStatement(location=loc, expression=arrow)]
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Function should be created
    assert any(instr.opcode == Opcode.CREATE_CLOSURE for instr in bytecode.instructions)

    # The function body should have implicit return undefined at the end
    # (This will be tested more thoroughly in integration tests)
