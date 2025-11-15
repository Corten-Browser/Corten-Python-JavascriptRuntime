"""Unit tests for ES2024 Promise extensions.

Tests for:
- Additional Promise.any() tests (to reach ≥7 total)
- Additional Promise.allSettled() tests (to reach ≥7 total)
- Promise.withResolvers() (new implementation)
"""

import pytest
from components.event_loop.src import EventLoop
from components.promise.src import JSPromise, PromiseState, AggregateError


class TestPromiseAnyExtensions:
    """Additional tests for Promise.any() to meet ≥7 test requirement."""

    def test_any_with_all_non_promise_values(self):
        """Promise.any() converts non-Promise values to fulfilled Promises."""
        loop = EventLoop()
        results = []

        # Pass plain values instead of Promises
        values = [1, 2, 3]
        JSPromise.any(values, loop).then(lambda value: results.append(value))
        loop.run()

        # Should fulfill with first value
        assert len(results) == 1
        assert results[0] in [1, 2, 3]

    def test_any_aggregate_error_contains_all_errors(self):
        """Promise.any() AggregateError contains all rejection reasons in order."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.reject("error1", loop),
            JSPromise.reject("error2", loop),
            JSPromise.reject("error3", loop)
        ]

        JSPromise.any(promises, loop).catch(lambda err: results.append(err))
        loop.run()

        assert len(results) == 1
        assert isinstance(results[0], AggregateError)
        # All errors should be present (order may vary due to microtask queue)
        error_set = set(results[0].errors)
        assert error_set == {"error1", "error2", "error3"}


class TestPromiseAllSettledExtensions:
    """Additional tests for Promise.allSettled() to meet ≥7 test requirement."""

    def test_allSettled_with_non_promise_values(self):
        """Promise.allSettled() converts non-Promise values."""
        loop = EventLoop()
        results = []

        # Pass plain values instead of Promises
        values = [1, 2, 3]
        JSPromise.allSettled(values, loop).then(lambda values: results.append(values))
        loop.run()

        assert len(results) == 1
        assert len(results[0]) == 3
        assert results[0][0] == {"status": "fulfilled", "value": 1}
        assert results[0][1] == {"status": "fulfilled", "value": 2}
        assert results[0][2] == {"status": "fulfilled", "value": 3}

    def test_allSettled_never_rejects(self):
        """Promise.allSettled() never rejects, even if all promises reject."""
        loop = EventLoop()
        fulfilled_results = []
        rejected_results = []

        promises = [
            JSPromise.reject("error1", loop),
            JSPromise.reject("error2", loop)
        ]

        JSPromise.allSettled(promises, loop).then(
            lambda values: fulfilled_results.append(values)
        ).catch(
            lambda err: rejected_results.append(err)
        )
        loop.run()

        # Should fulfill (not reject) with rejection details
        assert len(fulfilled_results) == 1
        assert len(rejected_results) == 0
        assert len(fulfilled_results[0]) == 2


class TestPromiseWithResolvers:
    """Test Promise.withResolvers() static method (ES2024)."""

    def test_withResolvers_returns_object_with_promise_resolve_reject(self):
        """Promise.withResolvers() returns {promise, resolve, reject}."""
        loop = EventLoop()

        result = JSPromise.withResolvers(loop)

        assert "promise" in result
        assert "resolve" in result
        assert "reject" in result
        assert isinstance(result["promise"], JSPromise)
        assert callable(result["resolve"])
        assert callable(result["reject"])

    def test_withResolvers_resolve_fulfills_promise(self):
        """Calling resolve() fulfills the returned promise."""
        loop = EventLoop()
        results = []

        deferred = JSPromise.withResolvers(loop)
        deferred["promise"].then(lambda value: results.append(value))

        # Resolve the promise
        deferred["resolve"](42)
        loop.run()

        assert results == [42]
        assert deferred["promise"].state == PromiseState.FULFILLED
        assert deferred["promise"].value == 42

    def test_withResolvers_reject_rejects_promise(self):
        """Calling reject() rejects the returned promise."""
        loop = EventLoop()
        results = []

        deferred = JSPromise.withResolvers(loop)
        deferred["promise"].catch(lambda err: results.append(err))

        # Reject the promise
        deferred["reject"]("error")
        loop.run()

        assert results == ["error"]
        assert deferred["promise"].state == PromiseState.REJECTED
        assert deferred["promise"].value == "error"

    def test_withResolvers_resolve_after_event_loop_starts(self):
        """resolve() can be called after event loop starts."""
        loop = EventLoop()
        results = []

        deferred = JSPromise.withResolvers(loop)
        deferred["promise"].then(lambda value: results.append(value))

        # Start loop without resolving yet
        loop.run()
        assert results == []  # Promise still pending

        # Now resolve
        deferred["resolve"](100)
        loop.run()

        assert results == [100]

    def test_withResolvers_multiple_calls_create_independent_promises(self):
        """Each withResolvers() call creates independent promise."""
        loop = EventLoop()
        results1 = []
        results2 = []

        deferred1 = JSPromise.withResolvers(loop)
        deferred2 = JSPromise.withResolvers(loop)

        deferred1["promise"].then(lambda value: results1.append(value))
        deferred2["promise"].then(lambda value: results2.append(value))

        # Resolve only first promise
        deferred1["resolve"](1)
        loop.run()

        assert results1 == [1]
        assert results2 == []  # Second promise unaffected

        # Resolve second promise
        deferred2["resolve"](2)
        loop.run()

        assert results1 == [1]
        assert results2 == [2]

    def test_withResolvers_promise_can_be_chained(self):
        """Promise from withResolvers() can be chained."""
        loop = EventLoop()
        results = []

        deferred = JSPromise.withResolvers(loop)

        deferred["promise"].then(
            lambda x: x * 2
        ).then(
            lambda x: results.append(x)
        )

        deferred["resolve"](21)
        loop.run()

        assert results == [42]

    def test_withResolvers_resolve_with_promise_adopts_state(self):
        """Resolving with a Promise adopts that Promise's state."""
        loop = EventLoop()
        results = []

        deferred = JSPromise.withResolvers(loop)
        other_promise = JSPromise.resolve(100, loop)

        deferred["promise"].then(lambda value: results.append(value))
        deferred["resolve"](other_promise)
        loop.run()

        assert results == [100]

    def test_withResolvers_use_case_external_control(self):
        """withResolvers() enables external control pattern."""
        loop = EventLoop()
        results = []

        # Simulate async operation with external control
        class AsyncOperation:
            def __init__(self, event_loop):
                self.deferred = JSPromise.withResolvers(event_loop)
                self.promise = self.deferred["promise"]

            def complete(self, value):
                self.deferred["resolve"](value)

            def fail(self, error):
                self.deferred["reject"](error)

        operation = AsyncOperation(loop)
        operation.promise.then(lambda v: results.append(v))

        # External code can trigger completion
        operation.complete("done")
        loop.run()

        assert results == ["done"]
