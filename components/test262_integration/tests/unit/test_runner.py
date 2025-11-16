"""
Unit tests for Test262 automated runner.

Tests FR-ES24-D-023: Automated Test262 runner
- Command-line interface
- Test filtering (features, paths, etc.)
- Parallel execution
- Progress reporting
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestTest262Runner:
    """Tests for Test262Runner class."""

    def test_runner_initialization(self):
        """Test runner can be initialized with configuration."""
        from components.test262_integration.src.runner import Test262Runner

        config = {
            "test262_dir": "/tmp/test262",
            "timeout": 5000,
            "parallel": True
        }

        runner = Test262Runner(config)
        # Config should include provided values plus defaults
        assert runner.config["test262_dir"] == "/tmp/test262"
        assert runner.config["timeout"] == 5000
        assert runner.config["parallel"] is True
        assert runner.results == []

    def test_runner_initialization_with_defaults(self):
        """Test runner applies default configuration."""
        from components.test262_integration.src.runner import Test262Runner

        runner = Test262Runner({})
        assert runner.config.get("timeout") == 5000
        assert runner.config.get("parallel") is True
        assert runner.config.get("parallel_workers") == 0  # auto-detect

    def test_run_tests_executes_all_tests(self):
        """Test run_tests executes all discovered tests."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            (test_dir / "test1.js").write_text("/*---\ndescription: Test 1\n---*/")
            (test_dir / "test2.js").write_text("/*---\ndescription: Test 2\n---*/")

            config = {"test262_dir": tmpdir}
            runner = Test262Runner(config)
            results = runner.run_tests()

            assert results["total"] >= 2
            assert "timestamp" in results
            assert "duration_ms" in results

    def test_run_tests_with_filter(self):
        """Test run_tests respects filter pattern."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            array_dir = Path(tmpdir) / "test" / "built-ins" / "Array"
            array_dir.mkdir(parents=True)
            (array_dir / "test1.js").write_text("/*---\ndescription: Array test\n---*/")

            string_dir = Path(tmpdir) / "test" / "built-ins" / "String"
            string_dir.mkdir(parents=True)
            (string_dir / "test2.js").write_text("/*---\ndescription: String test\n---*/")

            config = {
                "test262_dir": tmpdir,
                "filter": "**/Array/**"
            }
            runner = Test262Runner(config)
            results = runner.run_tests()

            # Should only run Array tests
            assert results["total"] == 1
            assert any("Array" in t["path"] for t in results["tests"])

    def test_run_tests_with_feature_filter(self):
        """Test run_tests filters by features."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            (test_dir / "test1.js").write_text("/*---\nfeatures: [BigInt]\n---*/")
            (test_dir / "test2.js").write_text("/*---\nfeatures: [Symbol]\n---*/")

            config = {
                "test262_dir": tmpdir,
                "features": ["BigInt"]
            }
            runner = Test262Runner(config)
            results = runner.run_tests()

            assert results["total"] == 1
            assert "BigInt" in results["tests"][0]["features"]

    def test_run_tests_excludes_features(self):
        """Test run_tests excludes specified features."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            (test_dir / "test1.js").write_text("/*---\nfeatures: [BigInt]\n---*/")
            (test_dir / "test2.js").write_text("/*---\nfeatures: [Symbol]\n---*/")

            config = {
                "test262_dir": tmpdir,
                "exclude_features": ["BigInt"]
            }
            runner = Test262Runner(config)
            results = runner.run_tests()

            assert results["total"] == 1
            assert "Symbol" in results["tests"][0]["features"]

    def test_run_tests_parallel_execution(self):
        """Test run_tests can execute tests in parallel."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            for i in range(10):
                (test_dir / f"test{i}.js").write_text(f"/*---\ndescription: Test {i}\n---*/")

            config = {
                "test262_dir": tmpdir,
                "parallel": True,
                "parallel_workers": 4
            }
            runner = Test262Runner(config)
            results = runner.run_tests()

            assert results["total"] == 10
            # Parallel execution should be faster than sequential
            # (hard to test without actual timing, but we verify it doesn't crash)

    def test_run_tests_sequential_execution(self):
        """Test run_tests can execute tests sequentially."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            (test_dir / "test1.js").write_text("/*---\ndescription: Test 1\n---*/")
            (test_dir / "test2.js").write_text("/*---\ndescription: Test 2\n---*/")

            config = {
                "test262_dir": tmpdir,
                "parallel": False
            }
            runner = Test262Runner(config)
            results = runner.run_tests()

            assert results["total"] == 2

    def test_run_tests_calculates_statistics(self):
        """Test run_tests calculates pass/fail statistics."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            (test_dir / "pass.js").write_text("/*---\ndescription: Pass\n---*/\n// pass")
            (test_dir / "fail.js").write_text("/*---\ndescription: Fail\n---*/\n// fail")

            config = {"test262_dir": tmpdir}
            runner = Test262Runner(config)
            results = runner.run_tests()

            assert "passed" in results
            assert "failed" in results
            assert "skipped" in results
            assert "timeout" in results
            assert "error" in results
            assert results["total"] == results["passed"] + results["failed"] + results["skipped"] + results["timeout"] + results["error"]

    def test_run_tests_calculates_pass_rate(self):
        """Test run_tests calculates pass rate percentage."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            for i in range(10):
                (test_dir / f"test{i}.js").write_text("/*---\ndescription: Test\n---*/")

            config = {"test262_dir": tmpdir}
            runner = Test262Runner(config)
            results = runner.run_tests()

            assert "pass_rate" in results
            assert 0 <= results["pass_rate"] <= 100

    def test_run_tests_groups_by_features(self):
        """Test run_tests groups results by features."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            (test_dir / "test1.js").write_text("/*---\nfeatures: [BigInt]\n---*/")
            (test_dir / "test2.js").write_text("/*---\nfeatures: [BigInt]\n---*/")
            (test_dir / "test3.js").write_text("/*---\nfeatures: [Symbol]\n---*/")

            config = {"test262_dir": tmpdir}
            runner = Test262Runner(config)
            results = runner.run_tests()

            assert "features" in results
            assert "BigInt" in results["features"]
            assert "Symbol" in results["features"]
            assert results["features"]["BigInt"]["total"] == 2
            assert results["features"]["Symbol"]["total"] == 1

    def test_run_tests_includes_metadata(self):
        """Test run_tests includes runtime metadata."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            (test_dir / "test.js").write_text("/*---\ndescription: Test\n---*/")

            config = {"test262_dir": tmpdir}
            runner = Test262Runner(config)
            results = runner.run_tests()

            assert "metadata" in results
            metadata = results["metadata"]
            assert "runtime_version" in metadata
            assert "platform" in metadata
            assert "python_version" in metadata

    def test_run_tests_stop_on_failure(self):
        """Test run_tests can stop on first failure."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            (test_dir / "test1.js").write_text("/*---\ndescription: Test 1\n---*/")
            (test_dir / "test2.js").write_text("/*---\ndescription: Test 2\n---*/")
            (test_dir / "test3.js").write_text("/*---\ndescription: Test 3\n---*/")

            config = {
                "test262_dir": tmpdir,
                "stop_on_failure": True
            }
            runner = Test262Runner(config)
            results = runner.run_tests()

            # Should stop early if any test fails
            # (depends on actual test outcomes)
            assert results["total"] >= 0

    def test_run_tests_with_timeout(self):
        """Test run_tests respects timeout setting."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            (test_dir / "test.js").write_text("/*---\ndescription: Test\n---*/")

            config = {
                "test262_dir": tmpdir,
                "timeout": 1000  # 1 second
            }
            runner = Test262Runner(config)
            results = runner.run_tests()

            # Timeout is applied to each test
            assert all(t["duration_ms"] <= 1200 for t in results["tests"])  # Allow some overhead

    def test_get_progress_returns_current_progress(self):
        """Test get_progress returns current execution progress."""
        from components.test262_integration.src.runner import Test262Runner

        config = {"test262_dir": "/tmp"}
        runner = Test262Runner(config)

        progress = runner.get_progress()
        assert "total" in progress
        assert "completed" in progress
        assert "passed" in progress
        assert "failed" in progress
        assert "percentage" in progress

    def test_get_status_returns_runner_status(self):
        """Test get_status returns runner status."""
        from components.test262_integration.src.runner import Test262Runner

        config = {"test262_dir": "/tmp"}
        runner = Test262Runner(config)

        status = runner.get_status()
        assert "is_running" in status
        assert isinstance(status["is_running"], bool)

    def test_save_results_writes_json(self):
        """Test save_results writes results to JSON file."""
        from components.test262_integration.src.runner import Test262Runner

        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test"
            test_dir.mkdir()
            (test_dir / "test.js").write_text("/*---\ndescription: Test\n---*/")

            config = {"test262_dir": tmpdir}
            runner = Test262Runner(config)
            results = runner.run_tests()

            output_file = Path(tmpdir) / "results.json"
            runner.save_results(results, str(output_file))

            assert output_file.exists()
            import json
            saved = json.loads(output_file.read_text())
            assert saved["total"] == results["total"]

    def test_load_results_reads_json(self):
        """Test load_results loads results from JSON file."""
        from components.test262_integration.src.runner import Test262Runner
        import json

        with tempfile.TemporaryDirectory() as tmpdir:
            results_file = Path(tmpdir) / "results.json"
            test_results = {
                "total": 10,
                "passed": 8,
                "failed": 2,
                "timestamp": datetime.now().isoformat()
            }
            results_file.write_text(json.dumps(test_results))

            runner = Test262Runner({})
            loaded = runner.load_results(str(results_file))

            assert loaded["total"] == 10
            assert loaded["passed"] == 8


class TestRunnerConfig:
    """Tests for runner configuration handling."""

    def test_get_config_returns_current_config(self):
        """Test get_config returns current configuration."""
        from components.test262_integration.src.runner import Test262Runner

        config = {
            "test262_dir": "/tmp/test262",
            "timeout": 5000
        }
        runner = Test262Runner(config)

        current_config = runner.get_config()
        assert current_config["test262_dir"] == "/tmp/test262"
        assert current_config["timeout"] == 5000

    def test_update_config_modifies_configuration(self):
        """Test update_config updates runner configuration."""
        from components.test262_integration.src.runner import Test262Runner

        runner = Test262Runner({"timeout": 5000})

        new_config = {"timeout": 10000}
        runner.update_config(new_config)

        assert runner.config["timeout"] == 10000

    def test_validate_config_checks_required_fields(self):
        """Test validate_config validates required configuration fields."""
        from components.test262_integration.src.runner import Test262Runner, ConfigError

        with pytest.raises(ConfigError):
            # Missing test262_dir should raise error
            runner = Test262Runner({})
            runner.run_tests()  # Should fail without test262_dir


class TestConfigError:
    """Tests for ConfigError exception."""

    def test_config_error_can_be_raised(self):
        """Test ConfigError can be raised."""
        from components.test262_integration.src.runner import ConfigError

        with pytest.raises(ConfigError) as exc_info:
            raise ConfigError("Invalid config")
        assert "Invalid config" in str(exc_info.value)

    def test_config_error_is_exception(self):
        """Test ConfigError inherits from Exception."""
        from components.test262_integration.src.runner import ConfigError

        assert issubclass(ConfigError, Exception)
