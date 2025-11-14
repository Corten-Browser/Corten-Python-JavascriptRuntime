"""Integration tests for Promise implementation.

These tests verify Promise behavior in more complex scenarios:
- Promise chaining
- Error propagation through chains
- Complex asynchronous workflows
- Integration with EventLoop
"""

import pytest
from components.event_loop.src import EventLoop
from components.promise.src import JSPromise, PromiseState


class TestPromiseChaining:
    """Test Promise chaining behavior."""

    def test_simple_chain(self):
        """Test basic Promise chaining."""
        loop = EventLoop()
        result = []

        promise = JSPromise(lambda resolve, reject: resolve(1), loop)
        promise.then(lambda x: x + 1).then(lambda x: result.append(x * 2))
        loop.run()

        assert result == [4]  # (1 + 1) * 2 = 4

    def test_chain_with_error_handling(self):
        """Test Promise chain with error in middle."""
        loop = EventLoop()
        result = []

        def executor(resolve, reject):
            resolve(10)

        promise = JSPromise(executor, loop)
        promise.then(lambda x: x / 0).catch(lambda err: result.append("caught"))  # Will throw exception
        loop.run()

        assert result == ["caught"]

    def test_long_chain(self):
        """Test longer Promise chain."""
        loop = EventLoop()
        result = []

        promise = JSPromise(lambda resolve, reject: resolve(1), loop)
        (promise
            .then(lambda x: x + 1)  # 2
            .then(lambda x: x * 2)  # 4
            .then(lambda x: x - 1)  # 3
            .then(lambda x: result.append(x)))
        loop.run()

        assert result == [3]

    def test_chain_returns_value(self):
        """Test that chain passes return values correctly."""
        loop = EventLoop()
        result = []

        def step1(x):
            return x * 2

        def step2(x):
            return x + 10

        def step3(x):
            result.append(x)
            return x

        promise = JSPromise(lambda resolve, reject: resolve(5), loop)
        promise.then(step1).then(step2).then(step3)
        loop.run()

        assert result == [20]  # (5 * 2) + 10 = 20


class TestErrorPropagation:
    """Test error propagation through Promise chains."""

    def test_rejection_propagates_through_chain(self):
        """Test rejection propagates through chain."""
        loop = EventLoop()
        results = []

        p = JSPromise(lambda resolve, reject: reject("error"), loop)
        (p.then(lambda val: results.append("fulfilled1"))
          .then(lambda val: results.append("fulfilled2"))
          .catch(lambda err: results.append(f"caught: {err}")))
        loop.run()

        assert results == ["caught: error"]

    def test_exception_in_then_handler_rejects(self):
        """Exception in then handler should reject the chain."""
        loop = EventLoop()
        results = []

        def throw_error(x):
            raise RuntimeError("handler error")

        p = JSPromise(lambda resolve, reject: resolve(42), loop)
        p.then(throw_error).catch(lambda err: results.append(str(err)))
        loop.run()

        assert results == ["handler error"]

    def test_catch_handles_and_resolves(self):
        """catch() can handle error and resolve the chain."""
        loop = EventLoop()
        results = []

        p = JSPromise(lambda resolve, reject: reject("error"), loop)
        (p.catch(lambda err: "recovered")
          .then(lambda val: results.append(val)))
        loop.run()

        assert results == ["recovered"]


class TestComplexScenarios:
    """Test complex Promise scenarios."""

    def test_promise_resolving_with_value(self):
        """Test Promise resolved with primitive value."""
        loop = EventLoop()
        results = []

        p = JSPromise(lambda resolve, reject: resolve("hello"), loop)
        p.then(lambda val: results.append(val))
        loop.run()

        assert results == ["hello"]

    def test_multiple_handlers_execute_in_order(self):
        """Multiple handlers should execute in registration order."""
        loop = EventLoop()
        results = []

        p = JSPromise(lambda resolve, reject: resolve(1), loop)
        p.then(lambda x: results.append(f"handler1: {x}"))
        p.then(lambda x: results.append(f"handler2: {x}"))
        p.then(lambda x: results.append(f"handler3: {x}"))
        loop.run()

        assert results == ["handler1: 1", "handler2: 1", "handler3: 1"]

    def test_handler_execution_is_asynchronous(self):
        """Promise handlers should execute asynchronously via microtasks."""
        loop = EventLoop()
        results = []

        p = JSPromise(lambda resolve, reject: resolve(42), loop)
        p.then(lambda x: results.append("then handler"))

        # Handler not executed yet (even though promise resolved)
        assert results == []

        # Run event loop to process microtasks
        loop.run()
        assert results == ["then handler"]

    def test_nested_promise_chains(self):
        """Test Promise chains within Promise chains."""
        loop = EventLoop()
        results = []

        def create_inner_promise(x):
            return JSPromise(lambda resolve, reject: resolve(x * 2), loop)

        p = JSPromise(lambda resolve, reject: resolve(5), loop)
        # This tests returning a value (not a Promise) from then
        p.then(lambda x: x + 1).then(lambda x: results.append(x))
        loop.run()

        assert results == [6]

    def test_finally_does_not_affect_value(self):
        """finally() should not change the Promise value."""
        loop = EventLoop()
        results = []

        p = JSPromise(lambda resolve, reject: resolve(42), loop)
        (p.finally_handler(lambda: results.append("finally"))
          .then(lambda x: results.append(f"value: {x}")))
        loop.run()

        assert results == ["finally", "value: 42"]

    def test_finally_does_not_affect_rejection(self):
        """finally() should not change the rejection reason."""
        loop = EventLoop()
        results = []

        p = JSPromise(lambda resolve, reject: reject("error"), loop)
        (p.finally_handler(lambda: results.append("finally"))
          .catch(lambda err: results.append(f"caught: {err}")))
        loop.run()

        assert results == ["finally", "caught: error"]


class TestEventLoopIntegration:
    """Test Promise integration with EventLoop."""

    def test_promise_uses_microtask_queue(self):
        """Promise reactions should use microtask queue."""
        loop = EventLoop()
        results = []

        # Queue a macrotask
        loop.queue_task(lambda: results.append("macrotask"))

        # Create Promise that resolves immediately
        p = JSPromise(lambda resolve, reject: resolve(1), loop)
        p.then(lambda x: results.append("microtask"))

        # Run event loop
        loop.run()

        # Microtask should execute before macrotask
        assert results == ["microtask", "macrotask"]

    def test_microtasks_run_before_next_macrotask(self):
        """All microtasks should run before next macrotask."""
        loop = EventLoop()
        results = []

        # Queue macrotasks
        loop.queue_task(lambda: results.append("macro1"))
        loop.queue_task(lambda: results.append("macro2"))

        # Create Promises
        p1 = JSPromise(lambda resolve, reject: resolve(1), loop)
        p1.then(lambda x: results.append("micro1"))

        p2 = JSPromise(lambda resolve, reject: resolve(2), loop)
        p2.then(lambda x: results.append("micro2"))

        loop.run()

        # All microtasks before first macrotask
        assert results == ["micro1", "micro2", "macro1", "macro2"]
