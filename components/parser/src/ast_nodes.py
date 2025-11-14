"""
Abstract Syntax Tree (AST) node classes for JavaScript.

Provides AST node classes for representing parsed JavaScript code,
including expressions, statements, and the program structure.
All nodes inherit from ASTNode and include source location tracking.
"""

from dataclasses import dataclass
from typing import List, Optional

from components.shared_types.src import SourceLocation


@dataclass
class ASTNode:
    """
    Base class for all AST nodes.

    All AST nodes include source location information for error reporting
    and debugging.

    Attributes:
        location: Source location where this node was parsed
    """

    location: SourceLocation


@dataclass
class Expression(ASTNode):
    """
    Base class for all expression nodes.

    Expressions produce values and can appear in contexts where a value
    is expected (assignments, function arguments, etc.).
    """


@dataclass
class Statement(ASTNode):
    """
    Base class for all statement nodes.

    Statements perform actions and do not produce values directly.
    They form the structure of JavaScript programs.
    """


# ============================================================================
# LITERALS AND IDENTIFIERS
# ============================================================================


@dataclass
class Literal(Expression):
    """
    Literal value expression.

    Represents literal values: numbers, strings, booleans, null, undefined.

    Attributes:
        value: The literal value (number, string, bool, None for null/undefined)
        location: Source location

    Example:
        >>> Literal(value=42, location=loc)  # Number literal
        >>> Literal(value="hello", location=loc)  # String literal
        >>> Literal(value=True, location=loc)  # Boolean literal
    """

    value: any


@dataclass
class Identifier(Expression):
    """
    Identifier expression.

    Represents variable names, function names, and property names.

    Attributes:
        name: The identifier name
        location: Source location

    Example:
        >>> Identifier(name="myVariable", location=loc)
    """

    name: str


# ============================================================================
# EXPRESSIONS
# ============================================================================


@dataclass
class BinaryExpression(Expression):
    """
    Binary operator expression.

    Represents expressions with two operands and an operator.
    Examples: a + b, x == y, i < 10

    Attributes:
        operator: Operator string (+, -, *, /, ==, !=, <, >, etc.)
        left: Left operand expression
        right: Right operand expression
        location: Source location

    Example:
        >>> BinaryExpression(
        ...     operator="+",
        ...     left=Identifier(name="a", location=loc),
        ...     right=Literal(value=5, location=loc),
        ...     location=loc
        ... )
    """

    operator: str
    left: Expression
    right: Expression


@dataclass
class CallExpression(Expression):
    """
    Function call expression.

    Represents function calls with arguments.
    Examples: add(1, 2), console.log("hello")

    Attributes:
        callee: Expression that evaluates to the function
        arguments: List of argument expressions
        location: Source location

    Example:
        >>> CallExpression(
        ...     callee=Identifier(name="add", location=loc),
        ...     arguments=[Literal(value=1, location=loc), Literal(value=2, location=loc)],
        ...     location=loc
        ... )
    """

    callee: Expression
    arguments: List[Expression]


@dataclass
class MemberExpression(Expression):
    """
    Property access expression.

    Represents property access on objects.
    Examples: obj.property (computed=False), obj[key] (computed=True)

    Attributes:
        object: Object expression
        property: Property expression
        computed: True for bracket notation obj[prop], False for dot notation obj.prop
        location: Source location

    Example:
        >>> # obj.property
        >>> MemberExpression(
        ...     object=Identifier(name="obj", location=loc),
        ...     property=Identifier(name="property", location=loc),
        ...     computed=False,
        ...     location=loc
        ... )
        >>> # obj[key]
        >>> MemberExpression(
        ...     object=Identifier(name="obj", location=loc),
        ...     property=Identifier(name="key", location=loc),
        ...     computed=True,
        ...     location=loc
        ... )
    """

    object: Expression
    property: Expression
    computed: bool


@dataclass
class FunctionExpression(Expression):
    """
    Function expression.

    Represents anonymous or named function expressions.
    Examples: function(x) { return x * 2; }, function double(x) { return x * 2; }

    Attributes:
        name: Function name (optional, None for anonymous functions)
        parameters: List of parameter names
        body: Function body (BlockStatement)
        location: Source location

    Example:
        >>> FunctionExpression(
        ...     name=None,
        ...     parameters=["x"],
        ...     body=BlockStatement(body=[...], location=loc),
        ...     location=loc
        ... )
    """

    name: Optional[str]
    parameters: List[str]
    body: "BlockStatement"


