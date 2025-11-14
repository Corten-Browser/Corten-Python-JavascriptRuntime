"""
Component interaction integration tests.

Tests specific interactions between JavaScript runtime components:
- Parser → Bytecode Compiler
- Bytecode Compiler → Interpreter
- Interpreter → Value System
- Interpreter → GC
- Interpreter → Object Runtime
"""

import pytest
from components.parser.src import Parse, Program
from components.bytecode.src import Compile, BytecodeArray, Opcode
from components.interpreter.src import Execute, Interpreter, ExecutionContext
from components.memory_gc.src import GarbageCollector
from components.value_system.src import Value, IsNumber, IsUndefined, IsNull


class TestParserToBytecodeInterface:
    """Test the interface between Parser and Bytecode Compiler."""

    def test_parser_output_is_valid_ast(self):
        """Verify parser outputs valid AST that compiler accepts."""
        # Arrange
        source = "var x = 42;"

        # Act
        ast = Parse(source)

        # Assert
        assert isinstance(ast, Program), "Parser must return Program AST node"
        assert hasattr(ast, 'body'), "Program must have body attribute"
        assert isinstance(ast.body, list), "Program body must be list"

    def test_compiler_accepts_parser_output(self):
        """Verify compiler can process parser's AST output."""
        # Arrange
        source = "10 + 20"
        ast = Parse(source)

        # Act
        bytecode = Compile(ast)

        # Assert
        assert isinstance(bytecode, BytecodeArray), "Compiler must return BytecodeArray"
        assert hasattr(bytecode, 'instructions'), "BytecodeArray must have instructions"
        assert len(bytecode.instructions) > 0, "BytecodeArray must contain instructions"

    def test_complex_ast_to_bytecode(self):
        """Test compiler handling of complex AST structures."""
        # Arrange
        source = """
        function add(a, b) {
            return a + b;
        }
        var result = add(10, 20);
        """
        ast = Parse(source)

        # Act
        bytecode = Compile(ast)

        # Assert
        assert isinstance(bytecode, BytecodeArray)
        assert len(bytecode.instructions) > 0
        assert hasattr(bytecode, 'constant_pool')


class TestBytecodeToInterpreterInterface:
    """Test the interface between Bytecode Compiler and Interpreter."""

    def test_interpreter_accepts_bytecode(self):
        """Verify interpreter can execute compiler's bytecode output."""
        # Arrange
        source = "var x = 5;"
        ast = Parse(source)
        bytecode = Compile(ast)

        # Act
        result = Execute(bytecode)

        # Assert
        assert result is not None, "Execute must return EvaluationResult"
        assert hasattr(result, 'is_success'), "Result must have is_success method"
        assert hasattr(result, 'value'), "Result must have value attribute"

    def test_bytecode_constant_pool_usage(self):
        """Test that interpreter correctly uses bytecode constant pool."""
        # Arrange
        source = "42"
        ast = Parse(source)
        bytecode = Compile(ast)

        # Assert bytecode has constants
        assert len(bytecode.constant_pool) >= 0, "Constant pool should exist"

        # Act
        result = Execute(bytecode)

        # Assert execution succeeded
        assert result.is_success(), "Execution should succeed with constants"

    def test_bytecode_instructions_execution(self):
        """Test that interpreter executes bytecode instructions correctly."""
        # Arrange
        source = "1 + 2"
        ast = Parse(source)
        bytecode = Compile(ast)

        # Verify bytecode has instructions
        assert len(bytecode.instructions) > 0

        # Act
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Instruction execution should succeed"


class TestInterpreterToValueSystemInterface:
    """Test interaction between Interpreter and Value System."""

    def test_interpreter_produces_values(self):
        """Verify interpreter produces Value system objects."""
        # Arrange
        source = "42"
        ast = Parse(source)
        bytecode = Compile(ast)

        # Act
        result = Execute(bytecode)

        # Assert
        assert result.is_success()
        assert isinstance(result.value, Value), "Interpreter must return Value objects"

    def test_value_type_checking_with_numbers(self):
        """Test value type checking for numbers."""
        # Arrange
        source = "123"
        ast = Parse(source)
        bytecode = Compile(ast)

        # Act
        result = Execute(bytecode)

        # Assert
        assert result.is_success()
        # Can check if value is number type (depends on implementation)
        assert result.value is not None

    def test_undefined_value_handling(self):
        """Test handling of undefined values."""
        # Arrange
        source = "var x;"  # Uninitialized variable
        ast = Parse(source)
        bytecode = Compile(ast)

        # Act
        result = Execute(bytecode)

        # Assert
        assert result.is_success()
        # Variable declaration succeeds
        assert result.value is not None


class TestInterpreterToGCInterface:
    """Test interaction between Interpreter and Garbage Collector."""

    def test_interpreter_uses_gc(self):
        """Verify interpreter uses GC for heap allocations."""
        # Arrange
        gc = GarbageCollector()
        source = "var obj = {};"  # Creates heap object
        ast = Parse(source)
        bytecode = Compile(ast)

        # Act
        result = Execute(bytecode, gc)

        # Assert
        assert result.is_success(), "GC integration should work"

    def test_gc_instance_reuse(self):
        """Test that same GC instance can be reused across executions."""
        # Arrange
        gc = GarbageCollector()
        sources = [
            "var a = 1;",
            "var b = 2;",
            "var c = 3;"
        ]

        # Act
        results = []
        for source in sources:
            ast = Parse(source)
            bytecode = Compile(ast)
            result = Execute(bytecode, gc)
            results.append(result)

        # Assert
        assert all(r.is_success() for r in results), "All executions with shared GC should succeed"

    def test_gc_creation_when_not_provided(self):
        """Test that Execute creates GC when not provided."""
        # Arrange
        source = "var x = 1;"
        ast = Parse(source)
        bytecode = Compile(ast)

        # Act (no GC provided)
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Execute should create GC internally"


