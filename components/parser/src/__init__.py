"""
Parser component for JavaScript runtime.

Provides lexical analysis (tokenization), syntax parsing (recursive descent),
and AST generation for ES5 core JavaScript.

Public API:
    # Lexer
    - Token: Lexical token dataclass
    - TokenType: Token type enumeration
    - Lexer: Lexical analyzer class

    # AST Nodes
    - ASTNode: Base AST node class
    - Expression: Base expression class
    - Statement: Base statement class
    - Literal, Identifier: Literal and identifier nodes
    - BinaryExpression, CallExpression, MemberExpression, FunctionExpression: Expression nodes
    - ExpressionStatement, VariableDeclaration, VariableDeclarator: Statement nodes
    - FunctionDeclaration, IfStatement, WhileStatement, ReturnStatement, BlockStatement: Statement nodes
    - Program: Root AST node

    # Parser
    - Parser: Recursive descent parser class
    - Parse: Main entry point function

Example:
    >>> from components.parser.src import Parse
    >>> ast = Parse("var x = 5;", "test.js")
    >>> len(ast.body)
    1
"""

from .token import Token, TokenType
from .lexer import Lexer
from .ast_nodes import (
    ASTNode,
    Expression,
    Statement,
    Literal,
    Identifier,
    BinaryExpression,
    CallExpression,
    MemberExpression,
    FunctionExpression,
    ArrayExpression,
    ObjectExpression,
    Property,
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
from .parser import Parser


def Parse(source: str, filename: str = "<stdin>") -> Program:
    """
    Parse JavaScript source into Abstract Syntax Tree (AST).

    Main entry point for parsing JavaScript code. Creates a lexer and parser,
    then parses the source into an AST.

    Args:
        source: JavaScript source code to parse
        filename: Name of source file (for error reporting)

    Returns:
        Program: Root node of the parsed AST

    Raises:
        SyntaxError: If source contains syntax errors

    Example:
        >>> ast = Parse("var x = 5;", "test.js")
        >>> isinstance(ast, Program)
        True
        >>> len(ast.body)
        1
        >>> isinstance(ast.body[0], VariableDeclaration)
        True
    """
    lexer = Lexer(source, filename)
    parser = Parser(lexer)
    return parser.parse()


__all__ = [
    # Lexer
    "Token",
    "TokenType",
    "Lexer",
    # AST Nodes
    "ASTNode",
    "Expression",
    "Statement",
    "Literal",
    "Identifier",
    "BinaryExpression",
    "CallExpression",
    "MemberExpression",
    "FunctionExpression",
    "ArrayExpression",
    "ObjectExpression",
    "Property",
    "ExpressionStatement",
    "VariableDeclarator",
    "VariableDeclaration",
    "FunctionDeclaration",
    "IfStatement",
    "WhileStatement",
    "ReturnStatement",
    "BlockStatement",
    "Program",
    # Parser
    "Parser",
    "Parse",
]

__version__ = "0.1.0"
