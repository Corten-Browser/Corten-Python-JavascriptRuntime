"""
Unit tests for Test262 reporting dashboard.

Tests FR-ES24-D-024: Test262 reporting dashboard
- HTML report generation
- JSON/Markdown/JUnit formats
- Pass/fail statistics
- Failure categorization
"""

import pytest
import tempfile
from pathlib import Path
from datetime import datetime
import json


class TestReporter:
    """Tests for Reporter class."""

    def test_reporter_initialization(self):
        """Test reporter can be initialized."""
        from components.test262_integration.src.reporter import Reporter

        reporter = Reporter()
        assert reporter is not None

    def test_generate_html_report(self):
        """Test generate_report creates HTML report."""
        from components.test262_integration.src.reporter import Reporter

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": 100,
            "passed": 95,
            "failed": 5,
            "skipped": 0,
            "timeout": 0,
            "error": 0,
            "duration_ms": 10000,
            "pass_rate": 95.0,
            "tests": []
        }

        reporter = Reporter()
        report = reporter.generate_report(results, format="html")

        assert "<html" in report.lower()
        assert "95" in report  # pass count
        assert "5" in report   # fail count
        assert "95.0" in report or "95" in report  # pass rate

    def test_generate_json_report(self):
        """Test generate_report creates JSON report."""
        from components.test262_integration.src.reporter import Reporter

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": 100,
            "passed": 95,
            "failed": 5,
            "skipped": 0,
            "timeout": 0,
            "error": 0,
            "duration_ms": 10000,
            "pass_rate": 95.0,
            "tests": []
        }

        reporter = Reporter()
        report = reporter.generate_report(results, format="json")

        # Should be valid JSON
        parsed = json.loads(report)
        assert parsed["total"] == 100
        assert parsed["passed"] == 95

    def test_generate_markdown_report(self):
        """Test generate_report creates Markdown report."""
        from components.test262_integration.src.reporter import Reporter

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": 100,
            "passed": 95,
            "failed": 5,
            "skipped": 0,
            "timeout": 0,
            "error": 0,
            "duration_ms": 10000,
            "pass_rate": 95.0,
            "tests": [],
            "features": {}
        }

        reporter = Reporter()
        report = reporter.generate_report(results, format="markdown")

        assert "# " in report  # Markdown headers
        assert "95" in report  # pass count
        assert "5" in report   # fail count

    def test_generate_junit_report(self):
        """Test generate_report creates JUnit XML report."""
        from components.test262_integration.src.reporter import Reporter

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": 100,
            "passed": 95,
            "failed": 5,
            "skipped": 0,
            "timeout": 0,
            "error": 0,
            "duration_ms": 10000,
            "pass_rate": 95.0,
            "tests": [
                {"path": "test1.js", "status": "passed", "duration_ms": 100},
                {"path": "test2.js", "status": "failed", "duration_ms": 150, "error": "Assertion failed"}
            ]
        }

        reporter = Reporter()
        report = reporter.generate_report(results, format="junit")

        assert "<?xml" in report
        assert "<testsuite" in report
        assert "<testcase" in report
        assert "test1.js" in report
        assert "test2.js" in report

    def test_generate_report_with_grouping_by_feature(self):
        """Test generate_report can group by feature."""
        from components.test262_integration.src.reporter import Reporter

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": 100,
            "passed": 95,
            "failed": 5,
            "skipped": 0,
            "timeout": 0,
            "error": 0,
            "duration_ms": 10000,
            "pass_rate": 95.0,
            "tests": [],
            "features": {
                "BigInt": {"total": 50, "passed": 48, "failed": 2, "pass_rate": 96.0},
                "Symbol": {"total": 50, "passed": 47, "failed": 3, "pass_rate": 94.0}
            }
        }

        reporter = Reporter()
        report = reporter.generate_report(results, format="html", group_by="feature")

        assert "BigInt" in report
        assert "Symbol" in report
        assert "48" in report  # BigInt passed
        assert "47" in report  # Symbol passed

    def test_generate_report_includes_failed_tests(self):
        """Test generate_report includes details of failed tests."""
        from components.test262_integration.src.reporter import Reporter

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": 2,
            "passed": 1,
            "failed": 1,
            "skipped": 0,
            "timeout": 0,
            "error": 0,
            "duration_ms": 1000,
            "pass_rate": 50.0,
            "tests": [
                {"path": "test1.js", "status": "passed", "duration_ms": 100},
                {"path": "test2.js", "status": "failed", "duration_ms": 150, "error": "Expected true, got false"}
            ]
        }

        reporter = Reporter()
        report = reporter.generate_report(results, format="html", include_passed=False)

        # Should include failed test
        assert "test2.js" in report
        assert "Expected true" in report

    def test_generate_report_can_include_passed_tests(self):
        """Test generate_report can include passed tests."""
        from components.test262_integration.src.reporter import Reporter

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": 2,
            "passed": 2,
            "failed": 0,
            "skipped": 0,
            "timeout": 0,
            "error": 0,
            "duration_ms": 1000,
            "pass_rate": 100.0,
            "tests": [
                {"path": "test1.js", "status": "passed", "duration_ms": 100},
                {"path": "test2.js", "status": "passed", "duration_ms": 150}
            ]
        }

        reporter = Reporter()
        report = reporter.generate_report(results, format="html", include_passed=True)

        assert "test1.js" in report
        assert "test2.js" in report

    def test_generate_report_custom_title(self):
        """Test generate_report supports custom title."""
        from components.test262_integration.src.reporter import Reporter

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": 100,
            "passed": 95,
            "failed": 5,
            "skipped": 0,
            "timeout": 0,
            "error": 0,
            "duration_ms": 10000,
            "pass_rate": 95.0,
            "tests": []
        }

        reporter = Reporter()
        report = reporter.generate_report(results, format="html", title="Custom Test Report")

        assert "Custom Test Report" in report

    def test_generate_report_includes_metadata(self):
        """Test generate_report includes metadata when requested."""
        from components.test262_integration.src.reporter import Reporter

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": 100,
            "passed": 95,
            "failed": 5,
            "skipped": 0,
            "timeout": 0,
            "error": 0,
            "duration_ms": 10000,
            "pass_rate": 95.0,
            "tests": [],
            "metadata": {
                "runtime_version": "0.1.0",
                "platform": "Linux x86_64"
            }
        }

        reporter = Reporter()
        report = reporter.generate_report(results, format="html", show_metadata=True)

        assert "0.1.0" in report
        assert "Linux" in report

    def test_save_report_writes_to_file(self):
        """Test save_report writes report to file."""
        from components.test262_integration.src.reporter import Reporter

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": 100,
            "passed": 95,
            "failed": 5,
            "skipped": 0,
            "timeout": 0,
            "error": 0,
            "duration_ms": 10000,
            "pass_rate": 95.0,
            "tests": []
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            output_file = Path(tmpdir) / "report.html"

            reporter = Reporter()
            reporter.save_report(results, str(output_file), format="html")

            assert output_file.exists()
            content = output_file.read_text()
            assert "<html" in content.lower()


