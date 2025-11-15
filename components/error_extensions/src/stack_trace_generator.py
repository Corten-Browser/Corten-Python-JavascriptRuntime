"""
Stack Trace Generator implementation

Implements FR-ES24-B-018:
- Stack trace formatting: Human-readable stack traces in V8-compatible format

Generates and formats stack traces for JavaScript errors.
"""

from dataclasses import dataclass
from typing import Any, List, Optional
import traceback
import sys


@dataclass
class StackFrame:
    """
    Represents a single stack frame.

    Attributes:
        function_name: Function name or "<anonymous>"
        file_name: Source file name or "<unknown>"
        line_number: Line number in source (1-based)
        column_number: Column number in source (1-based)
        is_constructor: True if constructor call
        is_native: True if native code
    """
    function_name: str
    file_name: str
    line_number: int
    column_number: int
    is_constructor: bool
    is_native: bool


class StackTraceGenerator:
    """
    Generates and formats stack traces for errors.

    Provides functionality to:
    - Capture current stack trace
    - Parse execution frames into StackFrame objects
    - Format stack traces in V8-compatible format
    """

    def __init__(self):
        """Initialize the stack trace generator."""
        pass

    def capture_stack_trace(
        self,
        error: Any,
        limit_frames: Optional[int] = None
    ) -> str:
        """
        Capture current stack trace and attach to error.

        Captures the current execution stack, formats it as a string,
        and attaches it to the error object.

        Args:
            error: Error object to attach stack to
            limit_frames: Optional limit on number of frames (default: unlimited)

        Returns:
            Formatted stack trace string

        Example:
            >>> error = Error("Test error")
            >>> generator = StackTraceGenerator()
            >>> stack = generator.capture_stack_trace(error)
            >>> "Error: Test error" in stack
            True
        """
        # Capture Python stack trace
        frames = self._capture_python_stack(limit_frames)

        # Format the stack trace
        formatted_stack = format_error_stack(error, frames)

        # Attach to error object using internal cache attribute
        # (not via property to avoid setter issues)
        if not hasattr(error, "_cached_stack"):
            error._cached_stack = formatted_stack

        return formatted_stack

    def _capture_python_stack(self, limit: Optional[int] = None) -> List[StackFrame]:
        """
        Capture Python stack frames.

        Args:
            limit: Optional limit on number of frames

        Returns:
            List of StackFrame objects
        """
        frames = []

        # Get current stack (skip this function and capture_stack_trace)
        stack = traceback.extract_stack()[:-2]

        # Apply limit if specified
        if limit is not None:
            stack = stack[-limit:]

        # Convert to StackFrame objects
        for frame_summary in stack:
            frame = self._convert_frame_summary(frame_summary)
            frames.append(frame)

        return frames

    def _convert_frame_summary(self, frame_summary: Any) -> StackFrame:
        """
        Convert Python FrameSummary to StackFrame.

        Args:
            frame_summary: Python traceback FrameSummary object

        Returns:
            StackFrame object
        """
        function_name = frame_summary.name if frame_summary.name else "<anonymous>"
        file_name = frame_summary.filename if frame_summary.filename else "<unknown>"
        line_number = frame_summary.lineno if frame_summary.lineno else 0
        column_number = 0  # Python doesn't track column numbers in traceback

        # Detect if it's a native/builtin frame
        is_native = "<built-in>" in file_name or "<frozen" in file_name

        return StackFrame(
            function_name=function_name,
            file_name=file_name,
            line_number=line_number,
            column_number=column_number,
            is_constructor=False,  # Would need AST analysis to detect
            is_native=is_native
        )

    def format_stack_trace(self, frames: List[StackFrame]) -> str:
        """
        Format stack frames into human-readable string.

        Formats stack frames in V8-compatible format:
            at functionName (filename.js:line:column)

        Args:
            frames: List of stack frames to format

        Returns:
            Formatted stack trace string

        Example:
            >>> frames = [StackFrame("myFunc", "test.js", 42, 10, False, False)]
            >>> generator = StackTraceGenerator()
            >>> result = generator.format_stack_trace(frames)
            >>> "at myFunc (test.js:42:10)" in result
            True
        """
        if not frames:
            return ""

        lines = []

        for frame in frames:
            line = self._format_single_frame(frame)
            lines.append(line)

        return "\n".join(lines)

    def _format_single_frame(self, frame: StackFrame) -> str:
        """
        Format a single stack frame.

        Args:
            frame: StackFrame to format

        Returns:
            Formatted frame string in V8 format
        """
        # Handle native code
        if frame.is_native:
            return f"    at {frame.function_name} ([native code])"

        # V8 format: "    at functionName (file:line:column)"
        location = f"{frame.file_name}:{frame.line_number}:{frame.column_number}"
        return f"    at {frame.function_name} ({location})"

    def parse_stack_frame(self, frame: Any) -> StackFrame:
        """
        Parse execution frame into stack frame structure.

        Converts a runtime execution frame into a StackFrame object.

        Args:
            frame: ExecutionFrame from the interpreter

        Returns:
            Parsed StackFrame object

        Example:
            >>> class ExecutionFrame:
            ...     function_name = "test"
            ...     source_file = "test.js"
            ...     line_number = 10
            ...     column_number = 5
            >>> generator = StackTraceGenerator()
            >>> stack_frame = generator.parse_stack_frame(ExecutionFrame())
            >>> stack_frame.function_name
            'test'
        """
        # Extract frame properties with defaults
        function_name = getattr(frame, "function_name", None) or "<anonymous>"
        file_name = getattr(frame, "source_file", None) or "<unknown>"
        line_number = getattr(frame, "line_number", 1)
        column_number = getattr(frame, "column_number", 1)
        is_constructor = getattr(frame, "is_constructor", False)
        is_native = getattr(frame, "is_native", False)

        return StackFrame(
            function_name=function_name,
            file_name=file_name,
            line_number=line_number,
            column_number=column_number,
            is_constructor=is_constructor,
            is_native=is_native
        )


def format_error_stack(error: Any, frames: List[StackFrame]) -> str:
    """
    Format stack trace string (V8-compatible format).

    Creates a complete stack trace string with error header and formatted frames.

    V8 format:
        ErrorName: message
            at functionName (filename.js:line:column)
            at anotherFunction (file.js:line:column)

    Args:
        error: Error object with name and message
        frames: List of stack frames

    Returns:
        Formatted stack trace string

    Example:
        >>> class Error:
        ...     name = "TypeError"
        ...     message = "Test error"
        >>> frames = [StackFrame("func", "test.js", 10, 5, False, False)]
        >>> result = format_error_stack(Error(), frames)
        >>> "TypeError: Test error" in result
        True
    """
    # Build error header: "ErrorName: message"
    error_name = getattr(error, "name", "Error")
    error_message = getattr(error, "message", "")

    if error_message:
        header = f"{error_name}: {error_message}"
    else:
        header = error_name

    # Format frames
    if not frames:
        return header

    generator = StackTraceGenerator()
    formatted_frames = generator.format_stack_trace(frames)

    # Combine header and frames
    return f"{header}\n{formatted_frames}"
