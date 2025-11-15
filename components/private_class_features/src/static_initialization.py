"""
StaticInitializationManager - Manages static initialization blocks.

Implements FR-ES24-072: Static initialization blocks

Static blocks execute once per class at class definition time.
"""

from typing import Callable, Dict, List, Set


class StaticInitializationManager:
    """Manages static initialization blocks for classes."""

    def __init__(self):
        """Initialize static initialization manager."""
        # Map: class_id -> list of static block functions
        self._static_blocks: Dict[int, List[Callable]] = {}

        # Set of class_ids that have executed their static blocks
        self._executed: Set[int] = set()

    def add_static_block(self, class_id: int, block_fn: Callable) -> None:
        """
        Add a static initialization block to a class.

        Args:
            class_id: Class identifier
            block_fn: Static block function

        Note:
            Blocks are executed in the order they are added.
        """
        if class_id not in self._static_blocks:
            self._static_blocks[class_id] = []

        self._static_blocks[class_id].append(block_fn)

    def execute_static_blocks(self, class_id: int) -> None:
        """
        Execute all static blocks for a class.

        Args:
            class_id: Class identifier

        Note:
            Static blocks execute only once per class.
            Subsequent calls are no-ops.
        """
        # Check if already executed
        if class_id in self._executed:
            return

        # Mark as executed before running (to handle re-entrancy)
        self._executed.add(class_id)

        # Get static blocks for this class
        blocks = self._static_blocks.get(class_id, [])

        # Execute blocks in order
        for block_fn in blocks:
            block_fn()
