"""
Integration tests for performance target verification.

Verifies that all 4 optimization requirements meet their targets:
- FR-ES24-D-018: Iteration 20% improvement
- FR-ES24-D-019: String 30% improvement
- FR-ES24-D-020: Array 25% improvement
- FR-ES24-D-021: Memory 15% reduction
"""

import pytest
from components.performance_optimization.src.benchmarks import BenchmarkRunner
from components.performance_optimization.src.iteration_opt import IterationOptimizer
from components.performance_optimization.src.string_opt import StringOptimizer
from components.performance_optimization.src.array_opt import ArrayOptimizer
from components.performance_optimization.src.memory_opt import MemoryOptimizer


class TestIterationOptimizationTarget:
    """Test FR-ES24-D-018: Iteration optimization 20% improvement."""

    def test_iteration_optimization_meets_target(self):
        """Verify iteration optimizations achieve 20%+ improvement."""
        optimizer = IterationOptimizer()
        result = optimizer.apply_optimizations()

        # Verify requirement ID
        assert result["requirementId"] == "FR-ES24-D-018"

        # Verify target met
        assert result["targetMet"] is True, \
            f"Iteration optimization failed to meet 20% target. Got {result['improvementPercentage']:.1f}%"

        # Verify improvement percentage
        assert result["improvementPercentage"] >= 20.0, \
            f"Expected >=20% improvement, got {result['improvementPercentage']:.1f}%"

        # Verify status
        assert result["status"] == "fully_optimized"

        # Verify optimizations were applied
        assert len(result["optimizations"]) > 0
        assert all(opt["applied"] for opt in result["optimizations"])

    def test_iteration_optimization_multiple_techniques(self):
        """Verify multiple optimization techniques are applied."""
        optimizer = IterationOptimizer()
        result = optimizer.apply_optimizations()

        # Should have at least 3 different optimization techniques
        assert len(result["optimizations"]) >= 3

        # Verify high-impact optimizations exist
        high_impact = [opt for opt in result["optimizations"] if opt["impact"] == "high"]
        assert len(high_impact) >= 1


class TestStringOptimizationTarget:
    """Test FR-ES24-D-019: String optimization 30% improvement."""

    def test_string_optimization_meets_target(self):
        """Verify string optimizations achieve 30%+ improvement."""
        optimizer = StringOptimizer()
        result = optimizer.apply_optimizations()

        # Verify requirement ID
        assert result["requirementId"] == "FR-ES24-D-019"

        # Verify target met
        assert result["targetMet"] is True, \
            f"String optimization failed to meet 30% target. Got {result['improvementPercentage']:.1f}%"

        # Verify improvement percentage
        assert result["improvementPercentage"] >= 30.0, \
            f"Expected >=30% improvement, got {result['improvementPercentage']:.1f}%"

        # Verify status
        assert result["status"] == "fully_optimized"

    def test_string_optimization_cache_effectiveness(self):
        """Verify caching optimizations are effective."""
        optimizer = StringOptimizer()
        result = optimizer.apply_optimizations()

        # Check for caching optimizations
        cache_opts = [
            opt for opt in result["optimizations"]
            if "cach" in opt["name"].lower() or "intern" in opt["name"].lower()
        ]
        assert len(cache_opts) >= 1, "Should have caching optimization"


class TestArrayOptimizationTarget:
    """Test FR-ES24-D-020: Array optimization 25% improvement."""

    def test_array_optimization_meets_target(self):
        """Verify array optimizations achieve 25%+ improvement."""
        optimizer = ArrayOptimizer()
        result = optimizer.apply_optimizations()

        # Verify requirement ID
        assert result["requirementId"] == "FR-ES24-D-020"

        # Verify target met
        assert result["targetMet"] is True, \
            f"Array optimization failed to meet 25% target. Got {result['improvementPercentage']:.1f}%"

        # Verify improvement percentage
        assert result["improvementPercentage"] >= 25.0, \
            f"Expected >=25% improvement, got {result['improvementPercentage']:.1f}%"

        # Verify status
        assert result["status"] == "fully_optimized"

    def test_array_optimization_builtin_usage(self):
        """Verify built-in function optimizations are used."""
        optimizer = ArrayOptimizer()
        result = optimizer.apply_optimizations()

        # Should use built-in optimizations
        builtin_opts = [
            opt for opt in result["optimizations"]
            if "built-in" in opt["description"].lower()
        ]
        assert len(builtin_opts) >= 1


class TestMemoryOptimizationTarget:
    """Test FR-ES24-D-021: Memory optimization 15% reduction."""

    def test_memory_optimization_meets_target(self):
        """Verify memory optimizations achieve 15%+ reduction."""
        optimizer = MemoryOptimizer()
        result = optimizer.apply_optimizations()

        # Verify requirement ID
        assert result["requirementId"] == "FR-ES24-D-021"

        # Verify target met
        assert result["targetMet"] is True, \
            f"Memory optimization failed to meet 15% reduction target. Got {result['reductionPercentage']:.1f}%"

        # Verify reduction percentage
        assert result["reductionPercentage"] >= 15.0, \
            f"Expected >=15% reduction, got {result['reductionPercentage']:.1f}%"

        # Verify status
        assert result["status"] == "fully_optimized"

        # Verify allocations reduced
        assert result["currentAllocations"] < result["baselineAllocations"]

    def test_memory_optimization_pooling(self):
        """Verify object pooling is implemented."""
        optimizer = MemoryOptimizer()
        result = optimizer.apply_optimizations()

        # Check for pooling optimizations
        pool_opts = [
            opt for opt in result["optimizations"]
            if "pool" in opt["name"].lower()
        ]
        assert len(pool_opts) >= 1, "Should have pooling optimization"


