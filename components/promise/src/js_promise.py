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

    @staticmethod
    def resolve(value, event_loop):
        """Create immediately fulfilled Promise.

        If value is already a Promise, return it unchanged.
        Otherwise, create a new Promise fulfilled with the value.

        Args:
            value: Value to fulfill with (or existing Promise)
            event_loop: EventLoop instance

        Returns:
            Promise (either existing or newly created)

        Example:
            >>> loop = EventLoop()
            >>> promise = JSPromise.resolve(42, loop)
            >>> promise.then(lambda x: print(x))
            >>> loop.run()
            42
        """
        if isinstance(value, JSPromise):
            return value  # Already a Promise

        return JSPromise(lambda resolve, reject: resolve(value), event_loop)

    @staticmethod
    def reject(reason, event_loop):
        """Create immediately rejected Promise.

        Args:
            reason: Rejection reason
            event_loop: EventLoop instance

        Returns:
            Rejected Promise

        Example:
            >>> loop = EventLoop()
            >>> promise = JSPromise.reject("error", loop)
            >>> promise.catch(lambda err: print(err))
            >>> loop.run()
            error
        """
        return JSPromise(lambda resolve, reject: reject(reason), event_loop)

    @staticmethod
    def all(promises, event_loop):
        """Fulfill when all Promises fulfill, reject if any rejects.

        Returns a Promise that:
        - Fulfills with array of values when all input promises fulfill
        - Rejects with first rejection reason if any promise rejects

        Args:
            promises: List of Promises (or values that will be converted)
            event_loop: EventLoop instance

        Returns:
            Promise that resolves with list of values or rejects with first rejection

        Example:
            >>> loop = EventLoop()
            >>> promises = [
            ...     JSPromise.resolve(1, loop),
            ...     JSPromise.resolve(2, loop)
            ... ]
            >>> JSPromise.all(promises, loop).then(lambda v: print(v))
            >>> loop.run()
            [1, 2]
        """
        results = [None] * len(promises)
        completed_count = [0]  # Use list to allow mutation in nested function

        def create_result_promise(resolve_outer, reject_outer):
            if len(promises) == 0:
                resolve_outer([])
                return

            def handle_fulfillment(index, value):
                results[index] = value
                completed_count[0] += 1
                if completed_count[0] == len(promises):
                    resolve_outer(results)

            def handle_rejection(reason):
                reject_outer(reason)

            for i, promise in enumerate(promises):
                # Ensure it's a Promise
                if not isinstance(promise, JSPromise):
                    promise = JSPromise.resolve(promise, event_loop)

                # Use lambda with default args to capture loop variable
                promise.then(
                    lambda value, idx=i: handle_fulfillment(idx, value),
                    handle_rejection
                )

        return JSPromise(create_result_promise, event_loop)

    @staticmethod
    def race(promises, event_loop):
        """Settle when first Promise settles (fulfill or reject).

        Returns a Promise that settles with the same value/reason as the
        first promise that settles.

        Args:
            promises: List of Promises
            event_loop: EventLoop instance

        Returns:
            Promise that settles with first settlement

        Example:
            >>> loop = EventLoop()
            >>> promises = [
            ...     JSPromise.resolve(1, loop),
            ...     JSPromise.resolve(2, loop)
            ... ]
            >>> JSPromise.race(promises, loop).then(lambda v: print(v))
            >>> loop.run()
            1
        """
        def create_result_promise(resolve_outer, reject_outer):
            if len(promises) == 0:
                # Never settles (per spec)
                return

            for promise in promises:
                # Ensure it's a Promise
                if not isinstance(promise, JSPromise):
                    promise = JSPromise.resolve(promise, event_loop)

                promise.then(resolve_outer, reject_outer)

        return JSPromise(create_result_promise, event_loop)

    @staticmethod
    def any(promises, event_loop):
        """Fulfill when first Promise fulfills, reject if all reject.

        Returns a Promise that:
        - Fulfills with the first fulfillment value
        - Rejects with AggregateError if all promises reject

        Args:
            promises: List of Promises
            event_loop: EventLoop instance

        Returns:
            Promise that fulfills with first fulfillment or rejects with AggregateError

        Example:
            >>> loop = EventLoop()
            >>> promises = [
            ...     JSPromise.reject("error1", loop),
            ...     JSPromise.resolve(42, loop)
            ... ]
            >>> JSPromise.any(promises, loop).then(lambda v: print(v))
            >>> loop.run()
            42
        """
        errors = []
        rejected_count = [0]

        def create_result_promise(resolve_outer, reject_outer):
            if len(promises) == 0:
                reject_outer(AggregateError([]))
                return

            def handle_rejection(index, reason):
                errors.append(reason)
                rejected_count[0] += 1
                if rejected_count[0] == len(promises):
                    reject_outer(AggregateError(errors))

            for i, promise in enumerate(promises):
                # Ensure it's a Promise
                if not isinstance(promise, JSPromise):
                    promise = JSPromise.resolve(promise, event_loop)

                promise.then(
                    resolve_outer,  # Any fulfillment wins
                    lambda reason, idx=i: handle_rejection(idx, reason)
                )

        return JSPromise(create_result_promise, event_loop)

    @staticmethod
    def allSettled(promises, event_loop):
        """Wait for all Promises to settle (fulfill or reject).

        Returns a Promise that always fulfills with an array of objects
        describing the outcome of each promise.

        Args:
            promises: List of Promises
            event_loop: EventLoop instance

        Returns:
            Promise that resolves with list of settlement results

        Example:
            >>> loop = EventLoop()
            >>> promises = [
            ...     JSPromise.resolve(1, loop),
            ...     JSPromise.reject("error", loop)
            ... ]
            >>> JSPromise.allSettled(promises, loop).then(lambda v: print(v))
            >>> loop.run()
            [{'status': 'fulfilled', 'value': 1}, {'status': 'rejected', 'reason': 'error'}]
        """
        results = [None] * len(promises)
        settled_count = [0]

        def create_result_promise(resolve_outer, reject_outer):
            if len(promises) == 0:
                resolve_outer([])
                return

            def handle_fulfillment(index, value):
                results[index] = {"status": "fulfilled", "value": value}
                settled_count[0] += 1
                if settled_count[0] == len(promises):
                    resolve_outer(results)

            def handle_rejection(index, reason):
                results[index] = {"status": "rejected", "reason": reason}
                settled_count[0] += 1
                if settled_count[0] == len(promises):
                    resolve_outer(results)

            for i, promise in enumerate(promises):
                # Ensure it's a Promise
                if not isinstance(promise, JSPromise):
                    promise = JSPromise.resolve(promise, event_loop)

                promise.then(
                    lambda value, idx=i: handle_fulfillment(idx, value),
                    lambda reason, idx=i: handle_rejection(idx, reason)
                )

        return JSPromise(create_result_promise, event_loop)

    @staticmethod
    def withResolvers(event_loop):
        """Create a Promise with exposed resolve/reject functions.

        This is the deferred promise pattern, useful when you need to
        control promise resolution from outside the executor.

        Returns a dictionary with three keys:
        - promise: The Promise instance
        - resolve: Function to fulfill the promise
        - reject: Function to reject the promise

        Args:
            event_loop: EventLoop instance

        Returns:
            Dictionary with {promise, resolve, reject}

        Example:
            >>> loop = EventLoop()
            >>> deferred = JSPromise.withResolvers(loop)
            >>> deferred["promise"].then(lambda x: print(x))
            >>> deferred["resolve"](42)
            >>> loop.run()
            42
        """
        # Store resolve/reject references
        resolve_ref = [None]
        reject_ref = [None]

        def executor(resolve, reject):
            # Capture resolve/reject functions
            resolve_ref[0] = resolve
            reject_ref[0] = reject

        # Create the promise
        promise = JSPromise(executor, event_loop)

        # Return object with promise and control functions
        return {
            "promise": promise,
            "resolve": resolve_ref[0],
            "reject": reject_ref[0]
        }

    def __await__(self):
        """
        Make JSPromise awaitable by Python's asyncio.

        This allows async functions using asyncio to await JSPromise instances.
        Coordinates between asyncio event loop and custom EventLoop.

        Returns:
            Generator that can be used by asyncio's await mechanism
        """
        import asyncio

        # If already settled, return immediately
        if self.state == PromiseState.FULFILLED:
            async def immediate_value():
                return self.value
            return immediate_value().__await__()

        if self.state == PromiseState.REJECTED:
            async def immediate_error():
                raise self.value
            return immediate_error().__await__()

        # Promise is pending - need to wait for resolution
        # Create asyncio Future to bridge the two event loop systems
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No running loop, try to get event loop
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

        future = loop.create_future()

        # Link JSPromise resolution to asyncio Future
        def on_fulfilled(value):
            if not future.done():
                loop.call_soon_threadsafe(future.set_result, value)

        def on_rejected(reason):
            if not future.done():
                if isinstance(reason, Exception):
                    loop.call_soon_threadsafe(future.set_exception, reason)
                else:
                    # Wrap non-exception rejections
                    loop.call_soon_threadsafe(future.set_exception, PromiseRejection(reason))

        # Attach callbacks to JSPromise
        self.then(on_fulfilled, on_rejected)

        # Return future's __await__
        return future.__await__()


class AggregateError(Exception):
    """Error representing multiple Promise rejections.

    Used by Promise.any() when all input promises reject.

    Attributes:
        errors: List of rejection reasons from all rejected promises
    """

    def __init__(self, errors):
        self.errors = errors
        super().__init__(f"All Promises rejected ({len(errors)} errors)")
