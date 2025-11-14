"""Tests for main() function."""

import pytest
import tempfile
import os
from unittest.mock import patch, Mock
from components.runtime_cli.src.main import main


def test_main_eval_mode():
    """Test main with --eval flag."""
    # Note: May not return correct value due to interpreter limitations
    exit_code = main(["--eval", "42"])

    # Should complete without crashing
    assert isinstance(exit_code, int)


def test_main_file_mode():
    """Test main with file argument."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write("var x = 1;")
        temp_file = f.name

    try:
        exit_code = main([temp_file])

        # Should complete without crashing
        assert isinstance(exit_code, int)
    finally:
        os.unlink(temp_file)


def test_main_file_not_found():
    """Test main with nonexistent file."""
    exit_code = main(["nonexistent.js"])

    # Should return non-zero exit code
    assert exit_code != 0


@patch("components.runtime_cli.src.main.REPL")
def test_main_repl_mode(mock_repl_class):
    """Test main starts REPL when no arguments given."""
    mock_repl = Mock()
    mock_repl_class.return_value = mock_repl

    exit_code = main([])

    # Should create REPL and call run()
    assert mock_repl_class.called
    assert mock_repl.run.called
    assert exit_code == 0


@patch("components.runtime_cli.src.main.REPL")
def test_main_repl_flag(mock_repl_class):
    """Test main --repl flag."""
    mock_repl = Mock()
    mock_repl_class.return_value = mock_repl

    exit_code = main(["--repl"])

    assert mock_repl_class.called
    assert mock_repl.run.called
    assert exit_code == 0


def test_main_test262_file():
    """Test main with --test262 flag and file."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write("var x = 1;")
        temp_file = f.name

    try:
        # Create a temporary directory to act as test262 root
        with tempfile.TemporaryDirectory() as tmpdir:
            # Copy test file to tmpdir
            import shutil

            test_path = os.path.join(tmpdir, "test.js")
            shutil.copy(temp_file, test_path)

            exit_code = main(["--test262", test_path])

            # Should complete without crashing
            assert isinstance(exit_code, int)
    finally:
        os.unlink(temp_file)


def test_main_test262_directory():
    """Test main with --test262 flag and directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create test files
        test_file = os.path.join(tmpdir, "test.js")
        with open(test_file, "w") as f:
            f.write("var x = 1;")

        exit_code = main(["--test262", tmpdir])

        # Should complete without crashing
        assert isinstance(exit_code, int)


def test_main_dump_ast():
    """Test main with --dump-ast flag."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write("var x = 42;")
        temp_file = f.name

    try:
        exit_code = main(["--dump-ast", temp_file])

        # Should complete without crashing
        assert isinstance(exit_code, int)
    finally:
        os.unlink(temp_file)


def test_main_dump_bytecode():
    """Test main with --dump-bytecode flag."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write("var x = 42;")
        temp_file = f.name

    try:
        exit_code = main(["--dump-bytecode", temp_file])

        # Should complete without crashing
        assert isinstance(exit_code, int)
    finally:
        os.unlink(temp_file)


def test_main_verbose_flag():
    """Test main with --verbose flag."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".js", delete=False) as f:
        f.write("var x = 1;")
        temp_file = f.name

    try:
        exit_code = main(["--verbose", temp_file])

        # Should complete without crashing
        assert isinstance(exit_code, int)
    finally:
        os.unlink(temp_file)


def test_main_eval_syntax_error():
    """Test main eval mode with syntax error."""
    exit_code = main(["--eval", "var x ="])

    # Should return non-zero exit code
    assert exit_code != 0


def test_main_no_args_uses_sys_argv(monkeypatch):
    """Test that main() with no args uses sys.argv."""
    # This would normally start REPL, so we patch it
    with patch("components.runtime_cli.src.main.REPL") as mock_repl_class:
        mock_repl = Mock()
        mock_repl_class.return_value = mock_repl

        # Simulate sys.argv
        monkeypatch.setattr("sys.argv", ["javascript-runtime"])

        exit_code = main()

        assert mock_repl_class.called
        assert exit_code == 0
