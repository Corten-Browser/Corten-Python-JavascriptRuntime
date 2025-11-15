"""
Generators and Iterators component for JavaScript runtime.

Implements generator functions, yield expressions, iterator protocol,
and for-of loops per ECMAScript 2024 specification.

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
]
