"""
Comprehensive tests for BytecodeCompiler.

These tests cover variable declarations, return statements, identifiers,
and various operators to achieve better code coverage.
"""

import pytest


def test_compile_variable_declaration():
    """Test compiling variable declaration."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import (
        Program,
        VariableDeclaration,
        VariableDeclarator,
        Identifier,
        Literal,
    )
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    # Program: var x = 42;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="var",
                declarations=[
                    VariableDeclarator(
                        name="x",
                        init=Literal(location=loc, value=42),
                    )
                ],
            )
        ],
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Should have LOAD_CONSTANT, STORE_LOCAL
    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.LOAD_CONSTANT in opcodes
    assert Opcode.STORE_LOCAL in opcodes
    assert bytecode.local_count == 1


def test_compile_variable_declaration_without_init():
    """Test compiling variable declaration without initializer."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import (
        Program,
        VariableDeclaration,
        VariableDeclarator,
        Identifier,
    )
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    # Program: var x;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            VariableDeclaration(
                location=loc,
                kind="var",
                declarations=[
                    VariableDeclarator(
                        name="x",
                        init=None,
                    )
                ],
            )
        ],
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Should have LOAD_UNDEFINED, STORE_LOCAL
    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.LOAD_UNDEFINED in opcodes
    assert Opcode.STORE_LOCAL in opcodes


def test_compile_identifier():
    """Test compiling identifier reference."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import (
        Program,
        ExpressionStatement,
        Identifier,
    )
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    # Program: x;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc, expression=Identifier(location=loc, name="x")
            )
        ],
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Should have LOAD_GLOBAL (since x is not defined locally)
    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.LOAD_GLOBAL in opcodes


def test_compile_return_statement_with_argument():
    """Test compiling return statement with argument."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import (
        Program,
        ReturnStatement,
        Literal,
    )
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    # Program: return 42;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[ReturnStatement(location=loc, argument=Literal(location=loc, value=42))],
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.LOAD_CONSTANT in opcodes
    assert Opcode.RETURN in opcodes


def test_compile_return_statement_without_argument():
    """Test compiling return statement without argument."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import Program, ReturnStatement
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    # Program: return;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[ReturnStatement(location=loc, argument=None)],
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.LOAD_UNDEFINED in opcodes
    assert Opcode.RETURN in opcodes


def test_compile_all_comparison_operators():
    """Test compiling all comparison operators."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import (
        Program,
        ExpressionStatement,
        BinaryExpression,
        Literal,
    )
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    operators_to_opcodes = [
        ("==", Opcode.EQUAL),
        ("!=", Opcode.NOT_EQUAL),
        ("<", Opcode.LESS_THAN),
        ("<=", Opcode.LESS_EQUAL),
        (">", Opcode.GREATER_THAN),
        (">=", Opcode.GREATER_EQUAL),
    ]

    for operator, expected_opcode in operators_to_opcodes:
        ast = Program(
            location=loc,
            body=[
                ExpressionStatement(
                    location=loc,
                    expression=BinaryExpression(
                        location=loc,
                        operator=operator,
                        left=Literal(location=loc, value=1),
                        right=Literal(location=loc, value=2),
                    ),
                )
            ],
        )

        compiler = BytecodeCompiler(ast)
        bytecode = compiler.compile()

        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert expected_opcode in opcodes, f"Failed for operator {operator}"


def test_compile_all_arithmetic_operators():
    """Test compiling all arithmetic operators."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import (
        Program,
        ExpressionStatement,
        BinaryExpression,
        Literal,
    )
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    operators_to_opcodes = [
        ("-", Opcode.SUBTRACT),
        ("*", Opcode.MULTIPLY),
        ("/", Opcode.DIVIDE),
        ("%", Opcode.MODULO),
    ]

    for operator, expected_opcode in operators_to_opcodes:
        ast = Program(
            location=loc,
            body=[
                ExpressionStatement(
                    location=loc,
                    expression=BinaryExpression(
                        location=loc,
                        operator=operator,
                        left=Literal(location=loc, value=10),
                        right=Literal(location=loc, value=2),
                    ),
                )
            ],
        )

        compiler = BytecodeCompiler(ast)
        bytecode = compiler.compile()

        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert expected_opcode in opcodes, f"Failed for operator {operator}"


def test_compile_literal_null():
    """Test compiling null literal."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import (
        Program,
        ExpressionStatement,
        Literal,
    )
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc, expression=Literal(location=loc, value=None)
            )
        ],
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.LOAD_NULL in opcodes


def test_compile_literal_booleans():
    """Test compiling boolean literals."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import (
        Program,
        ExpressionStatement,
        Literal,
    )
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    # Test true
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc, expression=Literal(location=loc, value=True)
            )
        ],
    )
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()
    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.LOAD_TRUE in opcodes

    # Test false
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc, expression=Literal(location=loc, value=False)
            )
        ],
    )
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()
    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.LOAD_FALSE in opcodes


def test_compile_call_expression():
    """Test compiling function call expression."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import (
        Program,
        ExpressionStatement,
        CallExpression,
        Identifier,
        Literal,
    )
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    # Program: foo(1, 2);
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=CallExpression(
                    location=loc,
                    callee=Identifier(location=loc, name="foo"),
                    arguments=[
                        Literal(location=loc, value=1),
                        Literal(location=loc, value=2),
                    ],
                ),
            )
        ],
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.CALL_FUNCTION in opcodes
    # Check argument count
    call_instr = next(
        instr for instr in bytecode.instructions if instr.opcode == Opcode.CALL_FUNCTION
    )
    assert call_instr.operand1 == 2  # Two arguments


def test_compile_unsupported_statement_raises_error():
    """Test that unsupported statement type raises CompileError."""
    from components.bytecode.src.compiler import BytecodeCompiler, CompileError
    from components.parser.src.ast_nodes import Program, Statement
    from components.shared_types.src.location import SourceLocation

    # Create a minimal unsupported statement type
    class UnsupportedStatement(Statement):
        pass

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(location=loc, body=[UnsupportedStatement(location=loc)])

    compiler = BytecodeCompiler(ast)

    with pytest.raises(CompileError):
        compiler.compile()


def test_compile_unsupported_expression_raises_error():
    """Test that unsupported expression type raises CompileError."""
    from components.bytecode.src.compiler import BytecodeCompiler, CompileError
    from components.parser.src.ast_nodes import Program, ExpressionStatement, Expression
    from components.shared_types.src.location import SourceLocation

    # Create a minimal unsupported expression type
    class UnsupportedExpression(Expression):
        pass

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc, expression=UnsupportedExpression(location=loc)
            )
        ],
    )

    compiler = BytecodeCompiler(ast)

    with pytest.raises(CompileError):
        compiler.compile()


def test_compile_unsupported_operator_raises_error():
    """Test that unsupported binary operator raises CompileError."""
    from components.bytecode.src.compiler import BytecodeCompiler, CompileError
    from components.parser.src.ast_nodes import (
        Program,
        ExpressionStatement,
        BinaryExpression,
        Literal,
    )
    from components.shared_types.src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=BinaryExpression(
                    location=loc,
                    operator="**",  # Unsupported operator
                    left=Literal(location=loc, value=2),
                    right=Literal(location=loc, value=3),
                ),
            )
        ],
    )

    compiler = BytecodeCompiler(ast)

    with pytest.raises(CompileError):
        compiler.compile()
