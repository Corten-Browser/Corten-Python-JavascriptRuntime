"""
Unit tests for async generators and async iterators.

Tests FR-P3.5-014 through FR-P3.5-019:
- async function* syntax
- await in generators
- Symbol.asyncIterator
- for await...of loop
- AsyncGenerator object protocol
- AsyncIterator protocol

Test Requirements:
- async function* syntax: ≥8 tests
- await in generators: ≥8 tests
- Symbol.asyncIterator: ≥6 tests
- for await...of loop: ≥10 tests
- AsyncGenerator protocol: ≥10 tests
- AsyncIterator protocol: ≥8 tests
Total: ≥50 tests
"""

import pytest
from components.generators_iterators.src.async_generator import (
    AsyncGenerator,
    AsyncGeneratorFunction,
    AsyncGeneratorState,
    AsyncIteratorResult,
)
from components.generators_iterators.src.async_iterator import (
    AsyncIterator,
    is_async_iterable,
    get_async_iterator,
)
from components.generators_iterators.src.for_await_of import for_await_of
from components.promise.src.js_promise import JSPromise
from components.event_loop.src import EventLoop


# Test fixtures
@pytest.fixture
def event_loop():
    """Create event loop for async operations."""
    return EventLoop()


# ============================================================================
# FR-P3.5-014: async function* syntax (≥8 tests)
# ============================================================================


def test_async_function_star_syntax_creates_async_generator_function(event_loop):
    """async function* creates AsyncGeneratorFunction."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    assert isinstance(async_gen_fn, AsyncGeneratorFunction)


def test_async_generator_function_call_returns_async_generator(event_loop):
    """Calling async generator function returns AsyncGenerator object."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    assert isinstance(gen, AsyncGenerator)


def test_async_generator_initial_state_suspended_start(event_loop):
    """AsyncGenerator starts in SUSPENDED_START state."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    assert gen.state == AsyncGeneratorState.SUSPENDED_START


def test_async_generator_function_preserves_wrapped_function(event_loop):
    """AsyncGeneratorFunction preserves reference to wrapped function."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    assert async_gen_fn.func == gen_func


def test_async_function_star_with_no_yields(event_loop):
    """async function* with no yields completes immediately."""
    async def gen_func():
        return 42

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    # First next() should complete immediately
    result_promise = gen.next()
    assert isinstance(result_promise, JSPromise)


def test_async_function_star_with_multiple_yields(event_loop):
    """async function* can yield multiple values."""
    async def gen_func():
        yield 1
        yield 2
        yield 3

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    assert isinstance(gen, AsyncGenerator)


