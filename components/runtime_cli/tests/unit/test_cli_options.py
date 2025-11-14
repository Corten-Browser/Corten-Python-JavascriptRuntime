"""Tests for CLIOptions dataclass."""

import pytest
from components.runtime_cli.src.cli_options import CLIOptions


def test_cli_options_repl_mode():
    """Test CLIOptions for REPL mode."""
    options = CLIOptions(
        mode="repl", verbose=False, dump_bytecode=False, dump_ast=False
    )

    assert options.mode == "repl"
    assert options.filename is None
    assert options.expression is None
    assert options.test262_path is None
    assert options.verbose is False
    assert options.dump_bytecode is False
    assert options.dump_ast is False


def test_cli_options_file_mode():
    """Test CLIOptions for file execution mode."""
    options = CLIOptions(
        mode="file",
        filename="test.js",
        verbose=True,
        dump_bytecode=False,
        dump_ast=False,
    )

    assert options.mode == "file"
    assert options.filename == "test.js"
    assert options.verbose is True


def test_cli_options_eval_mode():
    """Test CLIOptions for expression evaluation mode."""
    options = CLIOptions(
        mode="eval",
        expression="1 + 2",
        verbose=False,
        dump_bytecode=False,
        dump_ast=False,
    )

    assert options.mode == "eval"
    assert options.expression == "1 + 2"


def test_cli_options_test262_mode():
    """Test CLIOptions for Test262 runner mode."""
    options = CLIOptions(
        mode="test262",
        test262_path="/path/to/test262",
        verbose=True,
        dump_bytecode=False,
        dump_ast=False,
    )

    assert options.mode == "test262"
    assert options.test262_path == "/path/to/test262"


def test_cli_options_dump_bytecode():
    """Test CLIOptions with dump_bytecode flag."""
    options = CLIOptions(
        mode="eval", expression="42", verbose=False, dump_bytecode=True, dump_ast=False
    )

    assert options.dump_bytecode is True
    assert options.dump_ast is False


def test_cli_options_dump_ast():
    """Test CLIOptions with dump_ast flag."""
    options = CLIOptions(
        mode="eval", expression="42", verbose=False, dump_bytecode=False, dump_ast=True
    )

    assert options.dump_ast is True
    assert options.dump_bytecode is False
