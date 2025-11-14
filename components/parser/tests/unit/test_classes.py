"""
Test class parsing functionality.

Tests parsing of ES6 class declarations, class expressions, methods,
inheritance, and class-related features.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src.lexer import Lexer
from components.parser.src.parser import Parser
from components.parser.src.ast_nodes import (
    Program,
    ClassDeclaration,
    ClassExpression,
    MethodDefinition,
    Identifier,
    FunctionExpression,
    BlockStatement,
    VariableDeclaration,
    VariableDeclarator,
    ReturnStatement,
    ExpressionStatement,
)


class TestClassDeclaration:
    """Test class declaration parsing."""

    def test_simple_class_declaration(self):
        """
        Given a simple class declaration
        When parsing the code
        Then a ClassDeclaration node should be created
        """
        # Given
        source = "class Person {}"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        assert isinstance(program, Program)
        assert len(program.body) == 1
        assert isinstance(program.body[0], ClassDeclaration)
        class_decl = program.body[0]
        assert isinstance(class_decl.id, Identifier)
        assert class_decl.id.name == "Person"
        assert class_decl.superClass is None
        assert class_decl.body == []

    def test_class_with_constructor(self):
        """
        Given a class with constructor method
        When parsing the code
        Then the constructor should be in the class body
        """
        # Given
        source = """
        class Person {
            constructor(name) {
                this.name = name;
            }
        }
        """
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        class_decl = program.body[0]
        assert isinstance(class_decl, ClassDeclaration)
        assert len(class_decl.body) == 1

        method = class_decl.body[0]
        assert isinstance(method, MethodDefinition)
        assert method.kind == "constructor"
        assert isinstance(method.key, Identifier)
        assert method.key.name == "constructor"
        assert method.static is False
        assert method.computed is False
        assert isinstance(method.value, FunctionExpression)
        assert method.value.parameters == ["name"]

    def test_class_with_instance_methods(self):
        """
        Given a class with instance methods
        When parsing the code
        Then all methods should be in the class body
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
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        class_decl = program.body[0]
        assert len(class_decl.body) == 2

        # First method
        add_method = class_decl.body[0]
        assert isinstance(add_method, MethodDefinition)
        assert add_method.kind == "method"
        assert add_method.key.name == "add"
        assert add_method.static is False
        assert add_method.value.parameters == ["a", "b"]

        # Second method
        multiply_method = class_decl.body[1]
        assert multiply_method.kind == "method"
        assert multiply_method.key.name == "multiply"
        assert multiply_method.static is False

    def test_class_with_static_methods(self):
        """
        Given a class with static methods
        When parsing the code
        Then static methods should be marked as static
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
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        class_decl = program.body[0]
        assert len(class_decl.body) == 2

        create_method = class_decl.body[0]
        assert create_method.kind == "method"
        assert create_method.key.name == "create"
        assert create_method.static is True

        helper_method = class_decl.body[1]
        assert helper_method.kind == "method"
        assert helper_method.key.name == "helper"
        assert helper_method.static is True

    def test_class_with_inheritance(self):
        """
        Given a class that extends another class
        When parsing the code
        Then the superClass should be set
        """
        # Given
        source = "class Student extends Person {}"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        class_decl = program.body[0]
        assert isinstance(class_decl, ClassDeclaration)
        assert class_decl.id.name == "Student"
        assert class_decl.superClass is not None
        assert isinstance(class_decl.superClass, Identifier)
        assert class_decl.superClass.name == "Person"

    def test_class_with_getters(self):
        """
        Given a class with getter methods
        When parsing the code
        Then getters should have kind='get'
        """
        # Given
        source = """
        class Person {
            get name() {
                return this._name;
            }
        }
        """
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        class_decl = program.body[0]
        assert len(class_decl.body) == 1

        getter = class_decl.body[0]
        assert isinstance(getter, MethodDefinition)
        assert getter.kind == "get"
        assert getter.key.name == "name"
        assert getter.static is False
        assert getter.value.parameters == []  # Getters have no parameters

    def test_class_with_setters(self):
        """
        Given a class with setter methods
        When parsing the code
        Then setters should have kind='set'
        """
        # Given
        source = """
        class Person {
            set name(value) {
                this._name = value;
            }
        }
        """
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        class_decl = program.body[0]
        assert len(class_decl.body) == 1

        setter = class_decl.body[0]
        assert isinstance(setter, MethodDefinition)
        assert setter.kind == "set"
        assert setter.key.name == "name"
        assert setter.static is False
        assert setter.value.parameters == ["value"]  # Setters have one parameter


class TestClassExpression:
    """Test class expression parsing."""

    def test_anonymous_class_expression(self):
        """
        Given an anonymous class expression
        When parsing the code
        Then ClassExpression with id=None should be created
        """
        # Given
        source = "const C = class {};"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        assert isinstance(program.body[0], VariableDeclaration)
        var_decl = program.body[0].declarations[0]
        assert isinstance(var_decl.init, ClassExpression)
        class_expr = var_decl.init
        assert class_expr.id is None
        assert class_expr.superClass is None
        assert class_expr.body == []

    def test_named_class_expression(self):
        """
        Given a named class expression
        When parsing the code
        Then ClassExpression with id should be created
        """
        # Given
        source = "const C = class Person {};"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        var_decl = program.body[0].declarations[0]
        class_expr = var_decl.init
        assert isinstance(class_expr, ClassExpression)
        assert isinstance(class_expr.id, Identifier)
        assert class_expr.id.name == "Person"

    def test_class_expression_with_extends(self):
        """
        Given a class expression with extends
        When parsing the code
        Then superClass should be set
        """
        # Given
        source = "const S = class Student extends Person {};"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        var_decl = program.body[0].declarations[0]
        class_expr = var_decl.init
        assert isinstance(class_expr, ClassExpression)
        assert class_expr.superClass is not None
        assert isinstance(class_expr.superClass, Identifier)
        assert class_expr.superClass.name == "Person"

    def test_class_expression_with_methods(self):
        """
        Given a class expression with methods
        When parsing the code
        Then methods should be in the class body
        """
        # Given
        source = """
        const C = class {
            greet() {
                return "Hello";
            }
        };
        """
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        var_decl = program.body[0].declarations[0]
        class_expr = var_decl.init
        assert len(class_expr.body) == 1
        assert class_expr.body[0].kind == "method"
        assert class_expr.body[0].key.name == "greet"


class TestComplexClassScenarios:
    """Test complex class scenarios."""

    def test_class_with_constructor_and_methods(self):
        """
        Given a class with both constructor and methods
        When parsing the code
        Then all should be present in body
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
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        class_decl = program.body[0]
        assert len(class_decl.body) == 3

        # Constructor
        assert class_decl.body[0].kind == "constructor"
        assert class_decl.body[0].static is False

        # Instance method
        assert class_decl.body[1].kind == "method"
        assert class_decl.body[1].key.name == "greet"
        assert class_decl.body[1].static is False

        # Static method
        assert class_decl.body[2].kind == "method"
        assert class_decl.body[2].key.name == "create"
        assert class_decl.body[2].static is True

    def test_class_with_getters_and_setters(self):
        """
        Given a class with both getters and setters
        When parsing the code
        Then both should be present with correct kinds
        """
        # Given
        source = """
        class Person {
            get name() {
                return this._name;
            }

            set name(value) {
                this._name = value;
            }
        }
        """
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        class_decl = program.body[0]
        assert len(class_decl.body) == 2

        getter = class_decl.body[0]
        assert getter.kind == "get"
        assert getter.key.name == "name"

        setter = class_decl.body[1]
        assert setter.kind == "set"
        assert setter.key.name == "name"

    def test_inheritance_chain(self):
        """
        Given multiple classes with inheritance
        When parsing the code
        Then inheritance relationships should be preserved
        """
        # Given
        source = """
        class Animal {}
        class Dog extends Animal {}
        class Cat extends Animal {}
        """
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        assert len(program.body) == 3

        # Animal has no super
        animal_class = program.body[0]
        assert animal_class.id.name == "Animal"
        assert animal_class.superClass is None

        # Dog extends Animal
        dog_class = program.body[1]
        assert dog_class.id.name == "Dog"
        assert dog_class.superClass.name == "Animal"

        # Cat extends Animal
        cat_class = program.body[2]
        assert cat_class.id.name == "Cat"
        assert cat_class.superClass.name == "Animal"

    def test_empty_methods(self):
        """
        Given a class with empty method bodies
        When parsing the code
        Then methods should have empty BlockStatement bodies
        """
        # Given
        source = """
        class Test {
            method() {}
        }
        """
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        class_decl = program.body[0]
        method = class_decl.body[0]
        assert isinstance(method.value.body, BlockStatement)
        assert method.value.body.body == []