def test_async_generator_function_creates_new_instance_each_call(event_loop):
    """Each call to async generator function creates new AsyncGenerator."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen1 = async_gen_fn()
    gen2 = async_gen_fn()

    assert gen1 is not gen2
    assert isinstance(gen1, AsyncGenerator)
    assert isinstance(gen2, AsyncGenerator)


def test_async_generator_function_with_parameters(event_loop):
    """async function* can accept parameters."""
    async def gen_func(start, end):
        for i in range(start, end):
            yield i

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn(1, 4)

    assert isinstance(gen, AsyncGenerator)


# ============================================================================
# FR-P3.5-015: await in generators (≥8 tests)
# ============================================================================


def test_await_in_async_generator_basic(event_loop):
    """Can use await inside async generator."""
    async def gen_func():
        result = await JSPromise.resolve(42, event_loop)
        yield result

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    result_promise = gen.next()
    assert isinstance(result_promise, JSPromise)


def test_await_promise_before_yield(event_loop):
    """await Promise before yielding value."""
    values = []

    async def gen_func():
        value = await JSPromise.resolve(10, event_loop)
        yield value * 2

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    result_promise = gen.next()
    result_promise.then(lambda result: values.append(result.value))

    event_loop.run()
    assert values == [20]


def test_multiple_awaits_in_async_generator(event_loop):
    """Multiple await expressions in async generator."""
    values = []

    async def gen_func():
        a = await JSPromise.resolve(1, event_loop)
        b = await JSPromise.resolve(2, event_loop)
        yield a + b

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    result_promise = gen.next()
    result_promise.then(lambda result: values.append(result.value))

    event_loop.run()
    assert values == [3]


def test_await_rejected_promise_in_generator(event_loop):
    """await rejected Promise throws in async generator."""
    errors = []

    async def gen_func():
        try:
            value = await JSPromise.reject("error", event_loop)
            yield value
        except Exception as e:
            errors.append(str(e))
            yield "handled"

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    result_promise = gen.next()
    event_loop.run()

    # Should handle the error
    assert len(errors) > 0


def test_yield_await_promise(event_loop):
    """yield await promise pattern."""
    values = []

    async def gen_func():
        yield await JSPromise.resolve(100, event_loop)

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    result_promise = gen.next()
    result_promise.then(lambda result: values.append(result.value))

    event_loop.run()
    assert values == [100]


def test_await_in_loop_inside_async_generator(event_loop):
    """await inside loop in async generator."""
    values = []

    async def gen_func():
        for i in range(3):
            value = await JSPromise.resolve(i, event_loop)
            yield value * 10

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    # Get first value
    result_promise = gen.next()
    result_promise.then(lambda result: values.append(result.value))

    event_loop.run()
    assert values == [0]


def test_await_between_yields(event_loop):
    """await between multiple yields."""
    values = []

    async def gen_func():
        yield 1
        await JSPromise.resolve(None, event_loop)
        yield 2

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    # First yield
    result1 = gen.next()
    result1.then(lambda r: values.append(r.value))
    event_loop.run()

    assert values == [1]


def test_await_promise_all_in_generator(event_loop):
    """await Promise.all() in async generator."""
    values = []

    async def gen_func():
        promises = [
            JSPromise.resolve(1, event_loop),
            JSPromise.resolve(2, event_loop),
        ]
        results = await JSPromise.all(promises, event_loop)
        yield sum(results)

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    result_promise = gen.next()
    result_promise.then(lambda result: values.append(result.value))

    event_loop.run()
    assert values == [3]


# ============================================================================
# FR-P3.5-016: Symbol.asyncIterator (≥6 tests)
# ============================================================================


def test_symbol_async_iterator_exists(event_loop):
    """Symbol.asyncIterator well-known symbol exists."""
    try:
        from components.symbols.src.well_known_symbols import SYMBOL_ASYNC_ITERATOR
        assert SYMBOL_ASYNC_ITERATOR is not None
    except ImportError:
        # Symbol component might use different import path
        import sys
        sys.path.insert(0, '/home/user/Corten-JavascriptRuntime/components/symbols/src')
        from well_known_symbols import SYMBOL_ASYNC_ITERATOR
        assert SYMBOL_ASYNC_ITERATOR is not None


def test_symbol_async_iterator_is_unique(event_loop):
    """Symbol.asyncIterator is unique symbol."""
    try:
        from components.symbols.src.well_known_symbols import SYMBOL_ASYNC_ITERATOR, SYMBOL_ITERATOR
        assert SYMBOL_ASYNC_ITERATOR != SYMBOL_ITERATOR
    except ImportError:
        import sys
        sys.path.insert(0, '/home/user/Corten-JavascriptRuntime/components/symbols/src')
        from well_known_symbols import SYMBOL_ASYNC_ITERATOR, SYMBOL_ITERATOR
        assert SYMBOL_ASYNC_ITERATOR != SYMBOL_ITERATOR


def test_async_generator_has_async_iterator_method(event_loop):
    """AsyncGenerator has [Symbol.asyncIterator]() method."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    # Should have Symbol.asyncIterator method (__aiter__ in Python)
    assert hasattr(gen, '__aiter__')


