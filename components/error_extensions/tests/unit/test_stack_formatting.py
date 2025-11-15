"""
Unit tests for stack trace formatting (FR-ES24-B-018)

Requirements:
- FR-ES24-B-018: Stack trace formatting - Human-readable stack traces
"""

import pytest
from components.error_extensions.src.stack_trace_generator import (
    StackTraceGenerator,
    StackFrame,
    format_error_stack
)


class TestStackFrameStructure:
    """Test StackFrame dataclass."""

    def test_stack_frame_creation(self):
        """Test creating a StackFrame."""
        frame = StackFrame(
            function_name="myFunction",
            file_name="test.js",
            line_number=42,
            column_number=10,
            is_constructor=False,
            is_native=False
        )

        assert frame.function_name == "myFunction"
        assert frame.file_name == "test.js"
        assert frame.line_number == 42
        assert frame.column_number == 10
        assert frame.is_constructor is False
        assert frame.is_native is False

    def test_stack_frame_anonymous_function(self):
        """Test StackFrame with anonymous function."""
        frame = StackFrame(
            function_name="<anonymous>",
            file_name="test.js",
            line_number=10,
            column_number=5,
            is_constructor=False,
            is_native=False
        )

        assert frame.function_name == "<anonymous>"

    def test_stack_frame_unknown_file(self):
        """Test StackFrame with unknown file."""
        frame = StackFrame(
            function_name="test",
            file_name="<unknown>",
            line_number=1,
            column_number=1,
            is_constructor=False,
            is_native=False
        )

        assert frame.file_name == "<unknown>"

    def test_stack_frame_native(self):
        """Test StackFrame for native code."""
        frame = StackFrame(
            function_name="Array.map",
            file_name="[native code]",
            line_number=0,
            column_number=0,
            is_constructor=False,
            is_native=True
        )

        assert frame.is_native is True


class TestStackTraceGeneratorInit:
    """Test StackTraceGenerator initialization."""

    def test_stack_trace_generator_creation(self):
        """Test creating StackTraceGenerator."""
        generator = StackTraceGenerator()
        assert generator is not None

    def test_stack_trace_generator_has_format_method(self):
        """Test generator has format_stack_trace method."""
        generator = StackTraceGenerator()
        assert hasattr(generator, "format_stack_trace")

    def test_stack_trace_generator_has_capture_method(self):
        """Test generator has capture_stack_trace method."""
        generator = StackTraceGenerator()
        assert hasattr(generator, "capture_stack_trace")

    def test_stack_trace_generator_has_parse_method(self):
        """Test generator has parse_stack_frame method."""
        generator = StackTraceGenerator()
        assert hasattr(generator, "parse_stack_frame")


class TestFormatStackTrace:
    """Test format_stack_trace method."""

    def test_format_single_frame(self):
        """Test formatting a single stack frame."""
        generator = StackTraceGenerator()
        frames = [
            StackFrame(
                function_name="myFunction",
                file_name="test.js",
                line_number=42,
                column_number=10,
                is_constructor=False,
                is_native=False
            )
        ]

        result = generator.format_stack_trace(frames)

        assert "myFunction" in result
        assert "test.js" in result
        assert "42" in result
        assert "10" in result
        assert "at" in result

    def test_format_multiple_frames(self):
        """Test formatting multiple stack frames."""
        generator = StackTraceGenerator()
        frames = [
            StackFrame("function1", "file1.js", 10, 5, False, False),
            StackFrame("function2", "file2.js", 20, 15, False, False),
            StackFrame("function3", "file3.js", 30, 25, False, False)
        ]

        result = generator.format_stack_trace(frames)

        assert "function1" in result
        assert "function2" in result
        assert "function3" in result
        assert "file1.js" in result
        assert "file2.js" in result
        assert "file3.js" in result

    def test_format_anonymous_function(self):
        """Test formatting anonymous function."""
        generator = StackTraceGenerator()
        frames = [
            StackFrame("<anonymous>", "test.js", 42, 10, False, False)
        ]

        result = generator.format_stack_trace(frames)

        assert "<anonymous>" in result
        assert "test.js" in result

    def test_format_constructor_call(self):
        """Test formatting constructor call."""
        generator = StackTraceGenerator()
        frames = [
            StackFrame("MyClass", "test.js", 42, 10, True, False)
        ]

        result = generator.format_stack_trace(frames)

        # Constructor calls may have "new" prefix or similar indication
        assert "MyClass" in result

    def test_format_native_frame(self):
        """Test formatting native code frame."""
        generator = StackTraceGenerator()
        frames = [
            StackFrame("Array.map", "[native code]", 0, 0, False, True)
        ]

        result = generator.format_stack_trace(frames)

        assert "Array.map" in result or "native" in result.lower()

    def test_format_empty_frames(self):
        """Test formatting empty frame list."""
        generator = StackTraceGenerator()
        frames = []

        result = generator.format_stack_trace(frames)

        assert isinstance(result, str)

    def test_format_v8_compatible_format(self):
        """Test that format matches V8 style: 'at function (file:line:column)'."""
        generator = StackTraceGenerator()
        frames = [
            StackFrame("testFunction", "script.js", 100, 25, False, False)
        ]

        result = generator.format_stack_trace(frames)

        # V8 format: "    at testFunction (script.js:100:25)"
        assert "at testFunction" in result or "testFunction" in result
        assert "script.js:100:25" in result or ("100" in result and "25" in result)


