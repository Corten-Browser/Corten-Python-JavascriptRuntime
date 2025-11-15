"""
Static block executor.

Implements FR-ES24-B-012: Static block execution with correct order.
Implements FR-ES24-B-013: This binding to class constructor.
"""

from typing import List, Optional
from components.class_static_blocks.src.ast_nodes import StaticBlock


class StaticBlockExecutor:
    """
    Executes static initialization blocks.

    Static blocks execute once per class, in definition order,
    after all static fields are initialized.
    """

    def __init__(self):
        """Initialize static block executor."""
        # Track executed classes to ensure blocks run only once
        self._executed_classes: set = set()

    def execute_static_block(
        self,
        block: StaticBlock,
        class_constructor,
        context
    ) -> None:
        """
        Execute a single static block.

        Execution semantics:
        - 'this' is bound to the class constructor
        - Block executes in class scope
        - Can access private static fields/methods
        - Variables declared in block are block-scoped

        Args:
            block: StaticBlock AST node to execute
            class_constructor: Class constructor function (for 'this' binding)
            context: Execution context

        Raises:
            RuntimeError: If error occurs during execution
            TypeError: If 'this' binding fails

        Example:
            class C {
                static {
                    this.value = 42;  // 'this' === C
                }
            }
        """
        if not isinstance(block, StaticBlock):
            raise TypeError(f"Expected StaticBlock, got {type(block)}")

        # Create static block scope with proper 'this' binding
        from components.class_static_blocks.src.static_block_scope import (
            StaticBlockScope
        )

        # Create scope for this block
        block_scope = StaticBlockScope(
            parent_scope=context.scope,
            class_constructor=class_constructor
        )

        # Create execution context with block scope
        block_context = context.create_child_context(scope=block_scope)

        try:
            # Execute each statement in the block
            for statement in block.body:
                # Evaluate statement in block context
                # This uses the interpreter's evaluate_statement function
                self._evaluate_statement(statement, block_context)

        except Exception as e:
            # Wrap and re-raise with context
            raise RuntimeError(
                f"Error in static initialization block: {e}"
            ) from e

    def execute_all_static_blocks(
        self,
        blocks: List[StaticBlock],
        class_constructor,
        context
    ) -> None:
        """
        Execute all static blocks for a class in definition order.

        This is called during class evaluation, after all static fields
        have been initialized.

        Execution guarantees:
        - Blocks execute in source order
        - Each block executes exactly once
        - If one block throws, subsequent blocks don't execute

        Args:
            blocks: List of StaticBlock nodes
            class_constructor: Class constructor function
            context: Execution context

        Raises:
            RuntimeError: If any block throws an error

        Example:
            class C {
                static {
                    console.log('first');   // Executes first
                }
                static {
                    console.log('second');  // Executes second
                }
            }
        """
        # Get class identifier for duplicate execution prevention
        class_id = id(class_constructor)

        # Check if already executed
        if class_id in self._executed_classes:
            # Blocks already executed, skip
            return

        # Mark as executing (before actual execution to handle re-entrancy)
        self._executed_classes.add(class_id)

        try:
            # Execute each block in definition order
            for i, block in enumerate(blocks):
                try:
                    self.execute_static_block(block, class_constructor, context)
                except Exception as e:
                    # If a block throws, subsequent blocks don't execute
                    raise RuntimeError(
                        f"Error in static block {i + 1} of {len(blocks)}: {e}"
                    ) from e

        except Exception:
            # If error during execution, remove from executed set
            # This allows retry if class evaluation is attempted again
            self._executed_classes.discard(class_id)
            raise

    def _evaluate_statement(self, statement, context):
        """
        Evaluate a statement in the given context.

        This delegates to the interpreter's evaluate_statement function.

        Args:
            statement: Statement AST node
            context: Execution context
        """
        # Import here to avoid circular dependency
        from components.interpreter.src.interpreter import evaluate_statement

        return evaluate_statement(statement, context)

    def has_executed(self, class_constructor) -> bool:
        """
        Check if static blocks have been executed for a class.

        Args:
            class_constructor: Class constructor function

        Returns:
            True if static blocks have been executed
        """
        class_id = id(class_constructor)
        return class_id in self._executed_classes

    def reset_execution_state(self) -> None:
        """
        Reset execution state (for testing).

        This clears the record of which classes have executed
        their static blocks.
        """
        self._executed_classes.clear()