@dataclass
class ArrowFunctionExpression(Expression):
    """
    Arrow function expression.

    Represents ES6 arrow functions with concise syntax.
    Examples: x => x * 2, (x, y) => x + y, () => 42, x => { return x; }

    Arrow functions differ from regular functions:
    - Lexical 'this' binding (captured from surrounding scope)
    - No 'arguments' object
    - Cannot be used as constructors
    - Implicit return for expression bodies

    Attributes:
        params: List of parameter identifiers
        body: Function body (Expression for implicit return, BlockStatement for explicit)
        is_async: Whether this is an async arrow function (for future support)
        location: Source location

    Example:
        >>> # x => x * 2 (expression body with implicit return)
        >>> ArrowFunctionExpression(
        ...     params=[Identifier(name="x", location=loc)],
        ...     body=BinaryExpression(operator="*", left=..., right=..., location=loc),
        ...     is_async=False,
        ...     location=loc
        ... )
        >>> # (x, y) => { return x + y; } (block body with explicit return)
        >>> ArrowFunctionExpression(
        ...     params=[Identifier(name="x", location=loc), Identifier(name="y", location=loc)],
        ...     body=BlockStatement(body=[ReturnStatement(...)], location=loc),
        ...     is_async=False,
        ...     location=loc
        ... )
    """

    params: List[Identifier]
    body: any  # Union[Expression, BlockStatement]
    is_async: bool = False


@dataclass
class ArrayExpression(Expression):
    """
    Array literal expression.

    Represents array literals with comma-separated elements.
    Examples: [1, 2, 3], [x, y + 1, fn()], [[1, 2], [3, 4]]

    Attributes:
        elements: List of element expressions
        location: Source location

    Example:
        >>> ArrayExpression(
        ...     elements=[
        ...         Literal(value=1, location=loc),
        ...         Literal(value=2, location=loc),
        ...         Literal(value=3, location=loc)
        ...     ],
        ...     location=loc
        ... )
    """

    elements: List[Expression]


@dataclass
class Property:
    """
    Object property definition.

    Represents a property in an object literal.
    Examples: x: 1, "key": value, method() {}, [expr]: value

    Attributes:
        key: Property key (Identifier or Literal)
        value: Property value expression
        kind: Property kind ("init" for normal properties, "method" for methods)
        computed: True for computed property names [expr], False for normal keys
        location: Source location

    Example:
        >>> Property(
        ...     key=Identifier(name="x", location=loc),
        ...     value=Literal(value=1, location=loc),
        ...     kind="init",
        ...     computed=False,
        ...     location=loc
        ... )
    """

    key: Expression
    value: Expression
    kind: str
    computed: bool
    location: SourceLocation


@dataclass
class ObjectExpression(Expression):
    """
    Object literal expression.

    Represents object literals with comma-separated properties.
    Examples: {x: 1, y: 2}, {name, age: 25}, {greet() { return "hi"; }}

    Attributes:
        properties: List of property definitions
        location: Source location

    Example:
        >>> ObjectExpression(
        ...     properties=[
        ...         Property(
        ...             key=Identifier(name="x", location=loc),
        ...             value=Literal(value=1, location=loc),
        ...             kind="init",
        ...             computed=False,
        ...             location=loc
        ...         )
        ...     ],
        ...     location=loc
        ... )
    """

    properties: List[Property]


# ============================================================================
# STATEMENTS
# ============================================================================


@dataclass
class ExpressionStatement(Statement):
    """
    Expression statement.

    Wraps an expression to use it as a statement.
    Example: x + 1; (expression evaluated but result discarded)

    Attributes:
        expression: The expression to evaluate
        location: Source location

    Example:
        >>> ExpressionStatement(
        ...     expression=CallExpression(...),
        ...     location=loc
        ... )
    """

    expression: Expression


