"""
Unit tests for AggregateError (FR-ES24-B-015, FR-ES24-B-016)

Requirements:
- FR-ES24-B-015: AggregateError - Error for multiple failures
- FR-ES24-B-016: AggregateError.errors property - Array of aggregated errors
"""

import pytest
from components.error_extensions.src.aggregate_error import AggregateError, create_aggregate_error


class TestAggregateErrorBasics:
    """Test AggregateError construction and basic properties."""

    def test_aggregate_error_construction_with_array(self):
        """Test creating AggregateError with array of errors."""
        errors = [ValueError("error1"), TypeError("error2"), RuntimeError("error3")]
        agg_error = AggregateError(errors, "Multiple errors occurred")

        assert agg_error.message == "Multiple errors occurred"
        assert agg_error.name == "AggregateError"
        assert len(agg_error.errors) == 3
        assert agg_error.errors[0] == errors[0]
        assert agg_error.errors[1] == errors[1]
        assert agg_error.errors[2] == errors[2]

    def test_aggregate_error_construction_with_empty_array(self):
        """Test creating AggregateError with empty error array."""
        agg_error = AggregateError([], "No errors")

        assert agg_error.message == "No errors"
        assert agg_error.name == "AggregateError"
        assert len(agg_error.errors) == 0
        assert agg_error.errors == []

    def test_aggregate_error_construction_default_message(self):
        """Test creating AggregateError with default empty message."""
        errors = [ValueError("error1")]
        agg_error = AggregateError(errors)

        assert agg_error.message == ""
        assert len(agg_error.errors) == 1

    def test_aggregate_error_with_cause(self):
        """Test creating AggregateError with cause option."""
        root_cause = ValueError("root cause")
        errors = [TypeError("error1"), RuntimeError("error2")]
        agg_error = AggregateError(errors, "Multiple errors", {"cause": root_cause})

        assert agg_error.cause == root_cause
        assert len(agg_error.errors) == 2
        assert agg_error.message == "Multiple errors"

    def test_aggregate_error_errors_property_is_array(self):
        """Test that errors property returns an array."""
        errors = [ValueError("error1"), TypeError("error2")]
        agg_error = AggregateError(errors)

        assert isinstance(agg_error.errors, list)
        assert len(agg_error.errors) == 2


class TestAggregateErrorErrorsProperty:
    """Test AggregateError.errors property behavior."""

    def test_errors_property_is_read_only(self):
        """Test that errors property cannot be reassigned."""
        errors = [ValueError("error1")]
        agg_error = AggregateError(errors, "Test")

        # Attempting to set errors should either raise or be ignored
        with pytest.raises((AttributeError, TypeError)):
            agg_error.errors = []

    def test_errors_property_is_copy_not_reference(self):
        """Test that errors property returns a copy, not a reference."""
        errors = [ValueError("error1"), TypeError("error2")]
        agg_error = AggregateError(errors, "Test")

        # Modifying the original array should not affect the error's errors
        errors.append(RuntimeError("error3"))

        assert len(agg_error.errors) == 2

    def test_errors_property_array_is_sealed(self):
        """Test that the errors array itself cannot be modified."""
        errors = [ValueError("error1"), TypeError("error2")]
        agg_error = AggregateError(errors, "Test")

        # The array should be sealed/frozen
        original_length = len(agg_error.errors)
        errors_ref = agg_error.errors

        # Try to modify (should fail or be ignored)
        try:
            errors_ref.append(RuntimeError("error3"))
        except (AttributeError, TypeError):
            pass  # Expected for immutable array

        # Check that the errors property still has original length
        assert len(agg_error.errors) == original_length

    def test_errors_property_preserves_error_order(self):
        """Test that errors property preserves insertion order."""
        errors = [
            ValueError("error1"),
            TypeError("error2"),
            RuntimeError("error3"),
            KeyError("error4")
        ]
        agg_error = AggregateError(errors, "Test")

        for i, error in enumerate(agg_error.errors):
            assert error == errors[i]


