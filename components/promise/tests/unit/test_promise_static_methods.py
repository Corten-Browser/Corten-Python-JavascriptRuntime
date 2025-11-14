"""Unit tests for Promise static methods.

Tests for:
- Promise.resolve()
- Promise.reject()
- Promise.all()
- Promise.race()
- Promise.any()
- Promise.allSettled()
- AggregateError exception
"""

import pytest
from components.event_loop.src import EventLoop
from components.promise.src import JSPromise, PromiseState, AggregateError


class TestPromiseResolve:
    """Test Promise.resolve() static method."""

    def test_resolve_with_value(self):
        """Promise.resolve(value) creates fulfilled Promise."""
        loop = EventLoop()

        promise = JSPromise.resolve(42, loop)
        loop.run()

        assert promise.state == PromiseState.FULFILLED
        assert promise.value == 42

    def test_resolve_with_promise(self):
        """Promise.resolve(promise) returns same promise."""
        loop = EventLoop()

        original = JSPromise(lambda resolve, reject: resolve(42), loop)
        result = JSPromise.resolve(original, loop)

        assert result is original

    def test_resolve_can_be_chained(self):
        """Promise.resolve() can be used in chains."""
        loop = EventLoop()
        results = []

        JSPromise.resolve(10, loop).then(lambda x: results.append(x * 2))
        loop.run()

        assert results == [20]

    def test_resolve_with_none(self):
        """Promise.resolve(None) creates fulfilled Promise with None."""
        loop = EventLoop()

        promise = JSPromise.resolve(None, loop)
        loop.run()

        assert promise.state == PromiseState.FULFILLED
        assert promise.value is None

    def test_resolve_with_string(self):
        """Promise.resolve() works with string values."""
        loop = EventLoop()

        promise = JSPromise.resolve("hello", loop)
        loop.run()

        assert promise.state == PromiseState.FULFILLED
        assert promise.value == "hello"


class TestPromiseReject:
    """Test Promise.reject() static method."""

    def test_reject_with_reason(self):
        """Promise.reject(reason) creates rejected Promise."""
        loop = EventLoop()

        promise = JSPromise.reject("error", loop)
        loop.run()

        assert promise.state == PromiseState.REJECTED
        assert promise.value == "error"

    def test_reject_can_be_caught(self):
        """Promise.reject() can be caught."""
        loop = EventLoop()
        results = []

        JSPromise.reject("error", loop).catch(lambda err: results.append(f"caught: {err}"))
        loop.run()

        assert results == ["caught: error"]

    def test_reject_with_exception(self):
        """Promise.reject() works with exception objects."""
        loop = EventLoop()

        error = ValueError("test error")
        promise = JSPromise.reject(error, loop)
        loop.run()

        assert promise.state == PromiseState.REJECTED
        assert promise.value is error

    def test_reject_with_none(self):
        """Promise.reject(None) creates rejected Promise with None."""
        loop = EventLoop()

        promise = JSPromise.reject(None, loop)
        loop.run()

        assert promise.state == PromiseState.REJECTED
        assert promise.value is None


