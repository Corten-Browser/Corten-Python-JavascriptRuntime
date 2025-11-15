"""
Unit tests for Promise implementation
"""
import pytest
from components.top_level_await.src.top_level_await_manager import Promise


class TestPromise:
    """Test Promise implementation"""

    def test_promise_init_no_executor(self):
        """Test creating promise without executor"""
        promise = Promise()
        assert promise is not None
        assert promise._state == 'pending'

    def test_promise_init_with_executor(self):
        """Test creating promise with executor"""
        executed = False

        def executor(resolve, reject):
            nonlocal executed
            executed = True
            resolve("value")

        promise = Promise(executor)
        assert executed is True
        assert promise._state == 'fulfilled'

    def test_promise_resolve(self):
        """Test promise resolution"""
        result = None

        def executor(resolve, reject):
            resolve("test_value")

        promise = Promise(executor)

        def on_fulfilled(value):
            nonlocal result
            result = value

        promise.then(on_fulfilled)
        assert result == "test_value"

    def test_promise_reject(self):
        """Test promise rejection"""
        error_result = None

        def executor(resolve, reject):
            reject(Exception("test_error"))

        promise = Promise(executor)

        def on_rejected(error):
            nonlocal error_result
            error_result = error

        promise.catch(on_rejected)
        assert error_result is not None
        assert str(error_result) == "test_error"

    def test_promise_then_with_fulfilled_state(self):
        """Test then on already fulfilled promise"""
        result = None

        def executor(resolve, reject):
            resolve("immediate")

        promise = Promise(executor)

        def on_fulfilled(value):
            nonlocal result
            result = value

        promise.then(on_fulfilled)
        assert result == "immediate"

    def test_promise_then_with_rejected_state(self):
        """Test then on already rejected promise"""
        error_result = None

        def executor(resolve, reject):
            reject(Exception("immediate_error"))

        promise = Promise(executor)

        def on_rejected(error):
            nonlocal error_result
            error_result = error

        promise.then(None, on_rejected)
        assert error_result is not None

    def test_promise_executor_exception(self):
        """Test promise with executor that throws exception"""
        def executor(resolve, reject):
            raise Exception("executor_error")

        promise = Promise(executor)
        assert promise._state == 'rejected'
        assert promise._error is not None

    def test_promise_callback_exception_handling(self):
        """Test that callback exceptions don't break promise"""
        def executor(resolve, reject):
            resolve("value")

        promise = Promise(executor)

        def bad_callback(value):
            raise Exception("callback_error")

        # Should not raise even if callback throws
        promise.then(bad_callback)
        assert promise._state == 'fulfilled'

    def test_promise_multiple_then_callbacks(self):
        """Test multiple then callbacks"""
        results = []

        promise = Promise()

        def callback1(value):
            results.append(value + "_1")

        def callback2(value):
            results.append(value + "_2")

        promise.then(callback1)
        promise.then(callback2)

        promise._resolve("test")

        assert len(results) == 2
        assert "test_1" in results
        assert "test_2" in results

    def test_promise_catch_method(self):
        """Test catch method"""
        error_caught = None

        promise = Promise()

        def on_error(error):
            nonlocal error_caught
            error_caught = error

        promise.catch(on_error)
        promise._reject(Exception("caught_error"))

        assert error_caught is not None
        assert str(error_caught) == "caught_error"

    def test_promise_then_returns_self(self):
        """Test that then returns promise for chaining"""
        promise = Promise()
        result = promise.then(lambda x: x)
        assert result is promise

    def test_promise_catch_returns_promise(self):
        """Test that catch returns promise for chaining"""
        promise = Promise()
        result = promise.catch(lambda x: x)
        assert result is promise

    def test_promise_reject_callback_exception_handling(self):
        """Test that reject callback exceptions don't break promise"""
        def executor(resolve, reject):
            reject(Exception("test_error"))

        promise = Promise(executor)

        def bad_callback(error):
            raise Exception("callback_error")

        # Should not raise even if callback throws
        promise.catch(bad_callback)
        assert promise._state == 'rejected'
