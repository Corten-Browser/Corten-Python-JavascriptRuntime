"""
Unit tests for benchmarking framework - RED phase
Tests the benchmark infrastructure before implementation
"""

import pytest
import time
from typing import Callable


class TestBenchmarkFramework:
    """Test the benchmarking framework infrastructure."""

    def test_import_benchmarks(self):
        """Test that benchmarks module can be imported."""
        from components.performance_optimization.src import benchmarks
        assert benchmarks is not None

    def test_benchmark_runner_exists(self):
        """Test that BenchmarkRunner class exists."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner
        runner = BenchmarkRunner()
        assert runner is not None

    def test_benchmark_simple_function(self):
        """Test benchmarking a simple function."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()

        # Simple function to benchmark
        def simple_add():
            return 1 + 1

        result = runner.benchmark(
            "simple_add",
            simple_add,
            iterations=100,
            warmup_iterations=10
        )

        # Verify result structure
        assert "id" in result
        assert "name" in result
        assert "operationsPerSecond" in result
        assert "meanTimeMs" in result
        assert "medianTimeMs" in result
        assert "minTimeMs" in result
        assert "maxTimeMs" in result
        assert "standardDeviation" in result
        assert "iterations" in result

        # Verify result values are reasonable
        assert result["operationsPerSecond"] > 0
        assert result["meanTimeMs"] >= 0
        assert result["iterations"] == 100

    def test_benchmark_with_gc_stats(self):
        """Test benchmarking with GC statistics collection."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()

        def allocate_memory():
            return [i for i in range(1000)]

        result = runner.benchmark(
            "allocate_memory",
            allocate_memory,
            iterations=100,
            collect_gc_stats=True
        )

        # Verify GC stats are present
        assert "gcStats" in result
        assert "collections" in result["gcStats"]
        assert "totalPauseMs" in result["gcStats"]

    def test_benchmark_with_memory_stats(self):
        """Test benchmarking with memory statistics collection."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()

        def allocate_list():
            return [i for i in range(1000)]

        result = runner.benchmark(
            "allocate_list",
            allocate_list,
            iterations=100,
            collect_memory_stats=True
        )

        # Verify memory stats are present
        assert "memoryStats" in result
        assert "allocations" in result["memoryStats"]
        assert "peakUsageMB" in result["memoryStats"]

    def test_benchmark_category_runner(self):
        """Test running benchmarks by category."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()

        # Register a benchmark
        runner.register_benchmark(
            id="test_iter",
            name="Test iteration",
            category="iteration",
            func=lambda: sum(range(100)),
            requirement_id="FR-ES24-D-018"
        )

        # Run category benchmarks
        results = runner.run_category("iteration", iterations=100)

        assert "category" in results
        assert "benchmarks" in results
        assert "summary" in results
        assert results["category"] == "iteration"
        assert len(results["benchmarks"]) > 0

    def test_benchmark_suite_runner(self):
        """Test running complete benchmark suite."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()

        # Register benchmarks in different categories
        runner.register_benchmark(
            id="test_iter",
            name="Test iteration",
            category="iteration",
            func=lambda: sum(range(100)),
            requirement_id="FR-ES24-D-018"
        )

        runner.register_benchmark(
            id="test_string",
            name="Test string concat",
            category="string",
            func=lambda: "hello" + "world",
            requirement_id="FR-ES24-D-019"
        )

        # Run suite
        results = runner.run_suite(categories=["iteration", "string"], iterations=100)

        assert "results" in results
        assert "overallSummary" in results
        assert len(results["results"]) == 2

    def test_statistical_significance(self):
        """Test statistical significance detection."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()

        # Two functions with measurably different performance
        def slow_func():
            time.sleep(0.0001)
            return sum(range(1000))

        def fast_func():
            return sum(range(1000))

        before = runner.benchmark("slow", slow_func, iterations=50)
        after = runner.benchmark("fast", fast_func, iterations=50)

        # Compare
        comparison = runner.compare_benchmarks(before, after)

        assert "improvementPercentage" in comparison
        assert "significant" in comparison
        assert comparison["improvementPercentage"] != 0


class TestPerformanceTargets:
    """Test performance target verification."""

    def test_iteration_target_verification(self):
        """Test iteration optimization target (20% improvement)."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()

        # Target: 20% improvement
        target = runner.verify_target(
            category="iteration",
            target_improvement=20.0,
            baseline_ops=1000.0,
            current_ops=1200.0  # 20% improvement
        )

        assert target["targetMet"] is True
        assert target["improvementPercentage"] >= 20.0

    def test_string_target_verification(self):
        """Test string optimization target (30% improvement)."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()

        # Target: 30% improvement
        target = runner.verify_target(
            category="string",
            target_improvement=30.0,
            baseline_ops=1000.0,
            current_ops=1300.0  # 30% improvement
        )

        assert target["targetMet"] is True
        assert target["improvementPercentage"] >= 30.0

    def test_array_target_verification(self):
        """Test array optimization target (25% improvement)."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()

        # Target: 25% improvement
        target = runner.verify_target(
            category="array",
            target_improvement=25.0,
            baseline_ops=1000.0,
            current_ops=1250.0  # 25% improvement
        )

        assert target["targetMet"] is True
        assert target["improvementPercentage"] >= 25.0

    def test_memory_target_verification(self):
        """Test memory optimization target (15% reduction)."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()

        # Target: 15% reduction in allocations
        target = runner.verify_memory_target(
            baseline_allocations=1000,
            current_allocations=850,  # 15% reduction
            target_reduction=15.0
        )

        assert target["targetMet"] is True
        assert target["reductionPercentage"] >= 15.0


class TestBenchmarkRegistry:
    """Test benchmark registration and management."""

    def test_register_benchmark(self):
        """Test registering a benchmark."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()

        runner.register_benchmark(
            id="test_1",
            name="Test benchmark",
            category="iteration",
            func=lambda: sum(range(100)),
            requirement_id="FR-ES24-D-018",
            description="Test description"
        )

        benchmarks = runner.list_benchmarks()
        assert len(benchmarks) > 0
        assert any(b["id"] == "test_1" for b in benchmarks)

    def test_list_benchmarks_by_category(self):
        """Test listing benchmarks by category."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()

        runner.register_benchmark(
            id="iter_1",
            name="Iteration test",
            category="iteration",
            func=lambda: sum(range(100)),
            requirement_id="FR-ES24-D-018"
        )

        runner.register_benchmark(
            id="str_1",
            name="String test",
            category="string",
            func=lambda: "hello" + "world",
            requirement_id="FR-ES24-D-019"
        )

        iter_benchmarks = runner.list_benchmarks(category="iteration")
        assert len(iter_benchmarks) > 0
        assert all(b["category"] == "iteration" for b in iter_benchmarks)

    def test_minimum_benchmark_count(self):
        """Test that we have at least 40 benchmarks (contract requirement)."""
        from components.performance_optimization.src.benchmarks import BenchmarkRunner

        runner = BenchmarkRunner()
        runner.register_all_benchmarks()  # Register all available benchmarks

        benchmarks = runner.list_benchmarks()
        assert len(benchmarks) >= 40, "Contract requires minimum 40 benchmarks"
