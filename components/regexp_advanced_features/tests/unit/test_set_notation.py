"""
FR-ES24-B-006: Set notation in /v flag - Advanced set operations
FR-ES24-B-007: String properties in /v - Unicode property syntax
"""

import pytest
from src.set_notation import SetNotationProcessor
from src.types import CharacterSet


class TestSetOperations:
    """Test set notation operations"""

    def test_union_operation(self):
        """Test set union"""
        processor = SetNotationProcessor()
        set1 = CharacterSet()
        set1.add_code_point(65)  # 'A'
        set1.add_code_point(66)  # 'B'

        set2 = CharacterSet()
        set2.add_code_point(66)  # 'B'
        set2.add_code_point(67)  # 'C'

        result = processor.evaluate_union([set1, set2])
        assert 65 in result.code_points
        assert 66 in result.code_points
        assert 67 in result.code_points

    def test_intersection_operation(self):
        """Test set intersection"""
        processor = SetNotationProcessor()
        set1 = CharacterSet()
        set1.add_code_point(65)
        set1.add_code_point(66)

        set2 = CharacterSet()
        set2.add_code_point(66)
        set2.add_code_point(67)

        result = processor.evaluate_intersection([set1, set2])
        assert 66 in result.code_points
        assert 65 not in result.code_points
        assert 67 not in result.code_points

    def test_subtraction_operation(self):
        """Test set subtraction"""
        processor = SetNotationProcessor()
        set1 = CharacterSet()
        set1.add_code_point(65)
        set1.add_code_point(66)
        set1.add_code_point(67)

        set2 = CharacterSet()
        set2.add_code_point(66)

        result = processor.evaluate_subtraction(set1, set2)
        assert 65 in result.code_points
        assert 67 in result.code_points
        assert 66 not in result.code_points

    @pytest.mark.skip(reason="Full pattern parsing pending")
    def test_parse_intersection_pattern(self):
        """Parse intersection in character class"""
        processor = SetNotationProcessor()
        # [A-Z&&[AEIOU]] - uppercase vowels
        pattern = r"[A-Z&&[AEIOU]]"
        result = processor.parse_set_operations(pattern)
        # Would verify only A, E, I, O, U in result

    @pytest.mark.skip(reason="Full pattern parsing pending")
    def test_parse_subtraction_pattern(self):
        """Parse subtraction in character class"""
        processor = SetNotationProcessor()
        # [A-Z--[AEIOU]] - uppercase consonants
        pattern = r"[A-Z--[AEIOU]]"
        result = processor.parse_set_operations(pattern)
        # Would verify vowels excluded


class TestStringProperties:
    """Test string properties in /v flag"""

    def test_parse_string_property(self):
        """Parse string property"""
        processor = SetNotationProcessor()
        prop = processor.parse_string_property("RGI_Emoji")
        assert prop.property_name == "RGI_Emoji"

    @pytest.mark.skip(reason="String property database pending")
    def test_emoji_sequence_matching(self):
        """Match emoji sequences with string properties"""
        # Would test matching multi-code-point sequences
        pass


class TestCharacterSet:
    """Test CharacterSet data structure"""

    def test_contains_code_point(self):
        """Test code point membership"""
        char_set = CharacterSet()
        char_set.add_code_point(65)
        assert char_set.contains(65)
        assert not char_set.contains(66)

    def test_contains_range(self):
        """Test range membership"""
        char_set = CharacterSet()
        char_set.add_range(65, 90)  # A-Z
        assert char_set.contains(65)  # A
        assert char_set.contains(90)  # Z
        assert char_set.contains(75)  # K
        assert not char_set.contains(97)  # a

    def test_mixed_points_and_ranges(self):
        """Test mixture of points and ranges"""
        char_set = CharacterSet()
        char_set.add_code_point(48)  # '0'
        char_set.add_range(65, 70)  # A-F
        assert char_set.contains(48)
        assert char_set.contains(65)
        assert char_set.contains(70)
        assert not char_set.contains(71)