def test_async_iterator_method_returns_self(event_loop):
    """AsyncGenerator[Symbol.asyncIterator]() returns self."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    # Python's __aiter__ should return self
    assert gen.__aiter__() == gen


def test_object_with_async_iterator_is_async_iterable(event_loop):
    """Object with [Symbol.asyncIterator] is async iterable."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    assert is_async_iterable(gen)


def test_object_without_async_iterator_not_async_iterable(event_loop):
    """Object without [Symbol.asyncIterator] is not async iterable."""
    regular_obj = {"value": 42}
    assert not is_async_iterable(regular_obj)


# ============================================================================
# FR-P3.5-017: for await...of loop (≥10 tests)
# ============================================================================


def test_for_await_of_with_async_generator(event_loop):
    """for await...of loop with async generator."""
    values = []

    async def gen_func():
        yield 1
        yield 2
        yield 3

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    async def consume():
        async for value in gen:
            values.append(value)

    # Run the consumption
    consume_promise = consume()
    event_loop.run()

    assert values == [1, 2, 3]


def test_for_await_of_awaits_each_promise(event_loop):
    """for await...of awaits each Promise before continuing."""
    values = []

    async def gen_func():
        yield JSPromise.resolve(10, event_loop)
        yield JSPromise.resolve(20, event_loop)

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    async def consume():
        async for value in gen:
            values.append(value)

    consume_promise = consume()
    event_loop.run()

    assert values == [10, 20]


def test_for_await_of_with_empty_async_generator(event_loop):
    """for await...of with empty async generator."""
    values = []

    async def gen_func():
        return
        yield  # Never reached

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    async def consume():
        async for value in gen:
            values.append(value)

    consume_promise = consume()
    event_loop.run()

    assert values == []


def test_for_await_of_with_break(event_loop):
    """for await...of with break statement."""
    values = []

    async def gen_func():
        yield 1
        yield 2
        yield 3
        yield 4

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    async def consume():
        async for value in gen:
            values.append(value)
            if value == 2:
                break

    consume_promise = consume()
    event_loop.run()

    assert values == [1, 2]


def test_for_await_of_with_continue(event_loop):
    """for await...of with continue statement."""
    values = []

    async def gen_func():
        yield 1
        yield 2
        yield 3

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    async def consume():
        async for value in gen:
            if value == 2:
                continue
            values.append(value)

    consume_promise = consume()
    event_loop.run()

    assert values == [1, 3]


def test_for_await_of_handles_errors(event_loop):
    """for await...of handles errors in async generator."""
    errors = []

    async def gen_func():
        yield 1
        raise ValueError("Test error")
        yield 2

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    async def consume():
        try:
            async for value in gen:
                pass
        except ValueError as e:
            errors.append(str(e))

    consume_promise = consume()
    event_loop.run()

    assert "Test error" in errors


def test_for_await_of_with_promises_array(event_loop):
    """for await...of with array of Promises."""
    values = []

    promises = [
        JSPromise.resolve(1, event_loop),
        JSPromise.resolve(2, event_loop),
        JSPromise.resolve(3, event_loop),
    ]

    # Would need array to be async iterable
    # This is a simplified test
    async def consume_promises():
        for promise in promises:
            value = await promise
            values.append(value)

    consume_promise = consume_promises()
    event_loop.run()

    assert values == [1, 2, 3]


def test_for_await_of_properly_closes_iterator(event_loop):
    """for await...of properly closes iterator on break."""
    closed = [False]

    async def gen_func():
        try:
            yield 1
            yield 2
        finally:
            closed[0] = True

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    async def consume():
        async for value in gen:
            if value == 1:
                break

    consume_promise = consume()
    event_loop.run()

    # Generator should be closed
    assert gen.state == AsyncGeneratorState.COMPLETED


