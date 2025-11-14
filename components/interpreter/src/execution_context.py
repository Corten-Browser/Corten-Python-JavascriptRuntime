"""
ExecutionContext - execution state for JavaScript code.

This module provides the ExecutionContext class which manages the global
execution state including global variables, call stack, and garbage collector.
"""

from typing import List, Dict
from components.memory_gc.src import GarbageCollector
from components.interpreter.src.call_frame import CallFrame


class ExecutionContext:
    """
    Execution state for JavaScript code.

    Manages the runtime execution environment including:
    - Global variable bindings
    - Function call stack
    - Garbage collector reference

    Attributes:
        global_scope: Dictionary of global variable bindings
        call_stack: Stack of function call frames
        gc: Garbage collector instance for memory management
    """

    def __init__(self, gc: GarbageCollector):
        """
        Create a new execution context.

        Args:
            gc: Garbage collector for memory management
        """
        self.gc = gc
        self.global_scope: Dict[str, any] = {}
        self.call_stack: List[CallFrame] = []

    def push_frame(self, frame: CallFrame) -> None:
        """
        Push a call frame onto the call stack.

        Args:
            frame: Call frame to push
        """
        self.call_stack.append(frame)

    def pop_frame(self) -> CallFrame:
        """
        Pop a call frame from the call stack.

        Returns:
            Call frame from top of stack

        Raises:
            IndexError: If call stack is empty
        """
        return self.call_stack.pop()

    def current_frame(self) -> CallFrame:
        """
        Get the current call frame without removing it.

        Returns:
            Call frame at top of stack

        Raises:
            IndexError: If call stack is empty
        """
        return self.call_stack[-1]
