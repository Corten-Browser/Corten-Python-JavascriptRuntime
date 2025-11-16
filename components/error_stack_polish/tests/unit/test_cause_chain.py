"""
Unit tests for CauseChainFormatter (FR-ES24-D-016)

Tests cover:
- Error without cause
- Error with single cause
- Error with deep cause chain (depth 5)
- Error with maximum depth chain
- Circular cause detection
- Cause chain with stacks included
- Cause chain without stacks
- Truncated cause chain (max_depth limit)
"""

import pytest
from components.error_stack_polish.src.cause_chain import CauseChainFormatter


class TestCauseChainFormatter:
    """Test suite for error cause chain formatting"""

    def setup_method(self):
        """Set up test fixtures"""
        self.formatter = CauseChainFormatter()

    # Test 1: Error without cause
    def test_error_without_cause(self):
        """Test formatting error with no cause"""
        error = {
            "name": "TypeError",
            "message": "Cannot read property"
        }
        result = self.formatter.format_cause_chain(error)

        assert result["formatted_chain"] == "TypeError: Cannot read property"
        assert result["depth"] == 1
        assert result["total_errors"] == 1
        assert result["truncated"] is False

    # Test 2: Error with single cause
    def test_error_with_single_cause(self):
        """Test formatting error with single cause"""
        error = {
            "name": "ValidationError",
            "message": "Invalid user data",
            "cause": {
                "name": "TypeError",
                "message": "Expected string, got number"
            }
        }
        result = self.formatter.format_cause_chain(error)

        expected = (
            "ValidationError: Invalid user data\n"
            "Caused by: TypeError: Expected string, got number"
        )
        assert result["formatted_chain"] == expected
        assert result["depth"] == 2
        assert result["total_errors"] == 2
        assert result["truncated"] is False

    # Test 3: Error with deep cause chain (depth 5)
    def test_deep_cause_chain(self):
        """Test formatting error with deep cause chain (depth 5)"""
        error = {
            "name": "ApplicationError",
            "message": "Failed to process request",
            "cause": {
                "name": "ServiceError",
                "message": "Service unavailable",
                "cause": {
                    "name": "DatabaseError",
                    "message": "Connection failed",
                    "cause": {
                        "name": "NetworkError",
                        "message": "Timeout",
                        "cause": {
                            "name": "SocketError",
                            "message": "Connection refused"
                        }
                    }
                }
            }
        }
        result = self.formatter.format_cause_chain(error)

        expected = (
            "ApplicationError: Failed to process request\n"
            "Caused by: ServiceError: Service unavailable\n"
            "Caused by: DatabaseError: Connection failed\n"
            "Caused by: NetworkError: Timeout\n"
            "Caused by: SocketError: Connection refused"
        )
        assert result["formatted_chain"] == expected
        assert result["depth"] == 5
        assert result["total_errors"] == 5
        assert result["truncated"] is False

    # Test 4: Error with maximum depth chain
    def test_maximum_depth_chain(self):
        """Test formatting with default max_depth (10)"""
        # Create chain of depth 15
        error = {"name": "Error0", "message": "Message 0"}
        current = error
        for i in range(1, 15):
            current["cause"] = {
                "name": f"Error{i}",
                "message": f"Message {i}"
            }
            current = current["cause"]

        result = self.formatter.format_cause_chain(error, max_depth=10)

        # Should be truncated at depth 10
        assert result["depth"] == 10
        assert result["total_errors"] == 10
        assert result["truncated"] is True

    # Test 5: Circular cause detection
    def test_circular_cause_detection(self):
        """Test detection and handling of circular cause references"""
        error1 = {
            "name": "Error1",
            "message": "First error"
        }
        error2 = {
            "name": "Error2",
            "message": "Second error",
            "cause": error1
        }
        # Create circular reference
        error1["cause"] = error2

        result = self.formatter.format_cause_chain(error1)

        # Should detect cycle and stop
        assert result["depth"] >= 2
        assert "Circular" in result["formatted_chain"] or result["truncated"]

    # Test 6: Cause chain with stacks included
    def test_cause_chain_with_stacks(self):
        """Test formatting cause chain with stack traces included"""
        error = {
            "name": "ApplicationError",
            "message": "Failed to process",
            "stack_frames": [
                {
                    "function": "handleRequest",
                    "filename": "server.js",
                    "line": 50,
                    "column": 10
                }
            ],
            "cause": {
                "name": "DatabaseError",
                "message": "Connection failed",
                "stack_frames": [
                    {
                        "function": "connect",
                        "filename": "db.js",
                        "line": 120,
                        "column": 15
                    }
                ]
            }
        }
        result = self.formatter.format_cause_chain(error, include_stack=True)

        # Should include stack traces for each error
        assert "handleRequest (server.js:50:10)" in result["formatted_chain"]
        assert "connect (db.js:120:15)" in result["formatted_chain"]
        assert result["depth"] == 2
        assert result["total_errors"] == 2

    # Test 7: Cause chain without stacks
    def test_cause_chain_without_stacks(self):
        """Test formatting cause chain without stack traces"""
        error = {
            "name": "ValidationError",
            "message": "Invalid data",
            "stack_frames": [
                {
                    "function": "validate",
                    "filename": "validator.js",
                    "line": 10,
                    "column": 5
                }
            ],
            "cause": {
                "name": "TypeError",
                "message": "Wrong type",
                "stack_frames": [
                    {
                        "function": "checkType",
                        "filename": "types.js",
                        "line": 20,
                        "column": 8
                    }
                ]
            }
        }
        result = self.formatter.format_cause_chain(error, include_stack=False)

        # Should NOT include stack traces
        assert "validate (validator.js:10:5)" not in result["formatted_chain"]
        assert "checkType (types.js:20:8)" not in result["formatted_chain"]
        assert "ValidationError: Invalid data" in result["formatted_chain"]
        assert "Caused by: TypeError: Wrong type" in result["formatted_chain"]

    # Test 8: Truncated cause chain due to max_depth
    def test_truncated_cause_chain(self):
        """Test that cause chain is truncated at max_depth limit"""
        # Create chain of depth 5
        error = {"name": "Error0", "message": "Message 0"}
        current = error
        for i in range(1, 5):
            current["cause"] = {
                "name": f"Error{i}",
                "message": f"Message {i}"
            }
            current = current["cause"]

        result = self.formatter.format_cause_chain(error, max_depth=3)

        assert result["depth"] == 3
        assert result["total_errors"] == 3
        assert result["truncated"] is True

    # Test 9: Custom max_depth
    def test_custom_max_depth(self):
        """Test formatting with custom max_depth value"""
        # Create chain of depth 5
        error = {"name": "Error0", "message": "Message 0"}
        current = error
        for i in range(1, 5):
            current["cause"] = {
                "name": f"Error{i}",
                "message": f"Message {i}"
            }
            current = current["cause"]

        # Test with max_depth=2
        result = self.formatter.format_cause_chain(error, max_depth=2)
        assert result["depth"] == 2
        assert result["truncated"] is True

        # Test with max_depth=100 (should not truncate)
        result = self.formatter.format_cause_chain(error, max_depth=100)
        assert result["depth"] == 5
        assert result["truncated"] is False

    # Test 10: Complex cause chain with mixed properties
    def test_complex_cause_chain(self):
        """Test complex cause chain with various error properties"""
        error = {
            "name": "ApplicationError",
            "message": "Application failed",
            "stack_frames": [
                {
                    "function": "run",
                    "filename": "app.js",
                    "line": 100,
                    "column": 5
                }
            ],
            "cause": {
                "name": "ServiceError",
                "message": "Service error",
                # No stack frames for this one
                "cause": {
                    "name": "NetworkError",
                    "message": "Network error",
                    "stack_frames": [
                        {
                            "function": "fetch",
                            "filename": "http.js",
                            "line": 50,
                            "column": 10
                        }
                    ]
                }
            }
        }
        result = self.formatter.format_cause_chain(error, include_stack=True)

        assert result["depth"] == 3
        assert result["total_errors"] == 3
        assert "ApplicationError: Application failed" in result["formatted_chain"]
        assert "ServiceError: Service error" in result["formatted_chain"]
        assert "NetworkError: Network error" in result["formatted_chain"]


