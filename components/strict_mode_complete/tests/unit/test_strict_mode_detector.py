"""
Unit tests for StrictModeDetector

Tests FR-ES24-B-047: "use strict" directive detection and propagation
"""

import pytest
from components.strict_mode_complete.src.strict_mode_detector import (
    StrictModeDetector,
    DirectivePrologueInfo,
)


# Mock Statement class for testing
class MockStatement:
    def __init__(self, type, value=None, expression=None):
        self.type = type
        self.value = value
        self.expression = expression


class MockExpression:
    def __init__(self, type, value=None):
        self.type = type
        self.value = value


class TestStrictModeDetector:
    """Tests for StrictModeDetector class"""

    def setup_method(self):
        """Set up test fixtures"""
        self.detector = StrictModeDetector()

    # Test basic "use strict" detection
    def test_detect_use_strict_directive(self):
        """Should detect 'use strict' as a directive"""
        stmt = MockStatement(
            "ExpressionStatement",
            expression=MockExpression("Literal", value="use strict")
        )
        assert self.detector.detect_directive(stmt) is True

    def test_detect_use_strict_double_quotes(self):
        """Should detect "use strict" with double quotes"""
        stmt = MockStatement(
            "ExpressionStatement",
            expression=MockExpression("Literal", value="use strict")
        )
        assert self.detector.detect_directive(stmt) is True

    def test_reject_non_strict_string(self):
        """Should not detect other string literals as directives"""
        stmt = MockStatement(
            "ExpressionStatement",
            expression=MockExpression("Literal", value="not strict")
        )
        assert self.detector.detect_directive(stmt) is False

    def test_reject_non_expression_statement(self):
        """Should not detect directives in non-expression statements"""
        stmt = MockStatement("VariableDeclaration")
        assert self.detector.detect_directive(stmt) is False

    def test_reject_use_strict_with_escapes(self):
        """Should not detect 'use strict' with character escapes as directive"""
        # "use\x20strict" is not a valid directive
        # Note: In real parsing, escapes would be preserved, but for testing
        # we use a different string value to simulate escape presence
        stmt = MockStatement(
            "ExpressionStatement",
            expression=MockExpression("Literal", value="use\\x20strict")  # Raw escape
        )
        assert self.detector.detect_directive(stmt) is False

    def test_reject_case_sensitive(self):
        """Should be case-sensitive - 'USE STRICT' is not a directive"""
        stmt = MockStatement(
            "ExpressionStatement",
            expression=MockExpression("Literal", value="USE STRICT")
        )
        assert self.detector.detect_directive(stmt) is False

    # Test directive prologue position
    def test_is_directive_prologue_first_statement(self):
        """First statement can be a directive"""
        statements = [
            MockStatement("ExpressionStatement", expression=MockExpression("Literal", value="use strict")),
            MockStatement("VariableDeclaration"),
        ]
        assert self.detector.is_directive_prologue(statements, 0) is True

    def test_is_directive_prologue_after_directive(self):
        """Directive can follow another directive"""
        statements = [
            MockStatement("ExpressionStatement", expression=MockExpression("Literal", value="use strict")),
            MockStatement("ExpressionStatement", expression=MockExpression("Literal", value="another directive")),
        ]
        assert self.detector.is_directive_prologue(statements, 1) is True

    def test_is_not_directive_prologue_after_non_directive(self):
        """Statement after non-directive is not in prologue"""
        statements = [
            MockStatement("VariableDeclaration"),
            MockStatement("ExpressionStatement", expression=MockExpression("Literal", value="use strict")),
        ]
        assert self.detector.is_directive_prologue(statements, 1) is False

    def test_is_not_directive_prologue_after_statement(self):
        """'use strict' after real statement is not a directive"""
        statements = [
            MockStatement("ExpressionStatement", expression=MockExpression("Literal", value="directive")),
            MockStatement("VariableDeclaration"),
            MockStatement("ExpressionStatement", expression=MockExpression("Literal", value="use strict")),
        ]
        assert self.detector.is_directive_prologue(statements, 2) is False

    # Test scan_for_directives
    def test_scan_for_directives_with_use_strict(self):
        """Should find 'use strict' in directive prologue"""
        statements = [
            MockStatement("ExpressionStatement", expression=MockExpression("Literal", value="use strict")),
            MockStatement("VariableDeclaration"),
        ]
        result = self.detector.scan_for_directives(statements)
        assert isinstance(result, DirectivePrologueInfo)
        assert result.has_use_strict is True
        assert result.directive_count == 1
        assert result.first_non_directive_index == 1

    def test_scan_for_directives_without_use_strict(self):
        """Should not find 'use strict' if not present"""
        statements = [
            MockStatement("ExpressionStatement", expression=MockExpression("Literal", value="other")),
            MockStatement("VariableDeclaration"),
        ]
        result = self.detector.scan_for_directives(statements)
        assert result.has_use_strict is False
        assert result.directive_count == 1
        assert result.first_non_directive_index == 1

    def test_scan_for_directives_multiple_directives(self):
        """Should count multiple directives"""
        statements = [
            MockStatement("ExpressionStatement", expression=MockExpression("Literal", value="directive1")),
            MockStatement("ExpressionStatement", expression=MockExpression("Literal", value="use strict")),
            MockStatement("ExpressionStatement", expression=MockExpression("Literal", value="directive3")),
            MockStatement("VariableDeclaration"),
        ]
        result = self.detector.scan_for_directives(statements)
        assert result.has_use_strict is True
        assert result.directive_count == 3
        assert result.first_non_directive_index == 3

    def test_scan_for_directives_empty_body(self):
        """Should handle empty function body"""
        statements = []
        result = self.detector.scan_for_directives(statements)
        assert result.has_use_strict is False
        assert result.directive_count == 0
        assert result.first_non_directive_index == 0

    def test_scan_for_directives_no_directives(self):
        """Should handle body with no directives"""
        statements = [
            MockStatement("VariableDeclaration"),
            MockStatement("ExpressionStatement", expression=MockExpression("Literal", value="use strict")),
        ]
        result = self.detector.scan_for_directives(statements)
        assert result.has_use_strict is False
        assert result.directive_count == 0
        assert result.first_non_directive_index == 0


class TestDirectivePrologueInfo:
    """Tests for DirectivePrologueInfo data structure"""

    def test_directive_prologue_info_creation(self):
        """Should create DirectivePrologueInfo with correct fields"""
        info = DirectivePrologueInfo(
            has_use_strict=True,
            directive_count=2,
            first_non_directive_index=2
        )
        assert info.has_use_strict is True
        assert info.directive_count == 2
        assert info.first_non_directive_index == 2

    def test_directive_prologue_info_no_strict(self):
        """Should create DirectivePrologueInfo without strict mode"""
        info = DirectivePrologueInfo(
            has_use_strict=False,
            directive_count=1,
            first_non_directive_index=1
        )
        assert info.has_use_strict is False
        assert info.directive_count == 1
        assert info.first_non_directive_index == 1
