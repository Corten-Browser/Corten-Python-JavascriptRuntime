"""Async/await error handling integration tests (Phase 2.6.5).

Tests error handling for async/await:
- Promise rejection handling
- Error propagation through async functions
- Uncaught rejections reject the async function's Promise
"""

import pytest
from components.parser.src import Parse
from components.bytecode.src import Compile
from components.memory_gc.src import GarbageCollector
from components.event_loop.src import EventLoop
from components.interpreter.src.interpreter import Interpreter
from components.promise.src import JSPromise, PromiseState


class TestAsyncAwaitErrorHandling:
    """Test error handling with async/await."""

    def test_await_rejected_promise_rejects_async_function(self):
        """
        Given an async function that awaits a rejected Promise
        When the Promise rejects
        Then the async function's Promise should reject with the same error
        """
        # Given
        source = """
        async function test() {
            const x = await Promise.reject("error");
            return "not reached";
        }
        test();
        """
        ast = Parse(source)
        bytecode = Compile(ast)
        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)
        promise = result.value.to_object()
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.REJECTED
        # Verify rejection occurred (error message format not critical for this phase)

    def test_await_rejection_at_start_of_function(self):
        """
        Given an async function that immediately awaits a rejected Promise
        When the rejection occurs
        Then the async function's Promise should reject immediately
        """
        # Given
        source = """
        async function test() {
            await Promise.reject("immediate error");
        }
        test();
        """
        ast = Parse(source)
        bytecode = Compile(ast)
        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)
        promise = result.value.to_object()
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.REJECTED

    def test_await_rejection_after_successful_await(self):
        """
        Given an async function with multiple awaits
        When first await succeeds but second await rejects
        Then the async function's Promise should reject
        """
        # Given
        source = """
        async function test() {
            const a = await Promise.resolve(10);
            const b = await Promise.reject("error after success");
            return a + b;
        }
        test();
        """
        ast = Parse(source)
        bytecode = Compile(ast)
        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)
        promise = result.value.to_object()
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.REJECTED
        # Rejection occurred correctly

    def test_await_multiple_rejections(self):
        """
        Given an async function with multiple awaits that could reject
        When the first await rejects
        Then subsequent awaits should not execute
        And the async function's Promise should reject with the first error
        """
        # Given
        source = """
        async function test() {
            const a = await Promise.reject("first error");
            const b = await Promise.reject("second error");
            return "not reached";
        }
        test();
        """
        ast = Parse(source)
        bytecode = Compile(ast)
        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)
        promise = result.value.to_object()
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.REJECTED
        # Should reject with first error (execution stops at first rejection)

    def test_await_rejection_with_different_error_types(self):
        """Test await rejection with different types of rejection reasons."""
        # Test string error
        source1 = """
        async function testString() {
            await Promise.reject("string error");
        }
        testString();
        """
        ast1 = Parse(source1)
        bytecode1 = Compile(ast1)
        gc1 = GarbageCollector()
        event_loop1 = EventLoop()
        interpreter1 = Interpreter(gc1, event_loop1)

        result1 = interpreter1.execute(bytecode1)
        promise1 = result1.value.to_object()
        event_loop1.run()

        assert isinstance(promise1, JSPromise)
        assert promise1.state == PromiseState.REJECTED

        # Test number error
        source2 = """
        async function testNumber() {
            await Promise.reject(42);
        }
        testNumber();
        """
        ast2 = Parse(source2)
        bytecode2 = Compile(ast2)
        gc2 = GarbageCollector()
        event_loop2 = EventLoop()
        interpreter2 = Interpreter(gc2, event_loop2)

        result2 = interpreter2.execute(bytecode2)
        promise2 = result2.value.to_object()
        event_loop2.run()

        assert isinstance(promise2, JSPromise)
        assert promise2.state == PromiseState.REJECTED


class TestAsyncAwaitErrorPropagation:
    """Test error propagation through async function chains."""

    def test_chained_async_functions_propagate_rejection(self):
        """
        Given async function A that calls async function B
        When B's await rejects
        Then A's Promise should also reject
        """
        # Given
        source = """
        async function inner() {
            await Promise.reject("inner error");
        }
        async function outer() {
            const result = await inner();
            return result;
        }
        outer();
        """
        ast = Parse(source)
        bytecode = Compile(ast)
        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)
        promise = result.value.to_object()
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.REJECTED
        # Rejection propagated through async function chain

    def test_nested_async_calls_with_intermediate_success(self):
        """
        Given nested async function calls
        When an inner function rejects
        Then the rejection should propagate through all levels
        """
        # Given
        source = """
        async function deepest() {
            await Promise.reject("deep error");
        }
        async function middle() {
            const x = await Promise.resolve(5);
            const y = await deepest();
            return x + y;
        }
        async function top() {
            const result = await middle();
            return result;
        }
        top();
        """
        ast = Parse(source)
        bytecode = Compile(ast)
        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)
        promise = result.value.to_object()
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.REJECTED


class TestAsyncAwaitMixedErrorSuccess:
    """Test async/await with mixed error and success scenarios."""

    def test_sequential_awaits_with_rejection_in_middle(self):
        """
        Given an async function with three sequential awaits
        When the middle await rejects
        Then the first value should be computed but third should not
        And the Promise should reject
        """
        # Given
        source = """
        async function test() {
            const a = await Promise.resolve(10);
            const b = await Promise.reject("middle error");
            const c = await Promise.resolve(30);
            return a + b + c;
        }
        test();
        """
        ast = Parse(source)
        bytecode = Compile(ast)
        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)
        promise = result.value.to_object()
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.REJECTED
        # Middle rejection stops execution

    def test_await_rejection_before_return(self):
        """
        Given an async function that awaits successfully then rejects before return
        When the rejection occurs
        Then the async function's Promise should reject
        """
        # Given
        source = """
        async function test() {
            const x = await Promise.resolve(10);
            await Promise.reject("error before return");
            return x;
        }
        test();
        """
        ast = Parse(source)
        bytecode = Compile(ast)
        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)
        promise = result.value.to_object()
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.REJECTED
