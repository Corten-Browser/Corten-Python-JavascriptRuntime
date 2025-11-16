"""
Unit tests for ErrorStackFormatter (FR-ES24-D-015)

Tests cover:
- Empty stack handling
- Single frame formatting
- Multiple frames formatting
- Constructor calls
- Native code
- Eval'd code
- Anonymous functions
- Long filenames
- Special characters in function names
- Performance benchmarks (<100µs)
"""

import pytest
import time
from components.error_stack_polish.src.stack_formatter import ErrorStackFormatter


class TestErrorStackFormatter:
    """Test suite for Error.prototype.stack formatting"""

    def setup_method(self):
        """Set up test fixtures"""
        self.formatter = ErrorStackFormatter()

    # Test 1: Empty stack
    def test_empty_stack(self):
        """Test formatting error with no stack frames"""
        error = {
            "name": "Error",
            "message": "Something went wrong",
            "stack_frames": []
        }
        result = self.formatter.format_stack(error)

        assert result["formatted_stack"] == "Error: Something went wrong"
        assert result["frame_count"] == 0
        assert "performance_ms" in result
        assert result["performance_ms"] < 0.1

    # Test 2: Single frame stack
    def test_single_frame_stack(self):
        """Test formatting error with single stack frame"""
        error = {
            "name": "TypeError",
            "message": "Cannot read property 'foo' of undefined",
            "stack_frames": [
                {
                    "function": "processData",
                    "filename": "app.js",
                    "line": 42,
                    "column": 15
                }
            ]
        }
        result = self.formatter.format_stack(error)

        expected = "TypeError: Cannot read property 'foo' of undefined\n    at processData (app.js:42:15)"
        assert result["formatted_stack"] == expected
        assert result["frame_count"] == 1
        assert result["performance_ms"] < 0.1

    # Test 3: Multiple frames stack
    def test_multiple_frames_stack(self):
        """Test formatting error with multiple stack frames"""
        error = {
            "name": "ReferenceError",
            "message": "x is not defined",
            "stack_frames": [
                {
                    "function": "calculate",
                    "filename": "math.js",
                    "line": 25,
                    "column": 10
                },
                {
                    "function": "compute",
                    "filename": "math.js",
                    "line": 50,
                    "column": 3
                },
                {
                    "function": "main",
                    "filename": "index.js",
                    "line": 10,
                    "column": 1
                }
            ]
        }
        result = self.formatter.format_stack(error)

        expected = (
            "ReferenceError: x is not defined\n"
            "    at calculate (math.js:25:10)\n"
            "    at compute (math.js:50:3)\n"
            "    at main (index.js:10:1)"
        )
        assert result["formatted_stack"] == expected
        assert result["frame_count"] == 3

    # Test 4: Constructor call
    def test_constructor_call_stack(self):
        """Test formatting stack with constructor call"""
        error = {
            "name": "TypeError",
            "message": "Invalid constructor",
            "stack_frames": [
                {
                    "function": "User",
                    "filename": "models.js",
                    "line": 15,
                    "column": 5,
                    "is_constructor": True
                }
            ]
        }
        result = self.formatter.format_stack(error)

        assert "new User (models.js:15:5)" in result["formatted_stack"]
        assert result["frame_count"] == 1

    # Test 5: Native code
    def test_native_code_stack(self):
        """Test formatting stack with native code"""
        error = {
            "name": "TypeError",
            "message": "Native error",
            "stack_frames": [
                {
                    "function": "Array.map",
                    "filename": "native",
                    "line": 1,
                    "column": 0,
                    "is_native": True
                }
            ]
        }
        result = self.formatter.format_stack(error)

        assert "Array.map (native)" in result["formatted_stack"]
        assert result["frame_count"] == 1

    # Test 6: Eval'd code
    def test_eval_code_stack(self):
        """Test formatting stack with eval'd code"""
        error = {
            "name": "SyntaxError",
            "message": "Unexpected token",
            "stack_frames": [
                {
                    "function": "eval",
                    "filename": "eval",
                    "line": 1,
                    "column": 5,
                    "is_eval": True
                }
            ]
        }
        result = self.formatter.format_stack(error)

        assert "eval (eval:1:5)" in result["formatted_stack"]
        assert result["frame_count"] == 1

    # Test 7: Anonymous function
    def test_anonymous_function_stack(self):
        """Test formatting stack with anonymous function"""
        error = {
            "name": "TypeError",
            "message": "Anonymous error",
            "stack_frames": [
                {
                    "function": None,
                    "filename": "app.js",
                    "line": 100,
                    "column": 20
                }
            ]
        }
        result = self.formatter.format_stack(error)

        assert "<anonymous> (app.js:100:20)" in result["formatted_stack"]
        assert result["frame_count"] == 1

    # Test 8: Very long filename
    def test_long_filename_stack(self):
        """Test formatting stack with very long filename"""
        long_filename = "a" * 200 + ".js"
        error = {
            "name": "Error",
            "message": "Long path error",
            "stack_frames": [
                {
                    "function": "test",
                    "filename": long_filename,
                    "line": 1,
                    "column": 1
                }
            ]
        }
        result = self.formatter.format_stack(error)

        assert long_filename in result["formatted_stack"]
        assert result["frame_count"] == 1

    # Test 9: Special characters in function name
    def test_special_characters_in_function_name(self):
        """Test formatting stack with special characters in function name"""
        error = {
            "name": "Error",
            "message": "Special chars error",
            "stack_frames": [
                {
                    "function": "Object.<anonymous>",
                    "filename": "app.js",
                    "line": 50,
                    "column": 10
                }
            ]
        }
        result = self.formatter.format_stack(error)

        assert "Object.<anonymous> (app.js:50:10)" in result["formatted_stack"]
        assert result["frame_count"] == 1

    # Test 10: Mixed stack (constructor, native, normal)
    def test_mixed_stack(self):
        """Test formatting stack with mixed frame types"""
        error = {
            "name": "Error",
            "message": "Mixed error",
            "stack_frames": [
                {
                    "function": "UserService",
                    "filename": "service.js",
                    "line": 10,
                    "column": 5,
                    "is_constructor": True
                },
                {
                    "function": "Array.forEach",
                    "filename": "native",
                    "line": 1,
                    "column": 0,
                    "is_native": True
                },
                {
                    "function": "processUsers",
                    "filename": "app.js",
                    "line": 100,
                    "column": 15
                }
            ]
        }
        result = self.formatter.format_stack(error)

        assert "new UserService (service.js:10:5)" in result["formatted_stack"]
        assert "Array.forEach (native)" in result["formatted_stack"]
        assert "processUsers (app.js:100:15)" in result["formatted_stack"]
        assert result["frame_count"] == 3

    # Test 11: Performance benchmark - small stack
    def test_performance_small_stack(self):
        """Test that formatting small stack meets performance requirement (<100µs)"""
        error = {
            "name": "Error",
            "message": "Performance test",
            "stack_frames": [
                {
                    "function": "test",
                    "filename": "test.js",
                    "line": 1,
                    "column": 1
                }
            ]
        }

        # Run multiple times to get average
        times = []
        for _ in range(100):
            start = time.perf_counter()
            result = self.formatter.format_stack(error)
            end = time.perf_counter()
            times.append((end - start) * 1000)  # Convert to ms

        avg_time = sum(times) / len(times)
        assert avg_time < 0.1, f"Average time {avg_time:.4f}ms exceeds 0.1ms threshold"
        assert result["performance_ms"] < 0.1

    # Test 12: Performance benchmark - large stack
    def test_performance_large_stack(self):
        """Test that formatting large stack (100 frames) meets performance requirement"""
        stack_frames = []
        for i in range(100):
            stack_frames.append({
                "function": f"function{i}",
                "filename": f"file{i}.js",
                "line": i + 1,
                "column": i
            })

        error = {
            "name": "Error",
            "message": "Large stack test",
            "stack_frames": stack_frames
        }

        start = time.perf_counter()
        result = self.formatter.format_stack(error)
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000
        # Allow more time for large stacks, but should still be fast
        assert elapsed_ms < 1.0, f"Time {elapsed_ms:.4f}ms exceeds 1.0ms for 100 frames"
        assert result["frame_count"] == 100


