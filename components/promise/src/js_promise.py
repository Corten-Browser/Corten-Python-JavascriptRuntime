"""JavaScript Promise implementation.

This module implements the core Promise functionality according to the
ECMAScript specification, including:
- Promise construction with executor function
- State management (pending, fulfilled, rejected)
- Resolution and rejection
- then(), catch(), and finally() methods
- Promise chaining
- Integration with the EventLoop's microtask queue
"""

from components.event_loop.src import EventLoop
from .promise_state import PromiseState


class PromiseRejection(Exception):
    """Wrapper for Promise rejection reasons that aren't exceptions.

    JavaScript Promises can be rejected with any value, but Python's
    raise statement requires an exception. This wrapper allows us to
    raise any value as a rejection reason.
    """

    def __init__(self, reason):
        self.reason = reason
        super().__init__(str(reason))


class JSPromise:
    """JavaScript Promise implementation.

    A Promise represents the eventual result of an asynchronous operation.
    It can be in one of three states: PENDING, FULFILLED, or REJECTED.

    Example:
        >>> loop = EventLoop()
        >>> promise = JSPromise(lambda resolve, reject: resolve(42), loop)
        >>> promise.then(lambda x: print(f"Got: {x}"))
        >>> loop.run()
        Got: 42

    Attributes:
        state: Current Promise state (PENDING, FULFILLED, REJECTED)
        value: Fulfillment value (if fulfilled) or rejection reason (if rejected)
        fulfillment_reactions: List of handlers to call when fulfilled
        rejection_reactions: List of handlers to call when rejected
        event_loop: EventLoop instance for queuing microtasks
    """

    def __init__(self, executor, event_loop):
        """Create a new Promise.

        The executor function is called immediately (synchronously) with two
        functions as arguments: resolve and reject. The executor typically
        initiates some asynchronous work, and then calls resolve or reject
        to settle the Promise.

        Args:
            executor: Function with signature (resolve, reject) => void
            event_loop: EventLoop instance for queuing microtasks

        Example:
            >>> loop = EventLoop()
            >>> def executor(resolve, reject):
            ...     resolve("success")
            >>> promise = JSPromise(executor, loop)
        """
        self.state = PromiseState.PENDING
        self.value = None  # Fulfillment value or rejection reason
        self.fulfillment_reactions = []  # .then() onFulfilled handlers
        self.rejection_reactions = []    # .catch() / .then() onRejected handlers
        self.event_loop = event_loop

        # Execute executor immediately (synchronously)
        try:
            resolve = self._create_resolve_function()
            reject = self._create_reject_function()
            executor(resolve, reject)
        except Exception as e:
            self._reject(e)

    def _create_resolve_function(self):
        """Create resolve() function passed to executor.

        Returns:
            Function that resolves the Promise when called
        """
        def resolve(value):
            if self.state != PromiseState.PENDING:
                return  # Promise already settled, ignore

            # Handle thenable (Promise-like object)
            if isinstance(value, JSPromise):
                # Adopt state of the Promise
                value.then(resolve, self._create_reject_function())
            else:
                self._fulfill(value)

        return resolve

    def _create_reject_function(self):
        """Create reject() function passed to executor.

        Returns:
            Function that rejects the Promise when called
        """
        def reject(reason):
            if self.state != PromiseState.PENDING:
                return  # Promise already settled, ignore

            self._reject(reason)

        return reject

    def _fulfill(self, value):
        """Transition to FULFILLED state.

        This method is called internally when the Promise is resolved with
        a non-Promise value. It updates the state, stores the value, and
        queues all fulfillment reactions as microtasks.

        Args:
            value: The fulfillment value
        """
        if self.state != PromiseState.PENDING:
            return  # Already settled

        self.state = PromiseState.FULFILLED
        self.value = value

        # Queue all fulfillment reactions as microtasks
        for reaction in self.fulfillment_reactions:
            self.event_loop.queue_microtask(lambda r=reaction: r(value))

        # Clear reactions (no longer needed)
        self.fulfillment_reactions = []
        self.rejection_reactions = []

    def _reject(self, reason):
        """Transition to REJECTED state.

        This method is called internally when the Promise is rejected.
        It updates the state, stores the reason, and queues all rejection
        reactions as microtasks.

        Args:
            reason: The rejection reason (typically an exception)
        """
        if self.state != PromiseState.PENDING:
            return  # Already settled

        self.state = PromiseState.REJECTED
        self.value = reason

        # Queue all rejection reactions as microtasks
        for reaction in self.rejection_reactions:
            self.event_loop.queue_microtask(lambda r=reaction: r(reason))

        # Clear reactions
        self.fulfillment_reactions = []
        self.rejection_reactions = []

    def then(self, on_fulfilled=None, on_rejected=None):
        """Register fulfillment/rejection handlers.

        The then() method returns a new Promise, allowing for chaining.
        It can take up to two arguments: callbacks for the success and
        failure cases of the Promise.

        Args:
            on_fulfilled: Callback when Promise fulfills (optional)
            on_rejected: Callback when Promise rejects (optional)

        Returns:
            New Promise for chaining

        Example:
            >>> loop = EventLoop()
            >>> promise = JSPromise(lambda resolve, reject: resolve(1), loop)
            >>> promise.then(lambda x: x + 1).then(lambda x: print(x))
            >>> loop.run()
            2
        """
        # Create new Promise for chaining
        result_promise = JSPromise(lambda resolve, reject: None, self.event_loop)
        result_resolve = result_promise._create_resolve_function()
        result_reject = result_promise._create_reject_function()

        def handle_fulfillment(value):
            try:
                if on_fulfilled and callable(on_fulfilled):
                    new_value = on_fulfilled(value)
                    result_resolve(new_value)
                else:
                    # No handler, pass value through
                    result_resolve(value)
            except PromiseRejection as e:
                # Explicit rejection via PromiseRejection wrapper
                result_reject(e.reason)
            except Exception as e:
                result_reject(e)

        def handle_rejection(reason):
            try:
                if on_rejected and callable(on_rejected):
                    new_value = on_rejected(reason)
                    result_resolve(new_value)  # Rejection handled, resolve result
                else:
                    # No handler, pass rejection through
                    result_reject(reason)
            except PromiseRejection as e:
                # Explicit rejection via PromiseRejection wrapper
                result_reject(e.reason)
            except Exception as e:
                result_reject(e)

        if self.state == PromiseState.PENDING:
            # Promise not settled yet, register reactions
            self.fulfillment_reactions.append(handle_fulfillment)
            self.rejection_reactions.append(handle_rejection)
        elif self.state == PromiseState.FULFILLED:
            # Promise already fulfilled, queue reaction as microtask
            self.event_loop.queue_microtask(lambda: handle_fulfillment(self.value))
        else:  # REJECTED
            # Promise already rejected, queue reaction as microtask
            self.event_loop.queue_microtask(lambda: handle_rejection(self.value))

        return result_promise

    def catch(self, on_rejected):
        """Shorthand for .then(None, on_rejected).

        The catch() method is used for error handling in Promise compositions.
        It's functionally equivalent to calling then(None, onRejected).

        Args:
            on_rejected: Callback when Promise rejects

        Returns:
            New Promise for chaining

        Example:
            >>> loop = EventLoop()
            >>> promise = JSPromise(lambda resolve, reject: reject("error"), loop)
            >>> promise.catch(lambda err: print(f"Error: {err}"))
            >>> loop.run()
            Error: error
        """
        return self.then(None, on_rejected)

    def finally_handler(self, on_finally):
        """Run callback regardless of fulfillment or rejection.

        The finally() method schedules a function to be called when the
        Promise is settled (either fulfilled or rejected). The callback
        does not receive any argument and the Promise resolves or rejects
        with the original value/reason.

        Args:
            on_finally: Callback to run when Promise settles

        Returns:
            New Promise that resolves/rejects with original value/reason

        Example:
            >>> loop = EventLoop()
            >>> promise = JSPromise(lambda resolve, reject: resolve(42), loop)
            >>> promise.finally_handler(lambda: print("Done"))
            >>> loop.run()
            Done
        """
        def fulfillment_handler(value):
            # Run finally callback (synchronously)
            on_finally()
            # Pass original value through
            return value

        def rejection_handler(reason):
            # Run finally callback (synchronously)
            on_finally()
            # Re-throw the rejection to propagate it
            # Use PromiseRejection wrapper to handle non-exception reasons
            if isinstance(reason, Exception):
                raise reason
            else:
                raise PromiseRejection(reason)

        # Register separate handlers for fulfillment and rejection
        return self.then(fulfillment_handler, rejection_handler)
