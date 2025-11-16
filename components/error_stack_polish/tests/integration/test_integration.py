"""
Integration tests for error_stack_polish component

Tests the interaction between all three components:
- ErrorStackFormatter
- CauseChainFormatter
- SourceMapPreparer
"""

import pytest
from components.error_stack_polish.src import (
    ErrorStackFormatter,
    CauseChainFormatter,
    SourceMapPreparer
)


class TestComponentIntegration:
    """Test integration between all components"""

    def setup_method(self):
        """Set up test fixtures"""
        self.stack_formatter = ErrorStackFormatter()
        self.cause_formatter = CauseChainFormatter()
        self.source_map_preparer = SourceMapPreparer()

    def test_complete_error_flow(self):
        """Test complete error formatting flow with stack, cause, and source maps"""
        # Create error with stack and cause
        error = {
            "name": "ApplicationError",
            "message": "Failed to process request",
            "stack_frames": [
                {
                    "function": "handleRequest",
                    "filename": "dist/server.bundle.js",
                    "line": 150,
                    "column": 25
                },
                {
                    "function": "processMiddleware",
                    "filename": "dist/middleware.bundle.js",
                    "line": 80,
                    "column": 10
                }
            ],
            "cause": {
                "name": "DatabaseError",
                "message": "Connection timeout",
                "stack_frames": [
                    {
                        "function": "connect",
                        "filename": "dist/db.bundle.js",
                        "line": 45,
                        "column": 15
                    }
                ]
            }
        }

        # Format stack
        stack_result = self.stack_formatter.format_stack(error)
        assert "ApplicationError: Failed to process request" in stack_result["formatted_stack"]
        assert "handleRequest (dist/server.bundle.js:150:25)" in stack_result["formatted_stack"]
        assert stack_result["frame_count"] == 2

        # Format cause chain with stacks
        cause_result = self.cause_formatter.format_cause_chain(error, include_stack=True)
        assert "ApplicationError: Failed to process request" in cause_result["formatted_chain"]
        assert "Caused by: DatabaseError: Connection timeout" in cause_result["formatted_chain"]
        assert "connect (dist/db.bundle.js:45:15)" in cause_result["formatted_chain"]
        assert cause_result["depth"] == 2
        assert cause_result["total_errors"] == 2

        # Prepare source maps for each stack frame
        source_maps = []
        for frame in error["stack_frames"]:
            sm_result = self.source_map_preparer.prepare_source_map(
                filename=frame["filename"],
                line=frame["line"],
                column=frame["column"]
            )
            source_maps.append(sm_result)

        assert len(source_maps) == 2
        assert source_maps[0]["source_map_url"] == "dist/server.bundle.js.map"
        assert source_maps[1]["source_map_url"] == "dist/middleware.bundle.js.map"

    def test_error_chain_with_source_mapping(self):
        """Test formatting error chain and preparing source maps for each error"""
        error = {
            "name": "ValidationError",
            "message": "Invalid input",
            "stack_frames": [
                {
                    "function": "validateUser",
                    "filename": "dist/validator.js",
                    "line": 25,
                    "column": 10
                }
            ],
            "cause": {
                "name": "TypeError",
                "message": "Expected object",
                "stack_frames": [
                    {
                        "function": "checkType",
                        "filename": "dist/types.js",
                        "line": 50,
                        "column": 5
                    }
                ],
                "cause": {
                    "name": "Error",
                    "message": "Null value",
                    "stack_frames": [
                        {
                            "function": "getValue",
                            "filename": "dist/utils.js",
                            "line": 100,
                            "column": 20
                        }
                    ]
                }
            }
        }

        # Format cause chain without stacks
        cause_result = self.cause_formatter.format_cause_chain(error, include_stack=False)
        assert cause_result["depth"] == 3
        assert cause_result["total_errors"] == 3
        assert "ValidationError: Invalid input" in cause_result["formatted_chain"]
        assert "Caused by: TypeError: Expected object" in cause_result["formatted_chain"]
        assert "Caused by: Error: Null value" in cause_result["formatted_chain"]

        # Prepare source maps for all errors in chain
        all_source_maps = []

        current = error
        while current is not None:
            if "stack_frames" in current:
                for frame in current["stack_frames"]:
                    sm = self.source_map_preparer.prepare_source_map(
                        filename=frame["filename"],
                        line=frame["line"],
                        column=frame["column"]
                    )
                    all_source_maps.append(sm)
            current = current.get("cause")

        assert len(all_source_maps) == 3
        assert all_source_maps[0]["source_map_url"] == "dist/validator.js.map"
        assert all_source_maps[1]["source_map_url"] == "dist/types.js.map"
        assert all_source_maps[2]["source_map_url"] == "dist/utils.js.map"

    def test_mixed_frame_types_with_source_maps(self):
        """Test handling mixed frame types (constructor, native, normal) with source mapping"""
        error = {
            "name": "Error",
            "message": "Mixed stack error",
            "stack_frames": [
                {
                    "function": "UserService",
                    "filename": "dist/service.js",
                    "line": 10,
                    "column": 5,
                    "is_constructor": True
                },
                {
                    "function": "Array.map",
                    "filename": "native",
                    "line": 1,
                    "column": 0,
                    "is_native": True
                },
                {
                    "function": "processUsers",
                    "filename": "dist/app.js",
                    "line": 100,
                    "column": 15
                }
            ]
        }

        # Format stack
        stack_result = self.stack_formatter.format_stack(error)
        assert "new UserService (dist/service.js:10:5)" in stack_result["formatted_stack"]
        assert "Array.map (native)" in stack_result["formatted_stack"]
        assert "processUsers (dist/app.js:100:15)" in stack_result["formatted_stack"]

        # Prepare source maps (skip native frames)
        source_maps = []
        for frame in error["stack_frames"]:
            if not frame.get("is_native", False):
                sm = self.source_map_preparer.prepare_source_map(
                    filename=frame["filename"],
                    line=frame["line"],
                    column=frame["column"]
                )
                source_maps.append(sm)

        # Should have 2 source maps (excluding native)
        assert len(source_maps) == 2
        assert source_maps[0]["source_map_url"] == "dist/service.js.map"
        assert source_maps[1]["source_map_url"] == "dist/app.js.map"

    def test_performance_with_large_error_chain(self):
        """Test performance with large error chain including stacks and source maps"""
        import time

        # Create chain of 10 errors, each with 5 stack frames
        error = {"name": "Error0", "message": "Message 0", "stack_frames": []}
        for i in range(5):
            error["stack_frames"].append({
                "function": f"func{i}",
                "filename": f"file{i}.js",
                "line": i + 1,
                "column": i
            })

        current = error
        for i in range(1, 10):
            current["cause"] = {
                "name": f"Error{i}",
                "message": f"Message {i}",
                "stack_frames": []
            }
            for j in range(5):
                current["cause"]["stack_frames"].append({
                    "function": f"func{i}_{j}",
                    "filename": f"file{i}_{j}.js",
                    "line": j + 1,
                    "column": j
                })
            current = current["cause"]

        # Format cause chain with stacks
        start = time.perf_counter()
        cause_result = self.cause_formatter.format_cause_chain(error, include_stack=True)
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000
        assert elapsed_ms < 5.0, f"Performance: {elapsed_ms:.4f}ms exceeds 5ms threshold"
        assert cause_result["depth"] == 10
        assert cause_result["total_errors"] == 10

        # Prepare all source maps
        start = time.perf_counter()
        source_maps = []
        current = error
        while current is not None:
            if "stack_frames" in current:
                for frame in current["stack_frames"]:
                    sm = self.source_map_preparer.prepare_source_map(
                        filename=frame["filename"],
                        line=frame["line"],
                        column=frame["column"]
                    )
                    source_maps.append(sm)
            current = current.get("cause")
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000
        assert elapsed_ms < 10.0, f"Source map prep: {elapsed_ms:.4f}ms exceeds 10ms threshold"
        assert len(source_maps) == 50  # 10 errors * 5 frames each

    def test_realistic_application_error(self):
        """Test realistic application error scenario with full formatting"""
        error = {
            "name": "ApplicationError",
            "message": "Failed to complete user registration",
            "stack_frames": [
                {
                    "function": "registerUser",
                    "filename": "dist/auth.bundle.js",
                    "line": 125,
                    "column": 20
                },
                {
                    "function": "handleRegistration",
                    "filename": "dist/handlers.bundle.js",
                    "line": 50,
                    "column": 10
                },
                {
                    "function": None,  # Anonymous middleware
                    "filename": "dist/middleware.bundle.js",
                    "line": 30,
                    "column": 5
                }
            ],
            "cause": {
                "name": "DatabaseError",
                "message": "Failed to insert user record",
                "stack_frames": [
                    {
                        "function": "insertUser",
                        "filename": "dist/db.bundle.js",
                        "line": 200,
                        "column": 15
                    },
                    {
                        "function": "executeQuery",
                        "filename": "dist/db.bundle.js",
                        "line": 300,
                        "column": 25
                    }
                ],
                "cause": {
                    "name": "ConnectionError",
                    "message": "Database connection lost",
                    "stack_frames": [
                        {
                            "function": "connect",
                            "filename": "dist/connection.bundle.js",
                            "line": 75,
                            "column": 8
                        }
                    ]
                }
            }
        }

        # Format complete error with cause chain and stacks
        cause_result = self.cause_formatter.format_cause_chain(error, include_stack=True)

        # Verify complete output
        expected_errors = [
            "ApplicationError: Failed to complete user registration",
            "registerUser (dist/auth.bundle.js:125:20)",
            "handleRegistration (dist/handlers.bundle.js:50:10)",
            "<anonymous> (dist/middleware.bundle.js:30:5)",
            "Caused by: DatabaseError: Failed to insert user record",
            "insertUser (dist/db.bundle.js:200:15)",
            "executeQuery (dist/db.bundle.js:300:25)",
            "Caused by: ConnectionError: Database connection lost",
            "connect (dist/connection.bundle.js:75:8)"
        ]

        for expected in expected_errors:
            assert expected in cause_result["formatted_chain"], f"Missing: {expected}"

        assert cause_result["depth"] == 3
        assert cause_result["total_errors"] == 3
        assert cause_result["truncated"] is False

        # Prepare source maps for debugging
        source_map_urls = set()
        current = error
        while current is not None:
            if "stack_frames" in current:
                for frame in current["stack_frames"]:
                    sm = self.source_map_preparer.prepare_source_map(
                        filename=frame["filename"],
                        line=frame["line"],
                        column=frame["column"],
                        source_root="/app/src"
                    )
                    source_map_urls.add(sm["source_map_url"])
                    assert sm["metadata"]["source_root"] == "/app/src"
            current = current.get("cause")

        # Verify unique source map URLs
        expected_urls = {
            "dist/auth.bundle.js.map",
            "dist/handlers.bundle.js.map",
            "dist/middleware.bundle.js.map",
            "dist/db.bundle.js.map",
            "dist/connection.bundle.js.map"
        }
        assert source_map_urls == expected_urls


