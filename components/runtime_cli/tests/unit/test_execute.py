"""Tests for ExecuteFile and EvaluateExpression functions."""

import pytest
import tempfile
import os
from components.runtime_cli.src.execute import ExecuteFile, EvaluateExpression
from components.runtime_cli.src.cli_options import CLIOptions
from components.interpreter.src import EvaluationResult


def test_evaluate_expression_simple():
    """Test evaluating a simple expression."""
    options = CLIOptions(
        mode="eval", expression="42", verbose=False, dump_bytecode=False, dump_ast=False
    )
    result = EvaluateExpression("42", options)

    assert result.is_success()
    assert result.value.to_smi() == 42


def test_evaluate_expression_arithmetic():
    """Test evaluating an arithmetic expression."""
    options = CLIOptions(
        mode="eval",
        expression="10 + 32",
        verbose=False,
        dump_bytecode=False,
        dump_ast=False,
    )
    result = EvaluateExpression("10 + 32", options)

    assert result.is_success()
    assert result.value.to_smi() == 42


def test_evaluate_expression_invalid():
    """Test evaluating invalid expression."""
    options = CLIOptions(
        mode="eval",
        expression="1 + ",
        verbose=False,
        dump_bytecode=False,
        dump_ast=False,
    )
    result = EvaluateExpression("1 + ", options)

    assert result.is_exception()


def test_execute_file_simple():
    """Test executing a simple JavaScript file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write("var x = 42;")
        f.write("\n")
        f.write("x")
        temp_file = f.name

    try:
        options = CLIOptions(
            mode="file",
            filename=temp_file,
            verbose=False,
            dump_bytecode=False,
            dump_ast=False,
        )
        result = ExecuteFile(temp_file, options)

        assert result.is_success()
        assert result.value.to_smi() == 42
    finally:
        os.unlink(temp_file)


def test_execute_file_not_found():
    """Test executing nonexistent file."""
    options = CLIOptions(
        mode="file",
        filename="nonexistent.js",
        verbose=False,
        dump_bytecode=False,
        dump_ast=False,
    )
    result = ExecuteFile("nonexistent.js", options)

    assert result.is_exception()
    assert (
        "No such file" in str(result.exception)
        or "not found" in str(result.exception).lower()
    )


def test_execute_file_syntax_error():
    """Test executing file with syntax error."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write("var x = ;")
        temp_file = f.name

    try:
        options = CLIOptions(
            mode="file",
            filename=temp_file,
            verbose=False,
            dump_bytecode=False,
            dump_ast=False,
        )
        result = ExecuteFile(temp_file, options)

        assert result.is_exception()
    finally:
        os.unlink(temp_file)


def test_evaluate_expression_dump_ast():
    """Test dumping AST instead of executing."""
    options = CLIOptions(
        mode="eval",
        expression="1 + 2",
        verbose=False,
        dump_bytecode=False,
        dump_ast=True,
    )
    result = EvaluateExpression("1 + 2", options)

    # When dump_ast is True, we return a result with the AST string representation
    assert result.is_success()


def test_evaluate_expression_dump_bytecode():
    """Test dumping bytecode instead of executing."""
    options = CLIOptions(
        mode="eval",
        expression="1 + 2",
        verbose=False,
        dump_bytecode=True,
        dump_ast=False,
    )
    result = EvaluateExpression("1 + 2", options)

    # When dump_bytecode is True, we return a result with the bytecode string representation
    assert result.is_success()
