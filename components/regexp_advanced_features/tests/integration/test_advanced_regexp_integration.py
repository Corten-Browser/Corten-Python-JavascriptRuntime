"""
Integration tests for advanced RegExp features

Tests the interaction of multiple advanced features together
"""

import pytest
from src.executor import RegExpExecutor
from src.parser import RegExpParser


class TestNamedGroupsWithFlags:
    """Test named groups with various flags"""

    def test_named_groups_with_ignore_case(self):
        """Named groups with case-insensitive matching"""
        executor = RegExpExecutor()
        pattern = r"(?<greeting>hello)"
        result = executor.execute(pattern, "HELLO", flags="i")
        assert result.matched
        assert result.groups["greeting"] == "HELLO"

    def test_named_groups_with_dotall(self):
        """Named groups with dotAll flag"""
        executor = RegExpExecutor()
        pattern = r"(?<content>start.+end)"
        result = executor.execute(pattern, "start\nmiddle\nend", flags="s")
        assert result.matched
        assert "middle" in result.groups["content"]

    def test_named_groups_with_indices(self):
        """Named groups with indices flag"""
        executor = RegExpExecutor()
        pattern = r"(?<year>\d{4})-(?<month>\d{2})"
        result = executor.execute_with_indices(pattern, "2024-11")
        assert result.matched
        assert "year" in result.groups
        assert "year" in result.indices.groups


class TestComplexPatterns:
    """Test complex patterns combining multiple features"""

    def test_date_validation_pattern(self):
        """Complex date validation with named groups"""
        executor = RegExpExecutor()
        pattern = r"(?<year>\d{4})-(?<month>0[1-9]|1[0-2])-(?<day>0[1-9]|[12]\d|3[01])"
        result = executor.execute(pattern, "2024-11-15")
        assert result.matched
        assert result.groups["year"] == "2024"
        assert result.groups["month"] == "11"
        assert result.groups["day"] == "15"

    def test_email_pattern_with_named_groups(self):
        """Email validation with named capture groups"""
        executor = RegExpExecutor()
        pattern = r"(?<user>[a-zA-Z0-9._%+-]+)@(?<domain>[a-zA-Z0-9.-]+)\.(?<tld>[a-zA-Z]{2,})"
        result = executor.execute(pattern, "user@example.com")
        assert result.matched
        assert result.groups["user"] == "user"
        assert result.groups["domain"] == "example"
        assert result.groups["tld"] == "com"

    def test_url_parsing_with_named_groups(self):
        """URL parsing with multiple named groups"""
        executor = RegExpExecutor()
        pattern = r"(?<protocol>https?):\/\/(?<host>[^\/]+)(?<path>\/.*)"
        result = executor.execute(pattern, "https://example.com/path/to/page")
        assert result.matched
        assert result.groups["protocol"] == "https"
        assert result.groups["host"] == "example.com"
        assert result.groups["path"] == "/path/to/page"


class TestFlagCombinations:
    """Test various flag combinations"""

    def test_global_multiline(self):
        """Global and multiline flags together"""
        parser = RegExpParser()
        flags = parser.parse_flags("gm")
        assert flags.global_flag is True
        assert flags.multiline is True

    def test_dotall_unicode(self):
        """dotAll and unicode flags together"""
        parser = RegExpParser()
        flags = parser.parse_flags("su")
        assert flags.dotall is True
        assert flags.unicode is True

    def test_indices_global(self):
        """Indices and global flags together"""
        parser = RegExpParser()
        flags = parser.parse_flags("dg")
        assert flags.indices is True
        assert flags.global_flag is True


class TestEdgeCases:
    """Test edge cases and error conditions"""

    def test_empty_pattern(self):
        """Empty pattern matches empty string"""
        executor = RegExpExecutor()
        result = executor.execute("", "test")
        # Empty pattern should match at start
        assert result.matched

    def test_pattern_with_all_flags(self):
        """Pattern with multiple compatible flags"""
        executor = RegExpExecutor()
        pattern = r"(?<word>\w+)"
        result = executor.execute(pattern, "Hello", flags="gimsdy")
        # Should work with all compatible flags
        assert result.matched

    def test_very_long_input(self):
        """Handle very long input strings"""
        executor = RegExpExecutor()
        pattern = r"(?<number>\d+)"
        long_str = "a" * 10000 + "12345" + "b" * 10000
        result = executor.execute(pattern, long_str)
        assert result.matched
        assert result.groups["number"] == "12345"


class TestRealWorldPatterns:
    """Test real-world use case patterns"""

    def test_phone_number_extraction(self):
        """Extract phone number components"""
        executor = RegExpExecutor()
        pattern = r"(?<area>\d{3})-(?<prefix>\d{3})-(?<line>\d{4})"
        result = executor.execute(pattern, "Call me at 555-123-4567")
        assert result.matched
        assert result.groups["area"] == "555"
        assert result.groups["prefix"] == "123"
        assert result.groups["line"] == "4567"

    def test_markdown_link_parsing(self):
        """Parse markdown links"""
        executor = RegExpExecutor()
        pattern = r"\[(?<text>[^\]]+)\]\((?<url>[^\)]+)\)"
        result = executor.execute(pattern, "Check [this link](https://example.com)")
        assert result.matched
        assert result.groups["text"] == "this link"
        assert result.groups["url"] == "https://example.com"

    def test_css_color_extraction(self):
        """Extract CSS color components"""
        executor = RegExpExecutor()
        pattern = r"#(?<red>[0-9A-Fa-f]{2})(?<green>[0-9A-Fa-f]{2})(?<blue>[0-9A-Fa-f]{2})"
        result = executor.execute(pattern, "color: #FF5733;", flags="i")
        assert result.matched
        assert result.groups["red"] == "FF"
        assert result.groups["green"] == "57"
        assert result.groups["blue"] == "33"


class TestBackreferences:
    """Test backreferences with named groups"""

    def test_simple_backreference(self):
        """Simple backreference to named group"""
        executor = RegExpExecutor()
        pattern = r"(?<word>\w+)\s+\k<word>"
        result = executor.execute(pattern, "hello hello")
        assert result.matched

    def test_backreference_no_match(self):
        """Backreference should not match different text"""
        executor = RegExpExecutor()
        pattern = r"(?<word>\w+)\s+\k<word>"
        result = executor.execute(pattern, "hello world")
        assert not result.matched

    def test_multiple_backreferences(self):
        """Multiple backreferences in pattern"""
        executor = RegExpExecutor()
        pattern = r"(?<a>\w+)\s+(?<b>\w+)\s+\k<a>\s+\k<b>"
        result = executor.execute(pattern, "foo bar foo bar")
        assert result.matched
