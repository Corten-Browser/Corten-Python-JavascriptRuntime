"""
Unit tests for EvaluationResult class.

Tests the result container for bytecode execution that can hold either
a successful value or an exception.
"""

import pytest
from components.value_system.src import Value


def test_evaluation_result_success_creation():
    """
    Given a successful value
    When creating an EvaluationResult
    Then result should be marked as success
    """
    from components.interpreter.src.evaluation_result import EvaluationResult

    # Given
    value = Value.from_smi(42)

    # When
    result = EvaluationResult(value=value)

    # Then
    assert result.is_success() is True
    assert result.is_exception() is False
    assert result.value == value
    assert result.exception is None


def test_evaluation_result_exception_creation():
    """
    Given an exception
    When creating an EvaluationResult
    Then result should be marked as exception
    """
    from components.interpreter.src.evaluation_result import EvaluationResult

    # Given
    exception = RuntimeError("Test error")

    # When
    result = EvaluationResult(exception=exception)

    # Then
    assert result.is_success() is False
    assert result.is_exception() is True
    assert result.value is None
    assert result.exception == exception


def test_evaluation_result_neither_value_nor_exception():
    """
    Given neither value nor exception
    When creating an EvaluationResult
    Then result should be marked as success with None value
    """
    from components.interpreter.src.evaluation_result import EvaluationResult

    # When
    result = EvaluationResult()

    # Then
    assert result.is_success() is True
    assert result.is_exception() is False
    assert result.value is None
    assert result.exception is None


def test_evaluation_result_value_access():
    """
    Given a successful result with value
    When accessing the value
    Then should return the stored value
    """
    from components.interpreter.src.evaluation_result import EvaluationResult

    # Given
    value = Value.from_smi(100)
    result = EvaluationResult(value=value)

    # When / Then
    assert result.value == value


def test_evaluation_result_exception_access():
    """
    Given an exception result
    When accessing the exception
    Then should return the stored exception
    """
    from components.interpreter.src.evaluation_result import EvaluationResult

    # Given
    exception = ValueError("Invalid value")
    result = EvaluationResult(exception=exception)

    # When / Then
    assert result.exception == exception