class TestPromiseAll:
    """Test Promise.all() static method."""

    def test_all_with_fulfilled_promises(self):
        """Promise.all() fulfills when all promises fulfill."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.resolve(1, loop),
            JSPromise.resolve(2, loop),
            JSPromise.resolve(3, loop)
        ]

        JSPromise.all(promises, loop).then(lambda values: results.append(values))
        loop.run()

        assert results == [[1, 2, 3]]

    def test_all_with_rejected_promise(self):
        """Promise.all() rejects if any promise rejects."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.resolve(1, loop),
            JSPromise.reject("error", loop),
            JSPromise.resolve(3, loop)
        ]

        JSPromise.all(promises, loop).catch(lambda err: results.append(err))
        loop.run()

        assert results == ["error"]

    def test_all_with_empty_list(self):
        """Promise.all([]) resolves immediately with empty array."""
        loop = EventLoop()
        results = []

        JSPromise.all([], loop).then(lambda values: results.append(values))
        loop.run()

        assert results == [[]]

    def test_all_rejects_with_first_rejection(self):
        """Promise.all() rejects with first rejection reason."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.reject("error1", loop),
            JSPromise.reject("error2", loop)
        ]

        JSPromise.all(promises, loop).catch(lambda err: results.append(err))
        loop.run()

        # Should reject with first error (microtask order)
        assert results[0] in ["error1", "error2"]

    def test_all_with_single_promise(self):
        """Promise.all() works with single promise."""
        loop = EventLoop()
        results = []

        promises = [JSPromise.resolve(42, loop)]

        JSPromise.all(promises, loop).then(lambda values: results.append(values))
        loop.run()

        assert results == [[42]]

    def test_all_preserves_order(self):
        """Promise.all() preserves input order in results."""
        loop = EventLoop()
        results = []
        resolve_funcs = []

        # Create promises that we control
        promises = [
            JSPromise(lambda resolve, reject: resolve_funcs.append(("p1", resolve)), loop),
            JSPromise(lambda resolve, reject: resolve_funcs.append(("p2", resolve)), loop),
            JSPromise(lambda resolve, reject: resolve_funcs.append(("p3", resolve)), loop)
        ]

        JSPromise.all(promises, loop).then(lambda values: results.append(values))

        # Resolve in different order
        resolve_funcs[2][1](3)  # Resolve p3 first
        resolve_funcs[0][1](1)  # Then p1
        resolve_funcs[1][1](2)  # Finally p2

        loop.run()

        # Should preserve input order
        assert results == [[1, 2, 3]]


class TestPromiseRace:
    """Test Promise.race() static method."""

    def test_race_with_first_fulfilled(self):
        """Promise.race() settles with first settlement."""
        loop = EventLoop()
        results = []
        resolve_funcs = []

        promises = [
            JSPromise(lambda resolve, reject: resolve_funcs.append(resolve), loop),
            JSPromise(lambda resolve, reject: resolve_funcs.append(resolve), loop)
        ]

        JSPromise.race(promises, loop).then(lambda value: results.append(value))

        # Resolve first promise
        resolve_funcs[0](42)
        loop.run()

        assert results == [42]

    def test_race_with_first_rejected(self):
        """Promise.race() can settle with first rejection."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.reject("error", loop),
            JSPromise.resolve(42, loop)
        ]

        JSPromise.race(promises, loop).catch(lambda err: results.append(err))
        loop.run()

        # Should settle with first (which could be either depending on microtask order)
        assert len(results) == 1

    def test_race_with_empty_list(self):
        """Promise.race([]) never settles."""
        loop = EventLoop()
        results = []

        promise = JSPromise.race([], loop)
        promise.then(lambda v: results.append(v))
        loop.run()

        assert results == []  # Never settles
        assert promise.state == PromiseState.PENDING

    def test_race_with_single_promise(self):
        """Promise.race() works with single promise."""
        loop = EventLoop()
        results = []

        promises = [JSPromise.resolve(42, loop)]

        JSPromise.race(promises, loop).then(lambda value: results.append(value))
        loop.run()

        assert results == [42]

    def test_race_ignores_later_settlements(self):
        """Promise.race() ignores settlements after first."""
        loop = EventLoop()
        results = []
        resolve_funcs = []

        promises = [
            JSPromise(lambda resolve, reject: resolve_funcs.append(("p1", resolve)), loop),
            JSPromise(lambda resolve, reject: resolve_funcs.append(("p2", resolve)), loop)
        ]

        JSPromise.race(promises, loop).then(lambda value: results.append(value))

        # Resolve both, but only first should count
        resolve_funcs[0][1](1)
        resolve_funcs[1][1](2)

        loop.run()

        assert results == [1]  # Only first result


