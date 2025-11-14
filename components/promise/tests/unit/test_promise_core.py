"""Unit tests for Promise core implementation.

These tests verify the fundamental Promise behavior according to ECMAScript spec:
- Promise construction and executor execution
- State transitions (PENDING -> FULFILLED/REJECTED)
- Promise resolution and rejection
- then() method and chaining
- catch() method
- finally() method
"""

import pytest
from components.event_loop.src import EventLoop
from components.promise.src import JSPromise, PromiseState


class TestPromiseConstruction:
    """Test Promise object creation and initialization."""

    def test_promise_creation(self):
        """Test creating a Promise."""
        loop = EventLoop()
        promise = JSPromise(lambda resolve, reject: None, loop)

        assert promise.state == PromiseState.PENDING
        assert promise.value is None
        assert promise.event_loop is loop

    def test_executor_runs_immediately(self):
        """Executor should run synchronously during construction."""
        loop = EventLoop()
        executed = []

        promise = JSPromise(lambda resolve, reject: executed.append(1), loop)

        assert executed == [1]

    def test_executor_receives_resolve_reject(self):
        """Executor should receive resolve and reject functions."""
        loop = EventLoop()

        def executor(resolve, reject):
            assert callable(resolve)
            assert callable(reject)

        promise = JSPromise(executor, loop)


class TestPromiseResolution:
    """Test Promise resolution and rejection behavior."""

    def test_resolve_fulfills_promise(self):
        """Calling resolve() should fulfill the Promise."""
        loop = EventLoop()

        def executor(resolve, reject):
            resolve(42)

        promise = JSPromise(executor, loop)
        loop.run()  # Process microtasks

        assert promise.state == PromiseState.FULFILLED
        assert promise.value == 42

    def test_reject_rejects_promise(self):
        """Calling reject() should reject the Promise."""
        loop = EventLoop()

        def executor(resolve, reject):
            reject("error")

        promise = JSPromise(executor, loop)
        loop.run()

        assert promise.state == PromiseState.REJECTED
        assert promise.value == "error"

    def test_exception_in_executor_rejects(self):
        """Exception in executor should reject the Promise."""
        loop = EventLoop()

        def executor(resolve, reject):
            raise ValueError("test error")

        promise = JSPromise(executor, loop)

        assert promise.state == PromiseState.REJECTED
        assert isinstance(promise.value, ValueError)
        assert str(promise.value) == "test error"

    def test_promise_can_only_settle_once_fulfill(self):
        """Once fulfilled, Promise cannot change state."""
        loop = EventLoop()
        resolve_func = None
        reject_func = None

        def executor(resolve, reject):
            nonlocal resolve_func, reject_func
            resolve_func = resolve
            reject_func = reject

        promise = JSPromise(executor, loop)

        resolve_func(42)
        loop.run()
        assert promise.state == PromiseState.FULFILLED
        assert promise.value == 42

        # Try to reject (should be ignored)
        reject_func("error")
        loop.run()
        assert promise.state == PromiseState.FULFILLED  # Still fulfilled
        assert promise.value == 42  # Original value

    def test_promise_can_only_settle_once_reject(self):
        """Once rejected, Promise cannot change state."""
        loop = EventLoop()
        resolve_func = None
        reject_func = None

        def executor(resolve, reject):
            nonlocal resolve_func, reject_func
            resolve_func = resolve
            reject_func = reject

        promise = JSPromise(executor, loop)

        reject_func("error")
        loop.run()
        assert promise.state == PromiseState.REJECTED
        assert promise.value == "error"

        # Try to resolve (should be ignored)
        resolve_func(42)
        loop.run()
        assert promise.state == PromiseState.REJECTED  # Still rejected
        assert promise.value == "error"  # Original reason


