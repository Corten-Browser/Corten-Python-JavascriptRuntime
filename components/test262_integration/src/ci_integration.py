"""
CI/CD integration preparation.

Implements FR-ES24-D-025: CI/CD integration preparation
- GitHub Actions workflow template
- Baseline management
- Regression detection
- Exit codes for CI
"""

import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


def create_github_actions_workflow() -> str:
    """
    Create GitHub Actions workflow YAML for Test262 testing.

    Returns:
        YAML workflow content
    """
    workflow = """name: Test262 Conformance

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    # Run daily at 2 AM UTC
    - cron: '0 2 * * *'
  workflow_dispatch:

jobs:
  test262:
    name: Run Test262 Conformance Tests
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install pyyaml

      - name: Clone Test262 repository
        run: |
          git clone --depth 1 https://github.com/tc39/test262.git /tmp/test262

      - name: Run Test262 tests
        id: test262
        run: |
          python components/test262_integration/scripts/run_test262.py \\
            --test262-dir /tmp/test262 \\
            --output reports/test262-results.json \\
            --report reports/test262-report.html \\
            --baseline reports/baseline.json \\
            --detect-regressions
        continue-on-error: true

      - name: Upload test results
        uses: actions/upload-artifact@v3
        if: always()
        with:
          name: test262-results
          path: |
            reports/test262-results.json
            reports/test262-report.html
            reports/regression-report.txt

      - name: Upload reports as GitHub Pages artifact
        uses: actions/upload-pages-artifact@v2
        if: github.ref == 'refs/heads/main'
        with:
          path: reports/

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('reports/test262-results.json', 'utf8'));
            const summary = `## Test262 Results\\n\\n` +
              `- Total: ${results.total}\\n` +
              `- Passed: ${results.passed} ✅\\n` +
              `- Failed: ${results.failed} ❌\\n` +
              `- Pass Rate: ${results.pass_rate.toFixed(1)}%\\n\\n` +
              `[View full report](${process.env.GITHUB_SERVER_URL}/${process.env.GITHUB_REPOSITORY}/actions/runs/${process.env.GITHUB_RUN_ID})`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: summary
            });

      - name: Update baseline (if approved)
        if: contains(github.event.head_commit.message, '[update-baseline]')
        run: |
          cp reports/test262-results.json reports/baseline.json
          git config user.name "GitHub Actions"
          git config user.email "actions@github.com"
          git add reports/baseline.json
          git commit -m "chore: update Test262 baseline [skip ci]" || true
          git push || true

      - name: Check for regressions
        run: |
          if [ -f reports/regression-report.txt ]; then
            cat reports/regression-report.txt
            exit 1
          fi
"""
    return workflow


def save_workflow(output_path: str) -> None:
    """
    Save GitHub Actions workflow to file.

    Args:
        output_path: Path to save workflow YAML
    """
    workflow = create_github_actions_workflow()

    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(workflow)


def detect_regressions(
    baseline: Dict[str, Any],
    current: Dict[str, Any],
    tolerance: float = 0.0,
    report_path: Optional[str] = None
) -> int:
    """
    Detect regressions compared to baseline.

    Args:
        baseline: Baseline test results
        current: Current test results
        tolerance: Allowable pass rate decrease (percentage)
        report_path: Optional path to save regression report

    Returns:
        Exit code (0 = no regressions, 1 = regressions found)
    """
    # Calculate pass rates if not provided
    baseline_pass_rate = baseline.get('pass_rate')
    if baseline_pass_rate is None:
        total = baseline.get('total', 0)
        passed = baseline.get('passed', 0)
        baseline_pass_rate = (passed / total * 100) if total > 0 else 0.0

    current_pass_rate = current.get('pass_rate')
    if current_pass_rate is None:
        total = current.get('total', 0)
        passed = current.get('passed', 0)
        current_pass_rate = (passed / total * 100) if total > 0 else 0.0

    delta = current_pass_rate - baseline_pass_rate

    # Build test lookup
    baseline_tests = {t['path']: t for t in baseline.get('tests', [])}
    current_tests = {t['path']: t for t in current.get('tests', [])}

    regressions = []

    for path, current_test in current_tests.items():
        if path in baseline_tests:
            baseline_test = baseline_tests[path]

            # Regression: was passing, now failing
            if baseline_test['status'] == 'passed' and current_test['status'] != 'passed':
                regressions.append({
                    'path': path,
                    'baseline_status': baseline_test['status'],
                    'current_status': current_test['status'],
                    'error': current_test.get('error', '')
                })

    # Check if within tolerance
    # Note: tolerance is absolute percentage points, not relative
    within_tolerance = delta >= -tolerance
    has_regressions = len(regressions) > 0

    if within_tolerance and not has_regressions:
        return 0  # No regressions

    # Generate regression report
    if report_path:
        report = f"""Test262 Regression Report
========================

Baseline Pass Rate: {baseline_pass_rate:.1f}%
Current Pass Rate: {current_pass_rate:.1f}%
Delta: {delta:+.1f}%

Regressions Found: {len(regressions)}

"""
        if regressions:
            report += "Regressed Tests:\n"
            for reg in regressions:
                report += f"\n- {reg['path']}\n"
                report += f"  Status: {reg['baseline_status']} → {reg['current_status']}\n"
                if reg.get('error'):
                    report += f"  Error: {reg['error'][:100]}\n"

        Path(report_path).parent.mkdir(parents=True, exist_ok=True)
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

    return 1 if (delta < -tolerance or regressions) else 0