class TestPromiseAny:
    """Test Promise.any() static method."""

    def test_any_with_first_fulfilled(self):
        """Promise.any() fulfills with first fulfillment."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.resolve(1, loop),
            JSPromise.resolve(2, loop)
        ]

        JSPromise.any(promises, loop).then(lambda value: results.append(value))
        loop.run()

        # Should fulfill with first (microtask order)
        assert len(results) == 1
        assert results[0] in [1, 2]

    def test_any_rejects_if_all_reject(self):
        """Promise.any() rejects with AggregateError if all reject."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.reject("error1", loop),
            JSPromise.reject("error2", loop)
        ]

        JSPromise.any(promises, loop).catch(lambda err: results.append(err))
        loop.run()

        assert len(results) == 1
        assert isinstance(results[0], AggregateError)
        assert len(results[0].errors) == 2

    def test_any_with_empty_list(self):
        """Promise.any([]) rejects with AggregateError."""
        loop = EventLoop()
        results = []

        JSPromise.any([], loop).catch(lambda err: results.append(err))
        loop.run()

        assert len(results) == 1
        assert isinstance(results[0], AggregateError)
        assert len(results[0].errors) == 0

    def test_any_ignores_rejections_if_one_fulfills(self):
        """Promise.any() fulfills even if some promises reject."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.reject("error", loop),
            JSPromise.resolve(42, loop)
        ]

        JSPromise.any(promises, loop).then(lambda value: results.append(value))
        loop.run()

        assert 42 in results

    def test_any_with_single_fulfilled_promise(self):
        """Promise.any() with single fulfilled promise."""
        loop = EventLoop()
        results = []

        promises = [JSPromise.resolve(42, loop)]

        JSPromise.any(promises, loop).then(lambda value: results.append(value))
        loop.run()

        assert results == [42]

    def test_any_with_single_rejected_promise(self):
        """Promise.any() with single rejected promise."""
        loop = EventLoop()
        results = []

        promises = [JSPromise.reject("error", loop)]

        JSPromise.any(promises, loop).catch(lambda err: results.append(err))
        loop.run()

        assert len(results) == 1
        assert isinstance(results[0], AggregateError)
        assert len(results[0].errors) == 1


class TestPromiseAllSettled:
    """Test Promise.allSettled() static method."""

    def test_allSettled_with_fulfilled_promises(self):
        """Promise.allSettled() with all fulfilled."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.resolve(1, loop),
            JSPromise.resolve(2, loop)
        ]

        JSPromise.allSettled(promises, loop).then(lambda values: results.append(values))
        loop.run()

        assert len(results) == 1
        assert len(results[0]) == 2
        assert results[0][0] == {"status": "fulfilled", "value": 1}
        assert results[0][1] == {"status": "fulfilled", "value": 2}

    def test_allSettled_with_rejected_promises(self):
        """Promise.allSettled() with all rejected."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.reject("error1", loop),
            JSPromise.reject("error2", loop)
        ]

        JSPromise.allSettled(promises, loop).then(lambda values: results.append(values))
        loop.run()

        assert len(results) == 1
        assert len(results[0]) == 2
        assert results[0][0] == {"status": "rejected", "reason": "error1"}
        assert results[0][1] == {"status": "rejected", "reason": "error2"}

    def test_allSettled_with_mixed(self):
        """Promise.allSettled() with mixed fulfilled/rejected."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.resolve(42, loop),
            JSPromise.reject("error", loop),
            JSPromise.resolve(100, loop)
        ]

        JSPromise.allSettled(promises, loop).then(lambda values: results.append(values))
        loop.run()

        assert len(results) == 1
        assert len(results[0]) == 3
        assert results[0][0] == {"status": "fulfilled", "value": 42}
        assert results[0][1] == {"status": "rejected", "reason": "error"}
        assert results[0][2] == {"status": "fulfilled", "value": 100}

    def test_allSettled_with_empty_list(self):
        """Promise.allSettled([]) resolves immediately."""
        loop = EventLoop()
        results = []

        JSPromise.allSettled([], loop).then(lambda values: results.append(values))
        loop.run()

        assert results == [[]]

    def test_allSettled_with_single_promise(self):
        """Promise.allSettled() with single promise."""
        loop = EventLoop()
        results = []

        promises = [JSPromise.resolve(42, loop)]

        JSPromise.allSettled(promises, loop).then(lambda values: results.append(values))
        loop.run()

        assert len(results) == 1
        assert results[0] == [{"status": "fulfilled", "value": 42}]

    def test_allSettled_preserves_order(self):
        """Promise.allSettled() preserves input order."""
        loop = EventLoop()
        results = []
        resolve_funcs = []
        reject_funcs = []

        promises = [
            JSPromise(lambda resolve, reject: (resolve_funcs.append(resolve), reject_funcs.append(reject)), loop),
            JSPromise(lambda resolve, reject: (resolve_funcs.append(resolve), reject_funcs.append(reject)), loop),
            JSPromise(lambda resolve, reject: (resolve_funcs.append(resolve), reject_funcs.append(reject)), loop)
        ]

        JSPromise.allSettled(promises, loop).then(lambda values: results.append(values))

        # Settle in different order
        reject_funcs[2]("error3")  # Reject p3 first
        resolve_funcs[0](1)         # Fulfill p1
        reject_funcs[1]("error2")   # Reject p2

        loop.run()

        assert len(results) == 1
        assert results[0][0] == {"status": "fulfilled", "value": 1}
        assert results[0][1] == {"status": "rejected", "reason": "error2"}
        assert results[0][2] == {"status": "rejected", "reason": "error3"}
