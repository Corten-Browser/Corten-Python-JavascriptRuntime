"""
Unit tests for AST node classes.

Tests verify that AST nodes correctly represent JavaScript syntax
structures and store source location information.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.shared_types.src import SourceLocation
from components.parser.src.ast_nodes import (
    ASTNode,
    Expression,
    Statement,
    Literal,
    Identifier,
    BinaryExpression,
    CallExpression,
    MemberExpression,
    FunctionExpression,
    ExpressionStatement,
    VariableDeclarator,
    VariableDeclaration,
    FunctionDeclaration,
    IfStatement,
    WhileStatement,
    ReturnStatement,
    BlockStatement,
    Program,
)


def test_literal_node():
    """
    Given a literal value
    When creating a Literal node
    Then it should store the value correctly
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    # Number literal
    num_lit = Literal(value=42, location=loc)
    assert num_lit.value == 42
    assert num_lit.location == loc

    # String literal
    str_lit = Literal(value="hello", location=loc)
    assert str_lit.value == "hello"

    # Boolean literal
    bool_lit = Literal(value=True, location=loc)
    assert bool_lit.value is True

    # Null literal
    null_lit = Literal(value=None, location=loc)
    assert null_lit.value is None


def test_identifier_node():
    """
    Given an identifier name
    When creating an Identifier node
    Then it should store the name correctly
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    ident = Identifier(name="myVariable", location=loc)
    assert ident.name == "myVariable"
    assert ident.location == loc


def test_binary_expression_node():
    """
    Given a binary operator and operands
    When creating a BinaryExpression node
    Then it should represent the operation correctly
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    left = Identifier(name="a", location=loc)
    right = Literal(value=5, location=loc)

    expr = BinaryExpression(operator="+", left=left, right=right, location=loc)

    assert expr.operator == "+"
    assert expr.left == left
    assert expr.right == right


def test_call_expression_node():
    """
    Given a function call
    When creating a CallExpression node
    Then it should store callee and arguments
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    callee = Identifier(name="add", location=loc)
    args = [Literal(value=1, location=loc), Literal(value=2, location=loc)]

    call = CallExpression(callee=callee, arguments=args, location=loc)

    assert call.callee == callee
    assert len(call.arguments) == 2
    assert call.arguments[0].value == 1
    assert call.arguments[1].value == 2


def test_member_expression_node():
    """
    Given a property access
    When creating a MemberExpression node
    Then it should represent the access correctly
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    obj = Identifier(name="obj", location=loc)
    prop = Identifier(name="property", location=loc)

    # Dot notation: obj.property
    member = MemberExpression(object=obj, property=prop, computed=False, location=loc)

    assert member.object == obj
    assert member.property == prop
    assert member.computed is False

    # Bracket notation: obj[property]
    member_computed = MemberExpression(
        object=obj, property=prop, computed=True, location=loc
    )

    assert member_computed.computed is True


def test_function_expression_node():
    """
    Given a function expression
    When creating a FunctionExpression node
    Then it should store parameters and body
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    body = BlockStatement(body=[], location=loc)

    # Anonymous function
    anon_func = FunctionExpression(
        name=None, parameters=["x", "y"], body=body, location=loc
    )

    assert anon_func.name is None
    assert anon_func.parameters == ["x", "y"]
    assert anon_func.body == body

    # Named function expression
    named_func = FunctionExpression(
        name="add", parameters=["a", "b"], body=body, location=loc
    )

    assert named_func.name == "add"


def test_expression_statement_node():
    """
    Given an expression
    When creating an ExpressionStatement node
    Then it should wrap the expression
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    expr = Identifier(name="x", location=loc)
    stmt = ExpressionStatement(expression=expr, location=loc)

    assert stmt.expression == expr


