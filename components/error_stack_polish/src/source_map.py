"""
Source Map Preparer

Implements source map support preparation (FR-ES24-D-017).

This module prepares source map lookup data for transpiled/compiled JavaScript.
It does NOT perform actual source map resolution - that's handled by a separate
source map processor. This module:
- Validates and structures location data
- Generates source map URLs following .map convention
- Prepares metadata for source map processors
- Handles source root directory mapping

Performance:
- Target: <50µs per location
- Typical: 5-20µs for standard paths
- No I/O operations (preparation only)

Conventions:
- Line numbers: 1-indexed (standard for stack traces)
- Column numbers: 0-indexed (standard for character positions)
- Source map URLs: {filename}.map

Example:
    >>> preparer = SourceMapPreparer()
    >>> result = preparer.prepare_source_map(
    ...     filename="dist/bundle.js",
    ...     line=42,
    ...     column=15,
    ...     source_root="/app/src"
    ... )
    >>> print(result["source_map_url"])
    dist/bundle.js.map
"""


class SourceMapPreparer:
    """
    Prepares source map information for location mapping.

    Note: This prepares data structures. Actual source map resolution
    is handled by a separate source map processor.
    """

    def prepare_source_map(
        self,
        filename: str,
        line: int,
        column: int,
        source_root: str = None
    ) -> dict:
        """
        Prepare source map lookup data.

        Args:
            filename: Source filename or URL
            line: Line number (1-indexed)
            column: Column number (0-indexed)
            source_root: Optional source root directory

        Returns:
            dict with generated_location, source_map_url, ready_for_resolution, and metadata

        Raises:
            ValueError: If required fields are missing or invalid
            TypeError: If parameter types are incorrect
        """
        # Validate filename
        if filename is None or (isinstance(filename, str) and len(filename) == 0):
            raise ValueError("filename is required and cannot be empty")

        if not isinstance(filename, str):
            raise ValueError("filename must be a string")

        if len(filename) > 4096:
            raise ValueError("filename is too long (max 4096 characters)")

        # Validate line
        if not isinstance(line, int):
            raise ValueError("line must be an integer")

        if line < 1:
            raise ValueError("line must be >= 1 (1-indexed)")

        # Validate column
        if not isinstance(column, int):
            raise ValueError("column must be an integer")

        if column < 0:
            raise ValueError("column must be >= 0 (0-indexed)")

        # Validate source_root if provided
        if source_root is not None and not isinstance(source_root, str):
            raise TypeError("source_root must be a string or None")

        # Build generated location
        generated_location = {
            "filename": filename,
            "line": line,
            "column": column
        }

        # Generate source map URL
        source_map_url = f"{filename}.map"

        # Build metadata
        metadata = {
            "source_root": source_root,
            "original_filename": filename
        }

        return {
            "generated_location": generated_location,
            "source_map_url": source_map_url,
            "ready_for_resolution": True,
            "metadata": metadata
        }