class TestClassEdgeCases:
    """Test edge cases in class parsing."""

    def test_class_with_no_methods(self):
        """
        Given a class with no methods
        When parsing the code
        Then class should have empty body
        """
        # Given
        source = "class Empty {}"
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        class_decl = program.body[0]
        assert class_decl.body == []

    def test_multiple_class_declarations(self):
        """
        Given multiple class declarations
        When parsing the code
        Then all classes should be parsed
        """
        # Given
        source = """
        class A {}
        class B {}
        class C {}
        """
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        assert len(program.body) == 3
        assert all(isinstance(stmt, ClassDeclaration) for stmt in program.body)
        assert program.body[0].id.name == "A"
        assert program.body[1].id.name == "B"
        assert program.body[2].id.name == "C"

    def test_class_with_only_static_methods(self):
        """
        Given a class with only static methods
        When parsing the code
        Then all methods should be marked as static
        """
        # Given
        source = """
        class Utils {
            static method1() {}
            static method2() {}
        }
        """
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        class_decl = program.body[0]
        assert len(class_decl.body) == 2
        assert all(method.static is True for method in class_decl.body)

    def test_static_getter_and_setter(self):
        """
        Given a class with static getter and setter
        When parsing the code
        Then they should be static with correct kinds
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
        lexer = Lexer(source)
        parser = Parser(lexer)

        # When
        program = parser.parse()

        # Then
        class_decl = program.body[0]
        assert len(class_decl.body) == 2

        static_getter = class_decl.body[0]
        assert static_getter.kind == "get"
        assert static_getter.static is True

        static_setter = class_decl.body[1]
        assert static_setter.kind == "set"
        assert static_setter.static is True