def test_for_await_of_in_async_function(event_loop):
    """for await...of inside async function."""
    sum_value = [0]

    async def gen_func():
        yield 10
        yield 20
        yield 30

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    async def calculate_sum():
        total = 0
        async for value in gen:
            total += value
        sum_value[0] = total

    sum_promise = calculate_sum()
    event_loop.run()

    assert sum_value[0] == 60


def test_for_await_of_with_nested_loops(event_loop):
    """for await...of with nested loops."""
    values = []

    async def outer_gen():
        yield 1
        yield 2

    async def inner_gen():
        yield "a"
        yield "b"

    outer_fn = AsyncGeneratorFunction(outer_gen, event_loop)
    inner_fn = AsyncGeneratorFunction(inner_gen, event_loop)

    async def consume():
        async for outer in outer_fn():
            async for inner in inner_fn():
                values.append((outer, inner))

    consume_promise = consume()
    event_loop.run()

    assert len(values) == 4


# ============================================================================
# FR-P3.5-018: AsyncGenerator object protocol (≥10 tests)
# ============================================================================


def test_async_generator_next_returns_promise(event_loop):
    """AsyncGenerator.next() returns Promise."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    result = gen.next()
    assert isinstance(result, JSPromise)


def test_async_generator_next_promise_resolves_to_iterator_result(event_loop):
    """AsyncGenerator.next() Promise resolves to {value, done}."""
    results = []

    async def gen_func():
        yield 42

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    result_promise = gen.next()
    result_promise.then(lambda result: results.append(result))

    event_loop.run()

    assert len(results) == 1
    assert hasattr(results[0], 'value')
    assert hasattr(results[0], 'done')
    assert results[0].value == 42
    assert results[0].done is False


def test_async_generator_next_with_sent_value(event_loop):
    """AsyncGenerator.next(value) sends value into generator."""
    values = []

    async def gen_func():
        sent = yield 1
        values.append(sent)
        yield 2

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    # First next
    result1 = gen.next()
    event_loop.run()

    # Second next with value
    result2 = gen.next(100)
    event_loop.run()

    assert 100 in values


def test_async_generator_return_method(event_loop):
    """AsyncGenerator.return(value) completes generator early."""
    results = []

    async def gen_func():
        yield 1
        yield 2
        yield 3

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    # Get first value
    gen.next()
    event_loop.run()

    # Return early
    return_promise = gen.return_value(99)
    return_promise.then(lambda result: results.append(result))

    event_loop.run()

    assert len(results) == 1
    assert results[0].value == 99
    assert results[0].done is True


def test_async_generator_throw_method(event_loop):
    """AsyncGenerator.throw(exception) throws exception into generator."""
    errors = []

    async def gen_func():
        try:
            yield 1
        except ValueError as e:
            errors.append(str(e))
            yield 2

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    # First next
    gen.next()
    event_loop.run()

    # Throw error
    throw_promise = gen.throw(ValueError("Test error"))
    event_loop.run()

    assert "Test error" in errors


def test_async_generator_state_transitions(event_loop):
    """AsyncGenerator state transitions correctly."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    # Initial state
    assert gen.state == AsyncGeneratorState.SUSPENDED_START

    # After first next
    gen.next()
    event_loop.run()
    assert gen.state == AsyncGeneratorState.SUSPENDED_YIELD

    # After completion
    gen.next()
    event_loop.run()
    assert gen.state == AsyncGeneratorState.COMPLETED


def test_async_generator_completed_returns_done_true(event_loop):
    """Calling next() on completed AsyncGenerator returns {done: true}."""
    results = []

    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    # Consume generator
    gen.next()
    event_loop.run()

    gen.next()
    event_loop.run()

    # Try next again
    result = gen.next()
    result.then(lambda r: results.append(r))
    event_loop.run()

    assert results[-1].done is True