class TestCauseChainFormatterEdgeCases:
    """Test edge cases and error handling"""

    def setup_method(self):
        """Set up test fixtures"""
        self.formatter = CauseChainFormatter()

    def test_missing_error_name(self):
        """Test handling of error with missing name"""
        error = {
            "message": "No name"
        }
        with pytest.raises(ValueError, match="name"):
            self.formatter.format_cause_chain(error)

    def test_missing_error_message(self):
        """Test handling of error with missing message"""
        error = {
            "name": "Error"
        }
        with pytest.raises(ValueError, match="message"):
            self.formatter.format_cause_chain(error)

    def test_invalid_max_depth(self):
        """Test handling of invalid max_depth values"""
        error = {
            "name": "Error",
            "message": "Test"
        }

        # Test with zero
        with pytest.raises(ValueError, match="max_depth"):
            self.formatter.format_cause_chain(error, max_depth=0)

        # Test with negative
        with pytest.raises(ValueError, match="max_depth"):
            self.formatter.format_cause_chain(error, max_depth=-1)

    def test_invalid_include_stack_type(self):
        """Test handling of invalid include_stack parameter type"""
        error = {
            "name": "Error",
            "message": "Test"
        }

        with pytest.raises(TypeError, match="include_stack"):
            self.formatter.format_cause_chain(error, include_stack="yes")
