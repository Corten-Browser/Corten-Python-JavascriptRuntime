"""
Benchmarking framework for performance optimization.

Provides comprehensive benchmarking infrastructure with:
- Accurate timing measurements
- Statistical significance testing
- GC and memory statistics
- Before/after comparison
- Performance target verification
"""

import gc
import time
import statistics
import tracemalloc
from typing import Callable, Dict, Any, List, Optional
from datetime import datetime
import uuid


class BenchmarkRunner:
    """
    Comprehensive benchmarking framework for performance optimization.

    Provides accurate timing, statistical analysis, and resource tracking.
    """

    def __init__(self):
        """Initialize benchmark runner with empty registry."""
        self._benchmarks: Dict[str, Dict[str, Any]] = {}
        self._results_cache: Dict[str, Dict[str, Any]] = {}

    def benchmark(
        self,
        name: str,
        func: Callable,
        iterations: int = 1000,
        warmup_iterations: int = 100,
        collect_gc_stats: bool = False,
        collect_memory_stats: bool = False
    ) -> Dict[str, Any]:
        """
        Benchmark a function with comprehensive metrics.

        Args:
            name: Benchmark name
            func: Function to benchmark
            iterations: Number of measurement iterations
            warmup_iterations: Number of warmup iterations
            collect_gc_stats: Whether to collect GC statistics
            collect_memory_stats: Whether to collect memory statistics

        Returns:
            Dictionary with benchmark metrics conforming to BenchmarkMetrics schema
        """
        # Warmup phase
        for _ in range(warmup_iterations):
            func()

        # Force GC before measurement
        gc.collect()

        # Start GC tracking if requested
        if collect_gc_stats:
            gc_before = gc.get_count()
            gc.enable()

        # Start memory tracking if requested
        if collect_memory_stats:
            tracemalloc.start()
            snapshot_before = tracemalloc.take_snapshot()

        # Measurement phase
        times = []
        for _ in range(iterations):
            start = time.perf_counter()
            func()
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to milliseconds

        # Stop memory tracking
        if collect_memory_stats:
            snapshot_after = tracemalloc.take_snapshot()
            tracemalloc.stop()

        # Stop GC tracking
        if collect_gc_stats:
            gc_after = gc.get_count()
            gc.disable()

        # Calculate statistics
        mean_time = statistics.mean(times)
        median_time = statistics.median(times)
        min_time = min(times)
        max_time = max(times)
        std_dev = statistics.stdev(times) if len(times) > 1 else 0.0
        ops_per_sec = 1000.0 / mean_time if mean_time > 0 else 0.0

        # Build result
        result = {
            "id": name,
            "name": name,
            "operationsPerSecond": ops_per_sec,
            "meanTimeMs": mean_time,
            "medianTimeMs": median_time,
            "minTimeMs": min_time,
            "maxTimeMs": max_time,
            "standardDeviation": std_dev,
            "iterations": iterations
        }

        # Add GC stats if collected
        if collect_gc_stats:
            gc_collections = sum(gc_after) - sum(gc_before)
            result["gcStats"] = {
                "collections": max(0, gc_collections),
                "totalPauseMs": 0.0,  # Python doesn't expose GC pause times directly
                "averagePauseMs": 0.0,
                "maxPauseMs": 0.0
            }

        # Add memory stats if collected
        if collect_memory_stats:
            top_stats = snapshot_after.compare_to(snapshot_before, 'lineno')
            total_allocated = sum(stat.size_diff for stat in top_stats if stat.size_diff > 0)

            # Calculate current memory usage from snapshot
            current_size = sum(stat.size for stat in snapshot_after.statistics('lineno'))
            peak_usage = current_size / (1024 * 1024)  # MB

            result["memoryStats"] = {
                "allocations": len([s for s in top_stats if s.size_diff > 0]),
                "deallocations": len([s for s in top_stats if s.size_diff < 0]),
                "peakUsageMB": peak_usage,
                "averageUsageMB": peak_usage,
                "totalAllocatedMB": total_allocated / (1024 * 1024)
            }

        return result

    def register_benchmark(
        self,
        id: str,
        name: str,
        category: str,
        func: Callable,
        requirement_id: str,
        description: str = "",
        enabled: bool = True
    ):
        """
        Register a benchmark for later execution.

        Args:
            id: Unique benchmark identifier
            name: Human-readable benchmark name
            category: Performance category (iteration, string, array, memory)
            func: Function to benchmark
            requirement_id: Associated functional requirement ID
            description: Benchmark description
            enabled: Whether benchmark is enabled
        """
        self._benchmarks[id] = {
            "id": id,
            "name": name,
            "category": category,
            "func": func,
            "requirementId": requirement_id,
            "description": description,
            "enabled": enabled
        }

    def list_benchmarks(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List registered benchmarks, optionally filtered by category.

        Args:
            category: Optional category filter

        Returns:
            List of benchmark info dictionaries
        """
        benchmarks = []
        for bench_id, bench_info in self._benchmarks.items():
            if category is None or bench_info["category"] == category:
                benchmarks.append({
                    "id": bench_info["id"],
                    "name": bench_info["name"],
                    "category": bench_info["category"],
                    "description": bench_info["description"],
                    "requirementId": bench_info["requirementId"],
                    "enabled": bench_info["enabled"]
                })
        return benchmarks

    def run_category(
        self,
        category: str,
        iterations: int = 1000,
        warmup_iterations: int = 100,
        collect_gc_stats: bool = True,
        collect_memory_stats: bool = True
    ) -> Dict[str, Any]:
        """
        Run all benchmarks in a category.

        Args:
            category: Category to run (iteration, string, array, memory)
            iterations: Number of iterations per benchmark
            warmup_iterations: Number of warmup iterations
            collect_gc_stats: Collect GC statistics
            collect_memory_stats: Collect memory statistics

        Returns:
            Dictionary with category results conforming to BenchmarkResult schema
        """
        start_time = time.time()

        # Get benchmarks for this category
        category_benchmarks = [
            b for b in self._benchmarks.values()
            if b["category"] == category and b["enabled"]
        ]

        # Run each benchmark
        benchmark_results = []
        for bench in category_benchmarks:
            result = self.benchmark(
                bench["name"],
                bench["func"],
                iterations=iterations,
                warmup_iterations=warmup_iterations,
                collect_gc_stats=collect_gc_stats,
                collect_memory_stats=collect_memory_stats
            )
            benchmark_results.append(result)

        # Calculate summary
        total = len(benchmark_results)
        passed = sum(1 for r in benchmark_results if r["operationsPerSecond"] > 0)
        failed = total - passed
        avg_ops = statistics.mean([r["operationsPerSecond"] for r in benchmark_results]) if total > 0 else 0

        end_time = time.time()
        duration_ms = (end_time - start_time) * 1000

        return {
            "category": category,
            "benchmarks": benchmark_results,
            "summary": {
                "totalBenchmarks": total,
                "passedBenchmarks": passed,
                "failedBenchmarks": failed,
                "averageOpsPerSecond": avg_ops,
                "totalDurationMs": duration_ms
            },
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "durationMs": duration_ms
        }

    def run_suite(
        self,
        categories: Optional[List[str]] = None,
        iterations: int = 1000,
        warmup_iterations: int = 100,
        parallel: bool = False
    ) -> Dict[str, Any]:
        """
        Run complete benchmark suite.

        Args:
            categories: Categories to run (None = all)
            iterations: Iterations per benchmark
            warmup_iterations: Warmup iterations
            parallel: Run in parallel (not implemented yet)

        Returns:
            Dictionary with suite results conforming to BenchmarkSuiteResult schema
        """
        start_time = time.time()

        # Determine categories to run
        if categories is None:
            categories = ["iteration", "string", "array", "memory"]

        # Run each category
        category_results = []
        for category in categories:
            result = self.run_category(
                category,
                iterations=iterations,
                warmup_iterations=warmup_iterations
            )
            category_results.append(result)

        # Calculate overall summary
        total_benchmarks = sum(r["summary"]["totalBenchmarks"] for r in category_results)
        passed_benchmarks = sum(r["summary"]["passedBenchmarks"] for r in category_results)
        failed_benchmarks = total_benchmarks - passed_benchmarks
        avg_ops = statistics.mean([
            r["summary"]["averageOpsPerSecond"]
            for r in category_results
            if r["summary"]["totalBenchmarks"] > 0
        ]) if category_results else 0

        end_time = time.time()
        total_duration_ms = (end_time - start_time) * 1000

        # Create minimal target verification (will be replaced by real data)
        target_verification = {
            "allTargetsMet": False,
            "targets": [],
            "overallScore": 0.0,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }

        return {
            "results": category_results,
            "overallSummary": {
                "totalBenchmarks": total_benchmarks,
                "passedBenchmarks": passed_benchmarks,
                "failedBenchmarks": failed_benchmarks,
                "averageOpsPerSecond": avg_ops,
                "totalDurationMs": total_duration_ms
            },
            "targetVerification": target_verification,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "totalDurationMs": total_duration_ms
        }

    def compare_benchmarks(
        self,
        before: Dict[str, Any],
        after: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compare two benchmark results.

        Args:
            before: Baseline benchmark result
            after: Optimized benchmark result

        Returns:
            Dictionary with comparison metrics
        """
        before_ops = before["operationsPerSecond"]
        after_ops = after["operationsPerSecond"]

        # Calculate improvement percentage
        if before_ops > 0:
            improvement = ((after_ops - before_ops) / before_ops) * 100
        else:
            improvement = 0.0

        # Simple significance test: >5% difference considered significant
        significant = abs(improvement) > 5.0

        # Check for regression
        regression = improvement < -5.0

        return {
            "benchmarkId": after.get("id", "unknown"),
            "benchmarkName": after.get("name", "unknown"),
            "beforeOpsPerSec": before_ops,
            "afterOpsPerSec": after_ops,
            "improvementPercentage": improvement,
            "beforeMeanTimeMs": before["meanTimeMs"],
            "afterMeanTimeMs": after["meanTimeMs"],
            "significant": significant,
            "regressionDetected": regression
        }

    def verify_target(
        self,
        category: str,
        target_improvement: float,
        baseline_ops: float,
        current_ops: float
    ) -> Dict[str, Any]:
        """
        Verify if performance target is met.

        Args:
            category: Category name
            target_improvement: Target improvement percentage
            baseline_ops: Baseline operations per second
            current_ops: Current operations per second

        Returns:
            Dictionary with target verification results
        """
        # Calculate actual improvement
        if baseline_ops > 0:
            improvement = ((current_ops - baseline_ops) / baseline_ops) * 100
        else:
            improvement = 0.0

        # Check if target is met
        target_met = improvement >= target_improvement

        return {
            "category": category,
            "targetImprovement": target_improvement,
            "baselinePerformance": baseline_ops,
            "currentPerformance": current_ops,
            "improvementPercentage": improvement,
            "targetMet": target_met
        }

    def verify_memory_target(
        self,
        baseline_allocations: int,
        current_allocations: int,
        target_reduction: float
    ) -> Dict[str, Any]:
        """
        Verify if memory reduction target is met.

        Args:
            baseline_allocations: Baseline allocation count
            current_allocations: Current allocation count
            target_reduction: Target reduction percentage

        Returns:
            Dictionary with memory target verification
        """
        # Calculate reduction percentage
        if baseline_allocations > 0:
            reduction = ((baseline_allocations - current_allocations) / baseline_allocations) * 100
        else:
            reduction = 0.0

        # Check if target is met
        target_met = reduction >= target_reduction

        return {
            "baselineAllocations": baseline_allocations,
            "currentAllocations": current_allocations,
            "reductionPercentage": reduction,
            "targetReduction": target_reduction,
            "targetMet": target_met
        }

    def register_all_benchmarks(self):
        """
        Register all available benchmarks across all categories.

        This method ensures we have at least 40 benchmarks as required by contract.
        """
        # Import optimizers to get their benchmark sets
        from .iteration_opt import IterationOptimizer
        from .string_opt import StringOptimizer
        from .array_opt import ArrayOptimizer
        from .memory_opt import MemoryOptimizer

        # Register iteration benchmarks (at least 10)
        iter_opt = IterationOptimizer()
        iter_benchmarks = iter_opt.get_benchmarks()
        for bench in iter_benchmarks:
            self.register_benchmark(**bench)

        # Register string benchmarks (at least 10)
        str_opt = StringOptimizer()
        str_benchmarks = str_opt.get_benchmarks()
        for bench in str_benchmarks:
            self.register_benchmark(**bench)

        # Register array benchmarks (at least 10)
        arr_opt = ArrayOptimizer()
        arr_benchmarks = arr_opt.get_benchmarks()
        for bench in arr_benchmarks:
            self.register_benchmark(**bench)

        # Register memory benchmarks (at least 10)
        mem_opt = MemoryOptimizer()
        mem_benchmarks = mem_opt.get_benchmarks()
        for bench in mem_benchmarks:
            self.register_benchmark(**bench)
