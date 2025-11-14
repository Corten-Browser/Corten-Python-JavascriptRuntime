"""Simple async/await integration tests (Phase 2.6.3+).

Tests basic async function execution with single and multiple await expressions.
Error handling will be tested in later phases.
"""

import pytest
from components.parser.src import Parse
from components.bytecode.src import Compile
from components.interpreter.src import Interpreter
from components.memory_gc.src import GarbageCollector
from components.event_loop.src import EventLoop
from components.promise.src import JSPromise, PromiseState
from components.value_system.src import Value


class TestAsyncFunctionBasics:
    """Test basic async function execution without await."""

    def test_async_function_returns_promise(self):
        """
        Given an async function without await
        When the function is called
        Then it should return a Promise immediately
        """
        # Given
        source = """
        async function test() {
            return 42;
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

        # Then
        result_obj = result.value.to_object()
        assert isinstance(result_obj, JSPromise), f"Expected JSPromise, got {type(result_obj)}"

    def test_async_function_resolves_simple_value(self):
        """
        Given an async function that returns a constant
        When the function executes and event loop runs
        Then the Promise should resolve with that constant
        """
        # Given
        source = """
        async function test() {
            return 42;
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
        promise = result.value.to_object()  # Get promise reference before event loop
        event_loop.run()  # Process microtasks

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 42

    def test_async_function_with_no_return(self):
        """
        Given an async function with no return statement
        When the function executes
        Then the Promise should resolve with undefined
        """
        # Given
        source = """
        async function test() {
            const x = 10;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED


class TestSingleAwait:
    """Test async functions with single await expression."""

    def test_await_promise_resolve(self):
        """
        Given an async function that awaits Promise.resolve
        When the Promise resolves
        Then the await expression should receive the resolved value
        """
        # Given
        source = """
        async function test() {
            const x = await Promise.resolve(10);
            return x * 2;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()  # Process microtasks

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 20

    def test_await_immediate_value(self):
        """
        Given an async function that awaits a non-Promise value
        When execution occurs
        Then the value should be wrapped in a resolved Promise
        """
        # Given
        source = """
        async function test() {
            const x = await 42;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 42

    def test_await_with_arithmetic(self):
        """
        Given an async function that performs arithmetic with awaited value
        When the Promise resolves
        Then arithmetic should be performed correctly
        """
        # Given
        source = """
        async function test() {
            const x = await Promise.resolve(5);
            return x + 5;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 10

    def test_await_with_local_variables(self):
        """
        Given an async function using local variables with await
        When execution occurs
        Then local variables should be preserved across await
        """
        # Given
        source = """
        async function test() {
            const a = 10;
            const b = await Promise.resolve(20);
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        if promise.state != PromiseState.FULFILLED:
            print(f"❌ Promise was REJECTED: {promise.value}")
            print(f"   Rejection type: {type(promise.value)}")
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 30


class TestAsyncAwaitIntegration:
    """Integration with Promise system and event loop."""

    def test_event_loop_processes_async_microtasks(self):
        """
        Given an async function with await
        When event loop runs
        Then microtasks should be processed in correct order
        """
        # Given
        source = """
        async function test() {
            const x = await Promise.resolve(5);
            return x + 5;
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
        promise = result.value.to_object()  # Get promise before event loop

        # Then - Promise should be pending before event loop runs
        assert promise.state == PromiseState.PENDING

        # When - Run event loop
        event_loop.run()

        # Then - Promise should be fulfilled after event loop runs
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 10

    def test_async_function_then_chaining(self):
        """
        Given an async function that returns a Promise
        When .then() is called on the result
        Then the then handler should receive the resolved value
        """
        # Given
        source = """
        async function test() {
            return 42;
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
        promise = result.value.to_object()  # Get promise before event loop

        # Track if handler was called
        result_value = [None]

        def handler(value):
            result_value[0] = value

        promise.then(handler, None)
        event_loop.run()

        # Then
        assert result_value[0] is not None
        assert result_value[0].to_smi() == 42

    def test_multiple_async_functions(self):
        """
        Given multiple async functions called sequentially
        When event loop runs
        Then all should resolve correctly
        """
        # Given
        source = """
        async function test1() {
            return 10;
        }
        async function test2() {
            return 20;
        }
        test2();
        """
        ast = Parse(source)
        bytecode = Compile(ast)
        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 20


class TestAsyncAwaitEdgeCases:
    """Edge cases and special scenarios."""

    def test_await_zero_value(self):
        """
        Given an async function that awaits 0
        When execution occurs
        Then 0 should be correctly handled (not treated as falsy)
        """
        # Given
        source = """
        async function test() {
            const x = await 0;
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
        interpreter.execute(bytecode)
        event_loop.run()

        # Then
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 0

    def test_async_function_immediate_return(self):
        """
        Given an async function with immediate return (no await)
        When the function executes
        Then Promise should resolve synchronously via microtask
        """
        # Given
        source = """
        async function test() {
            return 100;
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
        promise = result.value.to_object()  # Get promise before event loop

        # Promise starts as pending
        initial_state = promise.state

        # Run event loop
        event_loop.run()

        # Then
        assert initial_state == PromiseState.PENDING or initial_state == PromiseState.FULFILLED
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 100

    def test_await_resolved_promise_chain(self):
        """
        Given an async function awaiting a Promise chain
        When the chain resolves
        Then the final value should be received
        """
        # Given
        source = """
        async function test() {
            const x = await Promise.resolve(5);
            return x * 3;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 15

    def test_nested_async_function_calls(self):
        """
        Given one async function calling another
        When both execute
        Then both should resolve correctly
        """
        # Given
        source = """
        async function inner() {
            return 10;
        }
        async function outer() {
            const x = await inner();
            return x * 2;
        }
        const promise = outer();
        """
        ast = Parse(source)
        bytecode = Compile(ast)
        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 20

    def test_async_function_with_conditional(self):
        """
        Given an async function with conditional logic
        When execution occurs with await in conditional
        Then correct branch should execute
        """
        # Given
        source = """
        async function test() {
            const x = await Promise.resolve(10);
            if (x > 5) {
                return 100;
            } else {
                return 200;
            }
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 100

    def test_await_negative_value(self):
        """
        Given an async function awaiting negative value
        When execution occurs
        Then negative value should be preserved
        """
        # Given
        source = """
        async function test() {
            const x = await -42;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == -42

    def test_async_function_returns_awaited_value(self):
        """
        Given an async function that directly returns await expression
        When execution occurs
        Then the awaited value should be the return value
        """
        # Given
        source = """
        async function test() {
            return await Promise.resolve(77);
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 77


class TestMultipleAwaits:
    """Test async functions with multiple await expressions (Phase 2.6.4)."""

    def test_two_sequential_awaits(self):
        """
        Given an async function with two await expressions
        When both Promises resolve
        Then both values should be available for computation
        """
        # Given
        source = """
        async function test() {
            const x = await Promise.resolve(10);
            const y = await Promise.resolve(20);
            return x + y;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        if promise.state != PromiseState.FULFILLED:
            print(f"❌ Promise was REJECTED: {promise.value}")
            print(f"   Rejection type: {type(promise.value)}")
        assert promise.state == PromiseState.FULFILLED
        # Should be 30 (10 + 20)
        assert promise.value.to_smi() == 30

    def test_three_sequential_awaits(self):
        """
        Given an async function with three await expressions
        When all Promises resolve
        Then all values should be summed correctly
        """
        # Given
        source = """
        async function test() {
            const a = await Promise.resolve(1);
            const b = await Promise.resolve(2);
            const c = await Promise.resolve(3);
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 6

    def test_await_with_local_preservation(self):
        """
        Given local variables defined before await
        When await completes
        Then local variables should still be available
        """
        # Given
        source = """
        async function test() {
            const x = 100;
            const y = await Promise.resolve(50);
            return x + y;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 150

    def test_multiple_awaits_with_computation(self):
        """
        Given an async function with multiple awaits and intermediate computation
        When execution occurs
        Then all computations should be correct
        """
        # Given
        source = """
        async function test() {
            const a = await Promise.resolve(10);
            const b = a * 2;
            const c = await Promise.resolve(5);
            return b + c;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        # Should be 25 (10*2 + 5)
        assert promise.value.to_smi() == 25

    def test_nested_async_calls_multiple_awaits(self):
        """
        Given nested async functions each with multiple awaits
        When both execute
        Then all awaits should resolve correctly
        """
        # Given
        source = """
        async function inner() {
            const x = await Promise.resolve(10);
            return x * 2;
        }
        async function outer() {
            const a = await inner();
            const b = await Promise.resolve(5);
            return a + b;
        }
        var promise = outer();
        """
        ast = Parse(source)
        bytecode = Compile(ast)
        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        # Should be 25 (20 + 5)
        assert promise.value.to_smi() == 25

    def test_four_sequential_awaits(self):
        """
        Given an async function with four await expressions
        When all Promises resolve
        Then computation across all values should work
        """
        # Given
        source = """
        async function test() {
            const a = await Promise.resolve(1);
            const b = await Promise.resolve(2);
            const c = await Promise.resolve(3);
            const d = await Promise.resolve(4);
            return (a + b) * (c + d);
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        # Should be 21 ((1+2) * (3+4))
        assert promise.value.to_smi() == 21

    def test_multiple_awaits_mixed_values(self):
        """
        Given an async function awaiting both Promises and immediate values
        When execution occurs
        Then all values should be handled correctly
        """
        # Given
        source = """
        async function test() {
            const a = await Promise.resolve(10);
            const b = await 5;
            const c = await Promise.resolve(3);
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 18


class TestLocalVariablePreservation:
    """Verify locals are preserved across await suspension/resumption (Phase 2.6.4)."""

    def test_single_local_preserved_across_await(self):
        """
        Given a single local variable before await
        When await completes
        Then the local should be available after
        """
        # Given
        source = """
        async function test() {
            const x = 10;
            const y = await Promise.resolve(5);
            return x + y;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 15

    def test_multiple_locals_preserved(self):
        """
        Given multiple local variables before await
        When await completes
        Then all locals should be preserved
        """
        # Given
        source = """
        async function test() {
            const a = 1;
            const b = 2;
            const c = 3;
            const d = await Promise.resolve(4);
            return a + b + c + d;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 10

    def test_locals_from_parameters_preserved(self):
        """
        Given function parameters used with await
        When await completes
        Then parameters should be preserved
        """
        # Given
        source = """
        async function test(a, b) {
            const c = await Promise.resolve(3);
            return a + b + c;
        }
        var promise = test(10, 20);
        """
        ast = Parse(source)
        bytecode = Compile(ast)
        gc = GarbageCollector()
        event_loop = EventLoop()
        interpreter = Interpreter(gc, event_loop)

        # When
        result = interpreter.execute(bytecode)
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 33

    def test_locals_across_multiple_awaits(self):
        """
        Given locals defined at different points
        When multiple awaits occur
        Then all locals should remain accessible
        """
        # Given
        source = """
        async function test() {
            const a = 5;
            const b = await Promise.resolve(10);
            const c = 3;
            const d = await Promise.resolve(2);
            return a * b + c * d;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        # Should be 56 (5*10 + 3*2)
        assert promise.value.to_smi() == 56

    def test_locals_used_multiple_times(self):
        """
        Given a local variable used both before and after await
        When await completes
        Then the variable should have the same value
        """
        # Given
        source = """
        async function test() {
            const x = 100;
            const before = x;
            const y = await Promise.resolve(1);
            const after = x;
            return before + after + y;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        # Should be 201 (100 + 100 + 1)
        assert promise.value.to_smi() == 201

    def test_complex_expression_locals_preserved(self):
        """
        Given locals with complex expressions
        When await occurs
        Then computed values should be preserved
        """
        # Given
        source = """
        async function test() {
            const a = 2 + 3;
            const b = a * 4;
            const c = await Promise.resolve(10);
            return b + c;
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
        promise = result.value.to_object()  # Get promise before event loop
        event_loop.run()

        # Then
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        # Should be 30 ((2+3)*4 + 10 = 20 + 10)
        assert promise.value.to_smi() == 30
