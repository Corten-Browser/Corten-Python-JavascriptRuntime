#!/usr/bin/env python3
"""Demonstration of ES2024 Promise extensions.

This script demonstrates the three Promise extension methods:
- Promise.any()
- Promise.allSettled()
- Promise.withResolvers()
"""

from components.event_loop.src import EventLoop
from components.promise.src import JSPromise, AggregateError


def demo_promise_any():
    """Demonstrate Promise.any() - first to fulfill wins."""
    print("=" * 60)
    print("Demo 1: Promise.any()")
    print("=" * 60)

    loop = EventLoop()

    # Success case: first to fulfill
    print("\n1. First to fulfill wins:")
    promises = [
        JSPromise.reject("error1", loop),
        JSPromise.resolve(42, loop),
        JSPromise.resolve(100, loop)
    ]

    JSPromise.any(promises, loop).then(
        lambda v: print(f"   ✓ Fulfilled with: {v}")
    )
    loop.run()

    # Failure case: all reject
    loop = EventLoop()
    print("\n2. All reject - AggregateError:")
    promises = [
        JSPromise.reject("error1", loop),
        JSPromise.reject("error2", loop),
        JSPromise.reject("error3", loop)
    ]

    JSPromise.any(promises, loop).catch(
        lambda err: print(f"   ✓ Rejected with AggregateError: {len(err.errors)} errors")
    )
    loop.run()


def demo_promise_allsettled():
    """Demonstrate Promise.allSettled() - wait for all."""
    print("\n" + "=" * 60)
    print("Demo 2: Promise.allSettled()")
    print("=" * 60)

    loop = EventLoop()

    print("\nMixed results (fulfill + reject):")
    promises = [
        JSPromise.resolve(42, loop),
        JSPromise.reject("error", loop),
        JSPromise.resolve(100, loop)
    ]

    def display_results(results):
        for i, result in enumerate(results):
            if result['status'] == 'fulfilled':
                print(f"   ✓ Promise {i}: fulfilled with {result['value']}")
            else:
                print(f"   ✗ Promise {i}: rejected with {result['reason']}")

    JSPromise.allSettled(promises, loop).then(display_results)
    loop.run()


def demo_promise_withresolvers():
    """Demonstrate Promise.withResolvers() - deferred promise."""
    print("\n" + "=" * 60)
    print("Demo 3: Promise.withResolvers()")
    print("=" * 60)

    # Example 1: Basic usage
    print("\n1. Basic deferred promise:")
    loop = EventLoop()

    deferred = JSPromise.withResolvers(loop)
    deferred["promise"].then(lambda v: print(f"   ✓ Resolved with: {v}"))

    print("   - Promise created")
    print("   - Resolving externally...")
    deferred["resolve"](42)
    loop.run()

    # Example 2: Async operation wrapper
    print("\n2. Async operation wrapper pattern:")
    loop = EventLoop()

    class AsyncOperation:
        def __init__(self, event_loop):
            self.deferred = JSPromise.withResolvers(event_loop)
            self.promise = self.deferred["promise"]

        def complete(self, value):
            self.deferred["resolve"](value)

        def fail(self, error):
            self.deferred["reject"](error)

    operation = AsyncOperation(loop)
    operation.promise.then(lambda v: print(f"   ✓ Operation completed: {v}"))

    print("   - Async operation started")
    print("   - Triggering completion...")
    operation.complete("success")
    loop.run()

    # Example 3: Multiple independent promises
    print("\n3. Multiple independent deferred promises:")
    loop = EventLoop()

    deferred1 = JSPromise.withResolvers(loop)
    deferred2 = JSPromise.withResolvers(loop)

    deferred1["promise"].then(lambda v: print(f"   ✓ Promise 1: {v}"))
    deferred2["promise"].then(lambda v: print(f"   ✓ Promise 2: {v}"))

    print("   - Resolving in reverse order...")
    deferred2["resolve"]("second")
    deferred1["resolve"]("first")
    loop.run()


def demo_complex_scenario():
    """Demonstrate complex scenario using all three methods."""
    print("\n" + "=" * 60)
    print("Demo 4: Complex Scenario - All Methods Combined")
    print("=" * 60)

    loop = EventLoop()

    # Create deferred promises
    deferred1 = JSPromise.withResolvers(loop)
    deferred2 = JSPromise.withResolvers(loop)
    deferred3 = JSPromise.withResolvers(loop)

    print("\n1. Using withResolvers() to create promises")
    print("2. Using any() to get first result")
    print("3. Using allSettled() to wait for all\n")

    # Use any() to get first result
    JSPromise.any(
        [deferred1["promise"], deferred2["promise"], deferred3["promise"]],
        loop
    ).then(lambda v: print(f"   ✓ any() resolved with: {v}"))

    # Use allSettled() to wait for all
    JSPromise.allSettled(
        [deferred1["promise"], deferred2["promise"], deferred3["promise"]],
        loop
    ).then(lambda results: print(f"   ✓ allSettled() got {len(results)} results"))

    # Resolve in different order
    deferred2["resolve"](20)
    deferred1["reject"]("error")
    deferred3["resolve"](30)

    loop.run()


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ES2024 Promise Extensions Demonstration")
    print("=" * 60)

    demo_promise_any()
    demo_promise_allsettled()
    demo_promise_withresolvers()
    demo_complex_scenario()

    print("\n" + "=" * 60)
    print("All demonstrations completed successfully!")
    print("=" * 60)
    print()
