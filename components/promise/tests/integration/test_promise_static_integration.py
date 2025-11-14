"""Integration tests for Promise static methods.

Tests complex scenarios involving:
- Chaining static methods
- Mixing Promises and non-Promise values
- Delayed resolutions
- Real-world usage patterns
"""

import pytest
from components.event_loop.src import EventLoop
from components.promise.src import JSPromise, PromiseState, AggregateError


class TestComplexStaticMethodScenarios:
    """Test complex scenarios with static methods."""

    def test_all_with_non_promise_values(self):
        """Promise.all() should handle non-Promise values."""
        loop = EventLoop()
        results = []

        # Mix Promises and non-Promise values
        promises = [
            JSPromise.resolve(1, loop),
            2,  # Non-Promise value
            JSPromise.resolve(3, loop)
        ]

        JSPromise.all(promises, loop).then(lambda values: results.append(values))
        loop.run()

        assert results == [[1, 2, 3]]

    def test_chaining_static_methods(self):
        """Test chaining multiple static method calls."""
        loop = EventLoop()
        results = []

        # Create promises, use all(), then chain
        promises = [
            JSPromise.resolve(1, loop),
            JSPromise.resolve(2, loop)
        ]

        (JSPromise.all(promises, loop)
         .then(lambda values: sum(values))
         .then(lambda total: results.append(total)))

        loop.run()

        assert results == [3]

    def test_race_with_delayed_resolution(self):
        """Test race with manually resolved promises."""
        loop = EventLoop()
        results = []
        resolve_funcs = []

        # Create pending promises
        p1 = JSPromise(lambda resolve, reject: resolve_funcs.append(("p1", resolve)), loop)
        p2 = JSPromise(lambda resolve, reject: resolve_funcs.append(("p2", resolve)), loop)

        JSPromise.race([p1, p2], loop).then(lambda value: results.append(value))

        # Resolve p2 first
        resolve_funcs[1][1](42)
        loop.run()

        assert results == [42]

    def test_nested_all_calls(self):
        """Test nested Promise.all() calls."""
        loop = EventLoop()
        results = []

        # Create nested structure
        inner1 = JSPromise.all([
            JSPromise.resolve(1, loop),
            JSPromise.resolve(2, loop)
        ], loop)

        inner2 = JSPromise.all([
            JSPromise.resolve(3, loop),
            JSPromise.resolve(4, loop)
        ], loop)

        JSPromise.all([inner1, inner2], loop).then(lambda values: results.append(values))
        loop.run()

        assert results == [[[1, 2], [3, 4]]]

    def test_any_race_combination(self):
        """Test combining Promise.any() and Promise.race()."""
        loop = EventLoop()
        results = []

        # Create promises
        p1 = JSPromise.resolve(1, loop)
        p2 = JSPromise.reject("error", loop)
        p3 = JSPromise.resolve(3, loop)

        # any([race([p1, p2]), p3])
        race_result = JSPromise.race([p1, p2], loop)
        JSPromise.any([race_result, p3], loop).then(lambda value: results.append(value))

        loop.run()

        # Should get one of the values
        assert len(results) == 1
        assert results[0] in [1, 3]

    def test_allSettled_then_all(self):
        """Test using allSettled results in Promise.all()."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.resolve(1, loop),
            JSPromise.reject("error", loop),
            JSPromise.resolve(3, loop)
        ]

        (JSPromise.allSettled(promises, loop)
         .then(lambda settlements: [
             s["value"] for s in settlements if s["status"] == "fulfilled"
         ])
         .then(lambda fulfilled_values: results.append(fulfilled_values)))

        loop.run()

        assert results == [[1, 3]]

    def test_resolve_with_pending_promise(self):
        """Test Promise.resolve() with pending promise."""
        loop = EventLoop()
        results = []
        resolve_funcs = []

        # Create pending promise
        def executor(resolve, reject):
            results.append("executor")
            resolve_funcs.append(resolve)

        pending = JSPromise(executor, loop)

        # resolve() should return same promise
        resolved = JSPromise.resolve(pending, loop)
        assert resolved is pending

        # Resolve the pending promise
        resolve_funcs[0](42)
        resolved.then(lambda v: results.append(v))

        loop.run()

        assert "executor" in results
        assert 42 in results

    def test_reject_in_all_stops_processing(self):
        """Test that rejection in Promise.all() stops waiting."""
        loop = EventLoop()
        results = []
        resolve_funcs = []

        # Create promises, one will reject
        p1 = JSPromise.resolve(1, loop)
        p2 = JSPromise.reject("error", loop)
        p3 = JSPromise(lambda resolve, reject: resolve_funcs.append(resolve), loop)

        JSPromise.all([p1, p2, p3], loop).catch(lambda err: results.append(err))
        loop.run()

        # Should reject immediately with "error"
        assert results == ["error"]

        # p3 may or may not be resolved, but shouldn't affect result
        resolve_funcs[0](3)
        loop.run()

        # Result should still be just ["error"]
        assert results == ["error"]

    def test_chaining_with_transformations(self):
        """Test complex chaining with data transformations."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.resolve("hello", loop),
            JSPromise.resolve("world", loop)
        ]

        (JSPromise.all(promises, loop)
         .then(lambda words: " ".join(words))
         .then(lambda sentence: sentence.upper())
         .then(lambda result: results.append(result)))

        loop.run()

        assert results == ["HELLO WORLD"]

    def test_error_handling_in_static_methods(self):
        """Test error handling propagation through static methods."""
        loop = EventLoop()
        results = []

        promises = [
            JSPromise.resolve(1, loop),
            JSPromise.resolve(2, loop)
        ]

        (JSPromise.all(promises, loop)
         .then(lambda values: 1 / 0)  # This will raise ZeroDivisionError
         .catch(lambda err: results.append(type(err).__name__)))

        loop.run()

        assert results == ["ZeroDivisionError"]

    def test_multiple_race_calls(self):
        """Test multiple race operations."""
        loop = EventLoop()
        results = []

        # First race
        race1 = JSPromise.race([
            JSPromise.resolve(1, loop),
            JSPromise.resolve(2, loop)
        ], loop)

        # Second race
        race2 = JSPromise.race([
            JSPromise.resolve(3, loop),
            JSPromise.resolve(4, loop)
        ], loop)

        # Race the races
        JSPromise.race([race1, race2], loop).then(lambda value: results.append(value))
        loop.run()

        assert len(results) == 1
        assert results[0] in [1, 2, 3, 4]

    def test_any_with_all_delayed_rejections(self):
        """Test Promise.any() where all promises reject eventually."""
        loop = EventLoop()
        results = []
        reject_funcs = []

        promises = [
            JSPromise(lambda resolve, reject: reject_funcs.append(reject), loop),
            JSPromise(lambda resolve, reject: reject_funcs.append(reject), loop)
        ]

        JSPromise.any(promises, loop).catch(lambda err: results.append(err))

        # Reject both
        reject_funcs[0]("error1")
        reject_funcs[1]("error2")

        loop.run()

        assert len(results) == 1
        assert isinstance(results[0], AggregateError)
        assert len(results[0].errors) == 2

    def test_complex_promise_chain_with_static_methods(self):
        """Test complex real-world scenario."""
        loop = EventLoop()
        results = []

        # Simulate fetching data from multiple sources
        def fetch_user_data():
            return JSPromise.resolve({"name": "Alice", "id": 1}, loop)

        def fetch_user_posts(user):
            return JSPromise.resolve([
                {"title": "Post 1", "userId": user["id"]},
                {"title": "Post 2", "userId": user["id"]}
            ], loop)

        def fetch_user_comments(user):
            return JSPromise.resolve([
                {"text": "Comment 1", "userId": user["id"]}
            ], loop)

        # Chain operations
        (fetch_user_data()
         .then(lambda user: JSPromise.all([
             JSPromise.resolve(user, loop),
             fetch_user_posts(user),
             fetch_user_comments(user)
         ], loop))
         .then(lambda data: {
             "user": data[0],
             "posts": data[1],
             "comments": data[2]
         })
         .then(lambda result: results.append(result)))

        loop.run()

        assert len(results) == 1
        assert results[0]["user"]["name"] == "Alice"
        assert len(results[0]["posts"]) == 2
        assert len(results[0]["comments"]) == 1
