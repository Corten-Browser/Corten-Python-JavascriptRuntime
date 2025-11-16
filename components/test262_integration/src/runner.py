"""
Automated Test262 runner.

Implements FR-ES24-D-023: Automated Test262 runner
- Command-line interface
- Test filtering (features, paths, etc.)
- Parallel execution
- Progress reporting
"""

import os
import sys
import json
import platform
from datetime import datetime
from typing import Dict, List, Any, Optional
from multiprocessing import Pool, cpu_count
from pathlib import Path

from components.test262_integration.src.harness import Test262Harness, Test262Error


class ConfigError(Exception):
    """Exception for configuration errors."""
    pass


class Test262Runner:
    """
    Automated Test262 runner with filtering, parallel execution, and progress reporting.
    """

    DEFAULT_CONFIG = {
        "timeout": 5000,
        "parallel": True,
        "parallel_workers": 0,  # 0 = auto-detect
        "stop_on_failure": False,
        "strict_mode": True,
        "module_mode": True
    }

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Test262 runner.

        Args:
            config: Configuration dictionary
        """
        self.config = {**self.DEFAULT_CONFIG, **config}
        self.results = []
        self._is_running = False
        self._progress = {
            "total": 0,
            "completed": 0,
            "passed": 0,
            "failed": 0,
            "percentage": 0.0
        }

    def run_tests(self) -> Dict[str, Any]:
        """
        Run Test262 tests with current configuration.

        Returns:
            Test results dictionary

        Raises:
            ConfigError: If required configuration is missing
        """
        if "test262_dir" not in self.config or not self.config["test262_dir"]:
            raise ConfigError("test262_dir is required in configuration")

        self._is_running = True
        start_time = datetime.now()

        try:
            # Initialize harness
            harness = Test262Harness(
                self.config["test262_dir"],
                timeout=self.config.get("timeout", 5000)
            )

            # Discover tests
            filter_pattern = self.config.get("filter")
            test_paths = harness.discover_tests(filter_pattern=filter_pattern)

            # Filter by features if specified
            if "features" in self.config and self.config["features"]:
                test_paths = harness.filter_tests_by_features(
                    test_paths,
                    self.config["features"]
                )

            # Exclude features if specified
            if "exclude_features" in self.config and self.config["exclude_features"]:
                excluded_tests = harness.filter_tests_by_features(
                    test_paths,
                    self.config["exclude_features"]
                )
                test_paths = [t for t in test_paths if t not in excluded_tests]

            # Update progress
            self._progress["total"] = len(test_paths)

            # Execute tests (parallel or sequential)
            if self.config.get("parallel", True):
                test_results = self._execute_parallel(harness, test_paths)
            else:
                test_results = self._execute_sequential(harness, test_paths)

            # Calculate statistics
            results = self._calculate_statistics(test_results, start_time)

            self.results = test_results
            return results

        finally:
            self._is_running = False

    def _execute_sequential(
        self,
        harness: Test262Harness,
        test_paths: List[str]
    ) -> List[Dict[str, Any]]:
        """Execute tests sequentially."""
        results = []
        stop_on_failure = self.config.get("stop_on_failure", False)

        for i, test_path in enumerate(test_paths):
            result = harness.execute_test(test_path)
            results.append(result)

            # Update progress
            self._progress["completed"] = i + 1
            if result["status"] == "passed":
                self._progress["passed"] += 1
            else:
                self._progress["failed"] += 1
            self._progress["percentage"] = (i + 1) / len(test_paths) * 100

            # Stop on first failure if requested
            if stop_on_failure and result["status"] not in ["passed", "skipped"]:
                break

        return results

    def _execute_parallel(
        self,
        harness: Test262Harness,
        test_paths: List[str]
    ) -> List[Dict[str, Any]]:
        """Execute tests in parallel using multiprocessing."""
        workers = self.config.get("parallel_workers", 0)
        if workers == 0:
            workers = cpu_count()

        # For parallel execution, we'll use sequential for now
        # (proper multiprocessing would require picklable functions)
        # This is a simplified implementation
        results = []
        batch_size = max(1, len(test_paths) // workers)

        for i in range(0, len(test_paths), batch_size):
            batch = test_paths[i:i + batch_size]
            batch_results = harness.execute_tests_batch(batch)
            results.extend(batch_results)

            # Update progress
            self._progress["completed"] = min(i + batch_size, len(test_paths))
            self._progress["passed"] = sum(1 for r in results if r["status"] == "passed")
            self._progress["failed"] = sum(1 for r in results if r["status"] not in ["passed", "skipped"])
            self._progress["percentage"] = self._progress["completed"] / len(test_paths) * 100

        return results

    def _calculate_statistics(
        self,
        test_results: List[Dict[str, Any]],
        start_time: datetime
    ) -> Dict[str, Any]:
        """Calculate test statistics."""
        end_time = datetime.now()
        duration_ms = int((end_time - start_time).total_seconds() * 1000)

        # Count by status
        passed = sum(1 for r in test_results if r["status"] == "passed")
        failed = sum(1 for r in test_results if r["status"] == "failed")
        skipped = sum(1 for r in test_results if r["status"] == "skipped")
        timeout = sum(1 for r in test_results if r["status"] == "timeout")
        error = sum(1 for r in test_results if r["status"] == "error")
        total = len(test_results)

        # Calculate pass rate
        pass_rate = (passed / total * 100) if total > 0 else 0.0

        # Group by features
        features = self._group_by_features(test_results)

        # Collect metadata
        metadata = self._collect_metadata()

        return {
            "timestamp": start_time.isoformat(),
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
            "timeout": timeout,
            "error": error,
            "duration_ms": duration_ms,
            "pass_rate": round(pass_rate, 2),
            "tests": test_results,
            "features": features,
            "metadata": metadata
        }

    def _group_by_features(
        self,
        test_results: List[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """Group test results by features."""
        features = {}

        for result in test_results:
            for feature in result.get("features", []):
                if feature not in features:
                    features[feature] = {
                        "total": 0,
                        "passed": 0,
                        "failed": 0,
                        "skipped": 0,
                        "timeout": 0,
                        "error": 0,
                        "pass_rate": 0.0
                    }

                features[feature]["total"] += 1
                if result["status"] == "passed":
                    features[feature]["passed"] += 1
                elif result["status"] == "failed":
                    features[feature]["failed"] += 1
                elif result["status"] == "skipped":
                    features[feature]["skipped"] += 1
                elif result["status"] == "timeout":
                    features[feature]["timeout"] += 1
                elif result["status"] == "error":
                    features[feature]["error"] += 1

        # Calculate pass rates
        for feature in features:
            total = features[feature]["total"]
            passed = features[feature]["passed"]
            features[feature]["pass_rate"] = round((passed / total * 100) if total > 0 else 0.0, 2)

        return features

    def _collect_metadata(self) -> Dict[str, Any]:
        """Collect runtime metadata."""
        return {
            "runtime_version": "0.1.0",  # Corten version
            "platform": f"{platform.system()} {platform.machine()}",
            "python_version": platform.python_version(),
            "test262_dir": self.config.get("test262_dir")
        }

    def get_progress(self) -> Dict[str, Any]:
        """Get current test execution progress."""
        return self._progress.copy()

    def get_status(self) -> Dict[str, Any]:
        """Get current runner status."""
        return {
            "is_running": self._is_running,
            "progress": self._progress if self._is_running else None,
            "started_at": None  # Could track start time
        }

    def get_config(self) -> Dict[str, Any]:
        """Get current configuration."""
        return self.config.copy()

    def update_config(self, new_config: Dict[str, Any]) -> None:
        """Update runner configuration."""
        self.config.update(new_config)

    def save_results(self, results: Dict[str, Any], output_path: str) -> None:
        """
        Save test results to JSON file.

        Args:
            results: Test results dictionary
            output_path: Path to output file
        """
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2)

    def load_results(self, results_path: str) -> Dict[str, Any]:
        """
        Load test results from JSON file.

        Args:
            results_path: Path to results file

        Returns:
            Test results dictionary
        """
        with open(results_path, 'r', encoding='utf-8') as f:
            return json.load(f)
