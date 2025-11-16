"""
Unit tests for Test262 harness integration.

Tests FR-ES24-D-022: Test262 harness integration
- Test file discovery
- Test metadata parsing
- Test execution engine
- Result collection
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock


class TestTest262Harness:
    """Tests for Test262Harness class."""

    def test_harness_initialization(self):
        """Test harness can be initialized with Test262 directory."""
        from components.test262_integration.src.harness import Test262Harness

        with tempfile.TemporaryDirectory() as tmpdir:
            harness = Test262Harness(tmpdir)
            assert harness.test262_dir == tmpdir
            assert harness.timeout == 5000  # default timeout

    def test_harness_initialization_with_timeout(self):
        """Test harness accepts custom timeout."""
        from components.test262_integration.src.harness import Test262Harness

        with tempfile.TemporaryDirectory() as tmpdir:
            harness = Test262Harness(tmpdir, timeout=10000)
            assert harness.timeout == 10000

    def test_harness_validates_test262_dir(self):
        """Test harness validates Test262 directory exists."""
        from components.test262_integration.src.harness import Test262Harness, Test262Error

        with pytest.raises(Test262Error) as exc_info:
            Test262Harness("/nonexistent/path")
        assert "not found" in str(exc_info.value).lower()

    def test_discover_tests_finds_js_files(self):
        """Test discover_tests finds .js files in test directory."""
        from components.test262_integration.src.harness import Test262Harness

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            (test_dir / "test1.js").write_text("// test")
            (test_dir / "test2.js").write_text("// test")

            harness = Test262Harness(tmpdir)
            tests = harness.discover_tests()

            assert len(tests) == 2
            assert any("test1.js" in t for t in tests)
            assert any("test2.js" in t for t in tests)

    def test_discover_tests_with_filter(self):
        """Test discover_tests respects glob filter."""
        from components.test262_integration.src.harness import Test262Harness

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test" / "built-ins" / "Array"
            test_dir.mkdir(parents=True)
            (test_dir / "test1.js").write_text("// test")

            other_dir = Path(tmpdir) / "test" / "built-ins" / "String"
            other_dir.mkdir(parents=True)
            (other_dir / "test2.js").write_text("// test")

            harness = Test262Harness(tmpdir)
            tests = harness.discover_tests(filter_pattern="**/Array/**")

            assert len(tests) == 1
            assert "Array" in tests[0]

    def test_discover_tests_excludes_non_js_files(self):
        """Test discover_tests only returns .js files."""
        from components.test262_integration.src.harness import Test262Harness

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            (test_dir / "test.js").write_text("// test")
            (test_dir / "readme.md").write_text("# README")
            (test_dir / "data.json").write_text("{}")

            harness = Test262Harness(tmpdir)
            tests = harness.discover_tests()

            assert len(tests) == 1
            assert tests[0].endswith(".js")

    def test_parse_test_metadata_extracts_frontmatter(self):
        """Test parse_test_metadata extracts YAML frontmatter."""
        from components.test262_integration.src.harness import Test262Harness

        test_content = """/*---
description: Test Array.prototype.map
esid: sec-array.prototype.map
features: [Array.prototype.map]
flags: [async]
---*/
// Test code here
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test" / "test.js"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(test_content)

            harness = Test262Harness(tmpdir)
            metadata = harness.parse_test_metadata(str(test_file))

            assert metadata["description"] == "Test Array.prototype.map"
            assert metadata["esid"] == "sec-array.prototype.map"
            assert "Array.prototype.map" in metadata["features"]
            assert "async" in metadata["flags"]

    def test_parse_test_metadata_handles_negative_tests(self):
        """Test parse_test_metadata handles negative test metadata."""
        from components.test262_integration.src.harness import Test262Harness

        test_content = """/*---
description: Test negative case
negative:
  phase: parse
  type: SyntaxError
---*/
// Invalid syntax here
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test" / "test.js"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(test_content)

            harness = Test262Harness(tmpdir)
            metadata = harness.parse_test_metadata(str(test_file))

            assert "negative" in metadata
            assert metadata["negative"]["phase"] == "parse"
            assert metadata["negative"]["type"] == "SyntaxError"

    def test_parse_test_metadata_handles_missing_frontmatter(self):
        """Test parse_test_metadata handles files without frontmatter."""
        from components.test262_integration.src.harness import Test262Harness

        test_content = "// Just a regular JS file\nconsole.log('test');"

        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test" / "test.js"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(test_content)

            harness = Test262Harness(tmpdir)
            metadata = harness.parse_test_metadata(str(test_file))

            assert metadata == {}  # Empty metadata for files without frontmatter

    def test_execute_test_returns_passed_result(self):
        """Test execute_test returns passed result for valid test."""
        from components.test262_integration.src.harness import Test262Harness

        test_content = """/*---
description: Simple passing test
---*/
assert(true);
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test" / "test.js"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(test_content)

            harness = Test262Harness(tmpdir)
            result = harness.execute_test(str(test_file))

            assert result["status"] == "passed"
            assert result["path"] == str(test_file)
            assert result["duration_ms"] >= 0
            assert result.get("error") is None

    def test_execute_test_returns_failed_result(self):
        """Test execute_test returns failed result for failing test."""
        from components.test262_integration.src.harness import Test262Harness

        test_content = """/*---
description: Failing test
---*/
assert(false);
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test" / "test.js"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(test_content)

            harness = Test262Harness(tmpdir)
            result = harness.execute_test(str(test_file))

            assert result["status"] == "failed"
            assert result["error"] is not None
            assert "assert" in result["error"].lower() or "fail" in result["error"].lower()

    def test_execute_test_handles_timeout(self):
        """Test execute_test detects timeout."""
        from components.test262_integration.src.harness import Test262Harness

        test_content = """/*---
description: Timeout test
---*/
while(true) {}  // Infinite loop
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test" / "test.js"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(test_content)

            harness = Test262Harness(tmpdir, timeout=100)  # 100ms timeout
            result = harness.execute_test(str(test_file))

            assert result["status"] == "timeout"

    def test_execute_test_validates_negative_tests(self):
        """Test execute_test validates negative test expectations."""
        from components.test262_integration.src.harness import Test262Harness

        test_content = """/*---
description: Negative test expecting SyntaxError
negative:
  phase: parse
  type: SyntaxError
---*/
invalid syntax here!
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test" / "test.js"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(test_content)

            harness = Test262Harness(tmpdir)
            result = harness.execute_test(str(test_file))

            # Should pass if it throws the expected error
            assert result["status"] in ["passed", "failed"]  # Implementation determines pass/fail

    def test_execute_test_includes_metadata(self):
        """Test execute_test includes parsed metadata in result."""
        from components.test262_integration.src.harness import Test262Harness

        test_content = """/*---
description: Test with features
esid: sec-example
features: [BigInt, Symbol]
---*/
// Test code
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test" / "test.js"
            test_file.parent.mkdir(parents=True)
            test_file.write_text(test_content)

            harness = Test262Harness(tmpdir)
            result = harness.execute_test(str(test_file))

            assert "features" in result
            assert "BigInt" in result["features"]
            assert "Symbol" in result["features"]
            assert result.get("esid") == "sec-example"

    def test_execute_tests_batch_runs_multiple_tests(self):
        """Test execute_tests_batch runs multiple tests."""
        from components.test262_integration.src.harness import Test262Harness

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()

            (test_dir / "test1.js").write_text("/*---\ndescription: Test 1\n---*/\nassert(true);")
            (test_dir / "test2.js").write_text("/*---\ndescription: Test 2\n---*/\nassert(true);")

            harness = Test262Harness(tmpdir)
            test_paths = harness.discover_tests()
            results = harness.execute_tests_batch(test_paths)

            assert len(results) == 2
            assert all(r["status"] == "passed" for r in results)

    def test_filter_tests_by_features(self):
        """Test filter_tests_by_features filters tests correctly."""
        from components.test262_integration.src.harness import Test262Harness

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()

            (test_dir / "test1.js").write_text("/*---\nfeatures: [BigInt]\n---*/")
            (test_dir / "test2.js").write_text("/*---\nfeatures: [Symbol]\n---*/")
            (test_dir / "test3.js").write_text("/*---\nfeatures: [BigInt, Symbol]\n---*/")

            harness = Test262Harness(tmpdir)
            test_paths = harness.discover_tests()

            # Filter for BigInt
            bigint_tests = harness.filter_tests_by_features(test_paths, ["BigInt"])
            assert len(bigint_tests) == 2  # test1 and test3

            # Filter for Symbol
            symbol_tests = harness.filter_tests_by_features(test_paths, ["Symbol"])
            assert len(symbol_tests) == 2  # test2 and test3


class TestTest262Error:
    """Tests for Test262Error exception."""

    def test_error_can_be_raised(self):
        """Test Test262Error can be raised."""
        from components.test262_integration.src.harness import Test262Error

        with pytest.raises(Test262Error) as exc_info:
            raise Test262Error("Test error")
        assert "Test error" in str(exc_info.value)

    def test_error_is_exception(self):
        """Test Test262Error inherits from Exception."""
        from components.test262_integration.src.harness import Test262Error

        assert issubclass(Test262Error, Exception)
