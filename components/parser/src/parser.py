"""
Recursive descent parser for JavaScript.

Provides parsing of ES5 JavaScript source code into Abstract Syntax Trees (AST).
Uses recursive descent parsing technique with proper operator precedence handling.
"""

from typing import List, Optional

from .lexer import Lexer
from .token import Token, TokenType
from .ast_nodes import *


class Parser:
    """
    Recursive descent parser for JavaScript.

    Parses JavaScript source code (via Lexer) into an Abstract Syntax Tree (AST).
    Supports ES5 core features: variables, functions, objects, arrays, operators,
    and control flow.

    Attributes:
        lexer: The lexer providing tokens
        current_token: Current token being processed

    Example:
        >>> lexer = Lexer("var x = 5;", "test.js")
        >>> parser = Parser(lexer)
        >>> ast = parser.parse()
        >>> isinstance(ast, Program)
        True
    """

    def __init__(self, lexer: Lexer):
        """
        Initialize parser with lexer.

        Args:
            lexer: Lexer instance providing tokens
        """
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def parse(self) -> Program:
        """
        Parse source code into AST.

        Returns:
            Program: Root node of the AST

        Raises:
            SyntaxError: If source contains syntax errors

        Example:
            >>> parser = Parser(lexer)
            >>> program = parser.parse()
            >>> len(program.body) > 0
            True
        """
        statements = []
        while self.current_token.type != TokenType.EOF:
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        return Program(body=statements, location=self.current_token.location)

    def _advance(self):
        """Advance to next token."""
        self.current_token = self.lexer.next_token()

    def _expect(self, token_type: TokenType) -> Token:
        """
        Expect a specific token type and advance.

        Args:
            token_type: Expected token type

        Returns:
            Token: The consumed token

        Raises:
            SyntaxError: If current token doesn't match expected type
        """
        if self.current_token.type != token_type:
            raise SyntaxError(
                f"Expected {token_type}, got {self.current_token.type} "
                f"at {self.current_token.location.filename}:"
                f"{self.current_token.location.line}:{self.current_token.location.column}"
            )
        token = self.current_token
        self._advance()
        return token

    def _parse_statement(self) -> Optional[Statement]:
        """
        Parse a statement.

        Returns:
            Statement: Parsed statement node or None
        """
        # Variable declaration
        if self.current_token.type == TokenType.VAR:
            return self._parse_variable_declaration()

        # Function declaration
        if self.current_token.type == TokenType.FUNCTION:
            return self._parse_function_declaration()

        # If statement
        if self.current_token.type == TokenType.IF:
            return self._parse_if_statement()

        # While statement
        if self.current_token.type == TokenType.WHILE:
            return self._parse_while_statement()

        # Return statement
        if self.current_token.type == TokenType.RETURN:
            return self._parse_return_statement()

        # Block statement
        if self.current_token.type == TokenType.LBRACE:
            return self._parse_block_statement()

        # Expression statement
        return self._parse_expression_statement()

    def _parse_variable_declaration(self) -> VariableDeclaration:
        """Parse variable declaration statement."""
        start_location = self.current_token.location
        self._expect(TokenType.VAR)

        declarations = []

        # Parse first declarator
        declarations.append(self._parse_variable_declarator())

        # Parse additional declarators (comma-separated)
        while self.current_token.type == TokenType.COMMA:
            self._advance()  # skip comma
            declarations.append(self._parse_variable_declarator())

        # Expect semicolon
        if self.current_token.type == TokenType.SEMICOLON:
            self._advance()

        return VariableDeclaration(declarations=declarations, location=start_location)

    def _parse_variable_declarator(self) -> VariableDeclarator:
        """Parse a single variable declarator."""
        name_token = self._expect(TokenType.IDENTIFIER)
        name = name_token.value

        init = None
        if self.current_token.type == TokenType.ASSIGN:
            self._advance()  # skip =
            init = self._parse_expression()

        return VariableDeclarator(name=name, init=init)

    def _parse_function_declaration(self) -> FunctionDeclaration:
        """Parse function declaration."""
        start_location = self.current_token.location
        self._expect(TokenType.FUNCTION)

        # Function name
        name_token = self._expect(TokenType.IDENTIFIER)
        name = name_token.value

        # Parameters
        self._expect(TokenType.LPAREN)
        parameters = self._parse_parameter_list()
        self._expect(TokenType.RPAREN)

        # Body
        body = self._parse_block_statement()

        return FunctionDeclaration(
            name=name, parameters=parameters, body=body, location=start_location
        )

    def _parse_parameter_list(self) -> List[str]:
        """Parse function parameter list."""
        parameters = []

        if self.current_token.type != TokenType.RPAREN:
            # Parse first parameter
            param_token = self._expect(TokenType.IDENTIFIER)
            parameters.append(param_token.value)

            # Parse additional parameters
            while self.current_token.type == TokenType.COMMA:
                self._advance()  # skip comma
                param_token = self._expect(TokenType.IDENTIFIER)
                parameters.append(param_token.value)

        return parameters

    def _parse_if_statement(self) -> IfStatement:
        """Parse if statement."""
        start_location = self.current_token.location
        self._expect(TokenType.IF)

        # Condition
        self._expect(TokenType.LPAREN)
        test = self._parse_expression()
        self._expect(TokenType.RPAREN)

        # Consequent
        consequent = self._parse_statement()

        # Alternate (else clause)
        alternate = None
        if self.current_token.type == TokenType.ELSE:
            self._advance()  # skip else
            alternate = self._parse_statement()

        return IfStatement(
            test=test,
            consequent=consequent,
            alternate=alternate,
            location=start_location,
        )

    def _parse_while_statement(self) -> WhileStatement:
        """Parse while statement."""
        start_location = self.current_token.location
        self._expect(TokenType.WHILE)

        # Condition
        self._expect(TokenType.LPAREN)
        test = self._parse_expression()
        self._expect(TokenType.RPAREN)

        # Body
        body = self._parse_statement()

        return WhileStatement(test=test, body=body, location=start_location)

    def _parse_return_statement(self) -> ReturnStatement:
        """Parse return statement."""
        start_location = self.current_token.location
        self._expect(TokenType.RETURN)

        # Argument (optional)
        argument = None
        if (
            self.current_token.type != TokenType.SEMICOLON
            and self.current_token.type != TokenType.EOF
        ):
            argument = self._parse_expression()

        # Semicolon (optional)
        if self.current_token.type == TokenType.SEMICOLON:
            self._advance()

        return ReturnStatement(argument=argument, location=start_location)

    def _parse_block_statement(self) -> BlockStatement:
        """Parse block statement."""
        start_location = self.current_token.location
        self._expect(TokenType.LBRACE)

        statements = []
        while (
            self.current_token.type != TokenType.RBRACE
            and self.current_token.type != TokenType.EOF
        ):
            stmt = self._parse_statement()
            if stmt:
                statements.append(stmt)

        self._expect(TokenType.RBRACE)

        return BlockStatement(body=statements, location=start_location)

    def _parse_expression_statement(self) -> ExpressionStatement:
        """Parse expression statement."""
        start_location = self.current_token.location
        expression = self._parse_expression()

        # Semicolon (optional)
        if self.current_token.type == TokenType.SEMICOLON:
            self._advance()

        return ExpressionStatement(expression=expression, location=start_location)

    def _parse_expression(self) -> Expression:
        """Parse expression with operator precedence."""
        return self._parse_assignment_expression()

    def _parse_assignment_expression(self) -> Expression:
        """Parse assignment expression."""
        left = self._parse_equality_expression()

        if self.current_token.type == TokenType.ASSIGN:
            op_token = self.current_token
            self._advance()
            right = self._parse_assignment_expression()
            return BinaryExpression(
                operator="=", left=left, right=right, location=op_token.location
            )

        return left

    def _parse_equality_expression(self) -> Expression:
        """Parse equality expression (==, !=)."""
        left = self._parse_comparison_expression()

        while self.current_token.type in (TokenType.EQUAL, TokenType.NOT_EQUAL):
            if self.current_token.type == TokenType.EQUAL:
                op = "=="
            else:
                op = "!="

            op_token = self.current_token
            self._advance()
            right = self._parse_comparison_expression()
            left = BinaryExpression(
                operator=op, left=left, right=right, location=op_token.location
            )

        return left

    def _parse_comparison_expression(self) -> Expression:
        """Parse comparison expression (<, >)."""
        left = self._parse_additive_expression()

        while self.current_token.type in (TokenType.LESS_THAN, TokenType.GREATER_THAN):
            if self.current_token.type == TokenType.LESS_THAN:
                op = "<"
            else:
                op = ">"

            op_token = self.current_token
            self._advance()
            right = self._parse_additive_expression()
            left = BinaryExpression(
                operator=op, left=left, right=right, location=op_token.location
            )

        return left

    def _parse_additive_expression(self) -> Expression:
        """Parse additive expression (+, -)."""
        left = self._parse_multiplicative_expression()

        while self.current_token.type in (TokenType.PLUS, TokenType.MINUS):
            if self.current_token.type == TokenType.PLUS:
                op = "+"
            else:
                op = "-"

            op_token = self.current_token
            self._advance()
            right = self._parse_multiplicative_expression()
            left = BinaryExpression(
                operator=op, left=left, right=right, location=op_token.location
            )

        return left

    def _parse_multiplicative_expression(self) -> Expression:
        """Parse multiplicative expression (*, /)."""
        left = self._parse_call_expression()

        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            if self.current_token.type == TokenType.MULTIPLY:
                op = "*"
            else:
                op = "/"

            op_token = self.current_token
            self._advance()
            right = self._parse_call_expression()
            left = BinaryExpression(
                operator=op, left=left, right=right, location=op_token.location
            )

        return left

    def _parse_call_expression(self) -> Expression:
        """Parse call and member expressions."""
        expr = self._parse_member_expression()

        while True:
            if self.current_token.type == TokenType.LPAREN:
                # Function call
                start_location = self.current_token.location
                self._advance()  # skip (
                arguments = self._parse_argument_list()
                self._expect(TokenType.RPAREN)
                expr = CallExpression(
                    callee=expr, arguments=arguments, location=start_location
                )
            else:
                break

        return expr

    def _parse_argument_list(self) -> List[Expression]:
        """Parse function call argument list."""
        arguments = []

        if self.current_token.type != TokenType.RPAREN:
            # Parse first argument
            arguments.append(self._parse_expression())

            # Parse additional arguments
            while self.current_token.type == TokenType.COMMA:
                self._advance()  # skip comma
                arguments.append(self._parse_expression())

        return arguments

    def _parse_member_expression(self) -> Expression:
        """Parse member expression (property access)."""
        expr = self._parse_primary_expression()

        while True:
            if self.current_token.type == TokenType.DOT:
                # Dot notation: obj.property
                start_location = self.current_token.location
                self._advance()  # skip .
                property_token = self._expect(TokenType.IDENTIFIER)
                property_expr = Identifier(
                    name=property_token.value, location=property_token.location
                )
                expr = MemberExpression(
                    object=expr,
                    property=property_expr,
                    computed=False,
                    location=start_location,
                )
            elif self.current_token.type == TokenType.LBRACKET:
                # Bracket notation: obj[property]
                start_location = self.current_token.location
                self._advance()  # skip [
                property_expr = self._parse_expression()
                self._expect(TokenType.RBRACKET)
                expr = MemberExpression(
                    object=expr,
                    property=property_expr,
                    computed=True,
                    location=start_location,
                )
            else:
                break

        return expr

    def _parse_primary_expression(self) -> Expression:
        """Parse primary expression (literals, identifiers, parenthesized)."""
        # Parenthesized expression
        if self.current_token.type == TokenType.LPAREN:
            self._advance()  # skip (
            expr = self._parse_expression()
            self._expect(TokenType.RPAREN)
            return expr

        # Array literal
        if self.current_token.type == TokenType.LBRACKET:
            return self._parse_array_literal()

        # Object literal
        if self.current_token.type == TokenType.LBRACE:
            return self._parse_object_literal()

        # Number literal
        if self.current_token.type == TokenType.NUMBER:
            token = self.current_token
            self._advance()
            return Literal(value=token.value, location=token.location)

        # String literal
        if self.current_token.type == TokenType.STRING:
            token = self.current_token
            self._advance()
            return Literal(value=token.value, location=token.location)

        # Boolean literals
        if self.current_token.type == TokenType.TRUE:
            token = self.current_token
            self._advance()
            return Literal(value=True, location=token.location)

        if self.current_token.type == TokenType.FALSE:
            token = self.current_token
            self._advance()
            return Literal(value=False, location=token.location)

        # Null literal
        if self.current_token.type == TokenType.NULL:
            token = self.current_token
            self._advance()
            return Literal(value=None, location=token.location)

        # Undefined literal
        if self.current_token.type == TokenType.UNDEFINED:
            token = self.current_token
            self._advance()
            return Literal(value=None, location=token.location)

        # Identifier
        if self.current_token.type == TokenType.IDENTIFIER:
            token = self.current_token
            self._advance()
            return Identifier(name=token.value, location=token.location)

        # Unknown token
        raise SyntaxError(
            f"Unexpected token {self.current_token.type} "
            f"at {self.current_token.location.filename}:"
            f"{self.current_token.location.line}:{self.current_token.location.column}"
        )

    def _parse_array_literal(self) -> ArrayExpression:
        """
        Parse array literal expression.

        Syntax: [element1, element2, ...]

        Returns:
            ArrayExpression: Parsed array literal
        """
        start_location = self.current_token.location
        self._expect(TokenType.LBRACKET)

        elements = []

        # Parse elements until closing bracket
        while (
            self.current_token.type != TokenType.RBRACKET
            and self.current_token.type != TokenType.EOF
        ):
            # Parse element expression
            elements.append(self._parse_expression())

            # Check for comma or closing bracket
            if self.current_token.type == TokenType.COMMA:
                self._advance()  # skip comma
                # Allow trailing comma
                if self.current_token.type == TokenType.RBRACKET:
                    break
            elif self.current_token.type != TokenType.RBRACKET:
                raise SyntaxError(
                    f"Expected ',' or ']' in array literal, got {self.current_token.type} "
                    f"at {self.current_token.location.filename}:"
                    f"{self.current_token.location.line}:{self.current_token.location.column}"
                )

        self._expect(TokenType.RBRACKET)

        return ArrayExpression(elements=elements, location=start_location)

    def _parse_object_literal(self) -> ObjectExpression:
        """
        Parse object literal expression.

        Syntax: {key: value, ...} or {key, ...} or {method() {...}}

        Returns:
            ObjectExpression: Parsed object literal
        """
        start_location = self.current_token.location
        self._expect(TokenType.LBRACE)

        properties = []

        # Parse properties until closing brace
        while (
            self.current_token.type != TokenType.RBRACE
            and self.current_token.type != TokenType.EOF
        ):
            # Parse property
            prop = self._parse_object_property()
            properties.append(prop)

            # Check for comma or closing brace
            if self.current_token.type == TokenType.COMMA:
                self._advance()  # skip comma
                # Allow trailing comma
                if self.current_token.type == TokenType.RBRACE:
                    break
            elif self.current_token.type != TokenType.RBRACE:
                raise SyntaxError(
                    f"Expected ',' or '}}' in object literal, got {self.current_token.type} "
                    f"at {self.current_token.location.filename}:"
                    f"{self.current_token.location.line}:{self.current_token.location.column}"
                )

        self._expect(TokenType.RBRACE)

        return ObjectExpression(properties=properties, location=start_location)

    def _parse_object_property(self) -> Property:
        """
        Parse object property.

        Handles:
        - key: value (normal property)
        - key (shorthand property)
        - method() { ... } (method definition)
        - [computed]: value (computed property name)

        Returns:
            Property: Parsed property
        """
        prop_start_location = self.current_token.location

        # Computed property name: [expr]
        computed = False
        if self.current_token.type == TokenType.LBRACKET:
            computed = True
            self._advance()  # skip [
            key = self._parse_expression()
            self._expect(TokenType.RBRACKET)
        # String literal key
        elif self.current_token.type == TokenType.STRING:
            key_token = self.current_token
            key = Literal(value=key_token.value, location=key_token.location)
            self._advance()
        # Identifier key
        elif self.current_token.type == TokenType.IDENTIFIER:
            key_token = self.current_token
            key = Identifier(name=key_token.value, location=key_token.location)
            self._advance()
        else:
            raise SyntaxError(
                f"Expected property key, got {self.current_token.type} "
                f"at {self.current_token.location.filename}:"
                f"{self.current_token.location.line}:{self.current_token.location.column}"
            )

        # Method definition: method() { ... }
        if self.current_token.type == TokenType.LPAREN:
            # Parse as method
            self._expect(TokenType.LPAREN)
            parameters = self._parse_parameter_list()
            self._expect(TokenType.RPAREN)
            body = self._parse_block_statement()

            value = FunctionExpression(
                name=None,
                parameters=parameters,
                body=body,
                location=prop_start_location,
            )

            return Property(
                key=key,
                value=value,
                kind="method",
                computed=computed,
                location=prop_start_location,
            )

        # Shorthand property: {x} expands to {x: x}
        if self.current_token.type != TokenType.COLON:
            # Must be identifier for shorthand
            if not isinstance(key, Identifier):
                raise SyntaxError(
                    f"Shorthand property must be identifier "
                    f"at {self.current_token.location.filename}:"
                    f"{self.current_token.location.line}:{self.current_token.location.column}"
                )
            # Shorthand: use same identifier for value
            value = Identifier(name=key.name, location=key.location)

            return Property(
                key=key,
                value=value,
                kind="init",
                computed=False,
                location=prop_start_location,
            )

        # Normal property: key: value
        self._expect(TokenType.COLON)
        value = self._parse_expression()

        return Property(
            key=key,
            value=value,
            kind="init",
            computed=computed,
            location=prop_start_location,
        )
