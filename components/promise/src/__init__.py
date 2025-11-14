"""Promise component for asynchronous programming.

This component implements JavaScript Promise functionality according to
the ECMAScript specification, providing:
- Promise construction and execution
- State management (pending, fulfilled, rejected)
- Asynchronous handler execution via microtasks
- Promise chaining with then(), catch(), finally()
- Integration with the EventLoop

Public API:
    JSPromise: Core Promise implementation
    PromiseState: Enum defining Promise states (PENDING, FULFILLED, REJECTED)

Example:
    >>> from components.event_loop.src import EventLoop
    >>> from components.promise.src import JSPromise, PromiseState
    >>>
    >>> loop = EventLoop()
    >>> promise = JSPromise(lambda resolve, reject: resolve(42), loop)
    >>> promise.then(lambda x: print(f"Result: {x}"))
    >>> loop.run()
    Result: 42
"""

from .js_promise import JSPromise, AggregateError
from .promise_state import PromiseState

__all__ = ['JSPromise', 'PromiseState', 'AggregateError']

__version__ = '0.1.0'
