"""
Recursive descent parser for JavaScript.

Provides parsing of ES5 JavaScript source code into Abstract Syntax Trees (AST).
Uses recursive descent parsing technique with proper operator precedence handling.
"""

from typing import List, Optional

from .lexer import Lexer
from .token import Token, TokenType
from .ast_nodes import (
    ForStatement,
    ForInStatement,
    ForOfStatement,
    Program,
    Statement,
    Expression,
    Literal,
    Identifier,
    TemplateLiteral,
    BinaryExpression,
    UnaryExpression,
    CallExpression,
    MemberExpression,
    FunctionExpression,
    ArrowFunctionExpression,
    AsyncFunctionDeclaration,
    AsyncFunctionExpression,
    AsyncArrowFunctionExpression,
    AwaitExpression,
    SpreadElement,
    ArrayExpression,
    ObjectExpression,
    Property,
    Pattern,
    ObjectPattern,
    ArrayPattern,
    PropertyPattern,
    AssignmentPattern,
    RestElement,
    ExpressionStatement,
    VariableDeclarator,
    VariableDeclaration,
    FunctionDeclaration,
    ClassDeclaration,
    ClassExpression,
    MethodDefinition,
    NewExpression,
    IfStatement,
    WhileStatement,
    ReturnStatement,
    BlockStatement,
    ImportDeclaration,
    ImportSpecifier,
    ImportDefaultSpecifier,
    ImportNamespaceSpecifier,
    ExportNamedDeclaration,
    ExportSpecifier,
    ExportDefaultDeclaration,
    ExportAllDeclaration,
)


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
        # Import statement
        if self.current_token.type == TokenType.IMPORT:
            return self._parse_import_declaration()

        # Export statement
        if self.current_token.type == TokenType.EXPORT:
            return self._parse_export_declaration()

        # Async function declaration
        if self.current_token.type == TokenType.ASYNC:
            # Look ahead to see if it's 'async function'
            next_token = self.lexer.peek_token(0)
            if next_token.type == TokenType.FUNCTION:
                return self._parse_async_function_declaration()

        # Variable declaration (var, let, const)
        if self.current_token.type in (TokenType.VAR, TokenType.LET, TokenType.CONST):
            return self._parse_variable_declaration()

        # Function declaration
        if self.current_token.type == TokenType.FUNCTION:
            return self._parse_function_declaration()

        # Class declaration
        if self.current_token.type == TokenType.CLASS:
            return self._parse_class_declaration()

        # If statement
        if self.current_token.type == TokenType.IF:
            return self._parse_if_statement()

        # While statement
        if self.current_token.type == TokenType.WHILE:
            return self._parse_while_statement()

        # For statement (traditional, for-in, for-of)
        if self.current_token.type == TokenType.FOR:
            return self._parse_for_statement()

        # Return statement
        if self.current_token.type == TokenType.RETURN:
            return self._parse_return_statement()

        # Block statement
        if self.current_token.type == TokenType.LBRACE:
            return self._parse_block_statement()

        # Expression statement
        return self._parse_expression_statement()

    def _parse_object_pattern(self) -> ObjectPattern:
        """
        Parse object destructuring pattern.

        Handles: {x, y}, {x: a, y: b}, {x, y: {z}}, {x = 10}, {x, ...rest}

        Returns:
            ObjectPattern: Parsed object pattern
        """
        start_location = self.current_token.location
        self._expect(TokenType.LBRACE)

        properties = []

        while self.current_token.type != TokenType.RBRACE:
            prop_start = self.current_token.location

            # Check for rest property: {...rest}
            if self.current_token.type == TokenType.SPREAD:
                rest_location = self.current_token.location
                self._advance()  # skip ...
                # Parse the rest argument (must be identifier)
                if self.current_token.type != TokenType.IDENTIFIER:
                    raise SyntaxError(
                        f"Expected identifier after ... in object pattern "
                        f"at {self.current_token.location.filename}:"
                        f"{self.current_token.location.line}:{self.current_token.location.column}"
                    )
                argument = Identifier(
                    name=self.current_token.value,
                    location=self.current_token.location
                )
                self._advance()
                element = RestElement(argument=argument, location=rest_location)
                properties.append(element)

                # Rest element must be last
                if self.current_token.type == TokenType.COMMA:
                    raise SyntaxError(
                        f"Rest element must be last element in object pattern "
                        f"at {self.current_token.location.filename}:"
                        f"{self.current_token.location.line}:{self.current_token.location.column}"
                    )
                break  # Rest element ends the pattern

            # Parse property key (identifier or computed)
            if self.current_token.type == TokenType.IDENTIFIER:
                key = Identifier(name=self.current_token.value, location=self.current_token.location)
                self._advance()

                # Check for shorthand {x} or colon {x: y} or default {x = 10}
                if self.current_token.type == TokenType.COLON:
                    # Long form: {x: y} or {x: {nested}}
                    self._advance()  # skip :
                    value = self._parse_pattern_or_identifier()
                    computed = False
                elif self.current_token.type == TokenType.ASSIGN:
                    # Default value: {x = 10}
                    self._advance()  # skip =
                    default_value = self._parse_assignment_expression()
                    value = AssignmentPattern(
                        left=Identifier(name=key.name, location=key.location),
                        right=default_value,
                        location=prop_start
                    )
                    computed = False
                else:
                    # Shorthand: {x}
                    value = Identifier(name=key.name, location=key.location)
                    computed = False

                properties.append(PropertyPattern(
                    key=key,
                    value=value,
                    computed=computed,
                    location=prop_start
                ))
            else:
                raise SyntaxError(
                    f"Expected identifier in object pattern "
                    f"at {self.current_token.location.filename}:"
                    f"{self.current_token.location.line}:{self.current_token.location.column}"
                )

            # Check for comma or end of pattern
            if self.current_token.type == TokenType.COMMA:
                self._advance()  # skip comma
                # Allow trailing comma
                if self.current_token.type == TokenType.RBRACE:
                    break
            elif self.current_token.type != TokenType.RBRACE:
                raise SyntaxError(
                    f"Expected comma or }} in object pattern "
                    f"at {self.current_token.location.filename}:"
                    f"{self.current_token.location.line}:{self.current_token.location.column}"
                )

        self._expect(TokenType.RBRACE)
        return ObjectPattern(properties=properties, location=start_location)

    def _parse_array_pattern(self) -> ArrayPattern:
        """
        Parse array destructuring pattern.

        Handles: [a, b], [a, , c], [[x, y], z], [a = 5], [a, ...rest]

        Returns:
            ArrayPattern: Parsed array pattern
        """
        start_location = self.current_token.location
        self._expect(TokenType.LBRACKET)

        elements = []

        while self.current_token.type != TokenType.RBRACKET:
            # Check for hole in array pattern: [a, , c]
            if self.current_token.type == TokenType.COMMA:
                elements.append(None)
                self._advance()
                continue

            # Check for rest element: [...rest]
            if self.current_token.type == TokenType.SPREAD:
                rest_location = self.current_token.location
                self._advance()  # skip ...
                # Parse the rest argument (can be identifier or pattern)
                argument = self._parse_pattern_or_identifier()
                element = RestElement(argument=argument, location=rest_location)
                elements.append(element)

                # Rest element must be last
                if self.current_token.type == TokenType.COMMA:
                    raise SyntaxError(
                        f"Rest element must be last element in array pattern "
                        f"at {self.current_token.location.filename}:"
                        f"{self.current_token.location.line}:{self.current_token.location.column}"
                    )
                break  # Rest element ends the pattern

            # Parse element (can be identifier, nested pattern, or assignment pattern)
            element = self._parse_pattern_or_identifier()

            # Check for default value: [a = 5]
            if self.current_token.type == TokenType.ASSIGN:
                elem_start = element.location if hasattr(element, 'location') else start_location
                self._advance()  # skip =
                default_value = self._parse_assignment_expression()
                element = AssignmentPattern(
                    left=element,
                    right=default_value,
                    location=elem_start
                )

            elements.append(element)

            # Check for comma or end of pattern
            if self.current_token.type == TokenType.COMMA:
                self._advance()  # skip comma
                # Allow trailing comma
                if self.current_token.type == TokenType.RBRACKET:
                    break
            elif self.current_token.type != TokenType.RBRACKET:
                raise SyntaxError(
                    f"Expected comma or ] in array pattern "
                    f"at {self.current_token.location.filename}:"
                    f"{self.current_token.location.line}:{self.current_token.location.column}"
                )

        self._expect(TokenType.RBRACKET)
        return ArrayPattern(elements=elements, location=start_location)

    def _parse_pattern_or_identifier(self):
        """
        Parse a pattern (object or array) or identifier.

        Used in destructuring contexts where either can appear.

        Returns:
            Union[Identifier, ObjectPattern, ArrayPattern]: Parsed pattern or identifier
        """
        if self.current_token.type == TokenType.LBRACE:
            return self._parse_object_pattern()
        elif self.current_token.type == TokenType.LBRACKET:
            return self._parse_array_pattern()
        elif self.current_token.type == TokenType.IDENTIFIER:
            identifier = Identifier(name=self.current_token.value, location=self.current_token.location)
            self._advance()
            return identifier
        else:
            raise SyntaxError(
                f"Expected identifier or pattern "
                f"at {self.current_token.location.filename}:"
                f"{self.current_token.location.line}:{self.current_token.location.column}"
            )

    def _parse_variable_declaration(self) -> VariableDeclaration:
        """
        Parse variable declaration statement.

        Supports var, let, and const declarations with proper validation.
        const declarations must have initializers.
        """
        start_location = self.current_token.location

        # Determine declaration kind
        if self.current_token.type == TokenType.VAR:
            kind = "var"
            self._expect(TokenType.VAR)
        elif self.current_token.type == TokenType.LET:
            kind = "let"
            self._expect(TokenType.LET)
        elif self.current_token.type == TokenType.CONST:
            kind = "const"
            self._expect(TokenType.CONST)
        else:
            raise SyntaxError(
                f"Expected var, let, or const, got {self.current_token.type} "
                f"at {self.current_token.location.filename}:"
                f"{self.current_token.location.line}:{self.current_token.location.column}"
            )

        declarations = []

        # Parse first declarator
        declarations.append(self._parse_variable_declarator(kind))

        # Parse additional declarators (comma-separated)
        while self.current_token.type == TokenType.COMMA:
            self._advance()  # skip comma
            declarations.append(self._parse_variable_declarator(kind))

        # Expect semicolon
        if self.current_token.type == TokenType.SEMICOLON:
            self._advance()

        return VariableDeclaration(
            kind=kind, declarations=declarations, location=start_location
        )

    def _parse_variable_declaration_for_loop(self) -> VariableDeclaration:
        """
        Parse variable declaration for for-loop context.

        Like _parse_variable_declaration() but does NOT consume trailing semicolon.
        Used in for loop headers where semicolons are part of for loop syntax.
        """
        start_location = self.current_token.location

        # Determine declaration kind
        if self.current_token.type == TokenType.VAR:
            kind = "var"
            self._expect(TokenType.VAR)
        elif self.current_token.type == TokenType.LET:
            kind = "let"
            self._expect(TokenType.LET)
        elif self.current_token.type == TokenType.CONST:
            kind = "const"
            self._expect(TokenType.CONST)
        else:
            raise SyntaxError(
                f"Expected var, let, or const, got {self.current_token.type} "
                f"at {self.current_token.location.filename}:"
                f"{self.current_token.location.line}:{self.current_token.location.column}"
            )

        declarations = []

        # Parse first declarator
        declarations.append(self._parse_variable_declarator(kind))

        # Parse additional declarators (comma-separated)
        while self.current_token.type == TokenType.COMMA:
            self._advance()  # skip comma
            declarations.append(self._parse_variable_declarator(kind))

        # Do NOT consume semicolon (for-loop will handle it)

        return VariableDeclaration(
            kind=kind, declarations=declarations, location=start_location
        )

    def _parse_variable_declarator(self, kind: str) -> VariableDeclarator:
        """
        Parse a single variable declarator.

        Supports both simple identifiers and destructuring patterns.

        Args:
            kind: Declaration kind ("var", "let", or "const")

        Returns:
            VariableDeclarator: Parsed declarator

        Raises:
            SyntaxError: If const declaration lacks initializer
        """
        start_location = self.current_token.location

        # Check if this is a destructuring pattern
        if self.current_token.type == TokenType.LBRACE:
            # Object destructuring: {x, y} = obj
            pattern_id = self._parse_object_pattern()
        elif self.current_token.type == TokenType.LBRACKET:
            # Array destructuring: [a, b] = arr
            pattern_id = self._parse_array_pattern()
        else:
            # Simple identifier: x = value
            name_token = self._expect(TokenType.IDENTIFIER)
            pattern_id = name_token.value

        init = None
        if self.current_token.type == TokenType.ASSIGN:
            self._advance()  # skip =
            init = self._parse_expression()

        # Validate const must have initializer
        if kind == "const" and init is None:
            raise SyntaxError(
                f"Missing initializer in const declaration "
                f"at {start_location.filename}:"
                f"{start_location.line}:{start_location.column}"
            )

        return VariableDeclarator(id=pattern_id, init=init)

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

    def _parse_async_function_declaration(self) -> AsyncFunctionDeclaration:
        """Parse async function declaration."""
        start_location = self.current_token.location
        self._expect(TokenType.ASYNC)
        self._expect(TokenType.FUNCTION)

        # Function name
        name_token = self._expect(TokenType.IDENTIFIER)
        func_id = Identifier(name=name_token.value, location=name_token.location)

        # Parameters
        self._expect(TokenType.LPAREN)
        parameters = self._parse_parameter_list()
        self._expect(TokenType.RPAREN)

        # Body
        body = self._parse_block_statement()

        return AsyncFunctionDeclaration(
            id=func_id, params=parameters, body=body, location=start_location
        )

    def _parse_parameter_list(self) -> List[str]:
        """
        Parse function parameter list.

        Supports regular parameters and rest parameters (...param).
        Rest parameters are stored with "..." prefix for now.
        """
        parameters = []

        if self.current_token.type != TokenType.RPAREN:
            # Parse first parameter
            if self.current_token.type == TokenType.SPREAD:
                self._advance()  # skip ...
                param_token = self._expect(TokenType.IDENTIFIER)
                parameters.append(f"...{param_token.value}")  # Mark as rest parameter
                # Rest parameter must be last
                if self.current_token.type == TokenType.COMMA:
                    raise SyntaxError(
                        f"Rest parameter must be last formal parameter "
                        f"at {self.current_token.location.filename}:"
                        f"{self.current_token.location.line}:{self.current_token.location.column}"
                    )
            else:
                param_token = self._expect(TokenType.IDENTIFIER)
                parameters.append(param_token.value)

            # Parse additional parameters
            while self.current_token.type == TokenType.COMMA:
                self._advance()  # skip comma

                if self.current_token.type == TokenType.SPREAD:
                    self._advance()  # skip ...
                    param_token = self._expect(TokenType.IDENTIFIER)
                    parameters.append(f"...{param_token.value}")  # Mark as rest parameter
                    # Rest parameter must be last
                    if self.current_token.type == TokenType.COMMA:
                        raise SyntaxError(
                            f"Rest parameter must be last formal parameter "
                            f"at {self.current_token.location.filename}:"
                            f"{self.current_token.location.line}:{self.current_token.location.column}"
                        )
                else:
                    param_token = self._expect(TokenType.IDENTIFIER)
                    parameters.append(param_token.value)

        return parameters

    def _parse_class_declaration(self) -> ClassDeclaration:
        """
        Parse class declaration.

        Syntax: class ClassName [extends SuperClass] { methods }

        Returns:
            ClassDeclaration: Parsed class declaration
        """
        start_location = self.current_token.location
        self._expect(TokenType.CLASS)

        # Class name (required for declarations)
        id_token = self._expect(TokenType.IDENTIFIER)
        class_id = Identifier(name=id_token.value, location=id_token.location)

        # Check for extends clause
        super_class = None
        if self.current_token.type == TokenType.EXTENDS:
            self._advance()  # skip extends
            # Parse super class expression (usually identifier)
            super_class = self._parse_primary_expression()

        # Parse class body
        body = self._parse_class_body()

        return ClassDeclaration(
            id=class_id, superClass=super_class, body=body, location=start_location
        )

    def _parse_class_expression(self) -> ClassExpression:
        """
        Parse class expression.

        Syntax: class [ClassName] [extends SuperClass] { methods }

        Returns:
            ClassExpression: Parsed class expression
        """
        start_location = self.current_token.location
        self._expect(TokenType.CLASS)

        # Class name (optional for expressions)
        class_id = None
        if self.current_token.type == TokenType.IDENTIFIER:
            id_token = self.current_token
            self._advance()
            class_id = Identifier(name=id_token.value, location=id_token.location)

        # Check for extends clause
        super_class = None
        if self.current_token.type == TokenType.EXTENDS:
            self._advance()  # skip extends
            # Parse super class expression (usually identifier)
            super_class = self._parse_primary_expression()

        # Parse class body
        body = self._parse_class_body()

        return ClassExpression(
            id=class_id, superClass=super_class, body=body, location=start_location
        )

    def _parse_class_body(self) -> List[MethodDefinition]:
        """
        Parse class body (methods).

        Syntax: { [static] [get|set] methodName(params) { body } }

        Returns:
            List[MethodDefinition]: List of method definitions
        """
        self._expect(TokenType.LBRACE)

        methods = []

        while self.current_token.type != TokenType.RBRACE:
            # Check for static modifier
            is_static = False
            if self.current_token.type == TokenType.STATIC:
                is_static = True
                self._advance()  # skip static

            # Check for getter/setter
            method_kind = "method"
            if self.current_token.type == TokenType.GET:
                method_kind = "get"
                self._advance()  # skip get
            elif self.current_token.type == TokenType.SET:
                method_kind = "set"
                self._advance()  # skip set

            # Method name
            method_start = self.current_token.location
            if self.current_token.type != TokenType.IDENTIFIER:
                raise SyntaxError(
                    f"Expected method name in class body "
                    f"at {self.current_token.location.filename}:"
                    f"{self.current_token.location.line}:{self.current_token.location.column}"
                )

            method_name = self.current_token.value
            method_name_token = self.current_token
            self._advance()

            # Check if it's the constructor
            if method_name == "constructor":
                method_kind = "constructor"

            # Method parameters
            self._expect(TokenType.LPAREN)
            parameters = self._parse_parameter_list()
            self._expect(TokenType.RPAREN)

            # Method body
            body = self._parse_block_statement()

            # Create method definition
            key = Identifier(name=method_name, location=method_name_token.location)
            value = FunctionExpression(
                name=None,  # Methods don't have names (they're properties)
                parameters=parameters,
                body=body,
                location=method_start,
            )

            method = MethodDefinition(
                key=key,
                value=value,
                kind=method_kind,
                computed=False,  # For now, only support non-computed property names
                static=is_static,
                location=method_start,
            )

            methods.append(method)

        self._expect(TokenType.RBRACE)

        return methods

    def _parse_function_expression(self) -> FunctionExpression:
        """Parse function expression (anonymous or named)."""
        start_location = self.current_token.location
        self._expect(TokenType.FUNCTION)

        # Function name (optional for expressions)
        name = None
        if self.current_token.type == TokenType.IDENTIFIER:
            name_token = self.current_token
            name = name_token.value
            self._advance()

        # Parameters
        self._expect(TokenType.LPAREN)
        parameters = self._parse_parameter_list()
        self._expect(TokenType.RPAREN)

        # Body
        body = self._parse_block_statement()

        return FunctionExpression(
            name=name, parameters=parameters, body=body, location=start_location
        )

    def _parse_async_function_expression(self) -> AsyncFunctionExpression:
        """Parse async function expression (anonymous or named)."""
        start_location = self.current_token.location
        self._expect(TokenType.ASYNC)
        self._expect(TokenType.FUNCTION)

        # Function name (optional for expressions)
        func_id = None
        if self.current_token.type == TokenType.IDENTIFIER:
            id_token = self.current_token
            func_id = Identifier(name=id_token.value, location=id_token.location)
            self._advance()

        # Parameters
        self._expect(TokenType.LPAREN)
        parameters = self._parse_parameter_list()
        self._expect(TokenType.RPAREN)

        # Body
        body = self._parse_block_statement()

        return AsyncFunctionExpression(
            id=func_id, params=parameters, body=body, location=start_location
        )

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

    def _parse_for_statement(self):
        """
        Parse for statement (traditional, for-in, or for-of).

        Handles three types:
        - Traditional: for (init; test; update) { ... }
        - For-in: for (var key in obj) { ... }
        - For-of: for (var value of array) { ... }

        Returns:
            ForStatement, ForInStatement, or ForOfStatement
        """
        start_location = self.current_token.location
        self._expect(TokenType.FOR)
        self._expect(TokenType.LPAREN)

        # Parse the left side (init for traditional, left for for-in/for-of)
        # This can be:
        # - VariableDeclaration (var/let/const)
        # - Identifier
        # - Expression
        # - Nothing (empty init in traditional for)

        left_or_init = None

        if self.current_token.type == TokenType.SEMICOLON:
            # Empty init in traditional for loop: for (;;)
            left_or_init = None
        elif self.current_token.type in (TokenType.VAR, TokenType.LET, TokenType.CONST):
            # Variable declaration (without semicolon consumption for for loop context)
            left_or_init = self._parse_variable_declaration_for_loop()
        elif self.current_token.type == TokenType.RPAREN:
            # Empty loop header (shouldn't happen, but handle gracefully)
            raise SyntaxError(
                f"Unexpected ) in for loop at {self.current_token.location.filename}:"
                f"{self.current_token.location.line}:{self.current_token.location.column}"
            )
        else:
            # Expression or identifier
            left_or_init = self._parse_assignment_expression()

        # Check what comes next to determine loop type
        if self.current_token.type == TokenType.IN:
            # For-in loop
            self._expect(TokenType.IN)
            right = self._parse_expression()
            self._expect(TokenType.RPAREN)
            body = self._parse_statement()
            return ForInStatement(left=left_or_init, right=right, body=body, location=start_location)

        elif self.current_token.type == TokenType.OF:
            # For-of loop
            self._expect(TokenType.OF)
            right = self._parse_expression()
            self._expect(TokenType.RPAREN)
            body = self._parse_statement()
            return ForOfStatement(left=left_or_init, right=right, body=body, location=start_location)

        else:
            # Traditional for loop
            init = left_or_init

            # Expect semicolon after init
            self._expect(TokenType.SEMICOLON)

            # Test condition (optional)
            test = None
            if self.current_token.type != TokenType.SEMICOLON:
                test = self._parse_expression()
            self._expect(TokenType.SEMICOLON)

            # Update expression (optional)
            update = None
            if self.current_token.type != TokenType.RPAREN:
                update = self._parse_expression()

            self._expect(TokenType.RPAREN)

            # Body
            body = self._parse_statement()

            return ForStatement(
                init=init,
                test=test,
                update=update,
                body=body,
                location=start_location
            )

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
        """Parse assignment expression or arrow function (async or sync)."""
        # Check for async arrow function
        if self.current_token.type == TokenType.ASYNC:
            # Look ahead to see if it's an async arrow function
            next_token = self.lexer.peek_token(0)
            if next_token.type in (TokenType.LPAREN, TokenType.IDENTIFIER):
                # Could be async arrow function
                # Save position to restore if not arrow
                saved_pos = self.current_token
                self._advance()  # consume 'async'

                if self._is_arrow_function():
                    # It's an async arrow function
                    return self._parse_arrow_function(is_async=True)
                else:
                    # Not an async arrow, this was an error - async must be followed by function or arrow
                    raise SyntaxError(
                        f"Unexpected 'async' keyword "
                        f"at {saved_pos.location.filename}:"
                        f"{saved_pos.location.line}:{saved_pos.location.column}"
                    )

        # Try to parse regular arrow function
        if self._is_arrow_function():
            return self._parse_arrow_function(is_async=False)

        # Otherwise parse normal assignment
        left = self._parse_equality_expression()

        if self.current_token.type == TokenType.ASSIGN:
            op_token = self.current_token
            self._advance()
            right = self._parse_assignment_expression()
            return BinaryExpression(
                operator="=", left=left, right=right, location=op_token.location
            )

        return left

    def _is_arrow_function(self) -> bool:
        """
        Check if current position is start of arrow function.

        Lookahead to distinguish:
        - x => expr (single param without parens)
        - (x) => expr (single param with parens)
        - (x, y) => expr (multiple params)
        - () => expr (no params)

        Returns:
            bool: True if arrow function detected, False otherwise
        """
        # Case 1: Single parameter without parens: x =>
        if self.current_token.type == TokenType.IDENTIFIER:
            next_token = self.lexer.peek_token(0)
            return next_token.type == TokenType.ARROW

        # Case 2: Parameters with parens: (x) => or (x, y) => or () =>
        if self.current_token.type == TokenType.LPAREN:
            # Need to look ahead past parameter list to find =>
            return self._lookahead_arrow_params()

        return False

    def _lookahead_arrow_params(self) -> bool:
        """
        Lookahead to check if parenthesized expression is arrow function params.

        Distinguishes:
        - (x) => expr (arrow function)
        - (x) (grouped expression followed by something else)

        Returns:
            bool: True if => found after closing paren
        """
        # We're at LPAREN, peek ahead to find matching RPAREN
        # Start at 1 because we're already at the first LPAREN
        paren_depth = 1
        offset = -1

        while True:
            offset += 1
            token = self.lexer.peek_token(offset)

            if token.type == TokenType.EOF:
                return False

            if token.type == TokenType.LPAREN:
                paren_depth += 1
            elif token.type == TokenType.RPAREN:
                paren_depth -= 1
                if paren_depth == 0:
                    # Found matching closing paren
                    # Check if next token is =>
                    next_token = self.lexer.peek_token(offset + 1)
                    return next_token.type == TokenType.ARROW

            # Safety: don't lookahead too far
            if offset > 100:
                return False

    def _parse_arrow_function(self, is_async: bool = False):
        """
        Parse arrow function expression (sync or async).

        Handles:
        - x => expr (single param without parens)
        - (x) => expr (single param with parens)
        - (x, y) => expr (multiple params)
        - () => expr (no params)
        - x => { block } (block body)
        - x => expr (expression body)
        - async x => expr (async arrow)
        - async (x) => expr (async arrow with parens)

        Args:
            is_async: Whether this is an async arrow function

        Returns:
            ArrowFunctionExpression or AsyncArrowFunctionExpression
        """
        start_location = self.current_token.location

        # Parse parameters
        params = []

        if self.current_token.type == TokenType.IDENTIFIER:
            # Single parameter without parens: x =>
            param_token = self.current_token
            params.append(
                Identifier(name=param_token.value, location=param_token.location)
            )
            self._advance()
        elif self.current_token.type == TokenType.LPAREN:
            # Parameters with parens: (x), (x, y), (), or (...rest)
            self._advance()  # skip (

            # Parse parameter list
            while (
                self.current_token.type != TokenType.RPAREN
                and self.current_token.type != TokenType.EOF
            ):
                # Check for rest parameter
                if self.current_token.type == TokenType.SPREAD:
                    rest_location = self.current_token.location
                    self._advance()  # skip ...
                    param_token = self._expect(TokenType.IDENTIFIER)
                    params.append(
                        RestElement(
                            argument=Identifier(
                                name=param_token.value, location=param_token.location
                            ),
                            location=rest_location,
                        )
                    )
                    # Rest parameter must be last
                    if self.current_token.type == TokenType.COMMA:
                        raise SyntaxError(
                            f"Rest parameter must be last formal parameter "
                            f"at {self.current_token.location.filename}:"
                            f"{self.current_token.location.line}:{self.current_token.location.column}"
                        )
                else:
                    # Parse parameter identifier
                    param_token = self._expect(TokenType.IDENTIFIER)
                    params.append(
                        Identifier(name=param_token.value, location=param_token.location)
                    )

                # Check for comma (more parameters)
                if self.current_token.type == TokenType.COMMA:
                    self._advance()  # skip comma
                elif self.current_token.type != TokenType.RPAREN:
                    raise SyntaxError(
                        f"Expected ',' or ')' in arrow function parameters, "
                        f"got {self.current_token.type} "
                        f"at {self.current_token.location.filename}:"
                        f"{self.current_token.location.line}:{self.current_token.location.column}"
                    )

            self._expect(TokenType.RPAREN)
        else:
            raise SyntaxError(
                f"Expected parameter or '(' in arrow function, "
                f"got {self.current_token.type} "
                f"at {self.current_token.location.filename}:"
                f"{self.current_token.location.line}:{self.current_token.location.column}"
            )

        # Expect arrow =>
        self._expect(TokenType.ARROW)

        # Parse body (expression or block)
        if self.current_token.type == TokenType.LBRACE:
            # Block body: { statements }
            body = self._parse_block_statement()
        else:
            # Expression body: expr (implicit return)
            body = self._parse_assignment_expression()

        # Return appropriate type based on is_async
        if is_async:
            return AsyncArrowFunctionExpression(
                params=params, body=body, location=start_location
            )
        else:
            return ArrowFunctionExpression(
                params=params, body=body, is_async=False, location=start_location
            )

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
        left = self._parse_unary_expression()

        while self.current_token.type in (TokenType.MULTIPLY, TokenType.DIVIDE):
            if self.current_token.type == TokenType.MULTIPLY:
                op = "*"
            else:
                op = "/"

            op_token = self.current_token
            self._advance()
            right = self._parse_unary_expression()
            left = BinaryExpression(
                operator=op, left=left, right=right, location=op_token.location
            )

        return left

    def _parse_unary_expression(self) -> Expression:
        """Parse unary expression (await, unary operators)."""
        # Await expression
        if self.current_token.type == TokenType.AWAIT:
            start_location = self.current_token.location
            self._advance()  # consume 'await'
            argument = self._parse_unary_expression()
            return AwaitExpression(argument=argument, location=start_location)

        # Unary operators: -, +
        # Note: ! (NOT), typeof, void, delete can be added later as needed
        if self.current_token.type in (TokenType.MINUS, TokenType.PLUS):
            start_location = self.current_token.location
            operator_token = self.current_token
            self._advance()  # consume operator
            argument = self._parse_unary_expression()

            # Map token type to operator string
            operator_map = {
                TokenType.MINUS: "-",
                TokenType.PLUS: "+",
            }
            operator = operator_map[operator_token.type]

            return UnaryExpression(
                operator=operator, argument=argument, location=start_location
            )

        # Fall through to call expression
        return self._parse_call_expression()

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

        # Template literal
        if self.current_token.type == TokenType.TEMPLATE_LITERAL:
            return self._parse_template_literal()

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

        # Class expression
        if self.current_token.type == TokenType.CLASS:
            return self._parse_class_expression()

        # Async function expression
        if self.current_token.type == TokenType.ASYNC:
            # Look ahead to see if it's 'async function'
            next_token = self.lexer.peek_token(0)
            if next_token.type == TokenType.FUNCTION:
                return self._parse_async_function_expression()

        # Function expression
        if self.current_token.type == TokenType.FUNCTION:
            return self._parse_function_expression()

        # New expression
        if self.current_token.type == TokenType.NEW:
            return self._parse_new_expression()

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

        Syntax: [element1, element2, ...] or [element1, ...spread, element2]

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
            # Check for spread element
            if self.current_token.type == TokenType.SPREAD:
                spread_location = self.current_token.location
                self._advance()  # skip ...
                # Parse the spread argument
                argument = self._parse_expression()
                elements.append(SpreadElement(argument=argument, location=spread_location))
            else:
                # Parse normal element expression
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

        Syntax: {key: value, ...} or {key, ...} or {method() {...}} or {...spread}

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
            # Check for spread property
            if self.current_token.type == TokenType.SPREAD:
                spread_location = self.current_token.location
                self._advance()  # skip ...
                # Parse the spread argument
                argument = self._parse_expression()
                # Use SpreadElement for object spread as well
                properties.append(SpreadElement(argument=argument, location=spread_location))
            else:
                # Parse normal property
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

    def _parse_template_literal(self) -> TemplateLiteral:
        """
        Parse a template literal expression.

        Template literals are backtick-delimited strings that can contain
        ${} expressions. This method parses the template, extracting static
        text parts (quasis) and embedded expressions.

        Returns:
            TemplateLiteral: Parsed template literal AST node

        Example:
            `Hello ${name}!` → quasis=["Hello ", "!"], expressions=[name]
        """
        token = self.current_token
        location = token.location
        template_content = token.value  # Full template content
        self._advance()

        # Parse template content to extract quasis and expressions
        quasis = []
        expressions = []

        i = 0
        current_quasi = ""

        while i < len(template_content):
            # Check for expression start ${
            if i < len(template_content) - 1 and template_content[i:i+2] == "${":
                # Save current quasi
                quasis.append(current_quasi)
                current_quasi = ""

                # Find matching }
                i += 2  # Skip ${
                expr_start = i
                brace_count = 1

                while i < len(template_content) and brace_count > 0:
                    if template_content[i] == "{":
                        brace_count += 1
                    elif template_content[i] == "}":
                        brace_count -= 1
                    i += 1

                # Extract expression text
                expr_text = template_content[expr_start:i-1]

                # Parse the expression
                expr_lexer = Lexer(expr_text, location.filename)
                expr_parser = Parser(expr_lexer)
                expr = expr_parser._parse_expression()
                expressions.append(expr)
            else:
                current_quasi += template_content[i]
                i += 1

        # Add final quasi
        quasis.append(current_quasi)

        return TemplateLiteral(
            quasis=quasis,
            expressions=expressions,
            location=location,
        )

    def _parse_new_expression(self) -> NewExpression:
        """
        Parse new Constructor(args) expression.

        Syntax: new Constructor(arg1, arg2, ...)

        Returns:
            NewExpression: Parsed new expression

        Example:
            >>> parser._parse_new_expression()  # parses "new Promise(executor)"
            NewExpression(callee=Identifier("Promise"), arguments=[...])
        """
        start_location = self.current_token.location
        self._expect(TokenType.NEW)  # Consume 'new' keyword

        # Parse constructor (can be Identifier or MemberExpression)
        # Use _parse_member_expression to handle both cases
        callee = self._parse_member_expression()

        # Parse arguments
        self._expect(TokenType.LPAREN)
        arguments = []

        if self.current_token.type != TokenType.RPAREN:
            # Parse first argument
            arguments.append(self._parse_assignment_expression())

            # Parse remaining arguments
            while self.current_token.type == TokenType.COMMA:
                self._advance()  # skip comma
                arguments.append(self._parse_assignment_expression())

        self._expect(TokenType.RPAREN)

        return NewExpression(
            callee=callee,
            arguments=arguments,
            location=start_location,
        )

    # ========================================================================
    # ES MODULES - IMPORT/EXPORT PARSING
    # ========================================================================

    def _parse_import_declaration(self) -> ImportDeclaration:
        """
        Parse import declaration.

        Variants:
        - import './module.js';                          (side-effect)
        - import foo from './module.js';                 (default)
        - import { x, y } from './module.js';            (named)
        - import { x as y } from './module.js';          (named with alias)
        - import * as name from './module.js';           (namespace)
        - import foo, { x } from './module.js';          (default + named)

        Returns:
            ImportDeclaration: Parsed import declaration
        """
        start_location = self.current_token.location
        self._expect(TokenType.IMPORT)

        specifiers = []

        # Check for side-effect import: import './module.js';
        if self.current_token.type == TokenType.STRING:
            source = Literal(value=self.current_token.value, location=self.current_token.location)
            self._advance()
            self._consume_semicolon()
            return ImportDeclaration(specifiers=[], source=source, location=start_location)

        # Check for namespace import: import * as name from './module.js';
        if self.current_token.type == TokenType.MULTIPLY:
            self._advance()  # consume *
            self._expect(TokenType.AS)
            local_token = self._expect(TokenType.IDENTIFIER)
            local = Identifier(name=local_token.value, location=local_token.location)
            specifiers.append(ImportNamespaceSpecifier(local=local, location=start_location))
        elif self.current_token.type == TokenType.LBRACE:
            # Named imports: import { x, y } from './module.js';
            specifiers.extend(self._parse_import_specifiers())
        else:
            # Default import: import foo from './module.js';
            # Or default + named: import foo, { x } from './module.js';
            if self.current_token.type == TokenType.IDENTIFIER:
                local_token = self._expect(TokenType.IDENTIFIER)
                local = Identifier(name=local_token.value, location=local_token.location)
                specifiers.append(ImportDefaultSpecifier(local=local, location=local_token.location))

                # Check for comma (default + named)
                if self.current_token.type == TokenType.COMMA:
                    self._advance()  # consume comma

                    # Check for namespace import after default
                    if self.current_token.type == TokenType.MULTIPLY:
                        self._advance()  # consume *
                        self._expect(TokenType.AS)
                        local_token = self._expect(TokenType.IDENTIFIER)
                        local = Identifier(name=local_token.value, location=local_token.location)
                        specifiers.append(ImportNamespaceSpecifier(local=local, location=start_location))
                    else:
                        # Named imports after default
                        specifiers.extend(self._parse_import_specifiers())

        # Parse FROM './module.js'
        self._expect(TokenType.FROM)
        source_token = self._expect(TokenType.STRING)
        source = Literal(value=source_token.value, location=source_token.location)

        self._consume_semicolon()

        return ImportDeclaration(specifiers=specifiers, source=source, location=start_location)

    def _parse_import_specifiers(self) -> List[ImportSpecifier]:
        """
        Parse list of import specifiers: { x, y as z, ... }

        Returns:
            List[ImportSpecifier]: List of parsed import specifiers
        """
        self._expect(TokenType.LBRACE)
        specifiers = []

        while self.current_token.type != TokenType.RBRACE:
            imported_token = self._expect(TokenType.IDENTIFIER)
            imported = Identifier(name=imported_token.value, location=imported_token.location)

            # Check for 'as' alias
            if self.current_token.type == TokenType.AS:
                self._advance()  # consume 'as'
                local_token = self._expect(TokenType.IDENTIFIER)
                local = Identifier(name=local_token.value, location=local_token.location)
            else:
                local = Identifier(name=imported_token.value, location=imported_token.location)

            specifiers.append(ImportSpecifier(imported=imported, local=local, location=imported_token.location))

            if self.current_token.type != TokenType.RBRACE:
                self._expect(TokenType.COMMA)

        self._expect(TokenType.RBRACE)
        return specifiers

    def _parse_export_declaration(self):
        """
        Parse export declaration.

        Variants:
        - export const x = 1;                     (named declaration)
        - export function foo() {}                (named function)
        - export class Bar {}                     (named class)
        - export { x, y };                        (named list)
        - export { x as y };                      (named with alias)
        - export { x } from './other.js';         (re-export named)
        - export * from './other.js';             (re-export all)
        - export * as name from './other.js';     (re-export all as namespace)
        - export default expression;              (default export)
        - export default function() {}            (default function)
        - export default class {}                 (default class)

        Returns:
            Union[ExportNamedDeclaration, ExportDefaultDeclaration, ExportAllDeclaration]
        """
        start_location = self.current_token.location
        self._expect(TokenType.EXPORT)

        # Check for default export
        if self.current_token.type == TokenType.DEFAULT:
            return self._parse_export_default_declaration(start_location)

        # Check for export * from
        if self.current_token.type == TokenType.MULTIPLY:
            return self._parse_export_all_declaration(start_location)

        # Check for export declaration: export const x = 1;
        if self._check_declaration_start():
            declaration = self._parse_declaration()
            return ExportNamedDeclaration(
                declaration=declaration,
                specifiers=[],
                source=None,
                location=start_location
            )

        # export { x, y } [from './module.js'];
        self._expect(TokenType.LBRACE)
        specifiers = self._parse_export_specifiers()
        self._expect(TokenType.RBRACE)

        # Check for 'from' (re-export)
        source = None
        if self.current_token.type == TokenType.FROM:
            self._advance()  # consume 'from'
            source_token = self._expect(TokenType.STRING)
            source = Literal(value=source_token.value, location=source_token.location)

        self._consume_semicolon()

        return ExportNamedDeclaration(
            declaration=None,
            specifiers=specifiers,
            source=source,
            location=start_location
        )

    def _parse_export_default_declaration(self, start_location):
        """
        Parse export default declaration.

        Handles:
        - export default function() {}
        - export default function name() {}
        - export default class {}
        - export default class Name {}
        - export default expression;

        Args:
            start_location: Start location of export keyword

        Returns:
            ExportDefaultDeclaration
        """
        self._advance()  # consume 'default'

        # Check for function/class declaration or expression
        if self.current_token.type == TokenType.FUNCTION:
            # Look ahead to check if function has a name
            # If next token is LPAREN, it's anonymous function expression
            # Otherwise it's a named function declaration
            next_token = self.lexer.peek_token(0)
            if next_token.type == TokenType.LPAREN:
                # Anonymous function: export default function() {}
                declaration = self._parse_function_expression()
            else:
                # Named function: export default function foo() {}
                declaration = self._parse_function_declaration()
        elif self.current_token.type == TokenType.CLASS:
            # Classes can also be anonymous or named
            # For now, use parse_class_expression for both
            # The class parser should handle both cases
            declaration = self._parse_class_declaration()
        else:
            # Expression
            declaration = self._parse_assignment_expression()
            self._consume_semicolon()

        return ExportDefaultDeclaration(declaration=declaration, location=start_location)

    def _parse_export_all_declaration(self, start_location):
        """
        Parse export * from './module.js';

        Handles:
        - export * from './module.js';
        - export * as name from './module.js';

        Args:
            start_location: Start location of export keyword

        Returns:
            ExportAllDeclaration
        """
        self._advance()  # consume *

        exported = None
        # Check for: export * as name from './module.js';
        if self.current_token.type == TokenType.AS:
            self._advance()  # consume 'as'
            exported_token = self._expect(TokenType.IDENTIFIER)
            exported = Identifier(name=exported_token.value, location=exported_token.location)

        self._expect(TokenType.FROM)
        source_token = self._expect(TokenType.STRING)
        source = Literal(value=source_token.value, location=source_token.location)

        self._consume_semicolon()

        return ExportAllDeclaration(source=source, exported=exported, location=start_location)

    def _parse_export_specifiers(self) -> List[ExportSpecifier]:
        """
        Parse list of export specifiers: { x, y as z }

        Returns:
            List[ExportSpecifier]: List of parsed export specifiers
        """
        specifiers = []

        while self.current_token.type != TokenType.RBRACE:
            local_token = self._expect(TokenType.IDENTIFIER)
            local = Identifier(name=local_token.value, location=local_token.location)

            # Check for 'as' alias
            if self.current_token.type == TokenType.AS:
                self._advance()  # consume 'as'
                exported_token = self._expect(TokenType.IDENTIFIER)
                exported = Identifier(name=exported_token.value, location=exported_token.location)
            else:
                exported = Identifier(name=local_token.value, location=local_token.location)

            specifiers.append(ExportSpecifier(local=local, exported=exported, location=local_token.location))

            if self.current_token.type != TokenType.RBRACE:
                self._expect(TokenType.COMMA)

        return specifiers

    def _parse_declaration(self):
        """
        Parse a declaration (variable, function, or class).

        Returns:
            Union[VariableDeclaration, FunctionDeclaration, ClassDeclaration]
        """
        if self.current_token.type in (TokenType.VAR, TokenType.LET, TokenType.CONST):
            return self._parse_variable_declaration()
        elif self.current_token.type == TokenType.FUNCTION:
            return self._parse_function_declaration()
        elif self.current_token.type == TokenType.CLASS:
            return self._parse_class_declaration()
        else:
            raise SyntaxError(
                f"Expected declaration, got {self.current_token.type} "
                f"at {self.current_token.location.filename}:"
                f"{self.current_token.location.line}:{self.current_token.location.column}"
            )

    def _check_declaration_start(self) -> bool:
        """
        Check if current token starts a declaration.

        Returns:
            bool: True if current token can start a declaration
        """
        return self.current_token.type in (
            TokenType.VAR,
            TokenType.LET,
            TokenType.CONST,
            TokenType.FUNCTION,
            TokenType.CLASS
        )

    def _consume_semicolon(self):
        """
        Consume semicolon if present (ASI - Automatic Semicolon Insertion).

        This method implements basic automatic semicolon insertion rules.
        It consumes a semicolon if present, but doesn't require one,
        allowing for ASI behavior.
        """
        if self.current_token.type == TokenType.SEMICOLON:
            self._advance()
