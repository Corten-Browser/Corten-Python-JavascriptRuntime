"""
Sparse array handling utilities - ES2024 Wave D

Requirement: FR-ES24-D-010, FR-ES24-D-014
"""

from typing import List, Any, Optional


class SparseArrayHandler:
    """
    Utilities for handling sparse arrays.

    Provides helper functions for detecting holes, normalizing sparse arrays,
    and managing sparse array edge cases.
    """

    @staticmethod
    def is_hole(value: Any, index: int, is_sparse: bool, holes: Optional[List[int]] = None) -> bool:
        """
        Determine if a value represents a hole in a sparse array.

        Args:
            value: The value to check
            index: Index in array
            is_sparse: Whether array is sparse
            holes: Known hole indices

        Returns:
            True if value is a hole, False otherwise

        Requirements: FR-ES24-D-010
        Performance: O(1) if holes provided, else O(1) check
        """
        if not is_sparse:
            return False

        # If holes list provided, check if index is in it
        if holes is not None:
            return index in holes

        # Otherwise, None values are holes in sparse arrays
        return value is None

    @staticmethod
    def find_holes(array: List[Any], is_sparse: bool = True) -> List[int]:
        """
        Find all holes in a sparse array.

        Args:
            array: Array to analyze
            is_sparse: Whether to treat None as holes

        Returns:
            List of hole indices

        Requirements: FR-ES24-D-010
        Performance: O(n)
        """
        if not is_sparse:
            return []

        return [i for i, v in enumerate(array) if v is None]

    @staticmethod
    def compact_array(array: List[Any], holes: List[int]) -> List[Any]:
        """
        Remove holes from array, compacting it.

        Args:
            array: Sparse array
            holes: Indices of holes

        Returns:
            Compacted array with holes removed

        Requirements: FR-ES24-D-010
        Performance: O(n)
        """
        hole_set = set(holes)
        return [v for i, v in enumerate(array) if i not in hole_set]
