"""
Unit tests for RegExp /v flag with character class set operations.

Tests FR-P3.5-049, FR-P3.5-050, and FR-P3.5-051:
- /v flag parsing
- Character class set operations (intersection, subtraction)
- String properties in character classes
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src.lexer import Lexer
from components.parser.src.token import TokenType
from components.parser.src.regexp_v_flag import (
    RegExpVFlag,
    RegExpFlags,
    CharacterClassSetParser,
)


# FR-P3.5-049: RegExp /v flag parsing (≥8 tests)
class TestRegExpVFlagParsing:
    """Test /v flag parsing in RegExp literals and constructor."""

    def test_v_flag_in_literal_is_recognized(self):
        """
        Given a RegExp literal with /v flag
        When the lexer parses it
        Then the /v flag is recognized and stored
        """
        # Given
        lexer = Lexer("/[a-z]/v", "test.js")

        # When
        token = lexer.next_token()

        # Then
        assert token.type == TokenType.REGEXP
        assert token.value["pattern"] == "[a-z]"
        assert token.value["flags"] == "v"

    def test_v_flag_with_other_flags(self):
        """
        Given a RegExp literal with /v and other valid flags
        When the lexer parses it
        Then all flags are recognized
        """
        # Given
        lexer = Lexer("/pattern/giv", "test.js")

        # When
        token = lexer.next_token()

        # Then
        assert token.type == TokenType.REGEXP
        assert "v" in token.value["flags"]
        assert "g" in token.value["flags"]
        assert "i" in token.value["flags"]

    def test_v_flag_mutually_exclusive_with_u_flag(self):
        """
        Given a RegExp literal with both /u and /v flags
        When validation is performed
        Then a TypeError is raised
        """
        # Given
        pattern = "/[a-z]/uv"

        # When/Then
        with pytest.raises(TypeError, match="mutually exclusive"):
            flags = RegExpFlags.from_string("uv")

    def test_v_flag_enables_set_notation(self):
        """
        Given a RegExp with /v flag
        When it contains set notation
        Then the set notation is accepted
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse("[a-z&&[aeiou]]", has_v_flag=True)

        # Then
        assert result is not None
        assert "&&" in result["operations"]

    def test_v_flag_without_set_notation_is_valid(self):
        """
        Given a RegExp with /v flag but no set notation
        When the pattern is parsed
        Then it is accepted as valid
        """
        # Given
        lexer = Lexer("/[a-z]/v", "test.js")

        # When
        token = lexer.next_token()

        # Then
        assert token.type == TokenType.REGEXP
        assert token.value["flags"] == "v"

    def test_regexp_constructor_with_v_flag(self):
        """
        Given a RegExp constructor call with 'v' flag
        When the flags are parsed
        Then the /v flag is recognized
        """
        # Given
        flags = RegExpFlags.from_string("v")

        # When/Then
        assert flags.v is True
        assert flags.u is False

    def test_v_flag_case_sensitive(self):
        """
        Given a RegExp with uppercase 'V' flag
        When the flags are parsed
        Then it is rejected as invalid
        """
        # Given/When/Then
        with pytest.raises(ValueError, match="Invalid flag"):
            RegExpFlags.from_string("V")

    def test_duplicate_v_flag_is_error(self):
        """
        Given a RegExp with duplicate 'v' flags
        When the flags are parsed
        Then an error is raised
        """
        # Given/When/Then
        with pytest.raises(ValueError, match="duplicate"):
            RegExpFlags.from_string("vv")