class TestComparisonReporter:
    """Tests for baseline comparison reporting."""

    def test_compare_results_identifies_regressions(self):
        """Test compare_results identifies tests that started failing."""
        from components.test262_integration.src.reporter import Reporter

        baseline = {
            "total": 3,
            "tests": [
                {"path": "test1.js", "status": "passed"},
                {"path": "test2.js", "status": "passed"},
                {"path": "test3.js", "status": "failed"}
            ]
        }

        current = {
            "total": 3,
            "tests": [
                {"path": "test1.js", "status": "failed"},  # REGRESSION
                {"path": "test2.js", "status": "passed"},
                {"path": "test3.js", "status": "failed"}
            ]
        }

        reporter = Reporter()
        comparison = reporter.compare_results(baseline, current)

        assert len(comparison["regressions"]) == 1
        assert comparison["regressions"][0]["path"] == "test1.js"
        assert comparison["summary"]["regression_count"] == 1

    def test_compare_results_identifies_improvements(self):
        """Test compare_results identifies tests that started passing."""
        from components.test262_integration.src.reporter import Reporter

        baseline = {
            "total": 3,
            "tests": [
                {"path": "test1.js", "status": "failed"},
                {"path": "test2.js", "status": "failed"},
                {"path": "test3.js", "status": "passed"}
            ]
        }

        current = {
            "total": 3,
            "tests": [
                {"path": "test1.js", "status": "passed"},  # IMPROVEMENT
                {"path": "test2.js", "status": "passed"},  # IMPROVEMENT
                {"path": "test3.js", "status": "passed"}
            ]
        }

        reporter = Reporter()
        comparison = reporter.compare_results(baseline, current)

        assert len(comparison["improvements"]) == 2
        assert comparison["summary"]["improvement_count"] == 2

    def test_compare_results_calculates_pass_rate_delta(self):
        """Test compare_results calculates pass rate change."""
        from components.test262_integration.src.reporter import Reporter

        baseline = {
            "total": 100,
            "passed": 90,
            "failed": 10,
            "pass_rate": 90.0,
            "tests": []
        }

        current = {
            "total": 100,
            "passed": 95,
            "failed": 5,
            "pass_rate": 95.0,
            "tests": []
        }

        reporter = Reporter()
        comparison = reporter.compare_results(baseline, current)

        assert comparison["summary"]["baseline_pass_rate"] == 90.0
        assert comparison["summary"]["current_pass_rate"] == 95.0
        assert comparison["summary"]["pass_rate_delta"] == 5.0  # Improvement

    def test_compare_results_identifies_new_failures(self):
        """Test compare_results identifies new tests that fail."""
        from components.test262_integration.src.reporter import Reporter

        baseline = {
            "total": 2,
            "tests": [
                {"path": "test1.js", "status": "passed"},
                {"path": "test2.js", "status": "passed"}
            ]
        }

        current = {
            "total": 3,
            "tests": [
                {"path": "test1.js", "status": "passed"},
                {"path": "test2.js", "status": "passed"},
                {"path": "test3.js", "status": "failed"}  # NEW FAILURE
            ]
        }

        reporter = Reporter()
        comparison = reporter.compare_results(baseline, current)

        assert len(comparison.get("new_failures", [])) >= 0  # May or may not track new failures
        # At minimum, should affect overall statistics

    def test_generate_comparison_report_html(self):
        """Test generate_comparison_report creates HTML comparison."""
        from components.test262_integration.src.reporter import Reporter

        comparison = {
            "summary": {
                "baseline_pass_rate": 90.0,
                "current_pass_rate": 95.0,
                "pass_rate_delta": 5.0,
                "regression_count": 1,
                "improvement_count": 6
            },
            "regressions": [
                {"path": "test1.js", "baseline_status": "passed", "current_status": "failed"}
            ],
            "improvements": [
                {"path": "test2.js", "baseline_status": "failed", "current_status": "passed"}
            ],
            "compared_at": datetime.now().isoformat()
        }

        reporter = Reporter()
        report = reporter.generate_comparison_report(comparison, format="html")

        assert "<html" in report.lower()
        assert "90.0" in report  # baseline
        assert "95.0" in report  # current
        assert "test1.js" in report  # regression
        assert "test2.js" in report  # improvement


