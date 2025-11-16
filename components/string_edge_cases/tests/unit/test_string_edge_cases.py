"""
Unit tests for String Edge Cases Component (ES2024 Wave D)

Tests cover all 4 requirements:
- FR-ES24-D-006: String.prototype methods with surrogate pairs
- FR-ES24-D-007: String.prototype.at() edge cases
- FR-ES24-D-008: String iterator edge cases
- FR-ES24-D-009: Unicode property escapes in RegExp

Following TDD RED-GREEN-REFACTOR pattern.
This is the RED phase - tests written before implementation.
"""

import pytest
from typing import Optional, List, Iterator


# Import the module we'll implement
# Initially these imports will fail - that's expected in RED phase
from components.string_edge_cases.src.edge_cases import StringEdgeCases


class TestStringAt:
    """
    Tests for String.prototype.at() edge cases
    Requirement: FR-ES24-D-007
    """

    def test_at_positive_index_ascii(self):
        """Test at() with positive index on ASCII string"""
        result = StringEdgeCases.at("hello", 1)
        assert result == {"result": "e", "code_point": 101}

    def test_at_negative_index_ascii(self):
        """Test at() with negative index (count from end)"""
        result = StringEdgeCases.at("hello", -1)
        assert result == {"result": "o", "code_point": 111}

    def test_at_negative_index_from_start(self):
        """Test at() with negative index at first character"""
        result = StringEdgeCases.at("hello", -5)
        assert result == {"result": "h", "code_point": 104}

    def test_at_out_of_bounds_positive(self):
        """Test at() with out-of-bounds positive index"""
        result = StringEdgeCases.at("hello", 100)
        assert result == {"result": None, "code_point": None}

    def test_at_out_of_bounds_negative(self):
        """Test at() with out-of-bounds negative index"""
        result = StringEdgeCases.at("hello", -6)
        assert result == {"result": None, "code_point": None}

    def test_at_empty_string(self):
        """Test at() on empty string"""
        result = StringEdgeCases.at("", 0)
        assert result == {"result": None, "code_point": None}

    def test_at_emoji_positive_index(self):
        """Test at() with emoji (surrogate pair)"""
        result = StringEdgeCases.at("hello 😀 world", 6)
        assert result == {"result": "😀", "code_point": 128512}

    def test_at_emoji_negative_index(self):
        """Test at() with negative index on emoji string"""
        # "😀" at the end: -1 should get it
        result = StringEdgeCases.at("hello😀", -1)
        assert result == {"result": "😀", "code_point": 128512}

    def test_at_multiple_emoji(self):
        """Test at() with multiple emoji"""
        result = StringEdgeCases.at("😀😁😂", 1)
        assert result == {"result": "😁", "code_point": 128513}

    def test_at_single_character(self):
        """Test at() with single character string"""
        result = StringEdgeCases.at("a", 0)
        assert result == {"result": "a", "code_point": 97}

    def test_at_invalid_string_type(self):
        """Test at() with non-string input raises TypeError"""
        with pytest.raises(TypeError, match="must be a string"):
            StringEdgeCases.at(123, 0)

    def test_at_invalid_index_type(self):
        """Test at() with non-integer index raises TypeError"""
        with pytest.raises(TypeError, match="must be an integer"):
            StringEdgeCases.at("hello", "0")


