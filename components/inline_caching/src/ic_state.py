"""
Inline Cache State Machine.

Defines the states an inline cache can be in:
- UNINITIALIZED: No shapes cached yet
- MONOMORPHIC: Single shape cached (fast path)
- POLYMORPHIC: 2-4 shapes cached (medium path)
- MEGAMORPHIC: >4 shapes seen (fallback to slow path)
"""
from enum import Enum, auto


class ICState(Enum):
    """
    Inline cache state enumeration.

    State transitions:
    UNINITIALIZED → MONOMORPHIC → POLYMORPHIC → MEGAMORPHIC

    Once megamorphic, the cache remains in that state permanently.
    """

    UNINITIALIZED = auto()  # No shapes cached
    MONOMORPHIC = auto()    # Single shape (fast)
    POLYMORPHIC = auto()    # 2-4 shapes (medium)
    MEGAMORPHIC = auto()    # >4 shapes (slow path)

    def __str__(self):
        """String representation."""
        return self.name

    def __repr__(self):
        """Representation."""
        return f"ICState.{self.name}"
