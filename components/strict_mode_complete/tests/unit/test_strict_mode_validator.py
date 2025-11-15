"""
Unit tests for StrictModeValidator

Tests FR-ES24-B-048 to FR-ES24-B-058:
- Assignment errors
- Deletion errors
- Parameter validation
- Octal literals
- eval/arguments restrictions
- with statement
- Reserved words
- Readonly property assignment
- Function declarations
"""

import pytest
from components.strict_mode_complete.src.strict_mode_validator import StrictModeValidator
from components.strict_mode_complete.src.errors import (
    StrictModeReferenceError,
    StrictModeSyntaxError,
    StrictModeTypeError,
    StrictModeErrorType,
)


# Mock classes for testing
class MockExpression:
    def __init__(self, type, name=None):
        self.type = type
        self.name = name


class MockScope:
    def __init__(self, bindings=None):
        self.bindings = bindings or {}

    def has_binding(self, name):
        return name in self.bindings


class MockJSObject:
    def __init__(self, properties=None):
        self.properties = properties or {}

    def get_property_descriptor(self, name):
        return self.properties.get(name)


class TestStrictModeValidatorAssignment:
    """Tests for FR-ES24-B-048: Assignment to undeclared variables"""

    def test_assignment_to_undeclared_strict_mode_throws(self):
        """Should throw ReferenceError for assignment to undeclared in strict mode"""
        validator = StrictModeValidator(is_strict=True)
        target = MockExpression("Identifier", name="x")
        scope = MockScope()  # Empty scope - no bindings

        with pytest.raises(StrictModeReferenceError) as exc_info:
            validator.validate_assignment(target, scope)

        assert "x" in str(exc_info.value)
        assert "undeclared" in str(exc_info.value).lower()

    def test_assignment_to_declared_allowed(self):
        """Should allow assignment to declared variable"""
        validator = StrictModeValidator(is_strict=True)
        target = MockExpression("Identifier", name="x")
        scope = MockScope(bindings={"x": True})

        # Should not throw
        validator.validate_assignment(target, scope)

    def test_assignment_in_non_strict_allowed(self):
        """Should allow assignment to undeclared in non-strict mode"""
        validator = StrictModeValidator(is_strict=False)
        target = MockExpression("Identifier", name="x")
        scope = MockScope()

        # Should not throw
        validator.validate_assignment(target, scope)

    def test_assignment_to_non_identifier_allowed(self):
        """Should allow assignment to non-identifier (e.g., obj.prop)"""
        validator = StrictModeValidator(is_strict=True)
        target = MockExpression("MemberExpression")
        scope = MockScope()

        # Should not throw for member expressions
        validator.validate_assignment(target, scope)


class TestStrictModeValidatorDeletion:
    """Tests for FR-ES24-B-049: Delete of unqualified identifier"""

    def test_delete_unqualified_identifier_throws(self):
        """Should throw SyntaxError for delete of unqualified identifier"""
        validator = StrictModeValidator(is_strict=True)
        target = MockExpression("Identifier", name="x")

        with pytest.raises(StrictModeSyntaxError) as exc_info:
            validator.validate_deletion(target)

        assert exc_info.value.violation_type == StrictModeErrorType.UNQUALIFIED_DELETE

    def test_delete_member_expression_allowed(self):
        """Should allow delete of qualified identifier (obj.prop)"""
        validator = StrictModeValidator(is_strict=True)
        target = MockExpression("MemberExpression")

        # Should not throw
        validator.validate_deletion(target)

    def test_delete_in_non_strict_allowed(self):
        """Should allow delete of unqualified identifier in non-strict"""
        validator = StrictModeValidator(is_strict=False)
        target = MockExpression("Identifier", name="x")

        # Should not throw
        validator.validate_deletion(target)


