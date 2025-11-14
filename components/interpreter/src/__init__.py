"""
Interpreter - bytecode interpreter, execution engine, runtime services.

This package provides the bytecode interpreter that executes compiled JavaScript
code. It manages execution context, call stack, and provides runtime services.

Public API:
    Classes:
        - Interpreter: Bytecode interpreter with dispatch loop
        - ExecutionContext: Execution state manager
        - CallFrame: Function call frame
        - EvaluationResult: Execution result container

    Functions:
        - Execute: Main entry point for bytecode execution

Example:
    >>> from components.interpreter.src import Execute
    >>> from components.bytecode.src import BytecodeArray, Instruction, Opcode
    >>>
    >>> # Create simple bytecode
    >>> bytecode = BytecodeArray()
    >>> bytecode.add_constant(42)
    >>> bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
    >>> bytecode.add_instruction(Instruction(Opcode.RETURN))
    >>>
    >>> # Execute
    >>> result = Execute(bytecode)
    >>> result.is_success()
    True
    >>> result.value.to_smi()
    42
"""

from typing import Optional
from components.memory_gc.src import GarbageCollector
from components.bytecode.src import BytecodeArray

# Import all public classes
from .interpreter import Interpreter
from .execution_context import ExecutionContext
from .call_frame import CallFrame
from .evaluation_result import EvaluationResult


def Execute(
    bytecode: BytecodeArray, gc: Optional[GarbageCollector] = None
) -> EvaluationResult:
    """
    Execute bytecode and return result.

    This is the main entry point for bytecode execution. Creates an
    interpreter instance and executes the provided bytecode.

    Args:
        bytecode: Compiled bytecode to execute
        gc: Garbage collector instance (creates new one if not provided)

    Returns:
        EvaluationResult containing return value or exception

    Example:
        >>> from components.interpreter.src import Execute
        >>> from components.bytecode.src import BytecodeArray, Instruction, Opcode
        >>>
        >>> bytecode = BytecodeArray()
        >>> bytecode.add_constant(100)
        >>> bytecode.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
        >>> bytecode.add_instruction(Instruction(Opcode.RETURN))
        >>>
        >>> result = Execute(bytecode)
        >>> result.is_success()
        True
    """
    if gc is None:
        gc = GarbageCollector()

    interpreter = Interpreter(gc)
    return interpreter.execute(bytecode)


__all__ = [
    # Classes
    "Interpreter",
    "ExecutionContext",
    "CallFrame",
    "EvaluationResult",
    # Functions
    "Execute",
]

__version__ = "0.1.0"