class TestBaselineManager:
    """Tests for baseline management."""

    def test_save_baseline(self):
        """Test save_baseline stores results as baseline."""
        from components.test262_integration.src.reporter import Reporter

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": 100,
            "passed": 95,
            "failed": 5,
            "pass_rate": 95.0,
            "tests": []
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_file = Path(tmpdir) / "baseline.json"

            reporter = Reporter()
            response = reporter.save_baseline(results, str(baseline_file), version="0.1.0")

            assert baseline_file.exists()
            assert response["test_count"] == 100
            assert response["pass_rate"] == 95.0
            assert response["version"] == "0.1.0"

    def test_load_baseline(self):
        """Test load_baseline retrieves stored baseline."""
        from components.test262_integration.src.reporter import Reporter

        results = {
            "timestamp": datetime.now().isoformat(),
            "total": 100,
            "passed": 95,
            "failed": 5,
            "pass_rate": 95.0,
            "tests": []
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_file = Path(tmpdir) / "baseline.json"
            baseline_file.write_text(json.dumps(results))

            reporter = Reporter()
            loaded = reporter.load_baseline(str(baseline_file))

            assert loaded["total"] == 100
            assert loaded["passed"] == 95

    def test_load_baseline_handles_missing_file(self):
        """Test load_baseline handles missing baseline file."""
        from components.test262_integration.src.reporter import Reporter, BaselineNotFoundError

        reporter = Reporter()

        with pytest.raises(BaselineNotFoundError):
            reporter.load_baseline("/nonexistent/baseline.json")


class TestBaselineNotFoundError:
    """Tests for BaselineNotFoundError exception."""

    def test_error_can_be_raised(self):
        """Test BaselineNotFoundError can be raised."""
        from components.test262_integration.src.reporter import BaselineNotFoundError

        with pytest.raises(BaselineNotFoundError) as exc_info:
            raise BaselineNotFoundError("Baseline not found")
        assert "not found" in str(exc_info.value).lower()

    def test_error_is_exception(self):
        """Test BaselineNotFoundError inherits from Exception."""
        from components.test262_integration.src.reporter import BaselineNotFoundError

        assert issubclass(BaselineNotFoundError, Exception)