def test_variable_declaration_node():
    """
    Given variable declarations
    When creating a VariableDeclaration node
    Then it should store all declarators
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    declarators = [
        VariableDeclarator(name="x", init=Literal(value=5, location=loc)),
        VariableDeclarator(name="y", init=Literal(value=10, location=loc)),
    ]

    var_decl = VariableDeclaration(declarations=declarators, location=loc)

    assert len(var_decl.declarations) == 2
    assert var_decl.declarations[0].name == "x"
    assert var_decl.declarations[0].init.value == 5
    assert var_decl.declarations[1].name == "y"
    assert var_decl.declarations[1].init.value == 10


def test_function_declaration_node():
    """
    Given a function declaration
    When creating a FunctionDeclaration node
    Then it should store name, parameters, and body
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    body = BlockStatement(body=[], location=loc)

    func_decl = FunctionDeclaration(
        name="add", parameters=["a", "b"], body=body, location=loc
    )

    assert func_decl.name == "add"
    assert func_decl.parameters == ["a", "b"]
    assert func_decl.body == body


def test_if_statement_node():
    """
    Given an if/else statement
    When creating an IfStatement node
    Then it should store test, consequent, and alternate
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    test = BinaryExpression(
        operator=">",
        left=Identifier(name="x", location=loc),
        right=Literal(value=0, location=loc),
        location=loc,
    )
    consequent = BlockStatement(body=[], location=loc)
    alternate = BlockStatement(body=[], location=loc)

    if_stmt = IfStatement(
        test=test, consequent=consequent, alternate=alternate, location=loc
    )

    assert if_stmt.test == test
    assert if_stmt.consequent == consequent
    assert if_stmt.alternate == alternate

    # If without else
    if_stmt_no_else = IfStatement(
        test=test, consequent=consequent, alternate=None, location=loc
    )

    assert if_stmt_no_else.alternate is None


def test_while_statement_node():
    """
    Given a while loop
    When creating a WhileStatement node
    Then it should store test and body
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    test = BinaryExpression(
        operator="<",
        left=Identifier(name="i", location=loc),
        right=Literal(value=10, location=loc),
        location=loc,
    )
    body = BlockStatement(body=[], location=loc)

    while_stmt = WhileStatement(test=test, body=body, location=loc)

    assert while_stmt.test == test
    assert while_stmt.body == body


def test_return_statement_node():
    """
    Given a return statement
    When creating a ReturnStatement node
    Then it should store the return value
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    # Return with value
    return_stmt = ReturnStatement(
        argument=Literal(value=42, location=loc), location=loc
    )

    assert return_stmt.argument.value == 42

    # Bare return
    bare_return = ReturnStatement(argument=None, location=loc)

    assert bare_return.argument is None


def test_block_statement_node():
    """
    Given a block of statements
    When creating a BlockStatement node
    Then it should store all statements
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    statements = [
        VariableDeclaration(
            declarations=[
                VariableDeclarator(name="x", init=Literal(value=1, location=loc))
            ],
            location=loc,
        ),
        ReturnStatement(argument=Identifier(name="x", location=loc), location=loc),
    ]

    block = BlockStatement(body=statements, location=loc)

    assert len(block.body) == 2
    assert isinstance(block.body[0], VariableDeclaration)
    assert isinstance(block.body[1], ReturnStatement)


def test_program_node():
    """
    Given a complete JavaScript program
    When creating a Program node
    Then it should store all top-level statements
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    statements = [
        VariableDeclaration(
            declarations=[
                VariableDeclarator(name="x", init=Literal(value=1, location=loc))
            ],
            location=loc,
        ),
        FunctionDeclaration(
            name="add",
            parameters=["a", "b"],
            body=BlockStatement(body=[], location=loc),
            location=loc,
        ),
    ]

    program = Program(body=statements, location=loc)

    assert len(program.body) == 2
    assert isinstance(program.body[0], VariableDeclaration)
    assert isinstance(program.body[1], FunctionDeclaration)


def test_ast_node_inheritance():
    """
    Given the AST node hierarchy
    When checking inheritance
    Then nodes should inherit from correct base classes
    """
    loc = SourceLocation(filename="test.js", line=1, column=1, offset=0)

    # Expressions inherit from Expression and ASTNode
    literal = Literal(value=42, location=loc)
    assert isinstance(literal, Expression)
    assert isinstance(literal, ASTNode)

    # Statements inherit from Statement and ASTNode
    return_stmt = ReturnStatement(argument=None, location=loc)
    assert isinstance(return_stmt, Statement)
    assert isinstance(return_stmt, ASTNode)

    # Program inherits from ASTNode
    program = Program(body=[], location=loc)
    assert isinstance(program, ASTNode)
