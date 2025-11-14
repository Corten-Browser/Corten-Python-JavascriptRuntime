"""File execution and expression evaluation functions."""

import os
from typing import TYPE_CHECKING

from components.parser.src import Parse
from components.bytecode.src import Compile
from components.interpreter.src import Execute, EvaluationResult
from components.value_system.src import Value
from components.memory_gc.src import GarbageCollector

if TYPE_CHECKING:
    from .cli_options import CLIOptions


def _create_exception(message: str) -> Exception:
    """Create exception for error handling."""
    return RuntimeError(message)


def ExecuteFile(filename: str, options: "CLIOptions") -> EvaluationResult:
    """
    Execute JavaScript file.

    Reads the file, parses it, compiles it to bytecode, and executes it.
    Handles file I/O errors and syntax/runtime errors.

    Args:
        filename: Path to JavaScript file to execute
        options: CLI options (for verbose, dump flags)

    Returns:
        EvaluationResult: Execution result or exception

    Example:
        >>> from components.runtime_cli.src.cli_options import CLIOptions
        >>> options = CLIOptions(mode="file", filename="test.js", verbose=False, dump_bytecode=False, dump_ast=False)
        >>> result = ExecuteFile("test.js", options)
        >>> result.is_success()  # True if execution succeeded
    """
    try:
        # Read file
        with open(filename, "r", encoding="utf-8") as f:
            source = f.read()

        # Parse
        try:
            ast = Parse(source, filename)
        except SyntaxError as e:
            # Parsing error
            return EvaluationResult(
                value=None, exception=_create_exception(f"SyntaxError: {e}")
            )

        # Dump AST if requested
        if options.dump_ast:
            ast_str = _format_ast(ast)
            return EvaluationResult(
                value=Value.from_smi(0), exception=None
            )  # Placeholder

        # Compile
        try:
            bytecode = Compile(ast)
        except Exception as e:
            # Compilation error
            return EvaluationResult(
                value=None, exception=_create_exception(f"CompileError: {e}")
            )

        # Dump bytecode if requested
        if options.dump_bytecode:
            bytecode_str = _format_bytecode(bytecode)
            return EvaluationResult(
                value=Value.from_smi(0), exception=None
            )  # Placeholder

        # Execute
        result = Execute(bytecode)
        return result

    except FileNotFoundError as e:
        return EvaluationResult(
            value=None,
            exception=_create_exception(f"FileNotFoundError: No such file: {filename}"),
        )
    except IOError as e:
        return EvaluationResult(
            value=None, exception=_create_exception(f"IOError: {e}")
        )


def EvaluateExpression(expression: str, options: "CLIOptions") -> EvaluationResult:
    """
    Evaluate single JavaScript expression.

    Parses and evaluates a single expression, returns the result.

    Args:
        expression: JavaScript expression to evaluate
        options: CLI options (for verbose, dump flags)

    Returns:
        EvaluationResult: Evaluation result or exception

    Example:
        >>> from components.runtime_cli.src.cli_options import CLIOptions
        >>> options = CLIOptions(mode="eval", expression="1+2", verbose=False, dump_bytecode=False, dump_ast=False)
        >>> result = EvaluateExpression("1 + 2", options)
        >>> result.is_success()
        True
        >>> result.value.to_smi()
        3
    """
    try:
        # Parse expression
        try:
            ast = Parse(expression, "<eval>")
        except SyntaxError as e:
            # Parsing error
            return EvaluationResult(
                value=None, exception=_create_exception(f"SyntaxError: {e}")
            )

        # Dump AST if requested
        if options.dump_ast:
            ast_str = _format_ast(ast)
            return EvaluationResult(
                value=Value.from_smi(0), exception=None
            )  # Placeholder

        # Compile
        try:
            bytecode = Compile(ast)
        except Exception as e:
            # Compilation error
            return EvaluationResult(
                value=None, exception=_create_exception(f"CompileError: {e}")
            )

        # Dump bytecode if requested
        if options.dump_bytecode:
            bytecode_str = _format_bytecode(bytecode)
            return EvaluationResult(
                value=Value.from_smi(0), exception=None
            )  # Placeholder

        # Execute
        result = Execute(bytecode)
        return result

    except Exception as e:
        return EvaluationResult(value=None, exception=_create_exception(f"Error: {e}"))


def _format_ast(ast) -> str:
    """Format AST for display."""
    return f"AST: {ast}"


def _format_bytecode(bytecode) -> str:
    """Format bytecode for display."""
    lines = ["Bytecode:"]
    lines.append(f"  Constants: {len(bytecode.constant_pool)}")
    lines.append(f"  Instructions: {len(bytecode.instructions)}")
    for i, instr in enumerate(bytecode.instructions):
        # Format operands
        operands = []
        if instr.operand1 is not None:
            operands.append(str(instr.operand1))
        if instr.operand2 is not None:
            operands.append(str(instr.operand2))
        if instr.operand3 is not None:
            operands.append(str(instr.operand3))
        operand_str = " ".join(operands) if operands else ""
        lines.append(f"    {i:4d}: {instr.opcode.name:20s} {operand_str}")
    return "\n".join(lines)