class TestComprehensiveBenchmarkSuite:
    """Test comprehensive benchmark suite with all categories."""

    def test_minimum_40_benchmarks(self):
        """Verify we have at least 40 benchmarks (contract requirement)."""
        runner = BenchmarkRunner()
        runner.register_all_benchmarks()

        benchmarks = runner.list_benchmarks()
        assert len(benchmarks) >= 40, \
            f"Contract requires minimum 40 benchmarks, got {len(benchmarks)}"

    def test_all_categories_represented(self):
        """Verify all 4 categories have benchmarks."""
        runner = BenchmarkRunner()
        runner.register_all_benchmarks()

        benchmarks = runner.list_benchmarks()

        categories = set(b["category"] for b in benchmarks)
        expected_categories = {"iteration", "string", "array", "memory"}

        assert categories == expected_categories, \
            f"Expected categories {expected_categories}, got {categories}"

    def test_each_category_has_minimum_benchmarks(self):
        """Verify each category has at least 10 benchmarks."""
        runner = BenchmarkRunner()
        runner.register_all_benchmarks()

        for category in ["iteration", "string", "array", "memory"]:
            category_benchmarks = runner.list_benchmarks(category=category)
            assert len(category_benchmarks) >= 10, \
                f"Category {category} has {len(category_benchmarks)} benchmarks, expected >=10"

    def test_all_benchmarks_enabled(self):
        """Verify all benchmarks are enabled by default."""
        runner = BenchmarkRunner()
        runner.register_all_benchmarks()

        benchmarks = runner.list_benchmarks()
        enabled_count = sum(1 for b in benchmarks if b["enabled"])

        assert enabled_count == len(benchmarks), \
            f"All benchmarks should be enabled by default. {enabled_count}/{len(benchmarks)} enabled"

    def test_all_benchmarks_have_requirements(self):
        """Verify all benchmarks are linked to requirements."""
        runner = BenchmarkRunner()
        runner.register_all_benchmarks()

        benchmarks = runner.list_benchmarks()

        for bench in benchmarks:
            assert "requirementId" in bench
            assert bench["requirementId"].startswith("FR-ES24-D-")
            # Should be one of the 4 optimization requirements
            assert bench["requirementId"] in [
                "FR-ES24-D-018",  # Iteration
                "FR-ES24-D-019",  # String
                "FR-ES24-D-020",  # Array
                "FR-ES24-D-021"   # Memory
            ]


class TestPerformanceTargetVerification:
    """Test overall performance target verification."""

    def test_all_targets_verification(self):
        """Verify all 4 performance targets can be checked together."""
        # Run all optimizations
        iter_opt = IterationOptimizer()
        str_opt = StringOptimizer()
        arr_opt = ArrayOptimizer()
        mem_opt = MemoryOptimizer()

        iter_result = iter_opt.apply_optimizations()
        str_result = str_opt.apply_optimizations()
        arr_result = arr_opt.apply_optimizations()
        mem_result = mem_opt.apply_optimizations()

        # All should meet targets
        assert iter_result["targetMet"] is True, "Iteration target not met"
        assert str_result["targetMet"] is True, "String target not met"
        assert arr_result["targetMet"] is True, "Array target not met"
        assert mem_result["targetMet"] is True, "Memory target not met"

        # Calculate overall success
        all_targets_met = (
            iter_result["targetMet"] and
            str_result["targetMet"] and
            arr_result["targetMet"] and
            mem_result["targetMet"]
        )

        assert all_targets_met is True, "Not all performance targets met"

    def test_performance_improvements_documented(self):
        """Verify all optimizations are documented with metrics."""
        optimizers = [
            IterationOptimizer(),
            StringOptimizer(),
            ArrayOptimizer(),
            MemoryOptimizer()
        ]

        for optimizer in optimizers:
            result = optimizer.apply_optimizations()

            # Each optimization should have documentation
            for opt in result["optimizations"]:
                assert "name" in opt
                assert "description" in opt
                assert "applied" in opt
                assert "impact" in opt
                assert opt["impact"] in ["low", "medium", "high"]

    def test_regression_prevention(self):
        """Verify optimizations don't cause performance regressions."""
        runner = BenchmarkRunner()

        # Register all benchmarks
        runner.register_all_benchmarks()

        # Run a sample of benchmarks
        categories = ["iteration", "string", "array"]
        for category in categories:
            result = runner.run_category(category, iterations=50, warmup_iterations=10)

            # All benchmarks should complete successfully
            assert result["summary"]["failedBenchmarks"] == 0, \
                f"Category {category} has failing benchmarks"

            # Should have reasonable performance
            assert result["summary"]["averageOpsPerSecond"] > 0, \
                f"Category {category} has zero ops/sec"
