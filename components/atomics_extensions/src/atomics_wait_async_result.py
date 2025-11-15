"""
AtomicsWaitAsyncResult data structure.

Represents the result of an Atomics.waitAsync() operation.
"""


class AtomicsWaitAsyncResult:
    """Result of Atomics.waitAsync() operation.

    Contains information about whether the wait is async or immediate,
    the wait status, and a promise for async waits.

    Attributes:
        async_status: True if async wait (returns promise), False if immediate
        value: Wait status - "ok", "not-equal", or "timed-out"
        promise: Promise that resolves when notified (only for async waits)
    """

    def __init__(self, async_status, value, promise=None):
        """Create wait async result.

        Args:
            async_status: True if async, False if immediate
            value: Status string ("ok", "not-equal", or "timed-out")
            promise: Promise for async waits (None for immediate)
        """
        self.async_status = async_status
        self.value = value
        self.promise = promise

    def __repr__(self):
        """String representation."""
        if self.async_status:
            return f"AtomicsWaitAsyncResult(async, {self.value}, promise={self.promise})"
        else:
            return f"AtomicsWaitAsyncResult(immediate, {self.value})"
