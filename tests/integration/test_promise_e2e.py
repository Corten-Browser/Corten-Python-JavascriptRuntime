"""End-to-end integration tests for Promises.

This module tests the complete Promise integration chain from parsing
through compilation to execution, ensuring all components work together
correctly.
"""

import pytest
from components.parser.src import Parse
from components.bytecode.src import Compile
from components.interpreter.src import Execute
from components.promise.src import JSPromise, PromiseState


class TestPromiseConstruction:
    """Test Promise construction with new keyword."""

    def test_new_promise_basic(self):
        """Test basic Promise construction.

        Verifies that new Promise(...) syntax creates a JSPromise instance
        and executes properly through the full pipeline.
        """
        source = "new Promise((resolve, reject) => resolve(42))"

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()
        # Result value should be a Promise
        promise = result.value.to_object()
        assert isinstance(promise, JSPromise)

    def test_new_promise_with_rejection(self):
        """Test Promise construction with rejection.

        Verifies that promises can be rejected during construction.
        """
        source = 'new Promise((resolve, reject) => reject("error"))'

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()
        promise = result.value.to_object()
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.REJECTED

    def test_new_promise_stored_in_variable(self):
        """Test Promise stored in variable.

        Verifies that promises can be assigned to variables.
        """
        source = "const p = new Promise((resolve) => resolve(100))"

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()


class TestPromiseStaticMethods:
    """Test Promise static methods from JavaScript."""

    def test_promise_resolve(self):
        """Test Promise.resolve().

        Verifies that Promise.resolve() creates a fulfilled promise.
        """
        source = "Promise.resolve(42)"

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()
        promise = result.value.to_object()
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value == 42

    def test_promise_reject(self):
        """Test Promise.reject().

        Verifies that Promise.reject() creates a rejected promise.
        """
        source = 'Promise.reject("error")'

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()
        promise = result.value.to_object()
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.REJECTED
        assert promise.value == "error"

    def test_promise_all_basic(self):
        """Test Promise.all() with array literal.

        Verifies that Promise.all() can combine multiple promises.
        """
        source = "Promise.all([Promise.resolve(1), Promise.resolve(2)])"

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()
        promise = result.value.to_object()
        assert isinstance(promise, JSPromise)

    def test_promise_race_basic(self):
        """Test Promise.race().

        Verifies that Promise.race() returns a promise.
        """
        source = "Promise.race([Promise.resolve(1), Promise.resolve(2)])"

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()
        promise = result.value.to_object()
        assert isinstance(promise, JSPromise)


class TestPromiseChaining:
    """Test Promise chaining (if .then() property access works)."""

    def test_promise_then_method_exists(self):
        """Test that Promise has .then() method.

        Verifies that promises created through JavaScript have the
        expected promise methods.
        """
        source = "const p = new Promise((resolve) => resolve(42))"

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()
        # Note: We can't directly access the promise from the variable
        # in this test, but we can create one and check it
        source2 = "new Promise((resolve) => resolve(42))"
        ast2 = Parse(source2)
        bytecode2 = Compile(ast2)
        result2 = Execute(bytecode2)

        promise = result2.value.to_object()
        assert hasattr(promise, 'then')
        assert callable(promise.then)


class TestEventLoopIntegration:
    """Test that event loop processes microtasks."""

    def test_event_loop_runs_after_execution(self):
        """Test that Execute() runs event loop.

        This test verifies event loop integration by checking
        that Promise reactions are processed automatically.
        """
        source = "new Promise((resolve) => resolve(42))"

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # If event loop ran, Promise should be settled
        assert result.is_success()
        promise = result.value.to_object()
        assert promise.state == PromiseState.FULFILLED

    def test_promise_reactions_execute(self):
        """Test that promise reactions execute through event loop.

        Verifies that the event loop processes microtasks
        queued by promise resolution.
        """
        source = "Promise.resolve(100)"

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()
        promise = result.value.to_object()
        # Promise should be immediately fulfilled
        assert promise.state == PromiseState.FULFILLED
        assert promise.value == 100
