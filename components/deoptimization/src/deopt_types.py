"""
Core data structures and types for deoptimization.
"""
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Dict, List, Any, Optional


class DeoptReason(Enum):
    """Reasons for deoptimization."""
    GUARD_FAILURE = auto()
    TYPE_MISMATCH = auto()
    OVERFLOW = auto()
    DIV_BY_ZERO = auto()
    NULL_DEREFERENCE = auto()
    OUT_OF_BOUNDS = auto()
    SHAPE_MISMATCH = auto()
    IC_MISS = auto()
    ASSUMPTION_VIOLATED = auto()


class DeoptMode(Enum):
    """Deoptimization modes."""
    EAGER = auto()  # Immediate bailout
    LAZY = auto()   # Defer until safe point


@dataclass
class ValueLocation:
    """Location of a value in JIT state."""
    location_type: str  # "register", "stack", "constant"
    location_id: int    # Register number or stack offset
    value_type: str     # Expected value type


@dataclass
class DeoptInfo:
    """Deoptimization metadata for a specific deopt point."""
    deopt_id: int
    bytecode_offset: int
    value_map: Dict[str, ValueLocation]
    frame_size: int
    reason: DeoptReason


@dataclass
class JITFrame:
    """JIT stack frame representation."""
    return_address: int
    registers: Dict[str, int]
    stack: List[int]


@dataclass
class InterpreterFrame:
    """Interpreter stack frame representation."""
    bytecode_offset: int
    locals: List[Any]  # List of JSValue
    stack: List[Any]   # List of JSValue


@dataclass
class JITState:
    """Current JIT execution state."""
    registers: Dict[str, int]
    stack_pointer: int
    instruction_pointer: int


@dataclass
class DeoptStats:
    """Deoptimization statistics."""
    total_deopts: int = 0
    eager_deopts: int = 0
    lazy_deopts: int = 0
    reason_counts: Dict[DeoptReason, int] = field(default_factory=dict)


@dataclass
class DeoptHotspot:
    """Frequently deoptimized location."""
    function_id: int
    location: int
    count: int
    reason: DeoptReason