class TestCodePointAt:
    """
    Tests for code_point_at() with surrogate pair handling
    Requirement: FR-ES24-D-006
    """

    def test_code_point_at_ascii(self):
        """Test code_point_at() with ASCII character"""
        result = StringEdgeCases.code_point_at("hello", 0)
        assert result == {"code_point": 104, "is_surrogate_pair": False}

    def test_code_point_at_emoji(self):
        """Test code_point_at() with emoji (surrogate pair)"""
        result = StringEdgeCases.code_point_at("😀", 0)
        assert result == {"code_point": 128512, "is_surrogate_pair": True}

    def test_code_point_at_emoji_in_string(self):
        """Test code_point_at() with emoji in middle of string"""
        result = StringEdgeCases.code_point_at("hello 😀 world", 6)
        assert result == {"code_point": 128512, "is_surrogate_pair": True}

    def test_code_point_at_high_surrogate_unpaired(self):
        """Test code_point_at() with unpaired high surrogate"""
        # High surrogate without low surrogate
        result = StringEdgeCases.code_point_at("\uD800", 0)
        assert result["code_point"] == 0xD800
        # Unpaired surrogate is not a proper pair
        assert result["is_surrogate_pair"] == False

    def test_code_point_at_low_surrogate_unpaired(self):
        """Test code_point_at() with unpaired low surrogate"""
        # Low surrogate without high surrogate
        result = StringEdgeCases.code_point_at("\uDC00", 0)
        assert result["code_point"] == 0xDC00
        assert result["is_surrogate_pair"] == False

    def test_code_point_at_out_of_bounds(self):
        """Test code_point_at() with out-of-bounds index"""
        result = StringEdgeCases.code_point_at("hello", 100)
        assert result == {"code_point": None, "is_surrogate_pair": False}

    def test_code_point_at_empty_string(self):
        """Test code_point_at() on empty string"""
        result = StringEdgeCases.code_point_at("", 0)
        assert result == {"code_point": None, "is_surrogate_pair": False}

    def test_code_point_at_multi_byte_unicode(self):
        """Test code_point_at() with multi-byte Unicode (non-surrogate)"""
        # Greek letter Alpha (U+0391)
        result = StringEdgeCases.code_point_at("Α", 0)
        assert result == {"code_point": 0x0391, "is_surrogate_pair": False}

    def test_code_point_at_multiple_emoji(self):
        """Test code_point_at() with multiple emoji in sequence"""
        emoji_string = "😀😁😂"
        result1 = StringEdgeCases.code_point_at(emoji_string, 0)
        result2 = StringEdgeCases.code_point_at(emoji_string, 1)
        result3 = StringEdgeCases.code_point_at(emoji_string, 2)

        assert result1 == {"code_point": 128512, "is_surrogate_pair": True}  # 😀
        assert result2 == {"code_point": 128513, "is_surrogate_pair": True}  # 😁
        assert result3 == {"code_point": 128514, "is_surrogate_pair": True}  # 😂

    def test_code_point_at_invalid_string_type(self):
        """Test code_point_at() with non-string input"""
        with pytest.raises(TypeError, match="must be a string"):
            StringEdgeCases.code_point_at(123, 0)

    def test_code_point_at_negative_index(self):
        """Test code_point_at() with negative index (should raise ValueError)"""
        with pytest.raises(ValueError, match="non-negative"):
            StringEdgeCases.code_point_at("hello", -1)


class TestIterateCodePoints:
    """
    Tests for iterate_code_points() string iterator
    Requirement: FR-ES24-D-008
    """

    def test_iterate_empty_string(self):
        """Test iterate_code_points() on empty string"""
        result = StringEdgeCases.iterate_code_points("")
        assert result == {
            "code_points": [],
            "count": 0,
            "has_surrogate_pairs": False
        }

    def test_iterate_ascii_only(self):
        """Test iterate_code_points() with ASCII-only string"""
        result = StringEdgeCases.iterate_code_points("hello")
        assert result == {
            "code_points": ["h", "e", "l", "l", "o"],
            "count": 5,
            "has_surrogate_pairs": False
        }

    def test_iterate_emoji_only(self):
        """Test iterate_code_points() with emoji-only string"""
        result = StringEdgeCases.iterate_code_points("😀😁😂")
        assert result == {
            "code_points": ["😀", "😁", "😂"],
            "count": 3,
            "has_surrogate_pairs": True
        }

    def test_iterate_mixed_ascii_emoji(self):
        """Test iterate_code_points() with mixed ASCII and emoji"""
        result = StringEdgeCases.iterate_code_points("hello 😀 world")
        expected_chars = ["h", "e", "l", "l", "o", " ", "😀", " ", "w", "o", "r", "l", "d"]
        assert result["code_points"] == expected_chars
        assert result["count"] == 13
        assert result["has_surrogate_pairs"] == True

    def test_iterate_unpaired_surrogates(self):
        """Test iterate_code_points() with unpaired surrogates"""
        # String with unpaired high surrogate
        result = StringEdgeCases.iterate_code_points("a\uD800b")
        assert result["code_points"] == ["a", "\uD800", "b"]
        assert result["count"] == 3

    def test_iterate_multiple_surrogate_pairs(self):
        """Test iterate_code_points() with many emoji"""
        emoji_string = "🌍🌎🌏"
        result = StringEdgeCases.iterate_code_points(emoji_string)
        assert result["code_points"] == ["🌍", "🌎", "🌏"]
        assert result["count"] == 3
        assert result["has_surrogate_pairs"] == True

    def test_iterate_single_character(self):
        """Test iterate_code_points() with single character"""
        result = StringEdgeCases.iterate_code_points("a")
        assert result == {
            "code_points": ["a"],
            "count": 1,
            "has_surrogate_pairs": False
        }

    def test_iterate_invalid_string_type(self):
        """Test iterate_code_points() with non-string input"""
        with pytest.raises(TypeError, match="must be a string"):
            StringEdgeCases.iterate_code_points(123)


