"""
Interpreter - bytecode interpreter and execution engine.

This module provides the Interpreter class which executes JavaScript bytecode
using a register-based virtual machine with opcode dispatch loop.
"""

from typing import List, Optional
from components.memory_gc.src import GarbageCollector
from components.value_system.src import Value, ToNumber, ToBoolean
from components.bytecode.src import BytecodeArray, Instruction, Opcode
from components.interpreter.src.execution_context import ExecutionContext
from components.interpreter.src.call_frame import CallFrame
from components.interpreter.src.evaluation_result import EvaluationResult


class Interpreter:
    """
    Bytecode interpreter and execution engine.

    Executes JavaScript bytecode using a stack-based virtual machine.
    Manages execution context, call stack, and runtime services.

    Attributes:
        gc: Garbage collector for memory management
        context: Current execution context
    """

    def __init__(self, gc: GarbageCollector):
        """
        Create a new interpreter.

        Args:
            gc: Garbage collector for memory management
        """
        self.gc = gc
        self.context = ExecutionContext(gc)

    def execute(
        self,
        bytecode: BytecodeArray,
        this_value: Optional[Value] = None,
        arguments: Optional[List[Value]] = None,
    ) -> EvaluationResult:
        """
        Execute bytecode and return result.

        Args:
            bytecode: Compiled bytecode to execute
            this_value: 'this' binding for execution (defaults to undefined)
            arguments: Argument values (defaults to empty list)

        Returns:
            EvaluationResult containing return value or exception
        """
        if this_value is None:
            this_value = Value.from_smi(0)  # Placeholder for undefined
        if arguments is None:
            arguments = []

        try:
            # Create call frame
            frame = CallFrame(bytecode, bytecode.local_count, this_value)

            # Initialize local variables with arguments
            for i, arg in enumerate(arguments):
                if i < len(frame.locals):
                    frame.locals[i] = arg

            # Push frame onto call stack
            self.context.push_frame(frame)

            # Execute bytecode
            result_value = self._execute_frame(frame)

            # Pop frame from call stack
            self.context.pop_frame()

            return EvaluationResult(value=result_value)

        except Exception as e:
            # Clean up call stack on exception
            if len(self.context.call_stack) > 0:
                self.context.pop_frame()
            return EvaluationResult(exception=e)

    def _execute_frame(self, frame: CallFrame) -> Value:
        """
        Execute bytecode in a call frame using dispatch loop.

        Args:
            frame: Call frame to execute

        Returns:
            Return value from execution
        """
        bytecode = frame.bytecode

        while frame.pc < len(bytecode.instructions):
            instruction = bytecode.instructions[frame.pc]
            frame.pc += 1

            # Dispatch opcode
            match instruction.opcode:
                # Literals
                case Opcode.LOAD_CONSTANT:
                    const_value = bytecode.constant_pool[instruction.operand1]
                    # Convert Python value to Value
                    if isinstance(const_value, int):
                        frame.push(Value.from_smi(const_value))
                    else:
                        # For now, store as SMI (will be improved)
                        frame.push(Value.from_smi(0))

                case Opcode.LOAD_UNDEFINED:
                    frame.push(Value.from_smi(0))  # Placeholder

                case Opcode.LOAD_NULL:
                    frame.push(Value.from_smi(0))  # Placeholder

                case Opcode.LOAD_TRUE:
                    frame.push(Value.from_smi(1))

                case Opcode.LOAD_FALSE:
                    frame.push(Value.from_smi(0))

                # Variables
                case Opcode.LOAD_GLOBAL:
                    name = bytecode.constant_pool[instruction.operand1]
                    value = self.get_global(name)
                    frame.push(value)

                case Opcode.STORE_GLOBAL:
                    name = bytecode.constant_pool[instruction.operand1]
                    value = frame.pop()
                    self.set_global(name, value)

                case Opcode.LOAD_LOCAL:
                    value = frame.locals[instruction.operand1]
                    frame.push(value)

                case Opcode.STORE_LOCAL:
                    value = frame.pop()
                    frame.locals[instruction.operand1] = value

                # Arithmetic
                case Opcode.ADD:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(left.to_smi() + right.to_smi())
                    frame.push(result)

                case Opcode.SUBTRACT:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(left.to_smi() - right.to_smi())
                    frame.push(result)

                case Opcode.MULTIPLY:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(left.to_smi() * right.to_smi())
                    frame.push(result)

                case Opcode.DIVIDE:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(int(left.to_smi() / right.to_smi()))
                    frame.push(result)

                case Opcode.MODULO:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(left.to_smi() % right.to_smi())
                    frame.push(result)

                case Opcode.NEGATE:
                    value = frame.pop()
                    result = Value.from_smi(-value.to_smi())
                    frame.push(result)

                # Comparison
                case Opcode.EQUAL:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(1 if left.to_smi() == right.to_smi() else 0)
                    frame.push(result)

                case Opcode.NOT_EQUAL:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(1 if left.to_smi() != right.to_smi() else 0)
                    frame.push(result)

                case Opcode.LESS_THAN:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(1 if left.to_smi() < right.to_smi() else 0)
                    frame.push(result)

                case Opcode.LESS_EQUAL:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(1 if left.to_smi() <= right.to_smi() else 0)
                    frame.push(result)

                case Opcode.GREATER_THAN:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(1 if left.to_smi() > right.to_smi() else 0)
                    frame.push(result)

                case Opcode.GREATER_EQUAL:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(1 if left.to_smi() >= right.to_smi() else 0)
                    frame.push(result)

                # Logical
                case Opcode.LOGICAL_AND:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(
                        1 if left.to_smi() and right.to_smi() else 0
                    )
                    frame.push(result)

                case Opcode.LOGICAL_OR:
                    right = frame.pop()
                    left = frame.pop()
                    result = Value.from_smi(1 if left.to_smi() or right.to_smi() else 0)
                    frame.push(result)

                case Opcode.LOGICAL_NOT:
                    value = frame.pop()
                    result = Value.from_smi(1 if not value.to_smi() else 0)
                    frame.push(result)

                # Control flow
                case Opcode.JUMP:
                    frame.pc = instruction.operand1

                case Opcode.JUMP_IF_TRUE:
                    value = frame.pop()
                    if value.to_smi():
                        frame.pc = instruction.operand1

                case Opcode.JUMP_IF_FALSE:
                    value = frame.pop()
                    if not value.to_smi():
                        frame.pc = instruction.operand1

                case Opcode.RETURN:
                    if len(frame.stack) > 0:
                        return frame.pop()
                    else:
                        return Value.from_smi(0)  # Return undefined

                # Stack manipulation
                case Opcode.POP:
                    frame.pop()

                case Opcode.DUP:
                    value = frame.peek()
                    frame.push(value)

                # Placeholder for unimplemented opcodes
                case _:
                    raise NotImplementedError(
                        f"Opcode {instruction.opcode} not yet implemented"
                    )

        # If we reach here without return, return undefined
        return Value.from_smi(0)

    def get_global(self, name: str) -> Value:
        """
        Get global variable value.

        Args:
            name: Variable name

        Returns:
            Variable value

        Raises:
            ReferenceError: If variable not defined
        """
        if name not in self.context.global_scope:
            raise ReferenceError(f"Undefined variable: {name}")
        return self.context.global_scope[name]

    def set_global(self, name: str, value: Value) -> None:
        """
        Set global variable value.

        Args:
            name: Variable name
            value: Variable value
        """
        self.context.global_scope[name] = value

    def call_function(
        self, function, this_value: Value, arguments: List[Value]  # JSFunction
    ) -> EvaluationResult:
        """
        Call JavaScript function.

        Args:
            function: Function to call
            this_value: 'this' binding
            arguments: Function arguments

        Returns:
            EvaluationResult from function execution
        """
        # Basic implementation - will be enhanced with JSFunction integration
        raise NotImplementedError("call_function will be implemented with JSFunction")