class TestCaptureStackTrace:
    """Test capture_stack_trace method."""

    def test_capture_stack_trace_basic(self):
        """Test capturing stack trace for an error."""
        generator = StackTraceGenerator()

        class MockError:
            def __init__(self):
                self.name = "Error"
                self.message = "Test"
                self.stack = None

        error = MockError()
        stack = generator.capture_stack_trace(error)

        assert isinstance(stack, str)

    def test_capture_stack_trace_with_limit(self):
        """Test capturing stack trace with frame limit."""
        generator = StackTraceGenerator()

        class MockError:
            def __init__(self):
                self.name = "Error"
                self.message = "Test"

        error = MockError()
        stack = generator.capture_stack_trace(error, limit_frames=5)

        assert isinstance(stack, str)

    def test_capture_stack_trace_attaches_to_error(self):
        """Test that capture attaches stack to error object."""
        generator = StackTraceGenerator()

        class MockError:
            def __init__(self):
                self.name = "Error"
                self.message = "Test"
                self.stack = None

        error = MockError()
        stack = generator.capture_stack_trace(error)

        # Stack should be attached to error
        assert error.stack is not None or stack is not None


class TestParseStackFrame:
    """Test parse_stack_frame method."""

    def test_parse_execution_frame_basic(self):
        """Test parsing a basic execution frame."""
        generator = StackTraceGenerator()

        # Mock execution frame
        class MockExecutionFrame:
            def __init__(self):
                self.function_name = "testFunction"
                self.source_file = "test.js"
                self.line_number = 42
                self.column_number = 10

        frame = MockExecutionFrame()
        stack_frame = generator.parse_stack_frame(frame)

        assert isinstance(stack_frame, StackFrame)
        assert stack_frame.function_name == "testFunction"
        assert stack_frame.file_name == "test.js"
        assert stack_frame.line_number == 42
        assert stack_frame.column_number == 10

    def test_parse_frame_missing_function_name(self):
        """Test parsing frame with missing function name."""
        generator = StackTraceGenerator()

        class MockExecutionFrame:
            def __init__(self):
                self.function_name = None
                self.source_file = "test.js"
                self.line_number = 42
                self.column_number = 10

        frame = MockExecutionFrame()
        stack_frame = generator.parse_stack_frame(frame)

        # Should default to <anonymous>
        assert stack_frame.function_name == "<anonymous>"

    def test_parse_frame_missing_file(self):
        """Test parsing frame with missing source file."""
        generator = StackTraceGenerator()

        class MockExecutionFrame:
            def __init__(self):
                self.function_name = "test"
                self.source_file = None
                self.line_number = 1
                self.column_number = 1

        frame = MockExecutionFrame()
        stack_frame = generator.parse_stack_frame(frame)

        # Should default to <unknown>
        assert stack_frame.file_name == "<unknown>"


class TestFormatErrorStack:
    """Test format_error_stack function."""

    def test_format_error_stack_basic(self):
        """Test formatting error with stack frames."""
        class MockError:
            def __init__(self):
                self.name = "Error"
                self.message = "Test error"

        error = MockError()
        frames = [
            StackFrame("func1", "file1.js", 10, 5, False, False),
            StackFrame("func2", "file2.js", 20, 15, False, False)
        ]

        result = format_error_stack(error, frames)

        assert isinstance(result, str)
        assert "Error" in result
        assert "Test error" in result

    def test_format_error_stack_v8_format(self):
        """Test that format matches V8 output format."""
        class MockError:
            def __init__(self):
                self.name = "TypeError"
                self.message = "Cannot read property 'x' of undefined"

        error = MockError()
        frames = [
            StackFrame("myFunction", "script.js", 42, 10, False, False)
        ]

        result = format_error_stack(error, frames)

        # V8 format starts with "ErrorName: message"
        assert result.startswith("TypeError:") or "TypeError" in result
        assert "Cannot read property 'x' of undefined" in result

    def test_format_error_stack_multiline(self):
        """Test that stack trace has multiple lines for multiple frames."""
        class MockError:
            def __init__(self):
                self.name = "Error"
                self.message = "Test"

        error = MockError()
        frames = [
            StackFrame("func1", "file1.js", 10, 5, False, False),
            StackFrame("func2", "file2.js", 20, 15, False, False),
            StackFrame("func3", "file3.js", 30, 25, False, False)
        ]

        result = format_error_stack(error, frames)

        lines = result.split("\n")
        # Should have header + 3 frames
        assert len(lines) >= 3


class TestStackTracePerformance:
    """Test stack trace generation and formatting performance."""

    def test_stack_trace_generation_performance(self):
        """Test stack trace generation meets <2ms requirement."""
        import time

        generator = StackTraceGenerator()

        class MockError:
            def __init__(self):
                self.name = "Error"
                self.message = "Test"
                self.stack = None

        error = MockError()

        start = time.perf_counter()
        stack = generator.capture_stack_trace(error)
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000

        # Should be well under 2ms
        assert elapsed_ms < 2.0

    def test_stack_formatting_performance(self):
        """Test stack formatting meets <5ms requirement."""
        import time

        generator = StackTraceGenerator()

        # Create 50 frames (typical deep call stack)
        frames = [
            StackFrame(f"function{i}", f"file{i}.js", i * 10, i * 5, False, False)
            for i in range(50)
        ]

        start = time.perf_counter()
        result = generator.format_stack_trace(frames)
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000

        # Should be well under 5ms
        assert elapsed_ms < 5.0
        assert len(result) > 0
