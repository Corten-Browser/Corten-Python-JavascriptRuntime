"""
Unit tests for StringMethods class - ES2024 String.prototype methods

TDD Phase: RED - Write failing tests first
Requirements tested:
- FR-ES24-011: String.prototype.at()
- FR-ES24-012: String.prototype.replaceAll()
- FR-ES24-013: String.prototype.matchAll()
- FR-ES24-014: String.prototype.trimStart()
- FR-ES24-015: String.prototype.trimEnd()
- FR-ES24-016: String.prototype.padStart()
- FR-ES24-017: String.prototype.padEnd()
- FR-ES24-018: String.prototype.codePointAt()
- FR-ES24-019: String.fromCodePoint()
- FR-ES24-020: String.raw()
"""

import pytest
from components.string_methods.src.string_methods import StringMethods


class TestAt:
    """Tests for String.prototype.at() - FR-ES24-011"""

    def test_at_positive_index(self):
        """Test at() with positive index"""
        result = StringMethods.at("hello", 1)
        assert result == "e"

    def test_at_negative_index(self):
        """Test at() with negative index (from end)"""
        result = StringMethods.at("hello", -1)
        assert result == "o"

    def test_at_negative_index_middle(self):
        """Test at() with negative index in middle"""
        result = StringMethods.at("hello", -2)
        assert result == "l"

    def test_at_index_zero(self):
        """Test at() with index 0"""
        result = StringMethods.at("hello", 0)
        assert result == "h"

    def test_at_index_out_of_bounds(self):
        """Test at() with out of bounds index"""
        result = StringMethods.at("hello", 10)
        assert result is None  # JavaScript returns undefined

    def test_at_negative_index_out_of_bounds(self):
        """Test at() with out of bounds negative index"""
        result = StringMethods.at("hello", -10)
        assert result is None

    def test_at_empty_string(self):
        """Test at() with empty string"""
        result = StringMethods.at("", 0)
        assert result is None

    def test_at_unicode_characters(self):
        """Test at() with Unicode characters"""
        result = StringMethods.at("😀🎉", 1)
        assert result == "🎉"


class TestTrimMethods:
    """Tests for trim methods - FR-ES24-014, FR-ES24-015"""

    def test_trim_start_spaces(self):
        """Test trimStart() with leading spaces"""
        result = StringMethods.trim_start("  hello")
        assert result == "hello"

    def test_trim_start_tabs(self):
        """Test trimStart() with leading tabs"""
        result = StringMethods.trim_start("\t\thello")
        assert result == "hello"

    def test_trim_start_mixed_whitespace(self):
        """Test trimStart() with mixed whitespace"""
        result = StringMethods.trim_start("  \t\n hello")
        assert result == "hello"

    def test_trim_start_preserves_trailing(self):
        """Test trimStart() preserves trailing whitespace"""
        result = StringMethods.trim_start("  hello  ")
        assert result == "hello  "

    def test_trim_start_no_leading_whitespace(self):
        """Test trimStart() with no leading whitespace"""
        result = StringMethods.trim_start("hello")
        assert result == "hello"

    def test_trim_end_spaces(self):
        """Test trimEnd() with trailing spaces"""
        result = StringMethods.trim_end("hello  ")
        assert result == "hello"

    def test_trim_end_tabs(self):
        """Test trimEnd() with trailing tabs"""
        result = StringMethods.trim_end("hello\t\t")
        assert result == "hello"

    def test_trim_end_mixed_whitespace(self):
        """Test trimEnd() with mixed whitespace"""
        result = StringMethods.trim_end("hello  \t\n ")
        assert result == "hello"

    def test_trim_end_preserves_leading(self):
        """Test trimEnd() preserves leading whitespace"""
        result = StringMethods.trim_end("  hello  ")
        assert result == "  hello"

    def test_trim_end_no_trailing_whitespace(self):
        """Test trimEnd() with no trailing whitespace"""
        result = StringMethods.trim_end("hello")
        assert result == "hello"


class TestPadMethods:
    """Tests for pad methods - FR-ES24-016, FR-ES24-017"""

    def test_pad_start_default_space(self):
        """Test padStart() with default space padding"""
        result = StringMethods.pad_start("5", 3)
        assert result == "  5"

    def test_pad_start_custom_string(self):
        """Test padStart() with custom padding string"""
        result = StringMethods.pad_start("5", 3, "0")
        assert result == "005"

    def test_pad_start_longer_pad_string(self):
        """Test padStart() with longer padding string"""
        result = StringMethods.pad_start("abc", 10, "foo")
        assert result == "foofoofabc"

    def test_pad_start_no_padding_needed(self):
        """Test padStart() when string is already long enough"""
        result = StringMethods.pad_start("hello", 3)
        assert result == "hello"

    def test_pad_start_exact_length(self):
        """Test padStart() when string is exact target length"""
        result = StringMethods.pad_start("hello", 5)
        assert result == "hello"

    def test_pad_end_default_space(self):
        """Test padEnd() with default space padding"""
        result = StringMethods.pad_end("5", 3)
        assert result == "5  "

    def test_pad_end_custom_string(self):
        """Test padEnd() with custom padding string"""
        result = StringMethods.pad_end("5", 3, "0")
        assert result == "500"

    def test_pad_end_longer_pad_string(self):
        """Test padEnd() with longer padding string"""
        result = StringMethods.pad_end("abc", 10, "foo")
        assert result == "abcfoofoof"

    def test_pad_end_no_padding_needed(self):
        """Test padEnd() when string is already long enough"""
        result = StringMethods.pad_end("hello", 3)
        assert result == "hello"

    def test_pad_end_exact_length(self):
        """Test padEnd() when string is exact target length"""
        result = StringMethods.pad_end("hello", 5)
        assert result == "hello"


