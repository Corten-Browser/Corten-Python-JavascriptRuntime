"""
Deoptimization trigger handling - handle guard failures and type mismatches.
"""
from typing import Any, TYPE_CHECKING

from components.deoptimization.src.deopt_types import DeoptReason

if TYPE_CHECKING:
    from components.deoptimization.src.deopt_manager import DeoptimizationManager


class DeoptTriggerHandler:
    """Handle deoptimization triggers from guard failures."""

    def __init__(self, manager: "DeoptimizationManager"):
        """
        Initialize trigger handler.

        Args:
            manager: Deoptimization manager
        """
        self.manager = manager

    def handle_guard_failure(
        self,
        guard_id: int,
        guard_location: int,
        actual_value: Any,
        function_id: int = 0
    ) -> Any:
        """
        Handle guard failure and trigger deoptimization.

        Args:
            guard_id: Failed guard identifier
            guard_location: Guard location in code
            actual_value: Actual value that failed guard
            function_id: Function ID (optional, default 0)

        Returns:
            Interpreter state to resume execution
        """
        # Trigger deoptimization through manager
        result = self.manager.deoptimize(
            function_id=function_id,
            deopt_point=guard_location,
            reason=DeoptReason.GUARD_FAILURE,
            mode=None  # Manager will decide
        )
        return result

    def handle_type_mismatch(
        self,
        expected_type: str,
        actual_type: str,
        location: int,
        function_id: int = 0
    ) -> Any:
        """
        Handle type mismatch deoptimization.

        Args:
            expected_type: Expected type
            actual_type: Actual type
            location: Code location
            function_id: Function ID (optional, default 0)

        Returns:
            Interpreter state
        """
        # Trigger deoptimization for type mismatch
        result = self.manager.deoptimize(
            function_id=function_id,
            deopt_point=location,
            reason=DeoptReason.TYPE_MISMATCH,
            mode=None
        )
        return result

    def _categorize_reason(self, reason_str: str) -> DeoptReason:
        """
        Categorize string reason to DeoptReason enum.

        Args:
            reason_str: Reason string

        Returns:
            DeoptReason enum value
        """
        reason_map = {
            "guard_failure": DeoptReason.GUARD_FAILURE,
            "type_mismatch": DeoptReason.TYPE_MISMATCH,
            "overflow": DeoptReason.OVERFLOW,
            "div_by_zero": DeoptReason.DIV_BY_ZERO,
            "null_dereference": DeoptReason.NULL_DEREFERENCE,
            "out_of_bounds": DeoptReason.OUT_OF_BOUNDS,
            "shape_mismatch": DeoptReason.SHAPE_MISMATCH,
            "ic_miss": DeoptReason.IC_MISS,
        }
        return reason_map.get(reason_str, DeoptReason.ASSUMPTION_VIOLATED)