class TestMatchUnicodeProperty:
    """
    Tests for match_unicode_property() with Unicode property escapes
    Requirement: FR-ES24-D-009
    """

    def test_match_emoji_property(self):
        """Test matching Emoji property"""
        result = StringEdgeCases.match_unicode_property("Hello 😀 World 🌍", "Emoji")
        assert result == {
            "matches": ["😀", "🌍"],
            "count": 2,
            "property": "Emoji"
        }

    def test_match_letter_property(self):
        """Test matching Letter property"""
        result = StringEdgeCases.match_unicode_property("Hello123World", "Letter")
        assert result["count"] == 10  # All letters, no numbers
        assert "1" not in result["matches"]
        assert "H" in result["matches"]

    def test_match_number_property(self):
        """Test matching Number property"""
        result = StringEdgeCases.match_unicode_property("abc123def456", "Number")
        assert result == {
            "matches": ["1", "2", "3", "4", "5", "6"],
            "count": 6,
            "property": "Number"
        }

    def test_match_script_greek(self):
        """Test matching Greek script"""
        result = StringEdgeCases.match_unicode_property("Αλφα Beta Γάμμα", "Script=Greek")
        # Should match Greek letters, not Latin
        assert result["count"] > 0
        assert "Α" in result["matches"]
        assert "B" not in result["matches"]  # Latin B not matched

    def test_match_script_latin(self):
        """Test matching Latin script"""
        result = StringEdgeCases.match_unicode_property("Hello Αλφα", "Script=Latin")
        # Should match Latin letters, not Greek
        assert "H" in result["matches"]
        assert "Α" not in result["matches"]

    def test_match_punctuation(self):
        """Test matching Punctuation property"""
        result = StringEdgeCases.match_unicode_property("Hello, World!", "Punctuation")
        assert result == {
            "matches": [",", "!"],
            "count": 2,
            "property": "Punctuation"
        }

    def test_match_no_matches(self):
        """Test match with no matches"""
        result = StringEdgeCases.match_unicode_property("Hello World", "Emoji")
        assert result == {
            "matches": [],
            "count": 0,
            "property": "Emoji"
        }

    def test_match_empty_string(self):
        """Test match on empty string"""
        result = StringEdgeCases.match_unicode_property("", "Letter")
        assert result == {
            "matches": [],
            "count": 0,
            "property": "Letter"
        }

    def test_match_all_characters(self):
        """Test match where all characters match"""
        result = StringEdgeCases.match_unicode_property("12345", "Number")
        assert result["count"] == 5
        assert result["matches"] == ["1", "2", "3", "4", "5"]

    def test_match_invalid_property(self):
        """Test match with invalid Unicode property"""
        with pytest.raises(ValueError, match="Invalid Unicode property"):
            StringEdgeCases.match_unicode_property("Hello", "InvalidProperty")

    def test_match_invalid_string_type(self):
        """Test match with non-string input"""
        with pytest.raises(TypeError, match="must be a string"):
            StringEdgeCases.match_unicode_property(123, "Letter")

    def test_match_script_han(self):
        """Test matching Han (Chinese) script"""
        result = StringEdgeCases.match_unicode_property("你好World", "Script=Han")
        assert result["count"] == 2
        assert "你" in result["matches"]
        assert "W" not in result["matches"]


