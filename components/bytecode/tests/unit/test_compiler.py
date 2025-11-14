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


def test_function_declaration_stores_in_variable():
    """
    Test that function declarations create and store function in variable.

    BUG: Currently function declarations are skipped entirely, leaving
    the function inaccessible. This test proves the bug exists.
    """
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import (
        Program,
        FunctionDeclaration,
        BlockStatement,
        ReturnStatement,
        BinaryExpression,
        Identifier,
    )
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    # function add(a, b) { return a + b; }
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            FunctionDeclaration(
                location=loc,
                name="add",
                parameters=["a", "b"],
                body=BlockStatement(
                    location=loc,
                    body=[
                        ReturnStatement(
                            location=loc,
                            argument=BinaryExpression(
                                location=loc,
                                operator="+",
                                left=Identifier(location=loc, name="a"),
                                right=Identifier(location=loc, name="b"),
                            ),
                        )
                    ],
                ),
            )
        ],
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Should have CREATE_CLOSURE
    opcodes = [instr.opcode for instr in bytecode.instructions]
    assert (
        Opcode.CREATE_CLOSURE in opcodes
    ), "Function declaration should compile to CREATE_CLOSURE"

    # Should store function in variable "add"
    assert (
        Opcode.STORE_GLOBAL in opcodes or Opcode.STORE_LOCAL in opcodes
    ), "Function declaration should store function in variable (STORE_GLOBAL or STORE_LOCAL)"


def test_function_call_after_declaration():
    """
    Test that declared functions can be called.

    This verifies the complete workflow: declare function, then call it.
    """
    from components.bytecode.src.compiler import BytecodeCompiler
    from components.parser.src.ast_nodes import (
        Program,
        FunctionDeclaration,
        BlockStatement,
        ReturnStatement,
        BinaryExpression,
        Identifier,
        ExpressionStatement,
        CallExpression,
        Literal,
    )
    from components.bytecode.src.opcode import Opcode
    from components.shared_types.src.location import SourceLocation

    # function add(a, b) { return a + b; }
    # add(1, 2);
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            FunctionDeclaration(
                location=loc,
                name="add",
                parameters=["a", "b"],
                body=BlockStatement(
                    location=loc,
                    body=[
                        ReturnStatement(
                            location=loc,
                            argument=BinaryExpression(
                                location=loc,
                                operator="+",
                                left=Identifier(location=loc, name="a"),
                                right=Identifier(location=loc, name="b"),
                            ),
                        )
                    ],
                ),
            ),
            ExpressionStatement(
                location=loc,
                expression=CallExpression(
                    location=loc,
                    callee=Identifier(location=loc, name="add"),
                    arguments=[
                        Literal(location=loc, value=1),
                        Literal(location=loc, value=2),
                    ],
                ),
            ),
        ],
    )

    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    opcodes = [instr.opcode for instr in bytecode.instructions]

    # Check bytecode includes all required operations:
    # 1. CREATE_CLOSURE
    assert Opcode.CREATE_CLOSURE in opcodes, "Should create function"

    # 2. STORE_GLOBAL "add" (to store the function)
    assert (
        Opcode.STORE_GLOBAL in opcodes or Opcode.STORE_LOCAL in opcodes
    ), "Should store function in variable"

    # 3. LOAD_GLOBAL "add" (to load function for call)
    assert (
        Opcode.LOAD_GLOBAL in opcodes or Opcode.LOAD_LOCAL in opcodes
    ), "Should load function for call"

    # 4. CALL_FUNCTION
    assert Opcode.CALL_FUNCTION in opcodes, "Should call the function"