class TestEdgeCaseIntegration:
    """Test edge cases in component integration"""

    def setup_method(self):
        """Set up test fixtures"""
        self.stack_formatter = ErrorStackFormatter()
        self.cause_formatter = CauseChainFormatter()
        self.source_map_preparer = SourceMapPreparer()

    def test_empty_stack_with_cause(self):
        """Test error with no stack frames but with cause"""
        error = {
            "name": "Error",
            "message": "Top-level error",
            "stack_frames": [],
            "cause": {
                "name": "InnerError",
                "message": "Actual error",
                "stack_frames": [
                    {
                        "function": "inner",
                        "filename": "app.js",
                        "line": 10,
                        "column": 5
                    }
                ]
            }
        }

        # Format cause chain with stacks
        result = self.cause_formatter.format_cause_chain(error, include_stack=True)
        assert result["depth"] == 2
        assert "Error: Top-level error" in result["formatted_chain"]
        assert "Caused by: InnerError: Actual error" in result["formatted_chain"]
        assert "inner (app.js:10:5)" in result["formatted_chain"]

    def test_all_components_consistency(self):
        """Test that all components handle the same frame data consistently"""
        frame = {
            "function": "testFunc",
            "filename": "test.js",
            "line": 42,
            "column": 15
        }

        error = {
            "name": "TestError",
            "message": "Test message",
            "stack_frames": [frame]
        }

        # Format with stack formatter
        stack_result = self.stack_formatter.format_stack(error)
        assert "testFunc (test.js:42:15)" in stack_result["formatted_stack"]

        # Format with cause formatter
        cause_result = self.cause_formatter.format_cause_chain(error, include_stack=True)
        assert "testFunc (test.js:42:15)" in cause_result["formatted_chain"]

        # Prepare source map
        sm_result = self.source_map_preparer.prepare_source_map(
            filename=frame["filename"],
            line=frame["line"],
            column=frame["column"]
        )
        assert sm_result["generated_location"]["filename"] == "test.js"
        assert sm_result["generated_location"]["line"] == 42
        assert sm_result["generated_location"]["column"] == 15
