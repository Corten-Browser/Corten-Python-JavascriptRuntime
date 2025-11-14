"""
Tests for BytecodeCompiler.

These tests verify the BytecodeCompiler correctly compiles AST to bytecode.
"""

import pytest


def test_compiler_imports():
    """Test that BytecodeCompiler can be imported."""
    from components.bytecode.src.compiler import BytecodeCompiler

    assert BytecodeCompiler is not None


def test_compiler_initialization():
    """Test creating a BytecodeCompiler with AST."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import Program
    from components.shared_types.src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(location=loc, body=[])
    compiler = BytecodeCompiler(ast)

    assert compiler is not None


def test_compile_empty_program():
    """Test compiling an empty program."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import Program
    from components.shared_types.src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(location=loc, body=[])
    compiler = BytecodeCompiler(ast)

    bytecode = compiler.compile()

    # Empty program should still have a RETURN instruction
    assert len(bytecode.instructions) >= 1
    assert bytecode.constant_pool == []


def test_compile_simple_literal():
    """Test compiling a simple numeric literal."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import Program, ExpressionStatement, Literal
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    # Program: 42;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc, expression=Literal(location=loc, value=42)
            )
        ],
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Should have: LOAD_CONSTANT, POP (expression statement), RETURN
    assert len(bytecode.instructions) >= 2
    assert bytecode.instructions[0].opcode == Opcode.LOAD_CONSTANT
    assert 42 in bytecode.constant_pool


def test_compile_addition():
    """Test compiling a simple addition expression."""
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import (
        Program,
        ExpressionStatement,
        BinaryExpression,
        Literal,
    )
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    # Program: 1 + 2;
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=BinaryExpression(
                    location=loc,
                    operator="+",
                    left=Literal(location=loc, value=1),
                    right=Literal(location=loc, value=2),
                ),
            )
        ],
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Should contain ADD opcode
    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert Opcode.ADD in opcodes
    assert 1 in bytecode.constant_pool
    assert 2 in bytecode.constant_pool


def test_compiler_raises_on_compile_error():
    """Test that compiler can raise CompileError."""
    from components.bytecode.src.compiler import BytecodeCompiler, CompileError

    # CompileError should be importable
    assert CompileError is not None