class TestThenMethod:
    """Test Promise.then() method behavior."""

    def test_then_registers_fulfillment_handler(self):
        """then() should register fulfillment handler."""
        loop = EventLoop()
        result = []

        def executor(resolve, reject):
            resolve(42)

        promise = JSPromise(executor, loop)
        promise.then(lambda value: result.append(value))
        loop.run()

        assert result == [42]

    def test_then_registers_rejection_handler(self):
        """then() should register rejection handler."""
        loop = EventLoop()
        result = []

        def executor(resolve, reject):
            reject("error")

        promise = JSPromise(executor, loop)
        promise.then(None, lambda reason: result.append(reason))
        loop.run()

        assert result == ["error"]

    def test_then_on_already_fulfilled_promise(self):
        """then() on already fulfilled Promise should queue microtask."""
        loop = EventLoop()
        result = []

        def executor(resolve, reject):
            resolve(42)

        promise = JSPromise(executor, loop)
        loop.run()  # Settle the promise

        # Now add handler after settlement
        promise.then(lambda value: result.append(value))
        assert result == []  # Not executed yet (microtask queued)

        loop.run()  # Process microtask
        assert result == [42]

    def test_then_on_already_rejected_promise(self):
        """then() on already rejected Promise should queue microtask."""
        loop = EventLoop()
        result = []

        def executor(resolve, reject):
            reject("error")

        promise = JSPromise(executor, loop)
        loop.run()  # Settle the promise

        # Now add handler after settlement
        promise.then(None, lambda reason: result.append(reason))
        assert result == []  # Not executed yet

        loop.run()  # Process microtask
        assert result == ["error"]

    def test_then_returns_new_promise(self):
        """then() should return a new Promise."""
        loop = EventLoop()

        promise1 = JSPromise(lambda resolve, reject: resolve(1), loop)
        promise2 = promise1.then(lambda x: x + 1)

        assert isinstance(promise2, JSPromise)
        assert promise2 is not promise1

    def test_multiple_then_handlers(self):
        """Multiple then() calls should all execute."""
        loop = EventLoop()
        result = []

        promise = JSPromise(lambda resolve, reject: resolve(42), loop)
        promise.then(lambda x: result.append(x))
        promise.then(lambda x: result.append(x * 2))
        promise.then(lambda x: result.append(x * 3))
        loop.run()

        assert result == [42, 84, 126]


class TestCatchMethod:
    """Test Promise.catch() method behavior."""

    def test_catch_is_shorthand_for_then(self):
        """catch() should be equivalent to then(None, onRejected)."""
        loop = EventLoop()
        result = []

        promise = JSPromise(lambda resolve, reject: reject("error"), loop)
        promise.catch(lambda reason: result.append(reason))
        loop.run()

        assert result == ["error"]

    def test_catch_does_not_handle_fulfillment(self):
        """catch() should not execute for fulfilled Promises."""
        loop = EventLoop()
        result = []

        promise = JSPromise(lambda resolve, reject: resolve(42), loop)
        promise.catch(lambda reason: result.append("caught"))
        loop.run()

        assert result == []  # Handler not called


class TestFinallyMethod:
    """Test Promise.finally() method behavior."""

    def test_finally_on_fulfilled_promise(self):
        """finally() should execute on fulfilled Promise."""
        loop = EventLoop()
        result = []

        promise = JSPromise(lambda resolve, reject: resolve(42), loop)
        promise.finally_handler(lambda: result.append("finally"))
        loop.run()

        assert result == ["finally"]

    def test_finally_on_rejected_promise(self):
        """finally() should execute on rejected Promise."""
        loop = EventLoop()
        result = []

        promise = JSPromise(lambda resolve, reject: reject("error"), loop)
        promise.finally_handler(lambda: result.append("finally"))
        loop.run()

        assert result == ["finally"]

    def test_finally_returns_promise(self):
        """finally() should return a Promise."""
        loop = EventLoop()

        promise1 = JSPromise(lambda resolve, reject: resolve(42), loop)
        promise2 = promise1.finally_handler(lambda: None)

        assert isinstance(promise2, JSPromise)
        assert promise2 is not promise1