class TestReplaceAll:
    """Tests for replaceAll() - FR-ES24-012"""

    def test_replace_all_simple_string(self):
        """Test replaceAll() with simple string"""
        result = StringMethods.replace_all("aabbcc", "a", "x")
        assert result == "xxbbcc"

    def test_replace_all_multiple_occurrences(self):
        """Test replaceAll() replaces all occurrences"""
        result = StringMethods.replace_all("test test test", "test", "pass")
        assert result == "pass pass pass"

    def test_replace_all_no_match(self):
        """Test replaceAll() when no match found"""
        result = StringMethods.replace_all("hello", "x", "y")
        assert result == "hello"

    def test_replace_all_empty_replacement(self):
        """Test replaceAll() with empty replacement (removal)"""
        result = StringMethods.replace_all("hello", "l", "")
        assert result == "heo"

    def test_replace_all_overlapping_pattern(self):
        """Test replaceAll() doesn't match overlapping patterns"""
        result = StringMethods.replace_all("aaaa", "aa", "b")
        assert result == "bb"


class TestMatchAll:
    """Tests for matchAll() - FR-ES24-013"""

    def test_match_all_simple_pattern(self):
        """Test matchAll() with simple pattern"""
        result = list(StringMethods.match_all("test test", r"test"))
        assert len(result) == 2
        assert result[0][0] == "test"
        assert result[1][0] == "test"

    def test_match_all_capture_groups(self):
        """Test matchAll() with capture groups"""
        result = list(StringMethods.match_all("test1 test2", r"test(\d)"))
        assert len(result) == 2
        assert result[0][1] == "1"
        assert result[1][1] == "2"

    def test_match_all_no_matches(self):
        """Test matchAll() when no matches found"""
        result = list(StringMethods.match_all("hello", r"x"))
        assert len(result) == 0

    def test_match_all_with_indices(self):
        """Test matchAll() returns match indices"""
        result = list(StringMethods.match_all("ab ab", r"ab"))
        # Each match should have index information
        assert len(result) == 2


class TestCodePoint:
    """Tests for code point methods - FR-ES24-018, FR-ES24-019"""

    def test_code_point_at_ascii(self):
        """Test codePointAt() with ASCII character"""
        result = StringMethods.code_point_at("A", 0)
        assert result == 65

    def test_code_point_at_unicode(self):
        """Test codePointAt() with Unicode character"""
        result = StringMethods.code_point_at("😀", 0)
        assert result == 0x1F600

    def test_code_point_at_out_of_bounds(self):
        """Test codePointAt() with out of bounds index"""
        result = StringMethods.code_point_at("A", 5)
        assert result is None

    def test_from_code_point_ascii(self):
        """Test fromCodePoint() with ASCII code point"""
        result = StringMethods.from_code_point([65])
        assert result == "A"

    def test_from_code_point_unicode(self):
        """Test fromCodePoint() with Unicode code point"""
        result = StringMethods.from_code_point([0x1F600])
        assert result == "😀"

    def test_from_code_point_multiple(self):
        """Test fromCodePoint() with multiple code points"""
        result = StringMethods.from_code_point([72, 101, 108, 108, 111])
        assert result == "Hello"

    def test_from_code_point_mixed(self):
        """Test fromCodePoint() with mixed ASCII and Unicode"""
        result = StringMethods.from_code_point([72, 0x1F600, 73])
        assert result == "H😀I"


class TestStringRaw:
    """Tests for String.raw() - FR-ES24-020"""

    def test_raw_basic(self):
        """Test raw() with basic template"""
        result = StringMethods.raw(["Hello ", " world"], ["beautiful"])
        assert result == "Hello beautiful world"

    def test_raw_escapes_preserved(self):
        """Test raw() preserves escape sequences"""
        result = StringMethods.raw(["C:\\", "\\file.txt"], ["Users"])
        assert result == "C:\\Users\\file.txt"

    def test_raw_newline_preserved(self):
        """Test raw() preserves newline literals"""
        result = StringMethods.raw(["Line 1\\n", ""], ["Line 2"])
        assert result == "Line 1\\nLine 2"

    def test_raw_no_substitutions(self):
        """Test raw() with no substitutions"""
        result = StringMethods.raw(["Hello world"], [])
        assert result == "Hello world"

    def test_raw_multiple_substitutions(self):
        """Test raw() with multiple substitutions"""
        result = StringMethods.raw(["", " + ", " = ", ""], ["1", "2", "3"])
        assert result == "1 + 2 = 3"