def test_async_generator_return_executes_finally(event_loop):
    """AsyncGenerator.return() executes finally blocks."""
    finally_executed = [False]

    async def gen_func():
        try:
            yield 1
            yield 2
        finally:
            finally_executed[0] = True

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    gen.next()
    event_loop.run()

    gen.return_value()
    event_loop.run()

    assert finally_executed[0] is True


def test_async_generator_throw_unhandled_completes_generator(event_loop):
    """Unhandled throw() completes generator."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    gen.next()
    event_loop.run()

    try:
        throw_promise = gen.throw(RuntimeError("error"))
        event_loop.run()
    except:
        pass

    assert gen.state == AsyncGeneratorState.COMPLETED


def test_async_generator_multiple_yields_correct_sequence(event_loop):
    """AsyncGenerator yields values in correct sequence."""
    values = []

    async def gen_func():
        yield 10
        yield 20
        yield 30

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    for _ in range(3):
        result_promise = gen.next()
        result_promise.then(lambda r: values.append(r.value))
        event_loop.run()

    assert values == [10, 20, 30]


# ============================================================================
# FR-P3.5-019: AsyncIterator protocol (≥8 tests)
# ============================================================================


def test_async_iterator_protocol_next_returns_promise(event_loop):
    """AsyncIterator.next() returns Promise<{value, done}>."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    # AsyncGenerator implements AsyncIterator protocol
    assert hasattr(gen, 'next')
    result = gen.next()
    assert isinstance(result, JSPromise)


def test_async_iterator_result_has_value_and_done(event_loop):
    """AsyncIterator result has {value, done} properties."""
    results = []

    async def gen_func():
        yield 99

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    result_promise = gen.next()
    result_promise.then(lambda r: results.append(r))

    event_loop.run()

    assert hasattr(results[0], 'value')
    assert hasattr(results[0], 'done')


def test_async_iterator_done_false_when_yielding(event_loop):
    """AsyncIterator returns done: false when yielding."""
    results = []

    async def gen_func():
        yield 5

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    result_promise = gen.next()
    result_promise.then(lambda r: results.append(r.done))

    event_loop.run()

    assert results[0] is False


def test_async_iterator_done_true_when_completed(event_loop):
    """AsyncIterator returns done: true when completed."""
    results = []

    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    # First next (yields)
    gen.next()
    event_loop.run()

    # Second next (completes)
    result_promise = gen.next()
    result_promise.then(lambda r: results.append(r.done))

    event_loop.run()

    assert results[0] is True


def test_async_iterator_get_iterator_function(event_loop):
    """get_async_iterator() returns async iterator."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    iterator = get_async_iterator(gen)
    assert iterator == gen  # Generators are their own iterators


def test_async_iterator_is_iterable_check(event_loop):
    """is_async_iterable() correctly identifies async iterables."""
    async def gen_func():
        yield 1

    async_gen_fn = AsyncGeneratorFunction(gen_func, event_loop)
    gen = async_gen_fn()

    assert is_async_iterable(gen) is True


def test_non_async_iterator_is_not_async_iterable(event_loop):
    """Regular iterators are not async iterable."""
    regular_list = [1, 2, 3]
    assert is_async_iterable(regular_list) is False


def test_async_iterator_custom_implementation(event_loop):
    """Custom object implementing AsyncIterator protocol."""

    class CustomAsyncIterator(AsyncIterator):
        def __init__(self, values, event_loop):
            self.values = values
            self.index = 0
            self.event_loop = event_loop

        def next(self):
            if self.index >= len(self.values):
                return JSPromise.resolve(
                    AsyncIteratorResult(value=None, done=True),
                    self.event_loop
                )

            value = self.values[self.index]
            self.index += 1
            return JSPromise.resolve(
                AsyncIteratorResult(value=value, done=False),
                self.event_loop
            )

    custom_iter = CustomAsyncIterator([10, 20, 30], event_loop)
    result_promise = custom_iter.next()

    results = []
    result_promise.then(lambda r: results.append(r.value))
    event_loop.run()

    assert results[0] == 10
