"""
FR-ES24-B-001: Named capture groups (?<name>...) syntax

Test suite for named capture group functionality including:
- Parsing named capture group syntax
- Extracting named groups from matches
- Accessing groups by name
- Handling duplicate group names
- Edge cases and error conditions
"""

import pytest
import re
from src.parser import RegExpParser
from src.executor import RegExpExecutor
from src.types import CaptureGroup, MatchResult


class TestNamedCaptureGroupParsing:
    """Test parsing of named capture group syntax"""

    def test_parse_simple_named_group(self):
        """Parse simple named capture group"""
        parser = RegExpParser()
        group = parser.parse_named_capture_group("(?<year>\\d{4})")

        assert group is not None
        assert group.name == "year"
        assert group.pattern == "\\d{4}"
        assert group.index >= 0

    def test_parse_multiple_named_groups(self):
        """Parse pattern with multiple named groups"""
        parser = RegExpParser()
        pattern = "(?<year>\\d{4})-(?<month>\\d{2})-(?<day>\\d{2})"
        groups = parser.parse_pattern_for_named_groups(pattern)

        assert len(groups) == 3
        assert groups[0].name == "year"
        assert groups[1].name == "month"
        assert groups[2].name == "day"

    def test_parse_nested_named_groups(self):
        """Parse nested named capture groups"""
        parser = RegExpParser()
        pattern = "(?<outer>a(?<inner>b)c)"
        groups = parser.parse_pattern_for_named_groups(pattern)

        assert len(groups) == 2
        assert any(g.name == "outer" for g in groups)
        assert any(g.name == "inner" for g in groups)

    def test_parse_named_group_with_special_chars(self):
        """Parse named group with valid identifier characters"""
        parser = RegExpParser()
        group = parser.parse_named_capture_group("(?<_name123>test)")

        assert group.name == "_name123"

    def test_invalid_group_name_syntax_error(self):
        """Invalid group name should raise SyntaxError"""
        parser = RegExpParser()

        with pytest.raises(SyntaxError):
            parser.parse_named_capture_group("(?<123invalid>test)")

        with pytest.raises(SyntaxError):
            parser.parse_named_capture_group("(?<name-with-dash>test)")

    def test_empty_group_name_error(self):
        """Empty group name should raise SyntaxError"""
        parser = RegExpParser()

        with pytest.raises(SyntaxError):
            parser.parse_named_capture_group("(?<>test)")

    def test_duplicate_group_names_error(self):
        """Duplicate group names should raise SyntaxError"""
        parser = RegExpParser()
        pattern = "(?<name>a)|(?<name>b)"

        with pytest.raises(SyntaxError):
            parser.parse_pattern_for_named_groups(pattern)


class TestNamedCaptureGroupExecution:
    """Test execution and matching with named groups"""

    def test_match_simple_named_group(self):
        """Match with simple named group"""
        executor = RegExpExecutor()
        pattern = "(?<year>\\d{4})"
        result = executor.execute(pattern, "Year: 2024")

        assert result.matched
        assert "year" in result.groups
        assert result.groups["year"] == "2024"

    def test_match_date_pattern(self):
        """Match date pattern with named groups"""
        executor = RegExpExecutor()
        pattern = "(?<year>\\d{4})-(?<month>\\d{2})-(?<day>\\d{2})"
        result = executor.execute(pattern, "2024-11-15")

        assert result.matched
        assert result.groups["year"] == "2024"
        assert result.groups["month"] == "11"
        assert result.groups["day"] == "15"

    def test_named_groups_in_captures_list(self):
        """Named groups should also appear in indexed captures"""
        executor = RegExpExecutor()
        pattern = "(?<year>\\d{4})-(?<month>\\d{2})"
        result = executor.execute(pattern, "2024-11")

        assert result.matched
        assert len(result.captures) >= 2
        assert result.captures[0] == "2024"
        assert result.captures[1] == "11"

    def test_mixed_named_and_unnamed_groups(self):
        """Mix of named and unnamed capture groups"""
        executor = RegExpExecutor()
        pattern = "(?<name>\\w+)-(\\d+)"
        result = executor.execute(pattern, "test-123")

        assert result.matched
        assert result.groups["name"] == "test"
        assert result.captures[1] == "123"

    def test_non_participating_named_group(self):
        """Non-participating named group should be undefined"""
        executor = RegExpExecutor()
        pattern = "(?<a>a)?b"
        result = executor.execute(pattern, "b")

        assert result.matched
        assert "a" not in result.groups or result.groups["a"] is None

    def test_backreference_to_named_group(self):
        """Backreference using \\k<name> syntax"""
        executor = RegExpExecutor()
        pattern = "(?<word>\\w+)\\s+\\k<word>"
        result = executor.execute(pattern, "hello hello")

        assert result.matched
        assert result.groups["word"] == "hello"

    def test_backreference_to_nonexistent_group_error(self):
        """Backreference to non-existent group should error"""
        executor = RegExpExecutor()
        pattern = "\\k<nonexistent>"

        with pytest.raises(SyntaxError):
            executor.execute(pattern, "test")


class TestNamedGroupEdgeCases:
    """Test edge cases for named capture groups"""

    @pytest.mark.skip(reason="Unicode property escapes not yet implemented")
    def test_unicode_in_named_group_content(self):
        """Named group matching Unicode content"""
        executor = RegExpExecutor()
        pattern = "(?<greeting>\\p{L}+)"
        result = executor.execute(pattern, "Hello", flags="u")

        assert result.matched
        assert result.groups["greeting"] == "Hello"

    def test_quantified_named_group(self):
        """Named group with quantifier captures last match"""
        executor = RegExpExecutor()
        pattern = "(?<digit>\\d)+"
        result = executor.execute(pattern, "123")

        assert result.matched
        assert result.groups["digit"] == "3"  # Last captured digit

    def test_optional_named_group(self):
        """Optional named group"""
        executor = RegExpExecutor()
        pattern = "a(?<opt>b)?c"

        result1 = executor.execute(pattern, "abc")
        assert result1.groups["opt"] == "b"

        result2 = executor.execute(pattern, "ac")
        assert "opt" not in result2.groups or result2.groups["opt"] is None

    def test_alternation_with_named_groups(self):
        """Alternation with different named groups"""
        executor = RegExpExecutor()
        pattern = "(?<letters>[a-z]+)|(?<digits>\\d+)"

        result1 = executor.execute(pattern, "abc")
        assert result1.groups["letters"] == "abc"
        assert "digits" not in result1.groups or result1.groups["digits"] is None

        result2 = executor.execute(pattern, "123")
        assert result2.groups["digits"] == "123"
        assert "letters" not in result2.groups or result2.groups["letters"] is None

    def test_very_long_group_name(self):
        """Very long but valid group name"""
        executor = RegExpExecutor()
        long_name = "a" * 100
        pattern = f"(?<{long_name}>test)"
        result = executor.execute(pattern, "test")

        assert result.matched
        assert long_name in result.groups
        assert result.groups[long_name] == "test"
