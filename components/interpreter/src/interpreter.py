"""
Interpreter - bytecode interpreter and execution engine.

This module provides the Interpreter class which executes JavaScript bytecode
using a register-based virtual machine with opcode dispatch loop.
"""

from typing import List, Optional
from components.memory_gc.src import GarbageCollector
from components.value_system.src import Value
from components.bytecode.src import BytecodeArray, Opcode
from components.interpreter.src.execution_context import ExecutionContext
from components.interpreter.src.call_frame import CallFrame
from components.interpreter.src.evaluation_result import EvaluationResult
from components.object_runtime.src import JSArray, JSObject


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
                    elif isinstance(const_value, str):
                        # Template literals: store strings as objects
                        frame.push(Value.from_object(const_value))
                    else:
                        # Other types - placeholder
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
                    # Phase 1: Enforce const immutability
                    local_index = instruction.operand1
                    value = frame.pop()

                    # Check if trying to reassign a const variable
                    if frame.is_const(local_index) and frame.is_initialized(
                        local_index
                    ):
                        raise TypeError(
                            f"Assignment to constant variable at local {local_index}"
                        )

                    # Store value
                    frame.locals[local_index] = value
                    # Mark as initialized
                    frame.mark_initialized(local_index)

                # Arithmetic
                case Opcode.ADD:
                    right = frame.pop()
                    left = frame.pop()

                    # Handle string concatenation for template literals
                    left_is_string = left.is_object() and isinstance(left.to_object(), str)
                    right_is_string = right.is_object() and isinstance(right.to_object(), str)

                    if left_is_string or right_is_string:
                        # String concatenation (JavaScript coercion)
                        left_str = left.to_object() if left_is_string else str(left.to_smi())
                        right_str = right.to_object() if right_is_string else str(right.to_smi())
                        result = Value.from_object(left_str + right_str)
                        frame.push(result)
                    else:
                        # Numeric addition
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
                    # Safe pop: only pop if stack has items
                    # This handles cases where destructuring leaves no items on stack
                    # (e.g., destructuring function returns vs object literals)
                    if len(frame.stack) > 0:
                        frame.pop()

                case Opcode.DUP:
                    value = frame.peek()
                    frame.push(value)

                # Array operations
                case Opcode.CREATE_ARRAY:
                    count = instruction.operand1 or 0
                    elements = []
                    # Pop elements in reverse order (last pushed = first element)
                    for _ in range(count):
                        elements.insert(0, frame.pop())

                    # Create JSArray
                    array = JSArray(self.gc)
                    for elem in elements:
                        array.push(elem)

                    # Push array to stack as Value
                    frame.push(Value.from_object(array))

                # Object operations
                case Opcode.CREATE_OBJECT:
                    # Create empty JSObject
                    obj = JSObject(self.gc)
                    # Push object to stack as Value
                    frame.push(Value.from_object(obj))

                case Opcode.STORE_PROPERTY:
                    # Get property name (either from constant pool or direct)
                    if isinstance(instruction.operand1, int):
                        key = bytecode.constant_pool[instruction.operand1]
                    else:
                        key = instruction.operand1  # Direct property name (for tests)
                    # Pop value from stack
                    value = frame.pop()
                    # Peek object from stack (don't pop - keep for next property)
                    obj_value = frame.peek()
                    obj = obj_value.to_object()
                    # Set property
                    obj.set_property(key, value)

                case Opcode.LOAD_PROPERTY:
                    # Get property name (either from constant pool or direct)
                    if isinstance(instruction.operand1, int):
                        key = bytecode.constant_pool[instruction.operand1]
                    else:
                        key = instruction.operand1  # Direct property name (for tests)
                    # Pop object from stack
                    obj_value = frame.pop()
                    obj = obj_value.to_object()
                    # Get property value
                    prop_value = obj.get_property(key)
                    # Push property value to stack
                    frame.push(prop_value)

                case Opcode.LOAD_ELEMENT:
                    # Pop index from stack
                    index_value = frame.pop()
                    # Pop array from stack
                    array_value = frame.pop()
                    array = array_value.to_object()
                    # Get element at index
                    element = array.get_element(index_value.to_smi())
                    # Push element to stack
                    frame.push(element)

                case Opcode.STORE_ELEMENT:
                    # Pop value to store
                    value = frame.pop()
                    # Pop index from stack
                    index_value = frame.pop()
                    # Pop array from stack (compiler uses DUP to keep reference)
                    array_value = frame.pop()
                    array = array_value.to_object()
                    # Store element at index
                    array.set_element(index_value.to_smi(), value)

                # Function operations
                case Opcode.CREATE_CLOSURE:
                    # Phase 1: Arrow functions execute like regular functions
                    # Phase 2 TODO:
                    # - Add is_arrow flag to JSFunction
                    # - Implement lexical this binding (capture this from definition scope)
                    # - Prevent arrow functions from being used as constructors
                    # - Remove arguments object for arrow functions

                    param_count = instruction.operand1
                    function_bytecode = instruction.operand2

                    # Create JSFunction that will execute the bytecode
                    # Capture current frame locals for closure support
                    closure_locals = frame.locals.copy()

                    def bytecode_callable(*args, captured_bytecode=function_bytecode):
                        """Execute bytecode with arguments."""
                        # Convert args to list of Values
                        arg_values = list(args)
                        # Execute the function bytecode
                        result = self.execute(
                            captured_bytecode,  # Use captured value, not reference
                            this_value=Value.from_smi(0),  # Phase 1: undefined this
                            arguments=arg_values,
                        )
                        return (
                            result.value if result.is_success() else Value.from_smi(0)
                        )

                    # Import JSFunction here to avoid circular dependency
                    from components.object_runtime.src import JSFunction

                    function = JSFunction(
                        self.gc, bytecode_callable, name="<anonymous>"
                    )

                    # Store bytecode and closure for later access
                    function.set_property(
                        "__bytecode__", Value.from_object(function_bytecode)
                    )
                    function.set_property(
                        "__closure__", Value.from_object(closure_locals)
                    )

                    # Push function to stack
                    frame.push(Value.from_object(function))

                case Opcode.CALL_FUNCTION:
                    # Get argument count
                    arg_count = instruction.operand1

                    # Pop arguments from stack (in reverse order)
                    args = []
                    for _ in range(arg_count):
                        args.insert(0, frame.pop())

                    # Pop function from stack
                    function_value = frame.pop()
                    function_obj = function_value.to_object()

                    # Check if it's a JSFunction
                    from components.object_runtime.src import JSFunction

                    if isinstance(function_obj, JSFunction):
                        # Call the function
                        result = function_obj.call(args, this_context=None)
                        # Push result to stack
                        frame.push(result)
                    else:
                        # Not a function - push undefined
                        frame.push(Value.from_smi(0))

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
