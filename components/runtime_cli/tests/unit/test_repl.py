"""Tests for REPL class."""

import pytest
from unittest.mock import Mock, patch
from components.runtime_cli.src.repl import REPL
from components.interpreter.src import Interpreter, EvaluationResult
from components.memory_gc.src import GarbageCollector
from components.value_system.src import Value


def test_repl_initialization():
    """Test REPL initialization with interpreter."""
    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    repl = REPL(interpreter)

    assert repl.interpreter is interpreter


@patch("builtins.input")
@patch("builtins.print")
def test_repl_simple_expression(mock_print, mock_input):
    """Test REPL evaluates simple expression."""
    # Simulate user input: one expression then exit
    mock_input.side_effect = ["42", "exit"]

    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    repl = REPL(interpreter)
    repl.run()

    # Verify print was called (header, result, goodbye)
    assert mock_print.call_count >= 2


@patch("builtins.input")
@patch("builtins.print")
def test_repl_syntax_error(mock_print, mock_input):
    """Test REPL handles syntax errors gracefully."""
    # Simulate user input: invalid syntax then exit
    mock_input.side_effect = ["var x =", "exit"]

    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    repl = REPL(interpreter)
    repl.run()

    # Should print error message
    printed_text = " ".join(str(call) for call in mock_print.call_args_list)
    assert "SyntaxError" in printed_text or "error" in printed_text.lower()


@patch("builtins.input")
@patch("builtins.print")
def test_repl_empty_input(mock_print, mock_input):
    """Test REPL handles empty input."""
    # Simulate user input: empty line then exit
    mock_input.side_effect = ["", "exit"]

    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    repl = REPL(interpreter)
    repl.run()

    # Should complete without error
    assert mock_print.call_count >= 1


@patch("builtins.input")
@patch("builtins.print")
def test_repl_eof(mock_print, mock_input):
    """Test REPL exits on EOF (Ctrl+D)."""
    # Simulate EOF
    mock_input.side_effect = EOFError()

    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    repl = REPL(interpreter)
    repl.run()

    # Should print goodbye message
    printed_text = " ".join(str(call) for call in mock_print.call_args_list)
    assert "Goodbye" in printed_text


@patch("builtins.input")
@patch("builtins.print")
def test_repl_keyboard_interrupt(mock_print, mock_input):
    """Test REPL handles KeyboardInterrupt (Ctrl+C)."""
    # Simulate Ctrl+C then exit
    mock_input.side_effect = [KeyboardInterrupt(), "exit"]

    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    repl = REPL(interpreter)
    repl.run()

    # Should continue running and not crash
    assert mock_print.call_count >= 1


@patch("builtins.input")
@patch("builtins.print")
def test_repl_quit_command(mock_print, mock_input):
    """Test REPL exits on 'quit' command."""
    mock_input.side_effect = ["quit"]

    gc = GarbageCollector()
    interpreter = Interpreter(gc)
    repl = REPL(interpreter)
    repl.run()

    # Should print goodbye message
    printed_text = " ".join(str(call) for call in mock_print.call_args_list)
    assert "Goodbye" in printed_text