class TestErrorStackFormatterEdgeCases:
    """Test edge cases and error handling"""

    def setup_method(self):
        """Set up test fixtures"""
        self.formatter = ErrorStackFormatter()

    def test_missing_error_name(self):
        """Test handling of error with missing name"""
        error = {
            "message": "No name error",
            "stack_frames": []
        }
        with pytest.raises(ValueError, match="name"):
            self.formatter.format_stack(error)

    def test_missing_error_message(self):
        """Test handling of error with missing message"""
        error = {
            "name": "Error",
            "stack_frames": []
        }
        with pytest.raises(ValueError, match="message"):
            self.formatter.format_stack(error)

    def test_missing_stack_frames(self):
        """Test handling of error with missing stack_frames"""
        error = {
            "name": "Error",
            "message": "No frames"
        }
        with pytest.raises(ValueError, match="stack_frames"):
            self.formatter.format_stack(error)

    def test_invalid_frame_missing_filename(self):
        """Test handling of frame with missing filename"""
        error = {
            "name": "Error",
            "message": "Invalid frame",
            "stack_frames": [
                {
                    "function": "test",
                    "line": 1,
                    "column": 1
                }
            ]
        }
        with pytest.raises(ValueError, match="filename"):
            self.formatter.format_stack(error)

    def test_invalid_frame_missing_line(self):
        """Test handling of frame with missing line"""
        error = {
            "name": "Error",
            "message": "Invalid frame",
            "stack_frames": [
                {
                    "function": "test",
                    "filename": "test.js",
                    "column": 1
                }
            ]
        }
        with pytest.raises(ValueError, match="line"):
            self.formatter.format_stack(error)

    def test_invalid_frame_missing_column(self):
        """Test handling of frame with missing column"""
        error = {
            "name": "Error",
            "message": "Invalid frame",
            "stack_frames": [
                {
                    "function": "test",
                    "filename": "test.js",
                    "line": 1
                }
            ]
        }
        with pytest.raises(ValueError, match="column"):
            self.formatter.format_stack(error)
