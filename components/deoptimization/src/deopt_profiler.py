"""Deoptimization profiling and analysis."""
from typing import List, Dict, Tuple
from collections import defaultdict

from components.deoptimization.src.deopt_types import (
    DeoptReason,
    DeoptStats,
    DeoptHotspot,
)


class DeoptProfiler:
    """Profile and analyze deoptimization patterns."""

    def __init__(self):
        """Initialize deopt profiler."""
        self.total_deopts = 0
        self.eager_deopts = 0
        self.lazy_deopts = 0
        self.reason_counts: Dict[DeoptReason, int] = defaultdict(int)
        self.location_counts: Dict[Tuple[int, int], int] = defaultdict(int)  # (func_id, location)
        self.location_reasons: Dict[Tuple[int, int], DeoptReason] = {}

    def record_deopt(
        self,
        function_id: int,
        reason: DeoptReason,
        location: int,
        is_eager: bool = True
    ) -> None:
        """Record deoptimization event."""
        self.total_deopts += 1
        if is_eager:
            self.eager_deopts += 1
        else:
            self.lazy_deopts += 1

        self.reason_counts[reason] += 1
        key = (function_id, location)
        self.location_counts[key] += 1
        self.location_reasons[key] = reason

    def get_stats(self) -> DeoptStats:
        """Get profiling statistics."""
        return DeoptStats(
            total_deopts=self.total_deopts,
            eager_deopts=self.eager_deopts,
            lazy_deopts=self.lazy_deopts,
            reason_counts=dict(self.reason_counts)
        )

    def get_hot_deopts(self, threshold: int = 100) -> List[DeoptHotspot]:
        """Identify frequently deoptimized locations."""
        hotspots = []
        for (func_id, location), count in self.location_counts.items():
            if count >= threshold:
                reason = self.location_reasons.get((func_id, location), DeoptReason.ASSUMPTION_VIOLATED)
                hotspots.append(DeoptHotspot(
                    function_id=func_id,
                    location=location,
                    count=count,
                    reason=reason
                ))
        return hotspots
