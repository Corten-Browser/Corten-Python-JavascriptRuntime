"""
Lexer for JavaScript source code tokenization.

Provides lexical analysis (tokenization) of ES5 JavaScript source code,
converting source text into a stream of tokens for parsing.
"""

from typing import List

from components.shared_types.src import SourceLocation
from .token import Token, TokenType


class Lexer:
    """
    Lexical analyzer for JavaScript source code.

    Converts JavaScript source code into a stream of tokens, handling
    keywords, identifiers, literals, operators, and punctuation.
    Tracks source locations for error reporting.

    Attributes:
        source: The source code to tokenize
        filename: The name of the source file
        position: Current position in source
        line: Current line number (1-indexed)
        column: Current column number (1-indexed)

    Example:
        >>> lexer = Lexer("var x = 5;", "test.js")
        >>> token = lexer.next_token()
        >>> token.type
        <TokenType.VAR: 1>
    """

    # Keyword mappings
    KEYWORDS = {
        "var": TokenType.VAR,
        "let": TokenType.LET,
        "const": TokenType.CONST,
        "function": TokenType.FUNCTION,
        "class": TokenType.CLASS,
        "extends": TokenType.EXTENDS,
        "static": TokenType.STATIC,
        "super": TokenType.SUPER,
        "get": TokenType.GET,
        "set": TokenType.SET,
        "if": TokenType.IF,
        "else": TokenType.ELSE,
        "while": TokenType.WHILE,
        "for": TokenType.FOR,
        "in": TokenType.IN,
        "of": TokenType.OF,
        "return": TokenType.RETURN,
        "break": TokenType.BREAK,
        "continue": TokenType.CONTINUE,
        "new": TokenType.NEW,
        "true": TokenType.TRUE,
        "false": TokenType.FALSE,
        "null": TokenType.NULL,
        "undefined": TokenType.UNDEFINED,
        "async": TokenType.ASYNC,
        "await": TokenType.AWAIT,
        "default": TokenType.DEFAULT,
        "import": TokenType.IMPORT,
        "export": TokenType.EXPORT,
        "from": TokenType.FROM,
        "as": TokenType.AS,
    }

    def __init__(self, source: str, filename: str = "<stdin>"):
        """
        Initialize lexer with source code.

        Args:
            source: JavaScript source code to tokenize
            filename: Name of source file for error reporting
        """
        self.source = source
        self.filename = filename
        self.position = 0
        self.line = 1
        self.column = 1
        self._token_buffer: List[Token] = []
        self._last_token: Token = None

    def next_token(self) -> Token:
        """
        Get the next token from source.

        Returns:
            Token: The next token in the source stream

        Example:
            >>> lexer = Lexer("var x", "test.js")
            >>> token = lexer.next_token()
            >>> token.type == TokenType.VAR
            True
        """
        # Check if we have buffered tokens from peek
        if self._token_buffer:
            token = self._token_buffer.pop(0)
        else:
            token = self._scan_token()

        self._last_token = token
        return token

    def peek_token(self, offset: int = 0) -> Token:
        """
        Peek ahead at tokens without consuming them.

        Args:
            offset: Number of tokens to look ahead (0 = current)

        Returns:
            Token: The token at the specified offset

        Example:
            >>> lexer = Lexer("var x = 5", "test.js")
            >>> token = lexer.peek_token(0)
            >>> token.type == TokenType.VAR
            True
            >>> lexer.next_token().type == TokenType.VAR
            True
        """
        # Fill buffer up to offset + 1
        while len(self._token_buffer) <= offset:
            self._token_buffer.append(self._scan_token())

        return self._token_buffer[offset]

    def _scan_token(self) -> Token:
        """
        Scan and return the next token.

        Returns:
            Token: The next token in the source
        """
        # Skip whitespace and comments
        self._skip_whitespace_and_comments()

        # Check for end of file
        if self.position >= len(self.source):
            return self._make_token(TokenType.EOF, None)

        start_line = self.line
        start_column = self.column
        start_offset = self.position

        char = self.source[self.position]

        # Identifiers and keywords
        if char.isalpha() or char in "_$":
            return self._scan_identifier()

        # Numbers
        if char.isdigit():
            return self._scan_number()

        # String literals
        if char == '"' or char == "'":
            return self._scan_string()

        # Template literals
        if char == "`":
            return self._scan_template_literal()

        # Regular expressions
        # Note: This is a simplified check. In a full implementation,
        # we'd need to check if division is expected based on previous token.
        if char == "/" and self._is_regexp_context():
            return self._scan_regexp()

        # Three-character operators
        if self.position + 2 < len(self.source):
            three_char = self.source[self.position : self.position + 3]
            if three_char == "...":
                self.position += 3
                self.column += 3
                return Token(
                    type=TokenType.SPREAD,
                    value=None,
                    location=SourceLocation(
                        filename=self.filename,
                        line=start_line,
                        column=start_column,
                        offset=start_offset,
                    ),
                )

        # Two-character operators
        if self.position + 1 < len(self.source):
            two_char = self.source[self.position : self.position + 2]
            if two_char == "==":
                self.position += 2
                self.column += 2
                return Token(
                    type=TokenType.EQUAL,
                    value=None,
                    location=SourceLocation(
                        filename=self.filename,
                        line=start_line,
                        column=start_column,
                        offset=start_offset,
                    ),
                )
            if two_char == "!=":
                self.position += 2
                self.column += 2
                return Token(
                    type=TokenType.NOT_EQUAL,
                    value=None,
                    location=SourceLocation(
                        filename=self.filename,
                        line=start_line,
                        column=start_column,
                        offset=start_offset,
                    ),
                )
            if two_char == "=>":
                self.position += 2
                self.column += 2
                return Token(
                    type=TokenType.ARROW,
                    value=None,
                    location=SourceLocation(
                        filename=self.filename,
                        line=start_line,
                        column=start_column,
                        offset=start_offset,
                    ),
                )

        # Single-character tokens
        single_char_tokens = {
            "+": TokenType.PLUS,
            "-": TokenType.MINUS,
            "*": TokenType.MULTIPLY,
            "/": TokenType.DIVIDE,
            "=": TokenType.ASSIGN,
            "<": TokenType.LESS_THAN,
            ">": TokenType.GREATER_THAN,
            "(": TokenType.LPAREN,
            ")": TokenType.RPAREN,
            "{": TokenType.LBRACE,
            "}": TokenType.RBRACE,
            "[": TokenType.LBRACKET,
            "]": TokenType.RBRACKET,
            ";": TokenType.SEMICOLON,
            ",": TokenType.COMMA,
            ".": TokenType.DOT,
            ":": TokenType.COLON,
        }

        if char in single_char_tokens:
            self.position += 1
            self.column += 1
            return Token(
                type=single_char_tokens[char],
                value=None,
                location=SourceLocation(
                    filename=self.filename,
                    line=start_line,
                    column=start_column,
                    offset=start_offset,
                ),
            )

        # Unknown character - skip it for now
        self.position += 1
        self.column += 1
        return self._scan_token()

    def _scan_identifier(self) -> Token:
        """
        Scan an identifier or keyword.

        Returns:
            Token: Identifier or keyword token
        """
        start_line = self.line
        start_column = self.column
        start_offset = self.position

        start = self.position
        while self.position < len(self.source) and (
            self.source[self.position].isalnum() or self.source[self.position] in "_$"
        ):
            self.position += 1
            self.column += 1

        text = self.source[start : self.position]

        # Check if it's a keyword
        if text in self.KEYWORDS:
            return Token(
                type=self.KEYWORDS[text],
                value=None,
                location=SourceLocation(
                    filename=self.filename,
                    line=start_line,
                    column=start_column,
                    offset=start_offset,
                ),
            )

        # It's an identifier
        return Token(
            type=TokenType.IDENTIFIER,
            value=text,
            location=SourceLocation(
                filename=self.filename,
                line=start_line,
                column=start_column,
                offset=start_offset,
            ),
        )

    def _scan_number(self) -> Token:
        """
        Scan a numeric literal.

        Returns:
            Token: Number token with numeric value
        """
        start_line = self.line
        start_column = self.column
        start_offset = self.position

        start = self.position
        while self.position < len(self.source) and (
            self.source[self.position].isdigit() or self.source[self.position] == "."
        ):
            self.position += 1
            self.column += 1

        text = self.source[start : self.position]

        # Convert to appropriate numeric type
        if "." in text:
            value = float(text)
        else:
            value = int(text)

        return Token(
            type=TokenType.NUMBER,
            value=value,
            location=SourceLocation(
                filename=self.filename,
                line=start_line,
                column=start_column,
                offset=start_offset,
            ),
        )

    def _scan_string(self) -> Token:
        """
        Scan a string literal.

        Returns:
            Token: String token with string value
        """
        start_line = self.line
        start_column = self.column
        start_offset = self.position

        quote = self.source[self.position]
        self.position += 1
        self.column += 1

        start = self.position
        while self.position < len(self.source) and self.source[self.position] != quote:
            if self.source[self.position] == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

        text = self.source[start : self.position]

        # Skip closing quote
        if self.position < len(self.source):
            self.position += 1
            self.column += 1

        return Token(
            type=TokenType.STRING,
            value=text,
            location=SourceLocation(
                filename=self.filename,
                line=start_line,
                column=start_column,
                offset=start_offset,
            ),
        )

    def _scan_template_literal(self) -> Token:
        """
        Scan a template literal.

        Template literals are enclosed in backticks and can contain newlines
        and ${} expressions. This method scans the entire template as a single
        token, preserving the ${} syntax for the parser to handle.

        Returns:
            Token: Template literal token with full template content
        """
        start_line = self.line
        start_column = self.column
        start_offset = self.position

        # Skip opening backtick
        self.position += 1
        self.column += 1

        start = self.position
        while self.position < len(self.source) and self.source[self.position] != "`":
            if self.source[self.position] == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

        text = self.source[start : self.position]

        # Skip closing backtick
        if self.position < len(self.source):
            self.position += 1
            self.column += 1

        return Token(
            type=TokenType.TEMPLATE_LITERAL,
            value=text,
            location=SourceLocation(
                filename=self.filename,
                line=start_line,
                column=start_column,
                offset=start_offset,
            ),
        )

    def _skip_whitespace_and_comments(self):
        """Skip whitespace and comments in source."""
        while self.position < len(self.source):
            char = self.source[self.position]

            # Skip whitespace
            if char in " \t\r\n":
                if char == "\n":
                    self.line += 1
                    self.column = 1
                else:
                    self.column += 1
                self.position += 1
                continue

            # Skip single-line comments
            if (
                char == "/"
                and self.position + 1 < len(self.source)
                and self.source[self.position + 1] == "/"
            ):
                # Skip until end of line
                while (
                    self.position < len(self.source)
                    and self.source[self.position] != "\n"
                ):
                    self.position += 1
                    self.column += 1
                # Skip the newline
                if self.position < len(self.source):
                    self.position += 1
                    self.line += 1
                    self.column = 1
                continue

            # Not whitespace or comment
            break

    def _scan_regexp(self) -> Token:
        """
        Scan a regular expression literal.

        Regular expressions are delimited by forward slashes and can have flags
        after the closing slash. Supports the /v flag for set operations.

        Returns:
            Token: RegExp token with pattern and flags

        Example:
            >>> lexer = Lexer("/[a-z]/giv", "test.js")
            >>> token = lexer.next_token()
            >>> token.value["pattern"]
            '[a-z]'
            >>> token.value["flags"]
            'giv'
        """
        start_line = self.line
        start_column = self.column
        start_offset = self.position

        # Skip opening /
        self.position += 1
        self.column += 1

        # Scan pattern until closing /
        pattern_start = self.position
        escaped = False

        while self.position < len(self.source):
            char = self.source[self.position]

            # Handle escape sequences
            if escaped:
                escaped = False
                self.position += 1
                self.column += 1
                continue

            if char == "\\":
                escaped = True
                self.position += 1
                self.column += 1
                continue

            # Check for closing /
            if char == "/":
                break

            # Handle character classes [...]
            if char == "[":
                # Scan until closing ]
                self.position += 1
                self.column += 1
                char_class_escaped = False

                while self.position < len(self.source):
                    char = self.source[self.position]

                    if char_class_escaped:
                        char_class_escaped = False
                        self.position += 1
                        self.column += 1
                        continue

                    if char == "\\":
                        char_class_escaped = True
                        self.position += 1
                        self.column += 1
                        continue

                    if char == "]":
                        self.position += 1
                        self.column += 1
                        break

                    self.position += 1
                    self.column += 1
                continue

            # Regular character
            if char == "\n":
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.position += 1

        pattern = self.source[pattern_start : self.position]

        # Skip closing /
        if self.position < len(self.source) and self.source[self.position] == "/":
            self.position += 1
            self.column += 1

        # Scan flags
        flags_start = self.position
        while self.position < len(self.source) and self.source[self.position].isalpha():
            self.position += 1
            self.column += 1

        flags = self.source[flags_start : self.position]

        return Token(
            type=TokenType.REGEXP,
            value={"pattern": pattern, "flags": flags},
            location=SourceLocation(
                filename=self.filename,
                line=start_line,
                column=start_column,
                offset=start_offset,
            ),
        )

    def _is_regexp_context(self) -> bool:
        """
        Check if current position is in a context where regexp is expected.

        Uses the previous token to determine if / starts a regexp or is division.
        After operators, keywords, and punctuation that can't be followed by
        division, / starts a regexp.

        Returns:
            bool: True if regexp is expected
        """
        # Look ahead to see if this looks like a comment or division assignment
        if self.position + 1 < len(self.source):
            next_char = self.source[self.position + 1]
            # Definitely a comment
            if next_char == "/" or next_char == "*":
                return False
            # Division assignment
            if next_char == "=":
                return False

        # If we have no previous token, assume regexp (e.g., at start of file)
        if self._last_token is None:
            return True

        # Regexp is expected after these tokens:
        # - Operators: =, (, [, {, ,, ;, :, !, &, |, ^, ~, ?, +, -, *, /, %
        # - Keywords: return, new, throw, typeof, void, delete, await
        # - Arrow: =>
        regexp_contexts = {
            TokenType.ASSIGN,
            TokenType.LPAREN,
            TokenType.LBRACKET,
            TokenType.LBRACE,
            TokenType.COMMA,
            TokenType.SEMICOLON,
            TokenType.COLON,
            TokenType.ARROW,
            TokenType.RETURN,
            TokenType.NEW,
            TokenType.EQUAL,
            TokenType.NOT_EQUAL,
            TokenType.LESS_THAN,
            TokenType.GREATER_THAN,
        }

        # Division is expected after these tokens:
        # - Identifiers, numbers, strings, ), ], }
        # - true, false, null, undefined, this
        division_contexts = {
            TokenType.IDENTIFIER,
            TokenType.NUMBER,
            TokenType.STRING,
            TokenType.RPAREN,
            TokenType.RBRACKET,
            TokenType.RBRACE,
            TokenType.TRUE,
            TokenType.FALSE,
            TokenType.NULL,
            TokenType.UNDEFINED,
        }

        if self._last_token.type in regexp_contexts:
            return True
        if self._last_token.type in division_contexts:
            return False

        # Default to division for safety
        return False

    def _make_token(self, token_type: TokenType, value) -> Token:
        """
        Create a token with current location.

        Args:
            token_type: Type of token
            value: Value of token

        Returns:
            Token: Created token
        """
        return Token(
            type=token_type,
            value=value,
            location=SourceLocation(
                filename=self.filename,
                line=self.line,
                column=self.column,
                offset=self.position,
            ),
        )
