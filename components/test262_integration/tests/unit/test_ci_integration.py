"""
Unit tests for CI/CD integration preparation.

Tests FR-ES24-D-025: CI/CD integration preparation
- GitHub Actions workflow template
- Baseline management
- Regression detection
- Exit codes for CI
"""

import pytest
import tempfile
from pathlib import Path
import json


class TestCIIntegration:
    """Tests for CI integration utilities."""

    def test_create_github_actions_workflow(self):
        """Test create_github_actions_workflow generates workflow YAML."""
        from components.test262_integration.src.ci_integration import create_github_actions_workflow

        workflow = create_github_actions_workflow()

        assert "name:" in workflow
        assert "on:" in workflow
        assert "jobs:" in workflow
        assert "test262" in workflow.lower()

    def test_github_actions_workflow_includes_checkout(self):
        """Test workflow includes repository checkout."""
        from components.test262_integration.src.ci_integration import create_github_actions_workflow

        workflow = create_github_actions_workflow()

        assert "actions/checkout" in workflow

    def test_github_actions_workflow_includes_python_setup(self):
        """Test workflow includes Python setup."""
        from components.test262_integration.src.ci_integration import create_github_actions_workflow

        workflow = create_github_actions_workflow()

        assert "actions/setup-python" in workflow or "python" in workflow.lower()

    def test_github_actions_workflow_includes_test262_checkout(self):
        """Test workflow includes Test262 repository checkout."""
        from components.test262_integration.src.ci_integration import create_github_actions_workflow

        workflow = create_github_actions_workflow()

        assert "test262" in workflow.lower()

    def test_github_actions_workflow_runs_tests(self):
        """Test workflow includes test execution step."""
        from components.test262_integration.src.ci_integration import create_github_actions_workflow

        workflow = create_github_actions_workflow()

        assert "run:" in workflow or "script:" in workflow

    def test_github_actions_workflow_uploads_artifacts(self):
        """Test workflow uploads test reports as artifacts."""
        from components.test262_integration.src.ci_integration import create_github_actions_workflow

        workflow = create_github_actions_workflow()

        assert "actions/upload-artifact" in workflow or "artifact" in workflow.lower()

    def test_save_workflow_writes_to_file(self):
        """Test save_workflow writes workflow to .github/workflows/."""
        from components.test262_integration.src.ci_integration import save_workflow

        with tempfile.TemporaryDirectory() as tmpdir:
            workflows_dir = Path(tmpdir) / ".github" / "workflows"
            workflows_dir.mkdir(parents=True)

            workflow_file = workflows_dir / "test262.yml"
            save_workflow(str(workflow_file))

            assert workflow_file.exists()
            content = workflow_file.read_text()
            assert "name:" in content


