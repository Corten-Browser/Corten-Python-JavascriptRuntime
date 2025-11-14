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
from components.event_loop.src import EventLoop

# Import all public classes
from .interpreter import Interpreter
from .execution_context import ExecutionContext
from .call_frame import CallFrame
from .evaluation_result import EvaluationResult


def Execute(
    bytecode: BytecodeArray, gc: Optional[GarbageCollector] = None
) -> EvaluationResult:
    """
    Execute bytecode with event loop support.

    This is the main entry point for bytecode execution. Creates an
    interpreter instance with an event loop, executes the provided bytecode,
    and runs the event loop to process any queued microtasks (such as
    Promise reactions).

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

    # Create event loop for asynchronous operations
    event_loop = EventLoop()

    # Create interpreter with event loop
    interpreter = Interpreter(gc, event_loop)

    # Execute main script
    result = interpreter.execute(bytecode)

    # Run event loop to process any queued microtasks
    event_loop.run()

    return result


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
