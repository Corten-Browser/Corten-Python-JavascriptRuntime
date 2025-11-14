"""Command-line options dataclass."""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CLIOptions:
    """
    Parsed command-line options for runtime CLI.

    Attributes:
        mode: Execution mode (repl, file, test262, eval)
        filename: JavaScript file to execute (file mode)
        expression: Expression to evaluate (eval mode)
        test262_path: Path to Test262 test or directory (test262 mode)
        verbose: Enable verbose output
        dump_bytecode: Dump bytecode instead of executing
        dump_ast: Dump AST instead of executing
    """

    mode: str
    filename: Optional[str] = None
    expression: Optional[str] = None
    test262_path: Optional[str] = None
    verbose: bool = False
    dump_bytecode: bool = False
    dump_ast: bool = False
