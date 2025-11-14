"""
Tests for the Compile() entry point function.

These tests verify the main Compile() function works correctly.
"""

import pytest


def test_compile_function_imports():
    """Test that Compile function can be imported."""
    from components.bytecode.src import Compile

    assert Compile is not None


def test_compile_function_compiles_ast():
    """Test that Compile function compiles AST to bytecode."""
    from components.bytecode.src import Compile
    from components.parser.src.ast_nodes import Program
    from components.shared_types.src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(location=loc, body=[])

    bytecode = Compile(ast)

    assert bytecode is not None
    assert len(bytecode.instructions) >= 1


def test_compile_function_returns_bytecode_array():
    """Test that Compile returns BytecodeArray."""
    from components.bytecode.src import Compile, BytecodeArray
    from components.parser.src.ast_nodes import Program
    from components.shared_types.src.location import SourceLocation

    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(location=loc, body=[])

    bytecode = Compile(ast)

    assert isinstance(bytecode, BytecodeArray)