class TestPerformance:
    """
    Performance tests to ensure operations meet <500µs targets
    """

    def test_at_performance_ascii(self):
        """Test at() performance on ASCII string"""
        import time
        string = "a" * 1000

        start = time.perf_counter()
        StringEdgeCases.at(string, 500)
        duration = (time.perf_counter() - start) * 1_000_000  # microseconds

        assert duration < 500, f"at() took {duration}µs (target: <500µs)"

    def test_at_performance_emoji(self):
        """Test at() performance on emoji string"""
        import time
        string = "😀" * 500

        start = time.perf_counter()
        StringEdgeCases.at(string, 250)
        duration = (time.perf_counter() - start) * 1_000_000

        assert duration < 500, f"at() with emoji took {duration}µs (target: <500µs)"

    def test_code_point_at_performance(self):
        """Test code_point_at() performance"""
        import time
        string = "hello world" * 100

        start = time.perf_counter()
        StringEdgeCases.code_point_at(string, 500)
        duration = (time.perf_counter() - start) * 1_000_000

        assert duration < 500, f"code_point_at() took {duration}µs (target: <500µs)"

    def test_iterate_code_points_performance(self):
        """Test iterate_code_points() performance per iteration"""
        import time
        string = "abc😀" * 250  # 1000 code points

        start = time.perf_counter()
        result = StringEdgeCases.iterate_code_points(string)
        duration = (time.perf_counter() - start) * 1_000_000

        # Total operation should be reasonable
        # Per-iteration cost: duration / count should be < 50µs per spec
        per_iteration = duration / result["count"] if result["count"] > 0 else 0
        assert per_iteration < 50, f"Per-iteration cost: {per_iteration}µs (target: <50µs)"

    def test_match_unicode_property_performance(self):
        """Test match_unicode_property() performance"""
        import time
        string = "Hello World 😀 " * 70  # ~1000 characters

        start = time.perf_counter()
        StringEdgeCases.match_unicode_property(string, "Letter")
        duration = (time.perf_counter() - start) * 1_000_000

        assert duration < 500, f"match_unicode_property() took {duration}µs (target: <500µs)"


class TestEdgeCaseBoundaries:
    """
    Test boundary conditions and edge cases
    """

    def test_at_exact_string_length(self):
        """Test at() with index exactly at string length"""
        result = StringEdgeCases.at("hello", 5)
        assert result == {"result": None, "code_point": None}

    def test_at_maximum_negative_index(self):
        """Test at() with very large negative index"""
        result = StringEdgeCases.at("hello", -10000)
        assert result == {"result": None, "code_point": None}

    def test_code_point_at_max_unicode(self):
        """Test code_point_at() with maximum valid Unicode code point"""
        # U+10FFFF is the maximum Unicode code point
        max_unicode_char = chr(0x10FFFF)
        result = StringEdgeCases.code_point_at(max_unicode_char, 0)
        assert result["code_point"] == 0x10FFFF

    def test_iterate_long_string(self):
        """Test iterate_code_points() with very long string"""
        long_string = "a" * 10000
        result = StringEdgeCases.iterate_code_points(long_string)
        assert result["count"] == 10000
        assert result["has_surrogate_pairs"] == False

    def test_surrogate_pair_boundary(self):
        """Test at() at surrogate pair boundary"""
        # String: "a😀b" where emoji is at index 1 (code point wise)
        result = StringEdgeCases.at("a😀b", 1)
        assert result["result"] == "😀"
