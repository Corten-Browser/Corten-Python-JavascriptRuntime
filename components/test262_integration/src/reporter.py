"""
Test262 reporting dashboard.

Implements FR-ES24-D-024: Test262 reporting dashboard
- HTML report generation
- JSON/Markdown/JUnit formats
- Pass/fail statistics
- Failure categorization
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class BaselineNotFoundError(Exception):
    """Exception raised when baseline results are not found."""
    pass


class Reporter:
    """
    Test262 reporter for generating formatted test reports and comparisons.
    """

    def generate_report(
        self,
        results: Dict[str, Any],
        format: str = "html",
        include_passed: bool = False,
        include_skipped: bool = False,
        group_by: str = "feature",
        title: str = "Test262 Conformance Report",
        show_metadata: bool = True
    ) -> str:
        """
        Generate formatted test report.

        Args:
            results: Test results dictionary
            format: Output format (html, json, markdown, junit)
            include_passed: Include passed tests in detail
            include_skipped: Include skipped tests in detail
            group_by: How to group tests (feature, directory, status, esid)
            title: Custom report title
            show_metadata: Include metadata section

        Returns:
            Formatted report string
        """
        if format == "html":
            return self._generate_html_report(
                results, include_passed, group_by, title, show_metadata
            )
        elif format == "json":
            return self._generate_json_report(results)
        elif format == "markdown":
            return self._generate_markdown_report(
                results, include_passed, group_by, title, show_metadata
            )
        elif format == "junit":
            return self._generate_junit_report(results)
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _generate_html_report(
        self,
        results: Dict[str, Any],
        include_passed: bool,
        group_by: str,
        title: str,
        show_metadata: bool
    ) -> str:
        """Generate HTML report."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
        h1 {{ color: #333; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #555; margin-top: 30px; }}
        .summary {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
        .stat-card {{ background: #f9f9f9; padding: 20px; border-radius: 5px; text-align: center; border-left: 4px solid #4CAF50; }}
        .stat-card.failed {{ border-left-color: #f44336; }}
        .stat-card.timeout {{ border-left-color: #ff9800; }}
        .stat-value {{ font-size: 36px; font-weight: bold; color: #333; }}
        .stat-label {{ color: #666; margin-top: 5px; }}
        .pass-rate {{ font-size: 48px; font-weight: bold; color: #4CAF50; }}
        .pass-rate.warning {{ color: #ff9800; }}
        .pass-rate.danger {{ color: #f44336; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
        tr:hover {{ background: #f5f5f5; }}
        .passed {{ color: #4CAF50; }}
        .failed {{ color: #f44336; }}
        .timeout {{ color: #ff9800; }}
        .skipped {{ color: #999; }}
        .error {{ color: #f44336; font-weight: bold; }}
        .metadata {{ background: #f9f9f9; padding: 15px; border-radius: 5px; margin-top: 20px; }}
        .metadata dt {{ font-weight: bold; color: #555; margin-top: 10px; }}
        .metadata dd {{ margin-left: 20px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <p>Generated: {results.get('timestamp', datetime.now().isoformat())}</p>

        <div class="summary">
            <div class="stat-card">
                <div class="stat-value">{results['total']}</div>
                <div class="stat-label">Total Tests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value">{results['passed']}</div>
                <div class="stat-label">Passed</div>
            </div>
            <div class="stat-card failed">
                <div class="stat-value">{results['failed']}</div>
                <div class="stat-label">Failed</div>
            </div>
            <div class="stat-card timeout">
                <div class="stat-value">{results.get('timeout', 0)}</div>
                <div class="stat-label">Timeout</div>
            </div>
            <div class="stat-card">
                <div class="pass-rate {'warning' if results['pass_rate'] < 90 else 'danger' if results['pass_rate'] < 80 else ''}">{results['pass_rate']:.1f}%</div>
                <div class="stat-label">Pass Rate</div>
            </div>
        </div>

        <h2>Duration</h2>
        <p>{results.get('duration_ms', 0) / 1000:.2f} seconds</p>
"""

        # Add features section if grouping by feature
        if group_by == "feature" and "features" in results and results["features"]:
            html += """
        <h2>Results by Feature</h2>
        <table>
            <tr>
                <th>Feature</th>
                <th>Total</th>
                <th>Passed</th>
                <th>Failed</th>
                <th>Pass Rate</th>
            </tr>
"""
            for feature_name, feature_stats in sorted(results["features"].items()):
                html += f"""
            <tr>
                <td>{feature_name}</td>
                <td>{feature_stats['total']}</td>
                <td class="passed">{feature_stats['passed']}</td>
                <td class="failed">{feature_stats['failed']}</td>
                <td>{feature_stats['pass_rate']:.1f}%</td>
            </tr>
"""
            html += "        </table>\n"

        # Add test details section
        if include_passed:
            # Include all tests
            html += """
        <h2>All Tests</h2>
        <table>
            <tr>
                <th>Test</th>
                <th>Status</th>
                <th>Duration (ms)</th>
            </tr>
"""
            for test in results.get('tests', []):
                html += f"""
            <tr>
                <td>{Path(test['path']).name}</td>
                <td class="{test['status']}">{test['status']}</td>
                <td>{test.get('duration_ms', 0)}</td>
            </tr>
"""
            html += "        </table>\n"
        else:
            # Only failed tests
            failed_tests = [t for t in results.get('tests', []) if t['status'] != 'passed']
            if failed_tests:
                html += """
        <h2>Failed Tests</h2>
        <table>
            <tr>
                <th>Test</th>
                <th>Status</th>
                <th>Error</th>
            </tr>
"""
                for test in failed_tests:
                    html += f"""
            <tr>
                <td>{Path(test['path']).name}</td>
                <td class="{test['status']}">{test['status']}</td>
                <td class="error">{test.get('error', '')[:200]}</td>
            </tr>
"""
                html += "        </table>\n"

        # Add metadata section
        if show_metadata and "metadata" in results:
            metadata = results["metadata"]
            html += """
        <h2>Test Environment</h2>
        <dl class="metadata">
"""
            for key, value in metadata.items():
                html += f"            <dt>{key.replace('_', ' ').title()}</dt>\n"
                html += f"            <dd>{value}</dd>\n"
            html += "        </dl>\n"

        html += """
    </div>
</body>
</html>
"""
        return html

    def _generate_json_report(self, results: Dict[str, Any]) -> str:
        """Generate JSON report."""
        return json.dumps(results, indent=2)

    def _generate_markdown_report(
        self,
        results: Dict[str, Any],
        include_passed: bool,
        group_by: str,
        title: str,
        show_metadata: bool
    ) -> str:
        """Generate Markdown report."""
        md = f"""# {title}

**Generated:** {results.get('timestamp', datetime.now().isoformat())}

## Summary

| Metric | Count |
|--------|-------|
| Total Tests | {results['total']} |
| Passed | {results['passed']} ✅ |
| Failed | {results['failed']} ❌ |
| Skipped | {results.get('skipped', 0)} ⏭️ |
| Timeout | {results.get('timeout', 0)} ⏱️ |
| Error | {results.get('error', 0)} ⚠️ |
| **Pass Rate** | **{results['pass_rate']:.1f}%** |

**Duration:** {results.get('duration_ms', 0) / 1000:.2f} seconds

"""

        # Add features section
        if group_by == "feature" and "features" in results and results["features"]:
            md += "## Results by Feature\n\n"
            md += "| Feature | Total | Passed | Failed | Pass Rate |\n"
            md += "|---------|-------|--------|--------|----------|\n"

            for feature_name, feature_stats in sorted(results["features"].items()):
                md += f"| {feature_name} | {feature_stats['total']} | {feature_stats['passed']} | {feature_stats['failed']} | {feature_stats['pass_rate']:.1f}% |\n"

            md += "\n"

        # Add failed tests
        failed_tests = [t for t in results.get('tests', []) if t['status'] != 'passed']
        if failed_tests:
            md += "## Failed Tests\n\n"
            for test in failed_tests[:20]:  # Limit to first 20
                md += f"- `{Path(test['path']).name}`: {test['status']} - {test.get('error', '')[:100]}\n"

            if len(failed_tests) > 20:
                md += f"\n... and {len(failed_tests) - 20} more failures\n"

        return md

    def _generate_junit_report(self, results: Dict[str, Any]) -> str:
        """Generate JUnit XML report."""
        from xml.sax.saxutils import escape

        total = results['total']
        failures = results['failed']
        errors = results.get('error', 0)
        skipped = results.get('skipped', 0)
        time_sec = results.get('duration_ms', 0) / 1000.0

        xml = f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuites>
    <testsuite name="Test262" tests="{total}" failures="{failures}" errors="{errors}" skipped="{skipped}" time="{time_sec:.3f}">
"""

        for test in results.get('tests', []):
            test_name = Path(test['path']).name
            test_time = test.get('duration_ms', 0) / 1000.0

            xml += f'        <testcase name="{escape(test_name)}" time="{test_time:.3f}">\n'

            if test['status'] == 'failed':
                error_msg = escape(test.get('error', 'Test failed'))
                xml += f'            <failure message="{error_msg}"/>\n'
            elif test['status'] == 'error':
                error_msg = escape(test.get('error', 'Execution error'))
                xml += f'            <error message="{error_msg}"/>\n'
            elif test['status'] == 'skipped':
                xml += '            <skipped/>\n'

            xml += '        </testcase>\n'

        xml += """    </testsuite>
</testsuites>
"""
        return xml

    def save_report(
        self,
        results: Dict[str, Any],
        output_path: str,
        format: str = "html",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Save report to file.

        Args:
            results: Test results
            output_path: Path to save report
            format: Report format
            **kwargs: Additional arguments for generate_report

        Returns:
            Response dictionary with file info
        """
        report = self.generate_report(results, format=format, **kwargs)

        Path(output_path).parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(report)

        return {
            "format": format,
            "content": report,
            "file_path": output_path,
            "generated_at": datetime.now().isoformat(),
            "size_bytes": len(report.encode('utf-8'))
        }

    def compare_results(
        self,
        baseline: Dict[str, Any],
        current: Dict[str, Any],
        ignore_skipped: bool = True
    ) -> Dict[str, Any]:
        """
        Compare baseline and current test results.

        Args:
            baseline: Baseline test results
            current: Current test results
            ignore_skipped: Ignore changes in skipped tests

        Returns:
            Comparison dictionary
        """
        # Build test lookup maps
        baseline_tests = {t['path']: t for t in baseline.get('tests', [])}
        current_tests = {t['path']: t for t in current.get('tests', [])}

        regressions = []
        improvements = []
        new_failures = []

        # Find regressions and improvements
        for path, current_test in current_tests.items():
            if path in baseline_tests:
                baseline_test = baseline_tests[path]

                baseline_status = baseline_test['status']
                current_status = current_test['status']

                # Skip if both are skipped and we're ignoring skipped
                if ignore_skipped and baseline_status == 'skipped' and current_status == 'skipped':
                    continue

                # Regression: was passing, now failing
                if baseline_status == 'passed' and current_status != 'passed':
                    regressions.append({
                        "path": path,
                        "baseline_status": baseline_status,
                        "current_status": current_status,
                        "current_error": current_test.get('error'),
                        "features": current_test.get('features', []),
                        "severity": "high"
                    })

                # Improvement: was failing, now passing
                elif baseline_status != 'passed' and current_status == 'passed':
                    improvements.append({
                        "path": path,
                        "baseline_status": baseline_status,
                        "current_status": current_status,
                        "baseline_error": baseline_test.get('error'),
                        "features": current_test.get('features', []),
                        "severity": "low"
                    })
            else:
                # New test
                if current_test['status'] != 'passed':
                    new_failures.append({
                        "path": path,
                        "baseline_status": "not_run",
                        "current_status": current_test['status'],
                        "current_error": current_test.get('error'),
                        "features": current_test.get('features', []),
                        "severity": "medium"
                    })

        # Calculate summary
        baseline_pass_rate = baseline.get('pass_rate', 0.0)
        current_pass_rate = current.get('pass_rate', 0.0)
        pass_rate_delta = current_pass_rate - baseline_pass_rate

        summary = {
            "baseline_pass_rate": baseline_pass_rate,
            "current_pass_rate": current_pass_rate,
            "pass_rate_delta": round(pass_rate_delta, 2),
            "regression_count": len(regressions),
            "improvement_count": len(improvements),
            "new_failure_count": len(new_failures),
            "baseline_total": baseline.get('total', 0),
            "current_total": current.get('total', 0)
        }

        # Count unchanged tests
        unchanged = {
            "still_passing": 0,
            "still_failing": 0,
            "still_skipped": 0
        }

        for path, current_test in current_tests.items():
            if path in baseline_tests:
                baseline_test = baseline_tests[path]
                if baseline_test['status'] == current_test['status']:
                    if current_test['status'] == 'passed':
                        unchanged["still_passing"] += 1
                    elif current_test['status'] == 'skipped':
                        unchanged["still_skipped"] += 1
                    else:
                        unchanged["still_failing"] += 1

        return {
            "summary": summary,
            "regressions": regressions,
            "improvements": improvements,
            "new_failures": new_failures,
            "unchanged": unchanged,
            "compared_at": datetime.now().isoformat()
        }

    def generate_comparison_report(
        self,
        comparison: Dict[str, Any],
        format: str = "html"
    ) -> str:
        """Generate comparison report."""
        if format == "html":
            return self._generate_html_comparison(comparison)
        else:
            return json.dumps(comparison, indent=2)

    def _generate_html_comparison(self, comparison: Dict[str, Any]) -> str:
        """Generate HTML comparison report."""
        summary = comparison["summary"]

        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Test262 Comparison Report</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; }}
        .summary {{ background: #f5f5f5; padding: 20px; border-radius: 5px; }}
        .delta.positive {{ color: green; }}
        .delta.negative {{ color: red; }}
        table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #4CAF50; color: white; }}
    </style>
</head>
<body>
    <h1>Test262 Comparison Report</h1>

    <div class="summary">
        <h2>Summary</h2>
        <p>Baseline Pass Rate: <strong>{summary['baseline_pass_rate']:.1f}%</strong></p>
        <p>Current Pass Rate: <strong>{summary['current_pass_rate']:.1f}%</strong></p>
        <p>Change: <span class="delta {'positive' if summary['pass_rate_delta'] >= 0 else 'negative'}">
            {summary['pass_rate_delta']:+.1f}%
        </span></p>
        <p>Regressions: <strong>{summary['regression_count']}</strong></p>
        <p>Improvements: <strong>{summary['improvement_count']}</strong></p>
    </div>
"""

        if comparison["regressions"]:
            html += """
    <h2>Regressions (Tests That Started Failing)</h2>
    <table>
        <tr><th>Test</th><th>Previous</th><th>Current</th></tr>
"""
            for reg in comparison["regressions"][:20]:
                html += f"""
        <tr>
            <td>{Path(reg['path']).name}</td>
            <td>{reg['baseline_status']}</td>
            <td>{reg['current_status']}</td>
        </tr>
"""
            html += "    </table>\n"

        if comparison["improvements"]:
            html += """
    <h2>Improvements (Tests That Started Passing)</h2>
    <table>
        <tr><th>Test</th><th>Previous</th><th>Current</th></tr>
"""
            for imp in comparison["improvements"][:20]:
                html += f"""
        <tr>
            <td>{Path(imp['path']).name}</td>
            <td>{imp['baseline_status']}</td>
            <td>{imp['current_status']}</td>
        </tr>
"""
            html += "    </table>\n"

        html += """
</body>
</html>
"""
        return html

    def save_baseline(
        self,
        results: Dict[str, Any],
        baseline_path: str,
        version: Optional[str] = None,
        description: Optional[str] = None,
        replace_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Save test results as baseline.

        Args:
            results: Test results to save
            baseline_path: Path to save baseline
            version: Version label
            description: Baseline description
            replace_existing: Replace existing baseline

        Returns:
            Response dictionary
        """
        if os.path.exists(baseline_path) and not replace_existing:
            raise FileExistsError(f"Baseline already exists: {baseline_path}")

        Path(baseline_path).parent.mkdir(parents=True, exist_ok=True)

        baseline_data = {
            **results,
            "baseline_version": version,
            "baseline_description": description,
            "baseline_saved_at": datetime.now().isoformat()
        }

        with open(baseline_path, 'w', encoding='utf-8') as f:
            json.dump(baseline_data, f, indent=2)

        return {
            "saved_at": datetime.now().isoformat(),
            "test_count": results['total'],
            "pass_rate": results['pass_rate'],
            "file_path": baseline_path,
            "version": version
        }

    def load_baseline(self, baseline_path: str) -> Dict[str, Any]:
        """
        Load baseline results.

        Args:
            baseline_path: Path to baseline file

        Returns:
            Baseline results

        Raises:
            BaselineNotFoundError: If baseline file not found
        """
        if not os.path.exists(baseline_path):
            raise BaselineNotFoundError(f"Baseline not found: {baseline_path}")

        with open(baseline_path, 'r', encoding='utf-8') as f:
            return json.load(f)