class TestRegressionDetection:
    """Tests for regression detection in CI."""

    def test_detect_regressions_returns_exit_code(self):
        """Test detect_regressions returns proper exit code for CI."""
        from components.test262_integration.src.ci_integration import detect_regressions

        baseline = {
            "total": 100,
            "passed": 95,
            "tests": [{"path": "test1.js", "status": "passed"}]
        }

        current = {
            "total": 100,
            "passed": 94,
            "tests": [{"path": "test1.js", "status": "failed"}]  # Regression
        }

        exit_code = detect_regressions(baseline, current)

        # Should return non-zero exit code when regressions found
        assert exit_code != 0

    def test_detect_regressions_passes_without_regressions(self):
        """Test detect_regressions returns 0 when no regressions."""
        from components.test262_integration.src.ci_integration import detect_regressions

        baseline = {
            "total": 100,
            "passed": 95,
            "tests": [{"path": "test1.js", "status": "passed"}]
        }

        current = {
            "total": 100,
            "passed": 96,
            "tests": [{"path": "test1.js", "status": "passed"}]  # No regression
        }

        exit_code = detect_regressions(baseline, current)

        # Should return 0 when no regressions
        assert exit_code == 0

    def test_detect_regressions_allows_tolerance(self):
        """Test detect_regressions can allow tolerance for minor regressions."""
        from components.test262_integration.src.ci_integration import detect_regressions

        baseline = {
            "total": 1000,
            "passed": 950,
            "tests": []
        }

        current = {
            "total": 1000,
            "passed": 949,  # 1 test regression out of 1000
            "tests": []
        }

        # With tolerance of 0.5%, should pass
        exit_code = detect_regressions(baseline, current, tolerance=0.5)
        assert exit_code == 0

        # Without tolerance, should fail
        exit_code = detect_regressions(baseline, current, tolerance=0.0)
        assert exit_code != 0

    def test_detect_regressions_generates_report(self):
        """Test detect_regressions can generate regression report."""
        from components.test262_integration.src.ci_integration import detect_regressions

        baseline = {
            "total": 3,
            "passed": 2,
            "tests": [
                {"path": "test1.js", "status": "passed"},
                {"path": "test2.js", "status": "passed"},
                {"path": "test3.js", "status": "failed"}
            ]
        }

        current = {
            "total": 3,
            "passed": 1,
            "tests": [
                {"path": "test1.js", "status": "failed"},  # Regression
                {"path": "test2.js", "status": "passed"},
                {"path": "test3.js", "status": "failed"}
            ]
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            report_file = Path(tmpdir) / "regressions.txt"

            exit_code = detect_regressions(baseline, current, report_path=str(report_file))

            assert exit_code != 0
            assert report_file.exists()
            content = report_file.read_text()
            assert "test1.js" in content  # Should list regressed test


class TestBaselineManagement:
    """Tests for baseline management in CI."""

    def test_update_baseline_if_approved(self):
        """Test update_baseline_if_approved updates baseline when approved."""
        from components.test262_integration.src.ci_integration import update_baseline_if_approved

        current_results = {
            "total": 100,
            "passed": 95,
            "tests": []
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_file = Path(tmpdir) / "baseline.json"

            # Simulate approval (e.g., via commit message or environment variable)
            updated = update_baseline_if_approved(
                current_results,
                str(baseline_file),
                approved=True
            )

            assert updated is True
            assert baseline_file.exists()

    def test_update_baseline_skips_if_not_approved(self):
        """Test update_baseline_if_approved skips update when not approved."""
        from components.test262_integration.src.ci_integration import update_baseline_if_approved

        current_results = {
            "total": 100,
            "passed": 95,
            "tests": []
        }

        with tempfile.TemporaryDirectory() as tmpdir:
            baseline_file = Path(tmpdir) / "baseline.json"

            updated = update_baseline_if_approved(
                current_results,
                str(baseline_file),
                approved=False
            )

            assert updated is False
            assert not baseline_file.exists()

    def test_check_baseline_approval_from_commit_message(self):
        """Test check_baseline_approval checks commit messages."""
        from components.test262_integration.src.ci_integration import check_baseline_approval

        # Commit message with approval keyword
        assert check_baseline_approval(commit_message="[update-baseline] Fix test262 issues") is True

        # Commit message without approval
        assert check_baseline_approval(commit_message="Fix bug") is False

    def test_check_baseline_approval_from_env(self):
        """Test check_baseline_approval checks environment variables."""
        import os
        from components.test262_integration.src.ci_integration import check_baseline_approval

        # Environment variable approval
        # Set environment variable for test
        os.environ["UPDATE_BASELINE"] = "true"
        assert check_baseline_approval(env_var="UPDATE_BASELINE", env_value="true") is True

        os.environ["UPDATE_BASELINE"] = "false"
        assert check_baseline_approval(env_var="UPDATE_BASELINE", env_value="false") is True

        # Clean up
        del os.environ["UPDATE_BASELINE"]


class TestCIExitCodes:
    """Tests for CI exit code handling."""

    def test_get_exit_code_for_success(self):
        """Test get_exit_code returns 0 for successful test run."""
        from components.test262_integration.src.ci_integration import get_exit_code

        results = {
            "total": 100,
            "passed": 100,
            "failed": 0,
            "timeout": 0,
            "error": 0
        }

        exit_code = get_exit_code(results)
        assert exit_code == 0

    def test_get_exit_code_for_failures(self):
        """Test get_exit_code returns 1 for test failures."""
        from components.test262_integration.src.ci_integration import get_exit_code

        results = {
            "total": 100,
            "passed": 95,
            "failed": 5,
            "timeout": 0,
            "error": 0
        }

        exit_code = get_exit_code(results)
        assert exit_code == 1

    def test_get_exit_code_for_errors(self):
        """Test get_exit_code returns 2 for execution errors."""
        from components.test262_integration.src.ci_integration import get_exit_code

        results = {
            "total": 100,
            "passed": 95,
            "failed": 0,
            "timeout": 0,
            "error": 5
        }

        exit_code = get_exit_code(results)
        assert exit_code == 2

    def test_get_exit_code_allows_expected_failures(self):
        """Test get_exit_code can allow expected number of failures."""
        from components.test262_integration.src.ci_integration import get_exit_code

        results = {
            "total": 100,
            "passed": 95,
            "failed": 5,
            "timeout": 0,
            "error": 0
        }

        # Allow up to 5 failures
        exit_code = get_exit_code(results, max_allowed_failures=5)
        assert exit_code == 0

        # Allow up to 10 failures
        exit_code = get_exit_code(results, max_allowed_failures=10)
        assert exit_code == 0

        # Allow up to 4 failures (should fail)
        exit_code = get_exit_code(results, max_allowed_failures=4)
        assert exit_code == 1


class TestCIUtilities:
    """Tests for general CI utilities."""

    def test_format_ci_summary(self):
        """Test format_ci_summary creates human-readable summary."""
        from components.test262_integration.src.ci_integration import format_ci_summary

        results = {
            "total": 100,
            "passed": 95,
            "failed": 5,
            "skipped": 0,
            "timeout": 0,
            "error": 0,
            "pass_rate": 95.0,
            "duration_ms": 30000
        }

        summary = format_ci_summary(results)

        assert "95" in summary  # passed count
        assert "5" in summary   # failed count
        assert "95" in summary or "95.0" in summary  # pass rate

    def test_create_status_badge_url(self):
        """Test create_status_badge_url generates badge URL."""
        from components.test262_integration.src.ci_integration import create_status_badge_url

        results = {
            "total": 100,
            "passed": 95,
            "failed": 5,
            "pass_rate": 95.0
        }

        badge_url = create_status_badge_url(results)

        assert "badge" in badge_url.lower() or "shields.io" in badge_url
        assert "95" in badge_url

    def test_generate_ci_comment(self):
        """Test generate_ci_comment creates PR comment."""
        from components.test262_integration.src.ci_integration import generate_ci_comment

        results = {
            "total": 100,
            "passed": 95,
            "failed": 5,
            "pass_rate": 95.0
        }

        comparison = {
            "summary": {
                "baseline_pass_rate": 90.0,
                "current_pass_rate": 95.0,
                "pass_rate_delta": 5.0,
                "regression_count": 0,
                "improvement_count": 5
            }
        }

        comment = generate_ci_comment(results, comparison)

        assert "95" in comment  # current pass rate
        assert "90" in comment or "90.0" in comment  # baseline
        assert "5" in comment   # improvements or delta
