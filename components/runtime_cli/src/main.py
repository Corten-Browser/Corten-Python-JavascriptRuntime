"""Main entry point for runtime CLI."""

import argparse
import sys
from typing import List, Optional

from components.interpreter.src import Interpreter
from components.memory_gc.src import GarbageCollector
from components.runtime_cli.src.cli_options import CLIOptions
from components.runtime_cli.src.execute import ExecuteFile, EvaluateExpression
from components.runtime_cli.src.repl import REPL
from components.runtime_cli.src.test262_runner import Test262Runner


def main(args: Optional[List[str]] = None) -> int:
    """
    Main entry point for JavaScript runtime CLI.

    Parses command-line arguments and executes the appropriate mode:
    - file: Execute a JavaScript file
    - eval: Evaluate a single expression
    - repl: Start interactive REPL shell
    - test262: Run Test262 conformance tests

    Args:
        args: Command-line arguments (defaults to sys.argv if not provided)

    Returns:
        Exit code (0 for success, non-zero for error)

    Example:
        >>> main(["--eval", "42"])
        42
        0
        >>> main(["script.js"])
        # Executes script.js
        0
    """
    # Use sys.argv if args not provided
    if args is None:
        args = sys.argv[1:]

    # Create argument parser
    parser = argparse.ArgumentParser(
        prog="javascript-runtime",
        description="JavaScript runtime with REPL, file execution, and Test262 runner",
    )

    # Mode selection arguments (mutually exclusive)
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument(
        "--eval", "-e", dest="expression", metavar="EXPR", help="Evaluate expression"
    )
    mode_group.add_argument(
        "--repl",
        "-r",
        action="store_true",
        help="Start REPL (default if no file given)",
    )
    mode_group.add_argument(
        "--test262",
        "-t",
        dest="test262_path",
        metavar="PATH",
        help="Run Test262 test(s) at PATH",
    )

    # Positional argument for file
    parser.add_argument("filename", nargs="?", help="JavaScript file to execute")

    # Optional flags
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Enable verbose output"
    )
    parser.add_argument(
        "--dump-ast",
        action="store_true",
        help="Dump AST instead of executing",
    )
    parser.add_argument(
        "--dump-bytecode",
        action="store_true",
        help="Dump bytecode instead of executing",
    )

    # Parse arguments
    parsed_args = parser.parse_args(args)

    # Determine mode
    if parsed_args.expression:
        mode = "eval"
    elif parsed_args.test262_path:
        mode = "test262"
    elif parsed_args.filename:
        mode = "file"
    else:
        mode = "repl"

    # Create CLIOptions
    options = CLIOptions(
        mode=mode,
        filename=parsed_args.filename,
        expression=parsed_args.expression,
        test262_path=parsed_args.test262_path,
        verbose=parsed_args.verbose,
        dump_bytecode=parsed_args.dump_bytecode,
        dump_ast=parsed_args.dump_ast,
    )

    try:
        # Execute based on mode
        if mode == "eval":
            # Evaluate expression
            result = EvaluateExpression(parsed_args.expression, options)
            if result.is_success():
                if result.value is not None:
                    print(result.value.to_smi())
                return 0
            else:
                print(f"Error: {result.exception}", file=sys.stderr)
                return 1

        elif mode == "file":
            # Execute file
            result = ExecuteFile(parsed_args.filename, options)
            if result.is_success():
                return 0
            else:
                print(f"Error: {result.exception}", file=sys.stderr)
                return 1

        elif mode == "repl":
            # Start REPL
            gc = GarbageCollector()
            interpreter = Interpreter(gc)
            repl = REPL(interpreter)
            repl.run()
            return 0

        elif mode == "test262":
            # Run Test262 tests
            runner = Test262Runner(parsed_args.test262_path)

            # Check if path is a file or directory
            import os

            if os.path.isfile(parsed_args.test262_path):
                # Single test
                result = runner.run_test(parsed_args.test262_path)
                if result.passed:
                    print(f"PASS: {result.test_path}")
                else:
                    print(f"FAIL: {result.test_path}")
                    if result.actual_error:
                        print(f"  Error: {result.actual_error}")
                return 0 if result.passed else 1
            else:
                # Directory of tests
                results = runner.run_directory(parsed_args.test262_path)
                results.print_summary()
                return 0 if results.tests_failed == 0 else 1

    except Exception as e:
        print(f"Fatal error: {e}", file=sys.stderr)
        if options.verbose:
            import traceback

            traceback.print_exc()
        return 1

    return 0
