"""
Generators and Iterators component for JavaScript runtime.

Implements generator functions, yield expressions, iterator protocol,
for-of loops, async generators, async iterators, and for-await-of loops
per ECMAScript 2024 specification.

Public API:
    From generator module:
        - GeneratorState: Generator execution states enum
        - IteratorResult: Iterator result object {value, done}
        - Generator: Generator object class
        - GeneratorFunction: Generator function wrapper

    From iterator module:
        - Iterator: Base iterator class
        - create_array_iterator: Create iterator for arrays
        - create_string_iterator: Create iterator for strings
        - is_iterable: Check if object is iterable
        - get_iterator: Get iterator from iterable

    From for_of module:
        - execute_for_of_loop: Execute for-of loop
        - ForOfLoopContext: Context manager for for-of loops
        - for_of_to_array: Collect iterable values to array

    From async_generator module (NEW - Phase 3.5):
        - AsyncGeneratorState: Async generator execution states enum
        - AsyncIteratorResult: Async iterator result object {value, done}
        - AsyncGenerator: Async generator object class
        - AsyncGeneratorFunction: Async generator function wrapper

    From async_iterator module (NEW - Phase 3.5):
        - AsyncIterator: Base async iterator class
        - AsyncIterable: Async iterable protocol
        - is_async_iterable: Check if object is async iterable
        - get_async_iterator: Get async iterator from async iterable
        - create_async_array_iterator: Create async iterator for arrays

    From for_await_of module (NEW - Phase 3.5):
        - for_await_of: Execute for-await-of loop
        - ForAwaitOfContext: Context manager for for-await-of loops
        - execute_for_await_of_sync: Synchronous wrapper for for-await-of
"""

from components.generators_iterators.src.generator import (
    GeneratorState,
    IteratorResult,
    Generator,
    GeneratorFunction,
    ExecutionContext,
)

from components.generators_iterators.src.iterator import (
    Iterator,
    Iterable,
    ArrayIterator,
    StringIterator,
    create_array_iterator,
    create_string_iterator,
    is_iterable,
    get_iterator,
)

from components.generators_iterators.src.for_of import (
    ForOfLoopContext,
    execute_for_of_loop,
    for_of_to_array,
)

# NEW - Phase 3.5: Async generators and iterators
from components.generators_iterators.src.async_generator import (
    AsyncGeneratorState,
    AsyncIteratorResult,
    AsyncGenerator,
    AsyncGeneratorFunction,
    AsyncExecutionContext,
)

from components.generators_iterators.src.async_iterator import (
    AsyncIterator,
    AsyncIterable,
    AsyncArrayIterator,
    is_async_iterable,
    get_async_iterator,
    create_async_array_iterator,
)

from components.generators_iterators.src.for_await_of import (
    for_await_of,
    ForAwaitOfContext,
    ForAwaitOfError,
    execute_for_await_of_sync,
)

__all__ = [
    # Generator exports
    'GeneratorState',
    'IteratorResult',
    'Generator',
    'GeneratorFunction',
    'ExecutionContext',
    # Iterator exports
    'Iterator',
    'Iterable',
    'ArrayIterator',
    'StringIterator',
    'create_array_iterator',
    'create_string_iterator',
    'is_iterable',
    'get_iterator',
    # For-of exports
    'ForOfLoopContext',
    'execute_for_of_loop',
    'for_of_to_array',
    # Async generator exports (Phase 3.5)
    'AsyncGeneratorState',
    'AsyncIteratorResult',
    'AsyncGenerator',
    'AsyncGeneratorFunction',
    'AsyncExecutionContext',
    # Async iterator exports (Phase 3.5)
    'AsyncIterator',
    'AsyncIterable',
    'AsyncArrayIterator',
    'is_async_iterable',
    'get_async_iterator',
    'create_async_array_iterator',
    # For-await-of exports (Phase 3.5)
    'for_await_of',
    'ForAwaitOfContext',
    'ForAwaitOfError',
    'execute_for_await_of_sync',
]
