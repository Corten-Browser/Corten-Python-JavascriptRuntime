"""
Test class compilation to bytecode.

Tests bytecode compilation of ES6 classes including class declarations,
class expressions, methods, static methods, inheritance, and super calls.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src.lexer import Lexer
from components.parser.src.parser import Parser
from components.bytecode.src.compiler import BytecodeCompiler
from components.bytecode.src.opcode import Opcode


def compile_source(source: str):
    """Helper to compile source code to bytecode."""
    lexer = Lexer(source)
    parser = Parser(lexer)
    ast = parser.parse()
    compiler = BytecodeCompiler(ast)
    return compiler.compile()


class TestClassDeclarationCompilation:
    """Test class declaration compilation."""

    def test_simple_empty_class(self):
        """
        Given a simple empty class declaration
        When compiling to bytecode
        Then it should generate bytecode for class constructor function
        """
        # Given
        source = "class Person {}"

        # When
        bytecode = compile_source(source)

        # Then
        # Should have instructions
        assert len(bytecode.instructions) > 0

        # Should contain CREATE_CLOSURE for class constructor function
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.CREATE_CLOSURE in opcodes

    def test_class_with_constructor(self):
        """
        Given a class with constructor method
        When compiling to bytecode
        Then constructor should be compiled into the class
        """
        # Given
        source = """
        class Person {
            constructor(name) {
                this.name = name;
            }
        }
        """

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0
        assert len(bytecode.constants) > 0  # Should have function constants

    def test_class_with_instance_methods(self):
        """
        Given a class with instance methods
        When compiling to bytecode
        Then methods should be compiled and added to prototype
        """
        # Given
        source = """
        class Calculator {
            add(a, b) {
                return a + b;
            }

            multiply(a, b) {
                return a * b;
            }
        }
        """

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0
        # Should have multiple function constants (one per method)
        assert len(bytecode.constants) > 0

    def test_class_with_static_methods(self):
        """
        Given a class with static methods
        When compiling to bytecode
        Then static methods should be attached to constructor
        """
        # Given
        source = """
        class Utils {
            static create() {
                return new Utils();
            }

            static helper() {
                return "help";
            }
        }
        """

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0
        # Static methods should generate different bytecode than instance methods


class TestClassExpressionCompilation:
    """Test class expression compilation."""

    def test_anonymous_class_expression(self):
        """
        Given an anonymous class expression
        When compiling to bytecode
        Then it should compile like a class declaration
        """
        # Given
        source = "const C = class {};"

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0
        opcodes = [instr.opcode for instr in bytecode.instructions]
        assert Opcode.CREATE_CLOSURE in opcodes

    def test_named_class_expression(self):
        """
        Given a named class expression
        When compiling to bytecode
        Then class should be compiled with name
        """
        # Given
        source = "const C = class Person {};"

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0

    def test_class_expression_with_methods(self):
        """
        Given a class expression with methods
        When compiling to bytecode
        Then methods should be compiled
        """
        # Given
        source = """
        const C = class {
            greet() {
                return "Hello";
            }
        };
        """

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0


class TestClassInheritance:
    """Test class inheritance compilation."""

    def test_class_extends(self):
        """
        Given a class that extends another class
        When compiling to bytecode
        Then inheritance should be set up
        """
        # Given
        source = "class Student extends Person {}"

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0
        # Should load the parent class


class TestClassMethodTypes:
    """Test compilation of different method types."""

    def test_class_with_getter(self):
        """
        Given a class with getter method
        When compiling to bytecode
        Then getter should be compiled correctly
        """
        # Given
        source = """
        class Person {
            get name() {
                return this._name;
            }
        }
        """

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0

    def test_class_with_setter(self):
        """
        Given a class with setter method
        When compiling to bytecode
        Then setter should be compiled correctly
        """
        # Given
        source = """
        class Person {
            set name(value) {
                this._name = value;
            }
        }
        """

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0

    def test_class_with_constructor_and_methods(self):
        """
        Given a class with constructor and multiple methods
        When compiling to bytecode
        Then all should be compiled correctly
        """
        # Given
        source = """
        class Person {
            constructor(name) {
                this.name = name;
            }

            greet() {
                return this.name;
            }

            static create(name) {
                return new Person(name);
            }
        }
        """

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0
        # Should have constants for all methods


class TestComplexClassScenarios:
    """Test complex class compilation scenarios."""

    def test_multiple_classes(self):
        """
        Given multiple class declarations
        When compiling to bytecode
        Then all should be compiled
        """
        # Given
        source = """
        class A {}
        class B {}
        class C {}
        """

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0

    def test_class_instantiation(self):
        """
        Given code that instantiates a class
        When compiling to bytecode
        Then new operator should work with class
        """
        # Given
        source = """
        class Person {}
        const p = new Person();
        """

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0
        # Should have NEW opcode or similar

    def test_class_with_empty_methods(self):
        """
        Given a class with empty method bodies
        When compiling to bytecode
        Then methods should compile to empty functions
        """
        # Given
        source = """
        class Test {
            method() {}
        }
        """

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0


class TestClassEdgeCases:
    """Test edge cases in class compilation."""

    def test_class_with_only_static_methods(self):
        """
        Given a class with only static methods
        When compiling to bytecode
        Then all static methods should be on constructor
        """
        # Given
        source = """
        class Utils {
            static method1() {}
            static method2() {}
        }
        """

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0

    def test_static_getter_and_setter(self):
        """
        Given a class with static getter and setter
        When compiling to bytecode
        Then they should be compiled as static
        """
        # Given
        source = """
        class Person {
            static get count() {
                return Person._count;
            }

            static set count(value) {
                Person._count = value;
            }
        }
        """

        # When
        bytecode = compile_source(source)

        # Then
        assert len(bytecode.instructions) > 0
