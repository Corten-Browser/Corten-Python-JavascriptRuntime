"""Lazy deoptimization - defer until safe point."""
from typing import List, Tuple
from dataclasses import dataclass

from components.deoptimization.src.deopt_types import DeoptReason
from components.deoptimization.src.state_materializer import InterpreterState


@dataclass
class PendingDeopt:
    """Pending deoptimization."""
    function_id: int
    deopt_point: int
    reason: DeoptReason


class LazyDeoptimizer:
    """Defer deoptimization until safe point."""

    def __init__(self):
        """Initialize lazy deoptimizer."""
        self.pending: List[PendingDeopt] = []

    def schedule_deopt(
        self,
        function_id: int,
        deopt_point: int,
        reason: DeoptReason
    ) -> None:
        """Schedule lazy deoptimization."""
        self.pending.append(PendingDeopt(function_id, deopt_point, reason))

    def process_pending(self) -> List[InterpreterState]:
        """Process all pending lazy deoptimizations."""
        results = []
        for deopt in self.pending:
            # Create placeholder interpreter state
            from components.deoptimization.src.deopt_types import InterpreterFrame
            frame = InterpreterFrame(bytecode_offset=deopt.deopt_point, locals=[], stack=[])
            state = InterpreterState(frame=frame)
            results.append(state)
        self.pending.clear()
        return results