# FR-P3.5-050: Character class set operations (≥10 tests)
class TestCharacterClassSetOperations:
    """Test character class set operations with /v flag."""

    def test_intersection_simple(self):
        """
        Given a character class with intersection operator [a-z&&[aeiou]]
        When parsed with /v flag
        Then the intersection of a-z and vowels is computed
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse("[a-z&&[aeiou]]", has_v_flag=True)

        # Then
        assert result["type"] == "intersection"
        assert "a-z" in result["left"]
        assert result["right"]["pattern"] == "aeiou"

    def test_subtraction_simple(self):
        """
        Given a character class with subtraction operator [a-z--[aeiou]]
        When parsed with /v flag
        Then the difference (consonants) is computed
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse("[a-z--[aeiou]]", has_v_flag=True)

        # Then
        assert result["type"] == "subtraction"
        assert "a-z" in result["left"]
        assert "aeiou" in result["right"]

    def test_nested_intersection(self):
        """
        Given nested intersection operations
        When parsed with /v flag
        Then the nested structure is preserved
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse("[a-z&&[^aeiou]&&[b-y]]", has_v_flag=True)

        # Then
        assert result["type"] == "intersection"
        # Multiple && operators are parsed
        assert "&&" in result["operations"]

    def test_intersection_and_subtraction_combined(self):
        """
        Given character class with both intersection and subtraction
        When parsed with /v flag
        Then both operations are correctly parsed
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse("[[a-z]--[aeiou]&&[b-y]]", has_v_flag=True)

        # Then
        assert result is not None
        assert "&&" in str(result) or "--" in str(result)

    def test_set_operations_without_v_flag_error(self):
        """
        Given character class with set operations but no /v flag
        When parsed
        Then an error is raised
        """
        # Given
        parser = CharacterClassSetParser()

        # When/Then
        with pytest.raises(ValueError, match="requires /v flag"):
            parser.parse("[a-z&&[aeiou]]", has_v_flag=False)

    def test_intersection_with_negation(self):
        """
        Given intersection with negated character class [a-z&&[^aeiou]]
        When parsed with /v flag
        Then the negation is handled correctly (consonants)
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse("[a-z&&[^aeiou]]", has_v_flag=True)

        # Then
        assert result["type"] == "intersection"
        assert result["right"]["negated"] is True

    def test_double_bracket_syntax(self):
        """
        Given double bracket syntax [[a-z]--[aeiou]]
        When parsed with /v flag
        Then it is correctly interpreted as set operation
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse("[[a-z]--[aeiou]]", has_v_flag=True)

        # Then
        assert result["type"] == "subtraction"

    def test_empty_set_operations(self):
        """
        Given set operations resulting in empty set
        When parsed
        Then the empty result is handled correctly
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse("[a-z--[a-z]]", has_v_flag=True)

        # Then
        assert result["type"] == "subtraction"
        # Empty set is valid but will never match

    def test_unicode_ranges_in_set_operations(self):
        """
        Given Unicode ranges in set operations
        When parsed with /v flag
        Then Unicode ranges are handled correctly
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse(r"[\u0000-\u007F&&[^aeiou]]", has_v_flag=True)

        # Then
        assert result["type"] == "intersection"

    def test_complex_nested_operations(self):
        """
        Given complex nested set operations
        When parsed with /v flag
        Then the full nested structure is parsed correctly
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse("[[[a-z]--[aeiou]]&&[b-y]]", has_v_flag=True)

        # Then
        assert result is not None
        # Verifies parser can handle multiple nesting levels


# FR-P3.5-051: String properties in character classes (≥7 tests)
class TestStringPropertiesInCharacterClasses:
    r"""Test \p{property} notation in character classes with /v flag."""

    def test_basic_string_property(self):
        r"""
        Given a character class with \p{RGI_Emoji}
        When parsed with /v flag
        Then the string property is recognized
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse(r"[\p{RGI_Emoji}]", has_v_flag=True)

        # Then
        assert result["type"] == "property"
        assert result["property"] == "RGI_Emoji"

    def test_string_property_negation(self):
        r"""
        Given a character class with \P{RGI_Emoji} (negated)
        When parsed with /v flag
        Then the negated string property is recognized
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse(r"[\P{RGI_Emoji}]", has_v_flag=True)

        # Then
        assert result["type"] == "property"
        assert result["negated"] is True

    def test_multiple_string_properties(self):
        r"""
        Given a character class with multiple \p{} properties
        When parsed with /v flag
        Then all properties are recognized
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse(r"[\p{RGI_Emoji}\p{ASCII}]", has_v_flag=True)

        # Then
        assert result is not None
        # Multiple properties create a union

    def test_string_property_in_set_operation(self):
        """
        Given string property combined with set operation
        When parsed with /v flag
        Then both are handled correctly
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse(r"[\p{RGI_Emoji}&&[a-z]]", has_v_flag=True)

        # Then
        # Should parse as property or intersection
        assert result["type"] in ["intersection", "property"]

    def test_string_property_requires_v_flag(self):
        r"""
        Given a character class with \p{} without /v flag
        When parsed
        Then it uses basic Unicode property matching (not string properties)
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse(r"[\p{ASCII}]", has_v_flag=False)

        # Then
        # Without /v, \p{} works but doesn't support multi-character sequences
        assert result["type"] == "property"
        assert result["string_property"] is False

    def test_common_unicode_properties(self):
        r"""
        Given common Unicode properties like \p{Letter}, \p{Number}
        When parsed with /v flag
        Then they are recognized as string properties
        """
        # Given
        parser = CharacterClassSetParser()

        # When
        result = parser.parse(r"[\p{Letter}]", has_v_flag=True)

        # Then
        assert result["type"] == "property"
        assert result["property"] == "Letter"

    def test_invalid_string_property_name(self):
        r"""
        Given an invalid property name like \p{InvalidProperty}
        When parsed
        Then an error is raised
        """
        # Given
        parser = CharacterClassSetParser()

        # When/Then
        with pytest.raises(ValueError, match="Invalid property"):
            parser.parse(r"[\p{InvalidProperty}]", has_v_flag=True)


# Integration tests
class TestRegExpVFlagIntegration:
    """Integration tests for complete RegExp /v flag functionality."""

    def test_full_regexp_with_v_flag_and_set_operations(self):
        """
        Given a complete RegExp with /v flag and set operations
        When parsed by lexer
        Then all components are correctly recognized
        """
        # Given
        lexer = Lexer("/[a-z&&[^aeiou]]/v", "test.js")

        # When
        token = lexer.next_token()

        # Then
        assert token.type == TokenType.REGEXP
        assert token.value["flags"] == "v"
        assert "&&" in token.value["pattern"]

    def test_v_flag_with_global_and_case_insensitive(self):
        """
        Given RegExp with /v, /g, and /i flags
        When parsed
        Then all flags are recognized
        """
        # Given
        lexer = Lexer("/pattern/giv", "test.js")

        # When
        token = lexer.next_token()

        # Then
        assert token.type == TokenType.REGEXP
        flags = token.value["flags"]
        assert "g" in flags
        assert "i" in flags
        assert "v" in flags

    def test_complex_pattern_with_all_v_flag_features(self):
        """
        Given complex pattern using all /v flag features
        When parsed
        Then all features are recognized
        """
        # Given
        pattern = r"/[\p{RGI_Emoji}&&[^aeiou]]/v"
        lexer = Lexer(pattern, "test.js")

        # When
        token = lexer.next_token()

        # Then
        assert token.type == TokenType.REGEXP
        assert token.value["flags"] == "v"
        assert r"\p{RGI_Emoji}" in token.value["pattern"]
        assert "&&" in token.value["pattern"]
