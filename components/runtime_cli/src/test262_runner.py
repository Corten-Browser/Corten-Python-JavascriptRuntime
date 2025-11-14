"""Test262 conformance test runner."""

import os
import time
from dataclasses import dataclass
from typing import Optional

from components.runtime_cli.src.execute import ExecuteFile
from components.runtime_cli.src.cli_options import CLIOptions


@dataclass
class TestResult:
    """
    Single Test262 test result.

    Attributes:
        test_path: Path to the test file
        passed: Whether the test passed
        expected_error: Expected error type from test metadata (if any)
        actual_error: Actual error message if test failed
        duration_ms: Test execution time in milliseconds
    """

    test_path: str
    passed: bool
    expected_error: Optional[str] = None
    actual_error: Optional[str] = None
    duration_ms: float = 0.0


class TestResults:
    """
    Aggregated Test262 test results.

    Tracks overall test statistics and provides summary methods.

    Attributes:
        tests_run: Total number of tests executed
        tests_passed: Number of tests that passed
        tests_failed: Number of tests that failed
        duration_ms: Total execution time in milliseconds
    """

    def __init__(self):
        """Initialize empty test results."""
        self.tests_run: int = 0
        self.tests_passed: int = 0
        self.tests_failed: int = 0
        self.duration_ms: float = 0.0

    def pass_rate(self) -> float:
        """
        Calculate pass rate percentage.

        Returns:
            Pass rate as percentage (0-100). Returns 0.0 if no tests run.
        """
        if self.tests_run == 0:
            return 0.0
        return (self.tests_passed / self.tests_run) * 100.0

    def print_summary(self) -> None:
        """Print test summary to stdout."""
        print(f"\nTest262 Results:")
        print(f"  Tests run: {self.tests_run}")
        print(f"  Passed: {self.tests_passed}")
        print(f"  Failed: {self.tests_failed}")
        print(f"  Pass rate: {self.pass_rate():.1f}%")
        print(f"  Duration: {self.duration_ms:.2f} ms")


class Test262Runner:
    """
    Test262 conformance test runner.

    Executes Test262 JavaScript conformance tests and reports results.

    Attributes:
        test262_root: Path to Test262 repository root directory

    Example:
        >>> runner = Test262Runner("/path/to/test262")
        >>> result = runner.run_test("test/language/expressions/addition/S11.6.1_A1.js")
        >>> result.passed
        True
        >>> results = runner.run_directory("test/language/expressions/addition")
        >>> results.pass_rate()
        95.5
    """

    def __init__(self, test262_root: str):
        """
        Initialize Test262 runner.

        Args:
            test262_root: Path to Test262 repository root directory

        Raises:
            ValueError: If test262_root doesn't exist or isn't a directory
        """
        if not os.path.isdir(test262_root):
            raise ValueError(f"Test262 root directory not found: {test262_root}")

        self.test262_root = test262_root

    def run_test(self, test_path: str) -> TestResult:
        """
        Run single Test262 test.

        Args:
            test_path: Path to test file (relative to test262_root or absolute)

        Returns:
            TestResult with test outcome

        Example:
            >>> runner = Test262Runner("/path/to/test262")
            >>> result = runner.run_test("test/language/expressions/addition/basic.js")
            >>> result.passed
            True
        """
        # Resolve path
        if not os.path.isabs(test_path):
            full_path = os.path.join(self.test262_root, test_path)
        else:
            full_path = test_path

        # Check if test file exists
        if not os.path.isfile(full_path):
            return TestResult(
                test_path=test_path,
                passed=False,
                actual_error=f"Test file not found: {full_path}",
                duration_ms=0.0,
            )

        # Create options for test execution
        options = CLIOptions(
            mode="file",
            filename=full_path,
            verbose=False,
            dump_bytecode=False,
            dump_ast=False,
        )

        # Execute test
        start_time = time.time()
        try:
            result = ExecuteFile(full_path, options)
            duration_ms = (time.time() - start_time) * 1000.0

            # Determine if test passed
            # For now, a test passes if execution succeeded
            # TODO: Parse test262 metadata to check for expected errors
            if result.is_success():
                return TestResult(
                    test_path=test_path, passed=True, duration_ms=duration_ms
                )
            else:
                return TestResult(
                    test_path=test_path,
                    passed=False,
                    actual_error=str(result.exception),
                    duration_ms=duration_ms,
                )

        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000.0
            return TestResult(
                test_path=test_path,
                passed=False,
                actual_error=str(e),
                duration_ms=duration_ms,
            )

    def run_directory(self, directory: str) -> TestResults:
        """
        Run all Test262 tests in directory recursively.

        Args:
            directory: Directory path (relative to test262_root or absolute)

        Returns:
            TestResults with aggregated results

        Example:
            >>> runner = Test262Runner("/path/to/test262")
            >>> results = runner.run_directory("test/language/expressions")
            >>> results.pass_rate()
            87.3
        """
        # Resolve directory path
        if not os.path.isabs(directory):
            full_dir = os.path.join(self.test262_root, directory)
        else:
            full_dir = directory

        results = TestResults()

        # Walk directory tree
        for root, dirs, files in os.walk(full_dir):
            for file in files:
                # Only process .js files
                if not file.endswith(".js"):
                    continue

                # Skip non-test files
                if file.startswith("_"):
                    continue

                test_path = os.path.join(root, file)

                # Run test
                result = self.run_test(test_path)

                # Update statistics
                results.tests_run += 1
                results.duration_ms += result.duration_ms

                if result.passed:
                    results.tests_passed += 1
                else:
                    results.tests_failed += 1

        return results
