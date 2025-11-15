"""Eager deoptimization - immediate bailout."""
from typing import TYPE_CHECKING

from components.deoptimization.src.deopt_types import JITState, DeoptMode, DeoptReason

if TYPE_CHECKING:
    from components.deoptimization.src.deopt_manager import DeoptimizationManager


class EagerDeoptimizer:
    """Immediate deoptimization (bailout)."""

    def __init__(self, manager: "DeoptimizationManager"):
        """Initialize eager deoptimizer."""
        self.manager = manager

    def bailout(
        self,
        function_id: int,
        bailout_point: int,
        jit_state: JITState
    ):
        """Immediate bailout to interpreter."""
        result = self.manager.deoptimize(
            function_id=function_id,
            deopt_point=bailout_point,
            reason=DeoptReason.NULL_DEREFERENCE,  # Critical failure
            mode=DeoptMode.EAGER
        )
        return result
