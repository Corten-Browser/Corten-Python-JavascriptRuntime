"""
Interpreter - bytecode interpreter and execution engine.

This module provides the Interpreter class which executes JavaScript bytecode
using a register-based virtual machine with opcode dispatch loop.
"""

from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from components.memory_gc.src import GarbageCollector
from components.value_system.src import Value
from components.bytecode.src import BytecodeArray, Opcode
from components.interpreter.src.execution_context import ExecutionContext
from components.interpreter.src.call_frame import CallFrame
from components.interpreter.src.evaluation_result import EvaluationResult
from components.object_runtime.src import JSArray, JSObject
from components.event_loop.src import EventLoop
from components.promise.src import JSPromise


class _AsyncSuspension(Exception):
    """Internal exception to signal async function suspension at await.

    This exception is used internally to unwind the call stack when
    an async function suspends at an await point. It should be caught
    by the async function executor and not propagate to user code.
    """

    pass


@dataclass
class AsyncFunctionState:
    """State for suspended async function.

    Attributes:
        instruction_pointer: Where to resume execution
        locals: Local variable values
        stack: Stack state at suspension point
        bytecode: Function bytecode being executed
        promise: Promise to resolve/reject when async function completes
    """

    instruction_pointer: int
    locals: List[Value]
    stack: List[Value]
    bytecode: BytecodeArray
    promise: JSPromise


