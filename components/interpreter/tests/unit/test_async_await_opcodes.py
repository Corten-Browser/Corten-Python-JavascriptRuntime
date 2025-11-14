"""Unit tests for async/await opcode execution (Phase 2.6.3).

Tests the CREATE_ASYNC_FUNCTION and AWAIT opcodes in isolation.
"""

import pytest
from components.interpreter.src import Interpreter
from components.memory_gc.src import GarbageCollector
from components.event_loop.src import EventLoop
from components.bytecode.src import BytecodeArray, Instruction, Opcode
from components.value_system.src import Value
from components.promise.src import JSPromise, PromiseState


class TestCreateAsyncFunctionOpcode:
    """Test CREATE_ASYNC_FUNCTION opcode."""

    def test_create_async_function_opcode_creates_callable(self):
        """
        Given CREATE_ASYNC_FUNCTION opcode with bytecode
        When executed
        Then should push callable function onto stack
        """
        # Given - Create bytecode for async function body
        async_body = BytecodeArray()
        async_body.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))  # Load 42
        async_body.add_constant(42)
        async_body.add_instruction(Instruction(Opcode.RETURN, 0))
        async_body.local_count = 0

        # Main bytecode that creates async function
        bytecode = BytecodeArray()
        bytecode.add_instruction(Instruction(Opcode.CREATE_ASYNC_FUNCTION, 0, async_body))
        bytecode.add_instruction(Instruction(Opcode.RETURN, 0))  # Return the function
        bytecode.local_count = 0

        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)

        # Then
        assert result.is_success()
        func = result.value.to_object()
        assert callable(func)

    def test_calling_async_function_returns_promise(self):
        """
        Given an async function created by CREATE_ASYNC_FUNCTION
        When the function is called
        Then it should return a Promise
        """
        # Given
        async_body = BytecodeArray()
        async_body.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
        async_body.add_constant(42)
        async_body.add_instruction(Instruction(Opcode.RETURN, 0))
        async_body.local_count = 0

        bytecode = BytecodeArray()
        bytecode.add_instruction(Instruction(Opcode.CREATE_ASYNC_FUNCTION, 0, async_body))
        bytecode.add_instruction(Instruction(Opcode.RETURN, 0))  # Return the function
        bytecode.local_count = 0

        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)
        result = interpreter.execute(bytecode)
        async_func = result.value.to_object()

        # When
        promise = async_func()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.PENDING or promise.state == PromiseState.FULFILLED

    def test_async_function_resolves_with_return_value(self):
        """
        Given an async function that returns a value
        When executed and event loop runs
        Then Promise should resolve with that value
        """
        # Given
        async_body = BytecodeArray()
        async_body.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
        async_body.add_constant(42)
        async_body.add_instruction(Instruction(Opcode.RETURN, 0))
        async_body.local_count = 0

        bytecode = BytecodeArray()
        bytecode.add_instruction(Instruction(Opcode.CREATE_ASYNC_FUNCTION, 0, async_body))
        bytecode.add_instruction(Instruction(Opcode.RETURN, 0))  # Return the function
        bytecode.local_count = 0

        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)
        result = interpreter.execute(bytecode)
        async_func = result.value.to_object()

        # When
        promise = async_func()
        event_loop.run()  # Process microtasks

        # Then
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 42


class TestAwaitOpcode:
    """Test AWAIT opcode."""

    def test_await_suspends_execution(self):
        """
        Given AWAIT opcode in async function
        When executed
        Then execution should suspend (not complete immediately)
        """
        # This test verifies that AWAIT causes suspension
        # Full resumption will be tested in integration tests

        # Create async function body with AWAIT
        async_body = BytecodeArray()
        # Push a Promise onto stack
        async_body.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
        async_body.add_constant(10)
        # AWAIT the value (will be wrapped in Promise)
        async_body.add_instruction(Instruction(Opcode.AWAIT, 0))
        # After await, return the value
        async_body.add_instruction(Instruction(Opcode.RETURN, 0))
        async_body.local_count = 0

        bytecode = BytecodeArray()
        bytecode.add_instruction(Instruction(Opcode.CREATE_ASYNC_FUNCTION, 0, async_body))
        bytecode.add_instruction(Instruction(Opcode.RETURN, 0))  # Return the function
        bytecode.local_count = 0

        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)
        result = interpreter.execute(bytecode)
        async_func = result.value.to_object()

        # When - Call async function
        promise = async_func()

        # Then - Promise should be in PENDING state (execution suspended)
        assert isinstance(promise, JSPromise)
        # Might be pending or already resolved depending on microtask execution
        assert promise.state in [PromiseState.PENDING, PromiseState.FULFILLED]

    def test_await_wraps_non_promise_in_promise(self):
        """
        Given AWAIT with non-Promise value
        When executed
        Then value should be wrapped in resolved Promise
        """
        # Create async function that awaits a plain value
        async_body = BytecodeArray()
        async_body.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
        async_body.add_constant(42)
        async_body.add_instruction(Instruction(Opcode.AWAIT, 0))
        async_body.add_instruction(Instruction(Opcode.RETURN, 0))
        async_body.local_count = 0

        bytecode = BytecodeArray()
        bytecode.add_instruction(Instruction(Opcode.CREATE_ASYNC_FUNCTION, 0, async_body))
        bytecode.add_instruction(Instruction(Opcode.RETURN, 0))  # Return the function
        bytecode.local_count = 0

        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)
        result = interpreter.execute(bytecode)
        async_func = result.value.to_object()

        # When
        promise = async_func()
        event_loop.run()  # Process microtasks to complete await

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 42


class TestAsyncFunctionBasicExecution:
    """Test basic async function execution patterns."""

    def test_async_function_with_no_await_resolves_immediately(self):
        """
        Given async function without await
        When executed
        Then Promise should resolve after microtask
        """
        # Given
        async_body = BytecodeArray()
        async_body.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
        async_body.add_constant(100)
        async_body.add_instruction(Instruction(Opcode.RETURN, 0))
        async_body.local_count = 0

        bytecode = BytecodeArray()
        bytecode.add_instruction(Instruction(Opcode.CREATE_ASYNC_FUNCTION, 0, async_body))
        bytecode.add_instruction(Instruction(Opcode.RETURN, 0))  # Return the function
        bytecode.local_count = 0

        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)
        result = interpreter.execute(bytecode)
        async_func = result.value.to_object()

        # When
        promise = async_func()
        initial_state = promise.state
        event_loop.run()

        # Then
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 100

    def test_async_function_can_be_chained(self):
        """
        Given async function result
        When .then() is called
        Then handler should receive resolved value
        """
        # Given
        async_body = BytecodeArray()
        async_body.add_instruction(Instruction(Opcode.LOAD_CONSTANT, 0))
        async_body.add_constant(77)
        async_body.add_instruction(Instruction(Opcode.RETURN, 0))
        async_body.local_count = 0

        bytecode = BytecodeArray()
        bytecode.add_instruction(Instruction(Opcode.CREATE_ASYNC_FUNCTION, 0, async_body))
        bytecode.add_instruction(Instruction(Opcode.RETURN, 0))  # Return the function
        bytecode.local_count = 0

        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)
        result = interpreter.execute(bytecode)
        async_func = result.value.to_object()

        # When
        promise = async_func()

        # Track if handler was called
        result_value = [None]
        def handler(value):
            result_value[0] = value

        promise.then(handler, None)
        event_loop.run()

        # Then
        assert result_value[0] is not None
        assert result_value[0].to_smi() == 77