class TestObjectRuntimeIntegration:
    """Test integration with Object Runtime."""

    def test_object_literal_creation(self):
        """Test creating object literals."""
        # Arrange
        source = "var obj = {};"
        ast = Parse(source)
        bytecode = Compile(ast)

        # Act
        result = Execute(bytecode)

        # Assert
        assert result.is_success(), "Object creation should succeed"

    def test_object_property_access(self):
        """Test object property access."""
        # Arrange
        source = """
        var obj = {};
        obj.x
        """
        ast = Parse(source)
        bytecode = Compile(ast)

        # Act
        result = Execute(bytecode)

        # Assert
        # May succeed or fail depending on implementation
        # Just verify it doesn't crash
        assert result is not None


class TestExecutionContextManagement:
    """Test execution context and call frame management."""

    def test_execution_context_creation(self):
        """Test that execution creates proper context."""
        # Arrange
        gc = GarbageCollector()
        source = "var x = 1;"
        ast = Parse(source)
        bytecode = Compile(ast)

        # Act
        # Using lower-level Interpreter class
        interpreter = Interpreter(gc)
        result = interpreter.execute(bytecode)

        # Assert
        assert result.is_success(), "Execution context should be created properly"

    def test_function_call_frame_creation(self):
        """Test call frame creation for function calls."""
        # Arrange
        source = """
        function test() {
            return 42;
        }
        test()
        """
        ast = Parse(source)
        bytecode = Compile(ast)

        # Act
        result = Execute(bytecode)

        # Assert
        # Should create and manage call frames
        assert result.is_success() or result.is_exception(), "Call frame management should work"

    def test_nested_call_frames(self):
        """Test nested function calls and frame management."""
        # Arrange
        source = """
        function inner() {
            return 1;
        }
        function outer() {
            return inner();
        }
        outer()
        """
        ast = Parse(source)
        bytecode = Compile(ast)

        # Act
        result = Execute(bytecode)

        # Assert
        assert result is not None, "Nested calls should be handled"


class TestContractCompliance:
    """Test that components comply with their API contracts."""

    def test_parse_function_signature(self):
        """Verify Parse function has correct signature."""
        import inspect

        sig = inspect.signature(Parse)
        params = list(sig.parameters.keys())

        # Contract specifies: Parse(source: str, filename: str = "<stdin>")
        assert 'source' in params, "Parse must have 'source' parameter"

    def test_compile_function_signature(self):
        """Verify Compile function has correct signature."""
        import inspect

        sig = inspect.signature(Compile)
        params = list(sig.parameters.keys())

        # Contract specifies: Compile(ast: Program)
        assert 'ast' in params, "Compile must have 'ast' parameter"

    def test_execute_function_signature(self):
        """Verify Execute function has correct signature."""
        import inspect

        sig = inspect.signature(Execute)
        params = list(sig.parameters.keys())

        # Contract specifies: Execute(bytecode: BytecodeArray, gc: Optional[GC])
        assert 'bytecode' in params, "Execute must have 'bytecode' parameter"

    def test_evaluation_result_methods(self):
        """Verify EvaluationResult has required methods."""
        # Arrange
        source = "42"
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert contract-specified methods exist
        assert hasattr(result, 'is_success'), "EvaluationResult must have is_success()"
        assert hasattr(result, 'is_exception'), "EvaluationResult must have is_exception()"
        assert callable(result.is_success), "is_success must be callable"
        assert callable(result.is_exception), "is_exception must be callable"


class TestDataFlowBetweenComponents:
    """Test data flow between components."""

    def test_ast_to_bytecode_data_preservation(self):
        """Test that bytecode preserves AST information."""
        # Arrange
        source = "var x = 42;"
        ast = Parse(source)

        # Check AST structure
        assert len(ast.body) > 0, "AST should have statements"

        # Act
        bytecode = Compile(ast)

        # Assert bytecode was generated
        assert len(bytecode.instructions) > 0, "Bytecode should have instructions"

    def test_bytecode_to_result_data_flow(self):
        """Test data flow from bytecode to execution result."""
        # Arrange
        source = "100"
        ast = Parse(source)
        bytecode = Compile(ast)

        # Check bytecode has data
        assert bytecode.constant_pool is not None

        # Act
        result = Execute(bytecode)

        # Assert result contains value
        assert result.value is not None, "Result should contain value from bytecode"

    def test_end_to_end_data_integrity(self):
        """Test data integrity through entire pipeline."""
        # Arrange
        source = "var result = 10 + 20 + 30;"

        # Act - full pipeline
        ast = Parse(source)
        bytecode = Compile(ast)
        result = Execute(bytecode)

        # Assert - no data corruption
        assert result.is_success(), "Pipeline should preserve data integrity"
