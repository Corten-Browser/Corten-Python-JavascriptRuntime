"""Main deoptimization manager."""
from typing import Dict, Any, Optional

from components.deoptimization.src.deopt_types import (
    DeoptReason,
    DeoptMode,
    DeoptStats,
    DeoptInfo,
    InterpreterFrame,
)
from components.deoptimization.src.state_materializer import InterpreterState
from components.deoptimization.src.frame_reconstructor import FrameReconstructor
from components.deoptimization.src.lazy_deopt import LazyDeoptimizer
from components.deoptimization.src.deopt_profiler import DeoptProfiler


class DeoptimizationManager:
    """Main manager for deoptimization operations."""

    def __init__(self):
        """Initialize deoptimization manager."""
        self.functions: Dict[int, Any] = {}  # function_id -> OptimizedCode
        self.reconstructor = FrameReconstructor()
        self.lazy_deoptimizer = LazyDeoptimizer()
        self.profiler = DeoptProfiler()

    def register_optimized_function(
        self,
        function_id: int,
        optimized_code: Any
    ) -> None:
        """Register optimized function for potential deoptimization."""
        self.functions[function_id] = optimized_code

    def deoptimize(
        self,
        function_id: int,
        deopt_point: int,
        reason: DeoptReason,
        mode: Optional[DeoptMode]
    ) -> Optional[InterpreterState]:
        """
        Perform deoptimization.

        Args:
            function_id: Function to deoptimize
            deopt_point: Deoptimization point offset
            reason: Deoptimization reason
            mode: Eager or lazy deoptimization

        Returns:
            Reconstructed interpreter state (None for lazy)

        Raises:
            KeyError: If function not registered
        """
        if function_id not in self.functions:
            raise KeyError(f"Function {function_id} not registered")

        # Record for profiling
        is_eager = mode == DeoptMode.EAGER if mode else True
        self.profiler.record_deopt(function_id, reason, deopt_point, is_eager)

        # Determine mode if not specified
        if mode is None:
            mode = DeoptMode.EAGER  # Default to eager

        if mode == DeoptMode.LAZY:
            # Schedule for later
            self.lazy_deoptimizer.schedule_deopt(function_id, deopt_point, reason)
            return None
        else:
            # Eager deoptimization - reconstruct immediately
            optimized_code = self.functions[function_id]
            deopt_info_map = getattr(optimized_code, "deopt_info", {})

            # Get deopt info for this point (or create placeholder)
            if deopt_point in deopt_info_map:
                deopt_info = deopt_info_map[deopt_point]
            else:
                # Create minimal deopt info
                deopt_info = DeoptInfo(
                    deopt_id=deopt_point,
                    bytecode_offset=deopt_point,
                    value_map={},
                    frame_size=0,
                    reason=reason
                )

            # Create interpreter frame
            frame = InterpreterFrame(
                bytecode_offset=deopt_info.bytecode_offset,
                locals=[],
                stack=[]
            )

            return InterpreterState(frame=frame)

    def get_stats(self) -> DeoptStats:
        """Get deoptimization statistics."""
        return self.profiler.get_stats()
