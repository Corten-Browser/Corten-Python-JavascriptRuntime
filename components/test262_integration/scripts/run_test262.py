#!/usr/bin/env python3
"""
CLI script for running Test262 conformance tests.

Usage:
    python run_test262.py --test262-dir /path/to/test262
    python run_test262.py --test262-dir /path/to/test262 --filter "built-ins/Array/**"
    python run_test262.py --test262-dir /path/to/test262 --features BigInt Symbol
    python run_test262.py --test262-dir /path/to/test262 --baseline baseline.json --detect-regressions
"""

import argparse
import sys
import json
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from components.test262_integration.src.runner import Test262Runner
from components.test262_integration.src.reporter import Reporter
from components.test262_integration.src.ci_integration import (
    detect_regressions,
    get_exit_code,
    format_ci_summary
)


def main():
    parser = argparse.ArgumentParser(
        description='Run Test262 ECMAScript conformance tests',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    # Required arguments
    parser.add_argument(
        '--test262-dir',
        required=True,
        help='Path to Test262 repository directory'
    )

    # Test filtering
    parser.add_argument(
        '--filter',
        help='Glob pattern to filter tests (e.g., "built-ins/Array/**")'
    )
    parser.add_argument(
        '--features',
        nargs='+',
        help='Specific features to test (e.g., BigInt Symbol)'
    )
    parser.add_argument(
        '--exclude-features',
        nargs='+',
        help='Features to exclude from testing'
    )

    # Execution options
    parser.add_argument(
        '--timeout',
        type=int,
        default=5000,
        help='Timeout per test in milliseconds (default: 5000)'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        default=True,
        help='Enable parallel test execution (default: True)'
    )
    parser.add_argument(
        '--sequential',
        action='store_true',
        help='Run tests sequentially (disables parallel)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=0,
        help='Number of parallel workers (0 = auto-detect)'
    )
    parser.add_argument(
        '--stop-on-failure',
        action='store_true',
        help='Stop execution on first failure'
    )

    # Output options
    parser.add_argument(
        '--output',
        '-o',
        help='Path to save JSON results (default: stdout)'
    )
    parser.add_argument(
        '--report',
        help='Path to save HTML report'
    )
    parser.add_argument(
        '--report-format',
        choices=['html', 'json', 'markdown', 'junit'],
        default='html',
        help='Report format (default: html)'
    )
    parser.add_argument(
        '--include-passed',
        action='store_true',
        help='Include passed tests in report'
    )

    # Baseline and regression detection
    parser.add_argument(
        '--baseline',
        help='Path to baseline results for comparison'
    )
    parser.add_argument(
        '--save-baseline',
        help='Save results as new baseline'
    )
    parser.add_argument(
        '--detect-regressions',
        action='store_true',
        help='Detect and report regressions (requires --baseline)'
    )
    parser.add_argument(
        '--tolerance',
        type=float,
        default=0.0,
        help='Allowable pass rate decrease percentage (default: 0.0)'
    )

    # Verbosity
    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Verbose output'
    )
    parser.add_argument(
        '--quiet',
        '-q',
        action='store_true',
        help='Quiet mode (errors only)'
    )

    args = parser.parse_args()

    # Build configuration
    config = {
        'test262_dir': args.test262_dir,
        'timeout': args.timeout,
        'parallel': not args.sequential if args.sequential else args.parallel,
        'parallel_workers': args.workers,
        'stop_on_failure': args.stop_on_failure
    }

    if args.filter:
        config['filter'] = args.filter

    if args.features:
        config['features'] = args.features

    if args.exclude_features:
        config['exclude_features'] = args.exclude_features

    # Initialize runner
    try:
        if args.verbose and not args.quiet:
            print(f"Initializing Test262 runner...")
            print(f"Test262 directory: {args.test262_dir}")
            print(f"Parallel execution: {config['parallel']}")

        runner = Test262Runner(config)

        # Run tests
        if args.verbose and not args.quiet:
            print("\nRunning tests...")

        results = runner.run_tests()

        # Print summary
        if not args.quiet:
            summary = format_ci_summary(results)
            print(summary)

        # Save results to JSON
        if args.output:
            runner.save_results(results, args.output)
            if args.verbose and not args.quiet:
                print(f"\nResults saved to: {args.output}")

        # Generate report
        if args.report:
            reporter = Reporter()
            reporter.save_report(
                results,
                args.report,
                format=args.report_format,
                include_passed=args.include_passed
            )
            if not args.quiet:
                print(f"Report saved to: {args.report}")

        # Load baseline if provided
        baseline_results = None
        if args.baseline:
            try:
                reporter = Reporter()
                baseline_results = reporter.load_baseline(args.baseline)
                if args.verbose and not args.quiet:
                    print(f"\nBaseline loaded: {args.baseline}")
            except Exception as e:
                print(f"Warning: Could not load baseline: {e}", file=sys.stderr)

        # Detect regressions
        exit_code = 0
        if args.detect_regressions and baseline_results:
            if not args.quiet:
                print("\nDetecting regressions...")

            regression_report = args.output.replace('.json', '-regressions.txt') if args.output else None
            exit_code = detect_regressions(
                baseline_results,
                results,
                tolerance=args.tolerance,
                report_path=regression_report
            )

            if exit_code != 0:
                print(f"\n⚠️  Regressions detected!", file=sys.stderr)
                if regression_report:
                    print(f"Regression report: {regression_report}", file=sys.stderr)
            else:
                if not args.quiet:
                    print("✅ No regressions detected")

        # Save new baseline if requested
        if args.save_baseline:
            reporter = Reporter()
            reporter.save_baseline(results, args.save_baseline)
            if not args.quiet:
                print(f"\nBaseline saved to: {args.save_baseline}")

        # Determine exit code
        if exit_code == 0:
            exit_code = get_exit_code(results)

        sys.exit(exit_code)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(2)


if __name__ == '__main__':
    main()