class TestAggregateErrorIterable:
    """Test AggregateError construction with different iterables."""

    def test_aggregate_error_with_tuple(self):
        """Test creating AggregateError with tuple of errors."""
        errors = (ValueError("error1"), TypeError("error2"))
        agg_error = AggregateError(errors, "Test")

        assert len(agg_error.errors) == 2
        assert agg_error.errors[0] == errors[0]
        assert agg_error.errors[1] == errors[1]

    def test_aggregate_error_with_generator(self):
        """Test creating AggregateError with generator."""
        def error_generator():
            yield ValueError("error1")
            yield TypeError("error2")
            yield RuntimeError("error3")

        agg_error = AggregateError(error_generator(), "Test")

        assert len(agg_error.errors) == 3
        assert isinstance(agg_error.errors[0], ValueError)
        assert isinstance(agg_error.errors[1], TypeError)
        assert isinstance(agg_error.errors[2], RuntimeError)

    def test_aggregate_error_with_set(self):
        """Test creating AggregateError with set of errors."""
        errors = {ValueError("error1"), TypeError("error2")}
        agg_error = AggregateError(errors, "Test")

        # Set order is not guaranteed, but all errors should be present
        assert len(agg_error.errors) == 2

    def test_aggregate_error_with_non_iterable_raises_error(self):
        """Test that non-iterable errors raises TypeError."""
        with pytest.raises(TypeError, match="is not iterable"):
            AggregateError(42, "Test")

    def test_aggregate_error_with_none_raises_error(self):
        """Test that None errors raises TypeError."""
        with pytest.raises(TypeError, match="is not iterable"):
            AggregateError(None, "Test")


class TestAggregateErrorMixedValues:
    """Test AggregateError with mixed error and non-error values."""

    def test_aggregate_error_with_non_error_objects(self):
        """Test that AggregateError accepts non-Error objects."""
        errors = [ValueError("error1"), "string error", 42, {"error": "object"}]
        agg_error = AggregateError(errors, "Mixed errors")

        assert len(agg_error.errors) == 4
        assert agg_error.errors[0] == errors[0]
        assert agg_error.errors[1] == "string error"
        assert agg_error.errors[2] == 42
        assert agg_error.errors[3] == {"error": "object"}

    def test_aggregate_error_with_none_values(self):
        """Test that AggregateError accepts None as an error value."""
        errors = [ValueError("error1"), None, TypeError("error2")]
        agg_error = AggregateError(errors, "Test")

        assert len(agg_error.errors) == 3
        assert agg_error.errors[1] is None


class TestAggregateErrorToString:
    """Test AggregateError string representation."""

    def test_aggregate_error_to_string_with_message(self):
        """Test toString returns name and message."""
        agg_error = AggregateError([ValueError("e1")], "Multiple errors occurred")
        result = agg_error.toString()

        assert "AggregateError" in result
        assert "Multiple errors occurred" in result

    def test_aggregate_error_to_string_without_message(self):
        """Test toString with empty message."""
        agg_error = AggregateError([ValueError("e1")])
        result = agg_error.toString()

        assert "AggregateError" in result

    def test_aggregate_error_str_representation(self):
        """Test __str__ method."""
        agg_error = AggregateError([ValueError("e1")], "Test error")
        str_repr = str(agg_error)

        assert "AggregateError" in str_repr
        assert "Test error" in str_repr


class TestAggregateErrorStack:
    """Test AggregateError has stack property."""

    def test_aggregate_error_has_stack_property(self):
        """Test that AggregateError has stack property."""
        agg_error = AggregateError([ValueError("e1")], "Test")

        assert hasattr(agg_error, "stack")
        assert isinstance(agg_error.stack, str)

    def test_aggregate_error_stack_contains_error_name(self):
        """Test that stack trace contains error name."""
        agg_error = AggregateError([ValueError("e1")], "Test error")

        assert "AggregateError" in agg_error.stack


class TestCreateAggregateErrorFactory:
    """Test create_aggregate_error factory function."""

    def test_create_aggregate_error_basic(self):
        """Test factory function creates AggregateError."""
        errors = [ValueError("e1"), TypeError("e2")]
        agg_error = create_aggregate_error(errors, "Test", {})

        assert isinstance(agg_error, AggregateError)
        assert len(agg_error.errors) == 2
        assert agg_error.message == "Test"

    def test_create_aggregate_error_with_cause(self):
        """Test factory function with cause option."""
        root_cause = ValueError("root")
        agg_error = create_aggregate_error([TypeError("e1")], "Test", {"cause": root_cause})

        assert agg_error.cause == root_cause


class TestAggregateErrorPerformance:
    """Test AggregateError performance requirements."""

    def test_aggregate_error_construction_performance(self):
        """Test AggregateError construction meets <1ms requirement for 100 errors."""
        import time

        errors = [ValueError(f"error{i}") for i in range(100)]

        start = time.perf_counter()
        agg_error = AggregateError(errors, "Performance test")
        end = time.perf_counter()

        elapsed_ms = (end - start) * 1000

        # Should be well under 1ms
        assert elapsed_ms < 1.0
        assert len(agg_error.errors) == 100