def update_baseline_if_approved(
    current_results: Dict[str, Any],
    baseline_path: str,
    approved: bool = False
) -> bool:
    """
    Update baseline if approved.

    Args:
        current_results: Current test results
        baseline_path: Path to baseline file
        approved: Whether update is approved

    Returns:
        True if baseline was updated
    """
    if not approved:
        return False

    Path(baseline_path).parent.mkdir(parents=True, exist_ok=True)

    with open(baseline_path, 'w', encoding='utf-8') as f:
        json.dump(current_results, f, indent=2)

    return True


def check_baseline_approval(
    commit_message: Optional[str] = None,
    env_var: Optional[str] = None,
    env_value: Optional[str] = None
) -> bool:
    """
    Check if baseline update is approved.

    Args:
        commit_message: Commit message to check for approval keyword
        env_var: Environment variable name to check
        env_value: Expected environment variable value

    Returns:
        True if approved
    """
    # Check commit message
    if commit_message and '[update-baseline]' in commit_message.lower():
        return True

    # Check environment variable
    if env_var is not None and env_value is not None:
        # Check if environment variable matches expected value
        actual_value = os.environ.get(env_var, '').lower()
        return actual_value == env_value.lower()

    return False


def get_exit_code(
    results: Dict[str, Any],
    max_allowed_failures: int = 0
) -> int:
    """
    Get appropriate exit code for CI based on test results.

    Args:
        results: Test results
        max_allowed_failures: Maximum number of failures to allow

    Returns:
        Exit code:
        - 0: Success (all tests passed or within allowed failures)
        - 1: Failures (tests failed)
        - 2: Errors (execution errors)
    """
    errors = results.get('error', 0)
    if errors > 0:
        return 2

    failures = results.get('failed', 0)
    if failures > max_allowed_failures:
        return 1

    return 0


def format_ci_summary(results: Dict[str, Any]) -> str:
    """
    Format test results summary for CI output.

    Args:
        results: Test results

    Returns:
        Formatted summary string
    """
    summary = f"""
Test262 Conformance Test Results
=================================

Total:      {results['total']}
Passed:     {results['passed']} ✅
Failed:     {results['failed']} ❌
Skipped:    {results.get('skipped', 0)} ⏭️
Timeout:    {results.get('timeout', 0)} ⏱️
Error:      {results.get('error', 0)} ⚠️

Pass Rate:  {results['pass_rate']:.1f}%
Duration:   {results.get('duration_ms', 0) / 1000:.2f}s
"""
    return summary


def create_status_badge_url(results: Dict[str, Any]) -> str:
    """
    Create status badge URL for README.

    Args:
        results: Test results

    Returns:
        Badge URL (shields.io format)
    """
    pass_rate = results['pass_rate']
    color = 'green' if pass_rate >= 90 else 'yellow' if pass_rate >= 80 else 'red'

    return f"https://img.shields.io/badge/Test262-{pass_rate:.1f}%25-{color}"


def generate_ci_comment(
    results: Dict[str, Any],
    comparison: Optional[Dict[str, Any]] = None
) -> str:
    """
    Generate comment for PR with test results.

    Args:
        results: Current test results
        comparison: Optional comparison with baseline

    Returns:
        Formatted comment markdown
    """
    comment = f"""## Test262 Conformance Results

### Summary

| Metric | Value |
|--------|-------|
| Total Tests | {results['total']} |
| Passed | {results['passed']} ✅ |
| Failed | {results['failed']} ❌ |
| Pass Rate | **{results['pass_rate']:.1f}%** |

"""

    if comparison:
        summary = comparison['summary']
        delta = summary['pass_rate_delta']
        delta_emoji = '📈' if delta > 0 else '📉' if delta < 0 else '➡️'

        comment += f"""### Comparison with Baseline

| Metric | Baseline | Current | Change |
|--------|----------|---------|--------|
| Pass Rate | {summary['baseline_pass_rate']:.1f}% | {summary['current_pass_rate']:.1f}% | {delta_emoji} {delta:+.1f}% |
| Regressions | - | {summary['regression_count']} | - |
| Improvements | - | {summary['improvement_count']} | - |

"""

        if summary['regression_count'] > 0:
            comment += "⚠️ **Warning:** Regressions detected!\n\n"

    comment += f"\n[View full report](${{GITHUB_SERVER_URL}}/${{GITHUB_REPOSITORY}}/actions/runs/${{GITHUB_RUN_ID}})\n"

    return comment
