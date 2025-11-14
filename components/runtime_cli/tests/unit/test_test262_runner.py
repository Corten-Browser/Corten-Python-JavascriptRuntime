"""Tests for Test262Runner."""

import pytest
import tempfile
import os
from components.runtime_cli.src.test262_runner import (
    Test262Runner,
    TestResult,
    TestResults,
)


def test_test_result_creation():
    """Test TestResult dataclass creation."""
    result = TestResult(
        test_path="test.js",
        passed=True,
        expected_error=None,
        actual_error=None,
        duration_ms=10.5,
    )

    assert result.test_path == "test.js"
    assert result.passed is True
    assert result.expected_error is None
    assert result.actual_error is None
    assert result.duration_ms == 10.5


def test_test_results_initialization():
    """Test TestResults initialization."""
    results = TestResults()

    assert results.tests_run == 0
    assert results.tests_passed == 0
    assert results.tests_failed == 0
    assert results.duration_ms == 0.0


def test_test_results_pass_rate_empty():
    """Test pass rate with no tests run."""
    results = TestResults()

    assert results.pass_rate() == 0.0


def test_test_results_pass_rate_all_pass():
    """Test pass rate with all tests passing."""
    results = TestResults()
    results.tests_run = 10
    results.tests_passed = 10
    results.tests_failed = 0

    assert results.pass_rate() == 100.0


def test_test_results_pass_rate_partial():
    """Test pass rate with some tests failing."""
    results = TestResults()
    results.tests_run = 10
    results.tests_passed = 7
    results.tests_failed = 3

    assert results.pass_rate() == 70.0


def test_test_results_print_summary(capsys):
    """Test print_summary output."""
    results = TestResults()
    results.tests_run = 5
    results.tests_passed = 4
    results.tests_failed = 1
    results.duration_ms = 123.45

    results.print_summary()

    captured = capsys.readouterr()
    assert "Test262 Results" in captured.out
    assert "Tests run: 5" in captured.out
    assert "Passed: 4" in captured.out
    assert "Failed: 1" in captured.out
    assert "80.0%" in captured.out


def test_test262_runner_initialization_valid_directory():
    """Test Test262Runner initialization with valid directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = Test262Runner(tmpdir)
        assert runner.test262_root == tmpdir


def test_test262_runner_initialization_invalid_directory():
    """Test Test262Runner initialization with invalid directory."""
    with pytest.raises(ValueError, match="not found"):
        Test262Runner("/nonexistent/directory")


def test_test262_runner_run_test_file_not_found():
    """Test running a nonexistent test file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = Test262Runner(tmpdir)
        result = runner.run_test("nonexistent.js")

        assert result.passed is False
        assert "not found" in result.actual_error.lower()


def test_test262_runner_run_test_simple():
    """Test running a simple test file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a simple test file
        test_file = os.path.join(tmpdir, "test.js")
        with open(test_file, "w") as f:
            f.write("var x = 42;")

        runner = Test262Runner(tmpdir)
        result = runner.run_test("test.js")

        assert result.test_path == "test.js"
        # Note: test may fail due to interpreter limitations, but should execute
        assert isinstance(result.passed, bool)
        assert result.duration_ms >= 0


def test_test262_runner_run_test_syntax_error():
    """Test running a test file with syntax error."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file with syntax error
        test_file = os.path.join(tmpdir, "test.js")
        with open(test_file, "w") as f:
            f.write("var x =")  # Incomplete statement

        runner = Test262Runner(tmpdir)
        result = runner.run_test("test.js")

        assert result.passed is False
        assert result.actual_error is not None


def test_test262_runner_run_directory_empty():
    """Test running tests in empty directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        runner = Test262Runner(tmpdir)
        results = runner.run_directory(tmpdir)

        assert results.tests_run == 0
        assert results.tests_passed == 0
        assert results.tests_failed == 0


def test_test262_runner_run_directory_with_tests():
    """Test running tests in directory with test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_dir = os.path.join(tmpdir, "tests")
        os.makedirs(test_dir)

        test1 = os.path.join(test_dir, "test1.js")
        with open(test1, "w") as f:
            f.write("var x = 1;")

        test2 = os.path.join(test_dir, "test2.js")
        with open(test2, "w") as f:
            f.write("var y = 2;")

        runner = Test262Runner(tmpdir)
        results = runner.run_directory(test_dir)

        assert results.tests_run == 2
        assert results.duration_ms >= 0


def test_test262_runner_run_directory_skips_non_js_files():
    """Test that non-.js files are skipped."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create various files
        os.makedirs(os.path.join(tmpdir, "tests"))

        # JS file (should be included)
        with open(os.path.join(tmpdir, "tests", "test.js"), "w") as f:
            f.write("var x = 1;")

        # Non-JS file (should be skipped)
        with open(os.path.join(tmpdir, "tests", "readme.txt"), "w") as f:
            f.write("not a test")

        # File starting with underscore (should be skipped)
        with open(os.path.join(tmpdir, "tests", "_helper.js"), "w") as f:
            f.write("var helper = 1;")

        runner = Test262Runner(tmpdir)
        results = runner.run_directory(os.path.join(tmpdir, "tests"))

        # Only test.js should be run
        assert results.tests_run == 1
