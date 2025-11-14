"""Simplified Promise integration tests focusing on working functionality."""

import pytest
from components.parser.src import Parse
from components.bytecode.src import Compile
from components.interpreter.src import Execute
from components.promise.src import JSPromise, PromiseState


class TestPromiseBasics:
    """Test basic Promise functionality that's currently working."""

    def test_new_promise_construction(self):
        """Test that new Promise syntax works."""
        source = "new Promise((resolve, reject) => resolve(42))"

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()
        promise = result.value.to_object()
        assert isinstance(promise, JSPromise)

    def test_promise_in_variable(self):
        """Test Promise stored in variable."""
        source = "const p = new Promise((resolve) => resolve(100))"

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()

    def test_promise_resolve_static(self):
        """Test Promise.resolve() static method."""
        source = "Promise.resolve(42)"

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()
        promise = result.value.to_object()
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.FULFILLED
        assert promise.value.to_smi() == 42

    def test_promise_reject_static(self):
        """Test Promise.reject() static method."""
        source = 'Promise.reject("error")'

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()
        promise = result.value.to_object()
        assert isinstance(promise, JSPromise)
        assert promise.state == PromiseState.REJECTED
        assert promise.value.to_object() == "error"

    def test_promise_has_methods(self):
        """Test that Promise instances have expected methods."""
        source = "new Promise((resolve) => resolve(1))"

        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        assert result.is_success()
        promise = result.value.to_object()
        assert hasattr(promise, 'then')
        assert hasattr(promise, 'catch')
        assert callable(promise.then)
        assert callable(promise.catch)


class TestParserIntegration:
    """Test parser correctly handles Promise syntax."""

    def test_new_keyword_parsing(self):
        """Test NEW keyword is parsed correctly."""
        from components.parser.src.ast_nodes import NewExpression

        source = "new Promise()"
        ast = Parse(source)

        assert len(ast.body) == 1
        stmt = ast.body[0]
        assert hasattr(stmt, 'expression')
        assert isinstance(stmt.expression, NewExpression)

    def test_promise_static_method_parsing(self):
        """Test Promise.resolve parsing."""
        from components.parser.src.ast_nodes import MemberExpression, CallExpression

        source = "Promise.resolve(42)"
        ast = Parse(source)

        assert len(ast.body) == 1
        stmt = ast.body[0]
        expr = stmt.expression
        assert isinstance(expr, CallExpression)
        assert isinstance(expr.callee, MemberExpression)


class TestBytecodeIntegration:
    """Test bytecode generation for Promises."""

    def test_new_opcode_generated(self):
        """Test NEW opcode is generated."""
        from components.bytecode.src.opcode import Opcode

        source = "new Promise(() => {})"
        ast = Parse(source)
        bytecode = Compile(ast)

        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.NEW in opcodes

    def test_promise_static_method_bytecode(self):
        """Test Promise.resolve compiles to correct bytecode."""
        from components.bytecode.src.opcode import Opcode

        source = "Promise.resolve(42)"
        ast = Parse(source)
        bytecode = Compile(ast)

        opcodes = [instr.opcode for instr in bytecode.instructions]
        # Should have LOAD_GLOBAL, LOAD_PROPERTY, LOAD_CONSTANT, CALL_FUNCTION
        assert Opcode.LOAD_GLOBAL in opcodes
        assert Opcode.LOAD_PROPERTY in opcodes
        assert Opcode.CALL_FUNCTION in opcodes
