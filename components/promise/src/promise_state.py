"""Promise state enumeration.

Defines the three states a Promise can be in according to ECMAScript specification.
"""

from enum import Enum, auto


class PromiseState(Enum):
    """Promise states per ECMAScript specification.

    A Promise is always in one of three states:
    - PENDING: Initial state, neither fulfilled nor rejected
    - FULFILLED: The operation completed successfully
    - REJECTED: The operation failed

    Once a Promise is fulfilled or rejected, it is settled and cannot change state.
    """

    PENDING = auto()
    FULFILLED = auto()
    REJECTED = auto()
