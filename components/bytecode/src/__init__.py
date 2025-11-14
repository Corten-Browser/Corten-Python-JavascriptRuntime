"""
Bytecode compiler for JavaScript runtime engine.

This package provides bytecode compilation from JavaScript AST to executable
bytecode for the virtual machine.

Public API:
    Opcodes:
        - Opcode: Enum of bytecode operation codes

    Data Structures:
        - Instruction: Single bytecode instruction
        - BytecodeArray: Compiled bytecode with constant pool

    Compiler:
        - BytecodeCompiler: AST to bytecode compiler
        - CompileError: Compilation error exception
        - Compile: Main entry point function

Example:
    >>> from components.parser.src import Parse
    >>> from components.bytecode.src import Compile
    >>>
    >>> ast = Parse("var x = 42;")
    >>> bytecode = Compile(ast)
    >>> len(bytecode.instructions) > 0
    True
"""

# Export opcodes
from .opcode import Opcode

# Export instruction types
from .instruction import Instruction

# Export bytecode array
from .bytecode_array import BytecodeArray

# Export compiler
from .compiler import BytecodeCompiler, CompileError


def Compile(ast) -> BytecodeArray:
    """
    Compile AST to bytecode.

    Main entry point for bytecode compilation. Takes a parsed JavaScript AST
    and generates executable bytecode.

    Args:
        ast: Program AST node from parser

    Returns:
        BytecodeArray containing compiled bytecode

    Raises:
        CompileError: If compilation fails

    Example:
        >>> from components.parser.src import Parse
        >>> from components.bytecode.src import Compile
        >>>
        >>> ast = Parse("1 + 2")
        >>> bytecode = Compile(ast)
        >>> len(bytecode.instructions) > 0
        True
        >>> len(bytecode.constant_pool) >= 2
        True
    """
    compiler = BytecodeCompiler(ast)
    return compiler.compile()


__all__ = [
    # Opcodes
    "Opcode",
    # Data structures
    "Instruction",
    "BytecodeArray",
    # Compiler
    "BytecodeCompiler",
    "CompileError",
    "Compile",
]

__version__ = "0.1.0"