class Interpreter:
    """
    Bytecode interpreter and execution engine.

    Executes JavaScript bytecode using a stack-based virtual machine.
    Manages execution context, call stack, and runtime services.

    Attributes:
        gc: Garbage collector for memory management
        context: Current execution context
    """

    def __init__(self, gc: GarbageCollector, event_loop: Optional[EventLoop] = None):
        """
        Create a new interpreter.

        Args:
            gc: Garbage collector for memory management
            event_loop: Event loop for asynchronous operations (optional)
        """
        self.gc = gc
        self.event_loop = event_loop if event_loop is not None else EventLoop()
        self.context = ExecutionContext(gc)

        # Async/await state management
        self.suspended_async_functions: Dict[str, AsyncFunctionState] = {}
        self.current_async_promise: Optional[JSPromise] = None

        # Add Promise constructor to global scope (wrapped in Value)
        promise_constructor = self._create_promise_constructor()
        self.context.global_scope["Promise"] = Value.from_object(promise_constructor)

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

        except _AsyncSuspension:
            # Async suspension - propagate up to caller (don't wrap in EvaluationResult)
            # Note: Frame already popped by AWAIT opcode, don't pop again
            raise  # Re-raise to let _start_async_function catch it

        except Exception as e:
            # Clean up call stack on exception
            if len(self.context.call_stack) > 0:
                self.context.pop_frame()
            return EvaluationResult(exception=e)

    def _create_promise_constructor(self):
        """Create Promise constructor with static methods.

        Returns:
            JSObject that acts as Promise constructor with static methods
        """
        interpreter = self

        # Create callable for Promise constructor
        def promise_constructor(executor):
            """new Promise(executor)"""
            # Unwrap executor from Value if needed
            if hasattr(executor, 'to_object'):
                executor_obj = executor.to_object()
            else:
                executor_obj = executor

            # Create wrapper that adapts JSFunction.call() to Python callable
            from components.object_runtime.src import JSFunction
            if isinstance(executor_obj, JSFunction):
                # Create Python callable that calls JSFunction properly
                def executor_fn(resolve, reject):
                    # Wrap resolve/reject as Values for JSFunction.call
                    from components.value_system.src import Value
                    resolve_value = Value.from_object(resolve)
                    reject_value = Value.from_object(reject)
                    # Call JSFunction with proper Value arguments
                    executor_obj.call([resolve_value, reject_value], this_context=None)
                    return None  # Executor doesn't return anything meaningful
            else:
                executor_fn = executor_obj

            return JSPromise(executor_fn, interpreter.event_loop)

        # Create JSObject for Promise constructor
        from components.object_runtime.src import JSObject

        promise_obj = JSObject(self.gc)

        # Store the callable in the object (for NEW opcode)
        promise_obj._callable = promise_constructor

        # Add static methods as properties
        def resolve_method(value):
            # Value can be passed as-is - JSPromise.resolve handles both Value and raw values
            return JSPromise.resolve(value, interpreter.event_loop)

        def reject_method(reason):
            # Reason can be passed as-is - JSPromise.reject handles both Value and raw values
            return JSPromise.reject(reason, interpreter.event_loop)

        def all_method(promises):
            # Unwrap Value to get JSArray
            if hasattr(promises, 'to_object'):
                array = promises.to_object()
            else:
                array = promises

            # Convert JSArray elements to Python list of promises
            from components.object_runtime.src import JSArray
            if isinstance(array, JSArray):
                promise_list = []
                for i in range(array._length):
                    elem = array.get_element(i)
                    # Unwrap Value to get actual promise
                    if hasattr(elem, 'to_object'):
                        promise_list.append(elem.to_object())
                    else:
                        promise_list.append(elem)
                return JSPromise.all(promise_list, interpreter.event_loop)
            else:
                # If it's already a list, use it directly
                return JSPromise.all(array, interpreter.event_loop)

        def race_method(promises):
            # Unwrap Value to get JSArray
            if hasattr(promises, 'to_object'):
                array = promises.to_object()
            else:
                array = promises

            # Convert JSArray elements to Python list of promises
            from components.object_runtime.src import JSArray
            if isinstance(array, JSArray):
                promise_list = []
                for i in range(array._length):
                    elem = array.get_element(i)
                    # Unwrap Value to get actual promise
                    if hasattr(elem, 'to_object'):
                        promise_list.append(elem.to_object())
                    else:
                        promise_list.append(elem)
                return JSPromise.race(promise_list, interpreter.event_loop)
            else:
                # If it's already a list, use it directly
                return JSPromise.race(array, interpreter.event_loop)

        def any_method(promises):
            # Unwrap Value to get JSArray
            if hasattr(promises, 'to_object'):
                array = promises.to_object()
            else:
                array = promises

            # Convert JSArray elements to Python list of promises
            from components.object_runtime.src import JSArray
            if isinstance(array, JSArray):
                promise_list = []
                for i in range(array._length):
                    elem = array.get_element(i)
                    # Unwrap Value to get actual promise
                    if hasattr(elem, 'to_object'):
                        promise_list.append(elem.to_object())
                    else:
                        promise_list.append(elem)
                return JSPromise.any(promise_list, interpreter.event_loop)
            else:
                # If it's already a list, use it directly
                return JSPromise.any(array, interpreter.event_loop)

        def allSettled_method(promises):
            # Unwrap Value to get JSArray
            if hasattr(promises, 'to_object'):
                array = promises.to_object()
            else:
                array = promises

            # Convert JSArray elements to Python list of promises
            from components.object_runtime.src import JSArray
            if isinstance(array, JSArray):
                promise_list = []
                for i in range(array._length):
                    elem = array.get_element(i)
                    # Unwrap Value to get actual promise
                    if hasattr(elem, 'to_object'):
                        promise_list.append(elem.to_object())
                    else:
                        promise_list.append(elem)
                return JSPromise.allSettled(promise_list, interpreter.event_loop)
            else:
                # If it's already a list, use it directly
                return JSPromise.allSettled(array, interpreter.event_loop)

        # Store static methods as properties
        promise_obj.set_property("resolve", Value.from_object(resolve_method))
        promise_obj.set_property("reject", Value.from_object(reject_method))
        promise_obj.set_property("all", Value.from_object(all_method))
        promise_obj.set_property("race", Value.from_object(race_method))
        promise_obj.set_property("any", Value.from_object(any_method))
        promise_obj.set_property("allSettled", Value.from_object(allSettled_method))

        return promise_obj

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
                    left_is_string = left.is_object() and isinstance(
                        left.to_object(), str
                    )
                    right_is_string = right.is_object() and isinstance(
                        right.to_object(), str
                    )

                    if left_is_string or right_is_string:
                        # String concatenation (JavaScript coercion)
                        left_str = (
                            left.to_object() if left_is_string else str(left.to_smi())
                        )
                        right_str = (
                            right.to_object()
                            if right_is_string
                            else str(right.to_smi())
                        )
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
                    elif callable(function_obj):
                        # Plain Python callable (e.g., Promise static methods, async function wrappers)
                        result = function_obj(*args)
                        # Wrap result in Value if it's not already
                        if isinstance(result, Value):
                            frame.push(result)
                        else:
                            frame.push(Value.from_object(result))
                    else:
                        # Not a function - push undefined
                        frame.push(Value.from_smi(0))

                case Opcode.NEW:
                    # Get argument count
                    arg_count = instruction.operand1 or 0

                    # Pop arguments in reverse order (last arg first)
                    arguments = []
                    for _ in range(arg_count):
                        arg_value = frame.pop()
                        arguments.insert(
                            0, arg_value
                        )  # Insert at beginning to maintain order

                    # Pop constructor function
                    constructor_value = frame.pop()

                    # Extract callable from Value
                    if hasattr(constructor_value, "to_object"):
                        constructor = constructor_value.to_object()
                    else:
                        constructor = constructor_value

                    # Check if constructor is a JSObject with _callable attribute
                    if hasattr(constructor, "_callable") and callable(
                        constructor._callable
                    ):
                        instance = constructor._callable(*arguments)
                        frame.push(Value.from_object(instance))
                    elif callable(constructor):
                        instance = constructor(*arguments)
                        frame.push(Value.from_object(instance))
                    else:
                        raise RuntimeError(
                            f"Cannot construct non-callable: {type(constructor)}"
                        )

                case Opcode.CREATE_ASYNC_FUNCTION:
                    # Get the async function bytecode
                    function_bytecode = instruction.operand2

                    # Create async function wrapper that returns Promise
                    def async_function_wrapper(
                        *args, captured_bytecode=function_bytecode
                    ):
                        """Async function wrapper that returns Promise."""

                        # Create Promise that starts async function execution
                        def executor(resolve, reject):
                            # Start async function execution
                            self._start_async_function(
                                captured_bytecode, args, resolve, reject
                            )

                        promise = JSPromise(executor, self.event_loop)
                        return promise

                    frame.push(Value.from_object(async_function_wrapper))

                case Opcode.AWAIT:
                    # Pop the value to await
                    awaited_value = frame.pop()

                    # Convert to Promise if not already
                    if isinstance(
                        (
                            awaited_value.to_object()
                            if hasattr(awaited_value, "to_object")
                            and awaited_value.is_object()
                            else awaited_value
                        ),
                        JSPromise,
                    ):
                        # Value contains a Promise object
                        promise = awaited_value.to_object()
                    elif isinstance(awaited_value, JSPromise):
                        # Already a Promise
                        promise = awaited_value
                    else:
                        # Unwrap Value to get raw Python value
                        if hasattr(awaited_value, "is_smi") and awaited_value.is_smi():
                            # It's an SMI - extract the integer
                            raw_value = awaited_value.to_smi()
                        elif (
                            hasattr(awaited_value, "is_object")
                            and awaited_value.is_object()
                        ):
                            # It's an object - extract it
                            raw_value = awaited_value.to_object()
                        else:
                            # It's already a raw value
                            raw_value = awaited_value
                        promise = JSPromise.resolve(raw_value, self.event_loop)

                    # Save current state for resumption
                    state = AsyncFunctionState(
                        instruction_pointer=frame.pc,  # Resume at next instruction
                        locals=frame.locals.copy(),
                        stack=frame.stack.copy(),
                        bytecode=bytecode,
                        promise=self.current_async_promise,  # The Promise this async function will resolve
                    )

                    # Register continuation - when promise settles, resume execution
                    promise.then(
                        lambda value: self._resume_async_function(state, value, False),
                        lambda error: self._resume_async_function(state, error, True),
                    )

                    # Suspend execution - signal suspension to caller
                    # Pop the frame since we're suspending
                    if len(self.context.call_stack) > 0:
                        self.context.pop_frame()

                    # Raise a special marker exception to signal suspension
                    raise _AsyncSuspension()

                # Placeholder for unimplemented opcodes
                case _:
                    raise NotImplementedError(
                        f"Opcode {instruction.opcode} not yet implemented"
                    )

        # If we reach here without return, return top of stack if present
        # This allows expression statements at top level to return their value
        if len(frame.stack) > 0:
            return frame.pop()
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

    def _start_async_function(self, bytecode: BytecodeArray, args, resolve, reject):
        """Start async function execution.

        Args:
            bytecode: Bytecode for the async function body
            args: Function arguments
            resolve: Promise resolve function
            reject: Promise reject function
        """
        try:
            # Store resolve/reject for this async function
            # Save the Promise that this async function should resolve
            old_promise = self.current_async_promise

            # Create a temporary Promise to track this async function's completion
            # (We can't access the actual Promise here, so we track resolve/reject)
            class PromiseHandlers:
                def __init__(self, res, rej):
                    self.resolve = res
                    self.reject = rej

            self.current_async_promise = PromiseHandlers(resolve, reject)

            # Convert args to list of Values
            arg_values = []
            for arg in args:
                if isinstance(arg, Value):
                    arg_values.append(arg)
                else:
                    arg_values.append(Value.from_object(arg))

            # Execute the async function body
            result = self.execute(
                bytecode, this_value=Value.from_smi(0), arguments=arg_values
            )

            # Restore previous async promise context
            self.current_async_promise = old_promise

            # If execution completed without await (no suspension), resolve immediately
            if result.is_success():
                resolve(result.value)
            else:
                reject(result.exception)

        except _AsyncSuspension:
            # Async function suspended at await - this is normal
            # The continuation will resolve/reject the Promise later
            # Restore context
            self.current_async_promise = old_promise
            # Don't resolve or reject - the Promise will be settled by the continuation

        except Exception as e:
            # Restore context on error
            self.current_async_promise = old_promise
            reject(e)

    def _resume_async_function(self, state: AsyncFunctionState, value, is_error: bool):
        """Resume async function after await resolves.

        Args:
            state: Saved async function state
            value: Resolved value or rejection reason
            is_error: True if value is an error (rejection)
        """
        # Save current async promise context at the start
        old_promise = self.current_async_promise
        self.current_async_promise = state.promise

        try:
            # Phase 2.6.5: Handle both success and error paths by resuming execution
            # Create a new frame with saved state
            frame = CallFrame(state.bytecode, len(state.locals), Value.from_smi(0))
            frame.locals = state.locals.copy()
            frame.stack = state.stack.copy()
            frame.pc = state.instruction_pointer

            if is_error:
                # Phase 2.6.5: When await rejects, raise an exception
                # This allows try/catch (when implemented) to catch it
                # If no try/catch, the exception will propagate and reject the Promise

                # Convert value to exception if it's not already one
                if isinstance(value, Exception):
                    error = value
                else:
                    # Wrap the rejection reason in an exception
                    error = Exception(str(value))

                # Push frame onto call stack (so exception context is correct)
                self.context.push_frame(frame)

                # Raise the exception - this will be caught by outer except block
                # and will reject the async function's Promise
                raise error
            else:
                # Success path: Push the awaited value onto stack
                if isinstance(value, Value):
                    frame.push(value)
                elif isinstance(value, int):
                    # Use SMI for integers
                    frame.push(Value.from_smi(value))
                else:
                    # Use object for other types
                    frame.push(Value.from_object(value))

                # Push frame onto call stack
                self.context.push_frame(frame)

                # Continue execution from saved instruction pointer
                result_value = self._execute_frame(frame)

                # Pop frame from call stack
                self.context.pop_frame()

                # Restore promise context
                self.current_async_promise = old_promise

                # Resolve the async function's Promise with the final result
                if hasattr(state.promise, "resolve"):
                    state.promise.resolve(result_value)
                else:
                    # state.promise is PromiseHandlers
                    state.promise.resolve(result_value)

        except _AsyncSuspension:
            # Another await encountered during resumption - this is normal for multiple awaits
            # Frame already popped by AWAIT opcode, don't pop again
            # Restore promise context
            self.current_async_promise = old_promise
            # Don't reject - suspension is normal, continuation will be queued

        except Exception as e:
            # Restore context on error
            self.current_async_promise = old_promise

            # Pop frame if still on stack (exception before AWAIT could pop it)
            if len(self.context.call_stack) > 0:
                self.context.pop_frame()

            # Reject the async function's Promise
            if hasattr(state.promise, "reject"):
                state.promise.reject(e)
            else:
                # state.promise is PromiseHandlers
                state.promise.reject(e)
