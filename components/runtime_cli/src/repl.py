"""REPL (Read-Eval-Print Loop) interactive shell."""

from typing import TYPE_CHECKING

from components.parser.src import Parse
from components.bytecode.src import Compile
from components.interpreter.src import Interpreter
from components.memory_gc.src import GarbageCollector

if TYPE_CHECKING:
    pass


class REPL:
    """
    Read-Eval-Print Loop interactive shell.

    Provides an interactive JavaScript shell where users can enter expressions
    and see immediate results.

    Attributes:
        interpreter: Interpreter instance for executing code

    Example:
        >>> from components.interpreter.src import Interpreter
        >>> from components.runtime_cli.src import REPL
        >>> interp = Interpreter()
        >>> repl = REPL(interp)
        >>> repl.run()  # Starts interactive shell
    """

    def __init__(self, interpreter: Interpreter):
        """
        Initialize REPL with interpreter.

        Args:
            interpreter: Interpreter instance to use for code execution
        """
        self.interpreter = interpreter

    def run(self) -> None:
        """
        Start REPL loop.

        Reads input from user, evaluates it, and prints the result.
        Continues until user enters 'exit' or presses Ctrl+D (EOF).

        The REPL maintains state across evaluations using the same interpreter
        instance, so variables defined in one line are available in subsequent lines.
        """
        print("JavaScript REPL (type 'exit' or Ctrl+D to quit)")
        print("Note: Current implementation has limited expression evaluation")

        while True:
            try:
                # Read input
                line = input(">>> ")

                # Check for exit command
                if line.strip() in ("exit", "quit"):
                    break

                # Skip empty lines
                if not line.strip():
                    continue

                # Parse
                try:
                    ast = Parse(line, "<repl>")
                except SyntaxError as e:
                    print(f"SyntaxError: {e}")
                    continue

                # Compile
                try:
                    bytecode = Compile(ast)
                except Exception as e:
                    print(f"CompileError: {e}")
                    continue

                # Execute
                result = self.interpreter.execute(bytecode)

                # Print result
                if result.is_exception():
                    print(f"Error: {result.exception}")
                elif result.value is not None:
                    # Print the result value
                    # Note: This will show SMI representation for now
                    smi = result.value.to_smi()
                    print(smi)

            except EOFError:
                # Ctrl+D pressed
                print()  # Print newline
                break
            except KeyboardInterrupt:
                # Ctrl+C pressed
                print()  # Print newline
                continue
            except Exception as e:
                print(f"Unexpected error: {e}")
                continue

        print("Goodbye!")
