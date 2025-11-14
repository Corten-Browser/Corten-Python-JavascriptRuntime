"""Module lifecycle status enumeration."""

from enum import Enum, auto


class ModuleStatus(Enum):
    """
    Module lifecycle states.

    State transitions:
    UNLINKED → LINKING → LINKED → EVALUATING → EVALUATED
                    ↓
                  ERROR
    """
    UNLINKED = auto()      # Module created, not yet linked
    LINKING = auto()       # Currently loading dependencies
    LINKED = auto()        # Dependencies loaded, ready to evaluate
    EVALUATING = auto()    # Currently executing module code
    EVALUATED = auto()     # Module fully executed
    ERROR = auto()         # Error during linking or evaluation