class TestStrictModeValidatorParameters:
    """Tests for FR-ES24-B-050: Duplicate parameter names"""

    def test_duplicate_parameters_throws(self):
        """Should throw SyntaxError for duplicate parameter names"""
        validator = StrictModeValidator(is_strict=True)

        with pytest.raises(StrictModeSyntaxError) as exc_info:
            validator.validate_parameters(["a", "b", "a"])

        assert exc_info.value.violation_type == StrictModeErrorType.DUPLICATE_PARAMETER
        assert "a" in str(exc_info.value)

    def test_unique_parameters_allowed(self):
        """Should allow unique parameter names"""
        validator = StrictModeValidator(is_strict=True)

        # Should not throw
        validator.validate_parameters(["a", "b", "c"])

    def test_empty_parameters_allowed(self):
        """Should allow empty parameter list"""
        validator = StrictModeValidator(is_strict=True)

        # Should not throw
        validator.validate_parameters([])

    def test_case_sensitive_parameters(self):
        """Parameters should be case-sensitive"""
        validator = StrictModeValidator(is_strict=True)

        # 'a' and 'A' are different - should not throw
        validator.validate_parameters(["a", "A", "b"])

    def test_duplicate_in_non_strict_allowed(self):
        """Should allow duplicate parameters in non-strict mode"""
        validator = StrictModeValidator(is_strict=False)

        # Should not throw
        validator.validate_parameters(["a", "a"])


class TestStrictModeValidatorOctalLiterals:
    """Tests for FR-ES24-B-051: Octal literal restrictions"""

    def test_legacy_octal_throws(self):
        """Should throw SyntaxError for legacy octal literals"""
        validator = StrictModeValidator(is_strict=True)

        with pytest.raises(StrictModeSyntaxError) as exc_info:
            validator.validate_octal_literal("0777")

        assert exc_info.value.violation_type == StrictModeErrorType.OCTAL_LITERAL

    def test_octal_with_zero_prefix_throws(self):
        """Should throw for 0-prefixed numbers that look octal"""
        validator = StrictModeValidator(is_strict=True)

        with pytest.raises(StrictModeSyntaxError):
            validator.validate_octal_literal("0123")

    def test_decimal_allowed(self):
        """Should allow normal decimal literals"""
        validator = StrictModeValidator(is_strict=True)

        # Should not throw
        validator.validate_octal_literal("123")
        validator.validate_octal_literal("0")

    def test_hex_allowed(self):
        """Should allow hexadecimal literals"""
        validator = StrictModeValidator(is_strict=True)

        # Should not throw
        validator.validate_octal_literal("0xFF")
        validator.validate_octal_literal("0xABC")

    def test_es6_octal_allowed(self):
        """Should allow ES6 octal syntax (0o prefix)"""
        validator = StrictModeValidator(is_strict=True)

        # Should not throw - ES6 octal is allowed
        validator.validate_octal_literal("0o777")

    def test_binary_allowed(self):
        """Should allow binary literals"""
        validator = StrictModeValidator(is_strict=True)

        # Should not throw
        validator.validate_octal_literal("0b1010")


class TestStrictModeValidatorEvalArguments:
    """Tests for FR-ES24-B-052: eval/arguments restrictions"""

    def test_eval_as_variable_throws(self):
        """Should throw SyntaxError for eval as variable name"""
        validator = StrictModeValidator(is_strict=True)

        with pytest.raises(StrictModeSyntaxError) as exc_info:
            validator.validate_identifier_name("eval", "variable")

        assert exc_info.value.violation_type == StrictModeErrorType.EVAL_ARGUMENTS_USAGE

    def test_arguments_as_variable_throws(self):
        """Should throw SyntaxError for arguments as variable name"""
        validator = StrictModeValidator(is_strict=True)

        with pytest.raises(StrictModeSyntaxError) as exc_info:
            validator.validate_identifier_name("arguments", "variable")

        assert exc_info.value.violation_type == StrictModeErrorType.EVAL_ARGUMENTS_USAGE

    def test_eval_as_parameter_throws(self):
        """Should throw SyntaxError for eval as parameter name"""
        validator = StrictModeValidator(is_strict=True)

        with pytest.raises(StrictModeSyntaxError):
            validator.validate_identifier_name("eval", "parameter")

    def test_arguments_as_parameter_throws(self):
        """Should throw SyntaxError for arguments as parameter name"""
        validator = StrictModeValidator(is_strict=True)

        with pytest.raises(StrictModeSyntaxError):
            validator.validate_identifier_name("arguments", "parameter")

    def test_normal_identifiers_allowed(self):
        """Should allow normal identifier names"""
        validator = StrictModeValidator(is_strict=True)

        # Should not throw
        validator.validate_identifier_name("foo", "variable")
        validator.validate_identifier_name("bar", "parameter")