@dataclass
class VariableDeclarator:
    """
    Single variable declarator in a variable declaration.

    Represents one variable in a var statement.
    Example: x = 5 (in var x = 5, y = 10;)

    Attributes:
        name: Variable name
        init: Initializer expression (optional)

    Example:
        >>> VariableDeclarator(name="x", init=Literal(value=5, location=loc))
    """

    name: str
    init: Optional[Expression]


@dataclass
class VariableDeclaration(Statement):
    """
    Variable declaration statement.

    Represents var, let, or const declarations.
    Example: var x = 5, y = 10; or let x = 1; or const y = 2;

    Attributes:
        kind: Declaration kind - "var", "let", or "const"
        declarations: List of variable declarators
        location: Source location

    Example:
        >>> VariableDeclaration(
        ...     kind="var",
        ...     declarations=[
        ...         VariableDeclarator(name="x", init=Literal(value=5, location=loc)),
        ...         VariableDeclarator(name="y", init=Literal(value=10, location=loc))
        ...     ],
        ...     location=loc
        ... )
    """

    kind: str
    declarations: List[VariableDeclarator]


@dataclass
class FunctionDeclaration(Statement):
    """
    Function declaration statement.

    Represents function declarations.
    Example: function add(a, b) { return a + b; }

    Attributes:
        name: Function name
        parameters: List of parameter names
        body: Function body (BlockStatement)
        location: Source location

    Example:
        >>> FunctionDeclaration(
        ...     name="add",
        ...     parameters=["a", "b"],
        ...     body=BlockStatement(body=[...], location=loc),
        ...     location=loc
        ... )
    """

    name: str
    parameters: List[str]
    body: "BlockStatement"


@dataclass
class IfStatement(Statement):
    """
    If statement.

    Represents if/else conditional statements.
    Example: if (x > 0) { ... } else { ... }

    Attributes:
        test: Condition expression
        consequent: Statement to execute if condition is true
        alternate: Statement to execute if condition is false (optional)
        location: Source location

    Example:
        >>> IfStatement(
        ...     test=BinaryExpression(operator=">", left=..., right=...),
        ...     consequent=BlockStatement(body=[...], location=loc),
        ...     alternate=BlockStatement(body=[...], location=loc),
        ...     location=loc
        ... )
    """

    test: Expression
    consequent: Statement
    alternate: Optional[Statement]


@dataclass
class WhileStatement(Statement):
    """
    While loop statement.

    Represents while loops.
    Example: while (i < 10) { i++; }

    Attributes:
        test: Loop condition expression
        body: Loop body statement
        location: Source location

    Example:
        >>> WhileStatement(
        ...     test=BinaryExpression(operator="<", left=..., right=...),
        ...     body=BlockStatement(body=[...], location=loc),
        ...     location=loc
        ... )
    """

    test: Expression
    body: Statement


@dataclass
class ReturnStatement(Statement):
    """
    Return statement.

    Represents return statements in functions.
    Example: return x + 1; or just return;

    Attributes:
        argument: Expression to return (optional, None for bare return)
        location: Source location

    Example:
        >>> ReturnStatement(
        ...     argument=BinaryExpression(...),
        ...     location=loc
        ... )
        >>> ReturnStatement(argument=None, location=loc)  # bare return
    """

    argument: Optional[Expression]


@dataclass
class BlockStatement(Statement):
    """
    Block statement.

    Represents a block of statements enclosed in braces.
    Example: { var x = 1; return x; }

    Attributes:
        body: List of statements in the block
        location: Source location

    Example:
        >>> BlockStatement(
        ...     body=[
        ...         VariableDeclaration(...),
        ...         ReturnStatement(...)
        ...     ],
        ...     location=loc
        ... )
    """

    body: List[Statement]


# ============================================================================
# PROGRAM ROOT
# ============================================================================


@dataclass
class Program(ASTNode):
    """
    Program root node.

    Represents the root of the AST for a complete JavaScript program.
    Contains all top-level statements.

    Attributes:
        body: List of top-level statements
        location: Source location

    Example:
        >>> Program(
        ...     body=[
        ...         VariableDeclaration(...),
        ...         FunctionDeclaration(...),
        ...         ExpressionStatement(...)
        ...     ],
        ...     location=loc
        ... )
    """

    body: List[Statement]
