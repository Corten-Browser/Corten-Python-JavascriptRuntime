"""
Tests for compiling array and object literals to bytecode.

These tests verify the BytecodeCompiler correctly compiles array and object
literal expressions to bytecode instructions.
"""

import pytest
from components.bytecode.src.compiler import BytecodeCompiler
from components.bytecode.src.opcode import Opcode
from components.parser.src.ast_nodes import (
    Program,
    ExpressionStatement,
    ArrayExpression,
    ObjectExpression,
    Property,
    Literal,
    Identifier,
    BinaryExpression,
)
from components.shared_types.src.location import SourceLocation


def test_compile_empty_array():
    """
    Given an empty array literal expression
    When the compiler compiles it
    Then it should emit CREATE_ARRAY instruction
    """
    # Given
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=ArrayExpression(location=loc, elements=[]),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions
    # Should have: CREATE_ARRAY, POP (expression statement), LOAD_UNDEFINED, RETURN
    assert any(inst.opcode == Opcode.CREATE_ARRAY for inst in instructions)


def test_compile_array_with_literals():
    """
    Given an array literal with numeric literals [1, 2, 3]
    When the compiler compiles it
    Then it should emit instructions to create array and add elements
    """
    # Given
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=ArrayExpression(
                    location=loc,
                    elements=[
                        Literal(location=loc, value=1),
                        Literal(location=loc, value=2),
                        Literal(location=loc, value=3),
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions
    # Should have CREATE_ARRAY and element loading
    assert any(inst.opcode == Opcode.CREATE_ARRAY for inst in instructions)
    # Constants 1, 2, 3 should be in constant pool
    assert 1 in bytecode.constant_pool
    assert 2 in bytecode.constant_pool
    assert 3 in bytecode.constant_pool


def test_compile_array_with_expressions():
    """
    Given an array with expressions [1 + 2, x, 5]
    When the compiler compiles it
    Then it should compile each expression and add to array
    """
    # Given
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=ArrayExpression(
                    location=loc,
                    elements=[
                        BinaryExpression(
                            location=loc,
                            operator="+",
                            left=Literal(location=loc, value=1),
                            right=Literal(location=loc, value=2),
                        ),
                        Identifier(location=loc, name="x"),
                        Literal(location=loc, value=5),
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions
    assert any(inst.opcode == Opcode.CREATE_ARRAY for inst in instructions)
    assert any(inst.opcode == Opcode.ADD for inst in instructions)


def test_compile_nested_arrays():
    """
    Given a nested array [[1, 2], [3, 4]]
    When the compiler compiles it
    Then it should create nested array structure
    """
    # Given
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=ArrayExpression(
                    location=loc,
                    elements=[
                        ArrayExpression(
                            location=loc,
                            elements=[
                                Literal(location=loc, value=1),
                                Literal(location=loc, value=2),
                            ],
                        ),
                        ArrayExpression(
                            location=loc,
                            elements=[
                                Literal(location=loc, value=3),
                                Literal(location=loc, value=4),
                            ],
                        ),
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions
    # Should have multiple CREATE_ARRAY instructions (one for each array)
    create_array_count = sum(
        1 for inst in instructions if inst.opcode == Opcode.CREATE_ARRAY
    )
    assert create_array_count == 3  # outer array + 2 inner arrays


def test_compile_empty_object():
    """
    Given an empty object literal {}
    When the compiler compiles it
    Then it should emit CREATE_OBJECT instruction
    """
    # Given
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=ObjectExpression(location=loc, properties=[]),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions
    # Should have: CREATE_OBJECT, POP, LOAD_UNDEFINED, RETURN
    assert any(inst.opcode == Opcode.CREATE_OBJECT for inst in instructions)


def test_compile_object_with_properties():
    """
    Given an object literal {x: 1, y: 2}
    When the compiler compiles it
    Then it should emit CREATE_OBJECT and STORE_PROPERTY instructions
    """
    # Given
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=ObjectExpression(
                    location=loc,
                    properties=[
                        Property(
                            key=Identifier(location=loc, name="x"),
                            value=Literal(location=loc, value=1),
                            kind="init",
                            computed=False,
                            location=loc,
                        ),
                        Property(
                            key=Identifier(location=loc, name="y"),
                            value=Literal(location=loc, value=2),
                            kind="init",
                            computed=False,
                            location=loc,
                        ),
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions
    assert any(inst.opcode == Opcode.CREATE_OBJECT for inst in instructions)
    # Should have STORE_PROPERTY for each property
    store_property_count = sum(
        1 for inst in instructions if inst.opcode == Opcode.STORE_PROPERTY
    )
    assert store_property_count == 2
    # Property names should be in constant pool
    assert "x" in bytecode.constant_pool
    assert "y" in bytecode.constant_pool


def test_compile_object_shorthand_properties():
    """
    Given an object with shorthand property {x}
    When the compiler compiles it
    Then it should compile as {x: x} (load variable, set property)
    """
    # Given
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    # Shorthand property is represented with key and value both as Identifier
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=ObjectExpression(
                    location=loc,
                    properties=[
                        Property(
                            key=Identifier(location=loc, name="x"),
                            value=Identifier(location=loc, name="x"),
                            kind="init",
                            computed=False,
                            location=loc,
                        ),
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions
    assert any(inst.opcode == Opcode.CREATE_OBJECT for inst in instructions)
    # Should load the variable x and store it as property "x"
    assert any(
        inst.opcode in (Opcode.LOAD_LOCAL, Opcode.LOAD_GLOBAL) for inst in instructions
    )
    assert any(inst.opcode == Opcode.STORE_PROPERTY for inst in instructions)


def test_compile_object_with_expressions():
    """
    Given an object with expression values {a: 1 + 2, b: x * 3}
    When the compiler compiles it
    Then it should compile expressions and store as properties
    """
    # Given
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=ObjectExpression(
                    location=loc,
                    properties=[
                        Property(
                            key=Identifier(location=loc, name="a"),
                            value=BinaryExpression(
                                location=loc,
                                operator="+",
                                left=Literal(location=loc, value=1),
                                right=Literal(location=loc, value=2),
                            ),
                            kind="init",
                            computed=False,
                            location=loc,
                        ),
                        Property(
                            key=Identifier(location=loc, name="b"),
                            value=BinaryExpression(
                                location=loc,
                                operator="*",
                                left=Identifier(location=loc, name="x"),
                                right=Literal(location=loc, value=3),
                            ),
                            kind="init",
                            computed=False,
                            location=loc,
                        ),
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions
    assert any(inst.opcode == Opcode.CREATE_OBJECT for inst in instructions)
    assert any(inst.opcode == Opcode.ADD for inst in instructions)
    assert any(inst.opcode == Opcode.MULTIPLY for inst in instructions)


def test_compile_object_computed_properties():
    """
    Given an object with computed property {[expr]: value}
    When the compiler compiles it
    Then it should evaluate expr for key, then set property
    """
    # Given
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=ObjectExpression(
                    location=loc,
                    properties=[
                        Property(
                            key=Literal(location=loc, value="key"),
                            value=Literal(location=loc, value=123),
                            kind="init",
                            computed=True,  # Computed property
                            location=loc,
                        ),
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions
    assert any(inst.opcode == Opcode.CREATE_OBJECT for inst in instructions)
    # For computed properties, key expression should be compiled
    assert any(inst.opcode == Opcode.LOAD_CONSTANT for inst in instructions)


def test_compile_nested_objects():
    """
    Given a nested object {a: {b: 1}}
    When the compiler compiles it
    Then it should create nested object structure
    """
    # Given
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=ObjectExpression(
                    location=loc,
                    properties=[
                        Property(
                            key=Identifier(location=loc, name="a"),
                            value=ObjectExpression(
                                location=loc,
                                properties=[
                                    Property(
                                        key=Identifier(location=loc, name="b"),
                                        value=Literal(location=loc, value=1),
                                        kind="init",
                                        computed=False,
                                        location=loc,
                                    ),
                                ],
                            ),
                            kind="init",
                            computed=False,
                            location=loc,
                        ),
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions
    # Should have multiple CREATE_OBJECT instructions
    create_object_count = sum(
        1 for inst in instructions if inst.opcode == Opcode.CREATE_OBJECT
    )
    assert create_object_count == 2  # outer object + inner object


def test_compile_mixed_array_object_literals():
    """
    Given mixed array and object literals [{x: 1}, [2, 3]]
    When the compiler compiles it
    Then it should handle both structures correctly
    """
    # Given
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)
    ast = Program(
        location=loc,
        body=[
            ExpressionStatement(
                location=loc,
                expression=ArrayExpression(
                    location=loc,
                    elements=[
                        ObjectExpression(
                            location=loc,
                            properties=[
                                Property(
                                    key=Identifier(location=loc, name="x"),
                                    value=Literal(location=loc, value=1),
                                    kind="init",
                                    computed=False,
                                    location=loc,
                                ),
                            ],
                        ),
                        ArrayExpression(
                            location=loc,
                            elements=[
                                Literal(location=loc, value=2),
                                Literal(location=loc, value=3),
                            ],
                        ),
                    ],
                ),
            )
        ],
    )

    # When
    compiler = BytecodeCompiler(ast)
    bytecode = compiler.compile()

    # Then
    instructions = bytecode.instructions
    assert any(inst.opcode == Opcode.CREATE_OBJECT for inst in instructions)
    assert any(inst.opcode == Opcode.CREATE_ARRAY for inst in instructions)
