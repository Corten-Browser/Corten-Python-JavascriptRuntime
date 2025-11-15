"""Integration tests for Promise.withResolvers() ES2024 feature.

Tests complex scenarios and interactions with other Promise methods.
"""

import pytest
from components.event_loop.src import EventLoop
from components.promise.src import JSPromise, PromiseState


class TestWithResolversIntegration:
    """Integration tests for Promise.withResolvers()."""

    def test_withResolvers_with_promise_all(self):
        """withResolvers() promises can be used with Promise.all()."""
        loop = EventLoop()
        results = []

        # Create deferred promises
        deferred1 = JSPromise.withResolvers(loop)
        deferred2 = JSPromise.withResolvers(loop)
        deferred3 = JSPromise.withResolvers(loop)

        # Use with Promise.all
        JSPromise.all(
            [deferred1["promise"], deferred2["promise"], deferred3["promise"]],
            loop
        ).then(lambda values: results.append(values))

        # Resolve in different order
        deferred2["resolve"](20)
        deferred1["resolve"](10)
        deferred3["resolve"](30)

        loop.run()

        assert results == [[10, 20, 30]]

    def test_withResolvers_async_operation_pattern(self):
        """withResolvers() enables async operation wrapper pattern."""
        loop = EventLoop()
        results = []

        class AsyncFileReader:
            """Simulates async file reading with deferred promise."""

            def __init__(self, event_loop):
                self.loop = event_loop
                self.deferred = None

            def read_file(self, filename):
                """Start async read, return promise."""
                self.deferred = JSPromise.withResolvers(self.loop)
                # Simulate async operation (normally would be in callback)
                return self.deferred["promise"]

            def on_data_received(self, data):
                """Called when data arrives."""
                if self.deferred:
                    self.deferred["resolve"](data)

            def on_error(self, error):
                """Called on error."""
                if self.deferred:
                    self.deferred["reject"](error)

        reader = AsyncFileReader(loop)
        promise = reader.read_file("test.txt")
        promise.then(lambda data: results.append(data))

        # Simulate data arrival
        reader.on_data_received("file contents")
        loop.run()

        assert results == ["file contents"]

    def test_withResolvers_promise_race(self):
        """withResolvers() works with Promise.race()."""
        loop = EventLoop()
        results = []

        deferred1 = JSPromise.withResolvers(loop)
        deferred2 = JSPromise.withResolvers(loop)

        JSPromise.race([deferred1["promise"], deferred2["promise"]], loop).then(
            lambda value: results.append(value)
        )

        # Resolve first wins
        deferred1["resolve"]("first")
        deferred2["resolve"]("second")

        loop.run()

        assert results == ["first"]

    def test_withResolvers_complex_orchestration(self):
        """withResolvers() enables complex async orchestration."""
        loop = EventLoop()
        results = []

        # Create multiple stages
        stage1 = JSPromise.withResolvers(loop)
        stage2 = JSPromise.withResolvers(loop)
        stage3 = JSPromise.withResolvers(loop)

        # Chain stages
        stage1["promise"].then(lambda x: x * 2).then(
            lambda x: stage2["resolve"](x)
        )

        stage2["promise"].then(lambda x: x + 10).then(
            lambda x: stage3["resolve"](x)
        )

        stage3["promise"].then(lambda x: results.append(x))

        # Trigger pipeline
        stage1["resolve"](5)
        loop.run()

        # 5 * 2 = 10, 10 + 10 = 20
        assert results == [20]

    def test_withResolvers_timeout_pattern(self):
        """withResolvers() enables timeout pattern."""
        loop = EventLoop()
        results = []

        def create_timeout_promise(timeout_ms):
            """Create a promise that resolves after timeout."""
            deferred = JSPromise.withResolvers(loop)
            # In real implementation, would use timer
            # For test, resolve immediately
            deferred["resolve"]("timeout")
            return deferred["promise"]

        def race_with_timeout(promise):
            """Race promise against timeout."""
            timeout = create_timeout_promise(1000)
            return JSPromise.race([promise, timeout], loop)

        # Create slow operation
        slow_op = JSPromise.withResolvers(loop)

        # Race it with timeout
        race_with_timeout(slow_op["promise"]).then(
            lambda result: results.append(result)
        )

        loop.run()

        # Timeout wins
        assert results == ["timeout"]

    def test_withResolvers_event_emitter_pattern(self):
        """withResolvers() enables event emitter to promise bridge."""
        loop = EventLoop()
        results = []

        class EventEmitter:
            """Simple event emitter."""

            def __init__(self):
                self.handlers = {}

            def on(self, event, handler):
                if event not in self.handlers:
                    self.handlers[event] = []
                self.handlers[event].append(handler)

            def emit(self, event, data):
                if event in self.handlers:
                    for handler in self.handlers[event]:
                        handler(data)

            def once_as_promise(self, event, event_loop):
                """Convert event to promise."""
                deferred = JSPromise.withResolvers(event_loop)

                def handler(data):
                    deferred["resolve"](data)

                self.on(event, handler)
                return deferred["promise"]

        emitter = EventEmitter()
        promise = emitter.once_as_promise("data", loop)
        promise.then(lambda data: results.append(data))

        # Emit event
        emitter.emit("data", {"value": 42})
        loop.run()

        assert results == [{"value": 42}]
