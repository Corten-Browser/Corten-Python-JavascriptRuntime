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
    - Variable kinds (var/let/const) for Phase 1 support

    Attributes:
        bytecode: Compiled bytecode for this function
        locals: Local variable slots (initialized to None)
        stack: Operand stack for intermediate values
        pc: Program counter (index of next instruction)
        this_value: 'this' binding for function call
        variable_kinds: Variable kind for each local ("var"/"let"/"const")
        variable_initialized: Track if const variable has been initialized

    Phase 1 Implementation Notes:
    - let/const are treated as function-scoped (like var)
    - const immutability is enforced (cannot reassign after initialization)
    - Full block scope and TDZ (Temporal Dead Zone) are Phase 2 features
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

        # Phase 1: Track variable kinds for let/const support
        # All variables default to "var" (most permissive)
        self.variable_kinds: List[str] = ["var"] * local_count
        # Track if each variable has been initialized (for const check)
        self.variable_initialized: List[bool] = [False] * local_count

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

    def set_variable_kind(self, index: int, kind: str) -> None:
        """
        Set the variable kind for a local variable slot.

        This is used to mark variables as var/let/const for proper
        semantic enforcement.

        Args:
            index: Local variable slot index
            kind: Variable kind ("var", "let", or "const")

        Raises:
            ValueError: If kind is not valid
            IndexError: If index is out of bounds
        """
        if kind not in ("var", "let", "const"):
            raise ValueError(f"Invalid variable kind: {kind}")
        if index < 0 or index >= len(self.variable_kinds):
            raise IndexError(f"Local index out of bounds: {index}")

        self.variable_kinds[index] = kind

    def is_const(self, index: int) -> bool:
        """
        Check if a local variable is const.

        Args:
            index: Local variable slot index

        Returns:
            True if variable is const, False otherwise
        """
        return self.variable_kinds[index] == "const"

    def is_initialized(self, index: int) -> bool:
        """
        Check if a local variable has been initialized.

        Args:
            index: Local variable slot index

        Returns:
            True if variable has been initialized, False otherwise
        """
        return self.variable_initialized[index]

    def mark_initialized(self, index: int) -> None:
        """
        Mark a local variable as initialized.

        Args:
            index: Local variable slot index
        """
        self.variable_initialized[index] = True
