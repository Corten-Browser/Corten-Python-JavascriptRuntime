"""
CallFrame - function call frame for bytecode execution.

This module provides the CallFrame class which represents a single function
invocation's execution state, including local variables, operand stack,
and program counter.
"""

from typing import List
from components.value_system.src import Value
from components.bytecode.src import BytecodeArray


class CallFrame:
    """
    Function call frame for bytecode execution.

    Manages the execution state for a single function call, including:
    - Local variables (parameters and local vars)
    - Operand stack for intermediate values
    - Program counter (instruction pointer)
    - 'this' binding for the function

    Attributes:
        bytecode: Compiled bytecode for this function
        locals: Local variable slots (initialized to None)
        stack: Operand stack for intermediate values
        pc: Program counter (index of next instruction)
        this_value: 'this' binding for function call
    """

    def __init__(self, bytecode: BytecodeArray, local_count: int, this_value: Value):
        """
        Create a new call frame.

        Args:
            bytecode: Compiled bytecode to execute
            local_count: Number of local variable slots
            this_value: 'this' binding for the function call
        """
        self.bytecode = bytecode
        self.locals: List[Value] = [None] * local_count
        self.stack: List[Value] = []
        self.pc = 0
        self.this_value = this_value

    def push(self, value: Value) -> None:
        """
        Push value onto operand stack.

        Args:
            value: Value to push onto stack
        """
        self.stack.append(value)

    def pop(self) -> Value:
        """
        Pop value from operand stack.

        Returns:
            Value from top of stack

        Raises:
            IndexError: If stack is empty
        """
        return self.stack.pop()

    def peek(self) -> Value:
        """
        Peek at top of operand stack without removing it.

        Returns:
            Value at top of stack

        Raises:
            IndexError: If stack is empty
        """
        return self.stack[-1]