class TestStrictModeValidatorWithStatement:
    """Tests for FR-ES24-B-054: with statement restrictions"""

    def test_with_statement_throws(self):
        """Should throw SyntaxError for with statement in strict mode"""
        validator = StrictModeValidator(is_strict=True)

        # Mock with statement
        with_stmt = type('WithStatement', (), {})()

        with pytest.raises(StrictModeSyntaxError) as exc_info:
            validator.validate_with_statement(with_stmt)

        assert exc_info.value.violation_type == StrictModeErrorType.WITH_STATEMENT

    def test_with_in_non_strict_allowed(self):
        """Should allow with statement in non-strict mode"""
        validator = StrictModeValidator(is_strict=False)

        with_stmt = type('WithStatement', (), {})()

        # Should not throw
        validator.validate_with_statement(with_stmt)


class TestStrictModeValidatorReservedWords:
    """Tests for FR-ES24-B-055: Future reserved words"""

    RESERVED_WORDS = [
        "implements", "interface", "let", "package",
        "private", "protected", "public", "static", "yield"
    ]

    @pytest.mark.parametrize("word", RESERVED_WORDS)
    def test_reserved_word_throws(self, word):
        """Should throw SyntaxError for future reserved words"""
        validator = StrictModeValidator(is_strict=True)

        with pytest.raises(StrictModeSyntaxError) as exc_info:
            validator.validate_reserved_word(word, "variable")

        assert exc_info.value.violation_type == StrictModeErrorType.RESERVED_WORD

    def test_reserved_words_in_non_strict_allowed(self):
        """Should allow reserved words in non-strict mode"""
        validator = StrictModeValidator(is_strict=False)

        # Should not throw
        validator.validate_reserved_word("implements", "variable")


class TestStrictModeValidatorReadonlyProperties:
    """Tests for FR-ES24-B-057: Assignment to readonly properties"""

    def test_assignment_to_readonly_throws(self):
        """Should throw TypeError for assignment to readonly property"""
        validator = StrictModeValidator(is_strict=True)

        obj = MockJSObject(properties={
            "x": {"writable": False, "value": 1}
        })

        with pytest.raises(StrictModeTypeError) as exc_info:
            validator.validate_property_write(obj, "x", 2)

        assert "x" in str(exc_info.value)

    def test_assignment_to_writable_allowed(self):
        """Should allow assignment to writable property"""
        validator = StrictModeValidator(is_strict=True)

        obj = MockJSObject(properties={
            "x": {"writable": True, "value": 1}
        })

        # Should not throw
        validator.validate_property_write(obj, "x", 2)

    def test_assignment_to_new_property_allowed(self):
        """Should allow assignment to new property (if extensible)"""
        validator = StrictModeValidator(is_strict=True)

        obj = MockJSObject()

        # Should not throw for new property
        validator.validate_property_write(obj, "newProp", 1)


class TestStrictModeValidatorFunctionDeclarations:
    """Tests for FR-ES24-B-058: Function declarations in blocks"""

    def test_function_in_block_allowed(self):
        """Function declarations in blocks should have block scope"""
        validator = StrictModeValidator(is_strict=True)

        # Mock function declaration
        func_decl = type('FunctionDeclaration', (), {"name": "f"})()
        parent = type('IfStatement', (), {})()

        # Should not throw - just validates semantics
        validator.validate_function_declaration(func_decl, parent)


class TestStrictModeValidatorContext:
    """Tests for StrictModeContext data structure"""

    def test_context_creation(self):
        """Should create StrictModeContext with correct fields"""
        from components.strict_mode_complete.src.strict_mode_validator import (
            StrictModeContext,
            ScopeType,
        )

        context = StrictModeContext(
            is_strict=True,
            scope_type=ScopeType.FUNCTION,
            has_local_directive=True,
            inherited_strict=False
        )

        assert context.is_strict is True
        assert context.scope_type == ScopeType.FUNCTION
        assert context.has_local_directive is True
        assert context.inherited_strict is False
