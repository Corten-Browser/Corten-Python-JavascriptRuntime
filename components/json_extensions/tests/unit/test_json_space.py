"""
Unit tests for JSON.stringify space parameter (FR-ES24-B-037)

Tests proper indentation handling:
- Numeric space parameter (number of spaces)
- String space parameter (custom indentation)
- Space parameter clamping (max 10)
- Proper formatting of nested structures
"""

import pytest


class TestJSONStringifySpaceNumeric:
    """Test numeric space parameter"""

    def test_space_number_basic_indentation(self):
        """Numeric space should indent with that many spaces"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": 1, "b": 2}
        result = stringifier.stringify(obj, None, 2)

        # Should have 2-space indentation
        assert '\n' in result
        lines = result.split('\n')
        # At least one line should have 2-space indent
        assert any(line.startswith('  ') for line in lines)

    def test_space_zero_no_formatting(self):
        """Space of 0 should produce compact JSON"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": 1, "b": 2}
        result = stringifier.stringify(obj, None, 0)

        # Should be compact (no extra whitespace)
        assert '\n' not in result

    def test_space_negative_ignored(self):
        """Negative space should be treated as 0 (compact)"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": 1}
        result = stringifier.stringify(obj, None, -5)

        # Should be compact
        assert '\n' not in result

    def test_space_max_10_clamped(self):
        """Space greater than 10 should be clamped to 10"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": {"b": 1}}
        result_20 = stringifier.stringify(obj, None, 20)
        result_10 = stringifier.stringify(obj, None, 10)

        # Both should have same indentation (max 10 spaces)
        # Count leading spaces on indented lines
        lines_20 = [line for line in result_20.split('\n') if line.strip()]
        lines_10 = [line for line in result_10.split('\n') if line.strip()]

        # Max indentation should be same
        max_indent_20 = max((len(line) - len(line.lstrip()) for line in lines_20), default=0)
        max_indent_10 = max((len(line) - len(line.lstrip()) for line in lines_10), default=0)

        # Should both be clamped to 10 or less
        assert max_indent_20 <= 10
        assert max_indent_10 <= 10

    def test_space_nested_objects(self):
        """Space parameter should properly indent nested objects"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {
            "level1": {
                "level2": {
                    "level3": 42
                }
            }
        }
        result = stringifier.stringify(obj, None, 2)

        # Should have increasing indentation levels
        lines = result.split('\n')
        indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]

        # Should have at least 3 different indentation levels (0, 2, 4, 6)
        assert len(set(indents)) >= 3

    def test_space_arrays(self):
        """Space parameter should properly format arrays"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        arr = [1, 2, [3, 4]]
        result = stringifier.stringify(arr, None, 2)

        # Should have newlines and indentation
        assert '\n' in result


class TestJSONStringifySpaceString:
    """Test string space parameter"""

    def test_space_string_custom_indent(self):
        """String space should use that string for indentation"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": 1, "b": 2}
        result = stringifier.stringify(obj, None, "\t")

        # Should use tab for indentation
        assert '\t' in result

    def test_space_string_custom_characters(self):
        """Space string can be custom characters"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": {"b": 1}}
        result = stringifier.stringify(obj, None, "-->")

        # Should use "-->" for indentation
        assert '-->' in result

    def test_space_string_max_10_characters(self):
        """String space should be clamped to 10 characters"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": {"b": 1}}
        long_indent = "=" * 20
        result = stringifier.stringify(obj, None, long_indent)

        # Indentation should not exceed 10 characters
        lines = result.split('\n')
        for line in lines:
            if line.startswith('='):
                # Count leading '=' characters
                indent_count = len(line) - len(line.lstrip('='))
                # At first level, should be at most 10
                assert indent_count <= 10 or indent_count == 20  # Could be 2 levels

    def test_space_string_nested(self):
        """String space should apply to nested levels"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": {"b": {"c": 1}}}
        result = stringifier.stringify(obj, None, "--")

        # Should have multiple levels of "--"
        assert '----' in result  # Level 2 indentation

    def test_space_empty_string_no_formatting(self):
        """Empty string space should produce compact JSON"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": 1}
        result = stringifier.stringify(obj, None, "")

        # Should be compact
        assert '\n' not in result


class TestJSONStringifySpaceFormatting:
    """Test proper formatting with space parameter"""

    def test_space_object_formatting(self):
        """Objects should be formatted with proper spacing"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": 1, "b": 2}
        result = stringifier.stringify(obj, None, 2)

        # Should have structure like:
        # {
        #   "a": 1,
        #   "b": 2
        # }
        assert result.startswith('{')
        assert result.endswith('}')
        assert '\n' in result

    def test_space_array_formatting(self):
        """Arrays should be formatted with proper spacing"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        arr = [1, 2, 3]
        result = stringifier.stringify(arr, None, 2)

        # Should have structure like:
        # [
        #   1,
        #   2,
        #   3
        # ]
        assert result.startswith('[')
        assert result.endswith(']')
        assert '\n' in result

    def test_space_mixed_structure(self):
        """Mixed objects and arrays should be formatted consistently"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        data = {
            "users": [
                {"name": "Alice", "age": 30},
                {"name": "Bob", "age": 25}
            ],
            "count": 2
        }
        result = stringifier.stringify(data, None, 2)

        # Should have proper indentation throughout
        lines = result.split('\n')
        # Check that we have multiple indentation levels
        indents = set(len(line) - len(line.lstrip()) for line in lines if line.strip())
        assert len(indents) >= 3  # At least 3 levels

    def test_space_empty_object(self):
        """Empty objects should be formatted compactly even with space"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        result = stringifier.stringify({}, None, 2)

        # Empty object should still be compact: {}
        assert result == '{}'

    def test_space_empty_array(self):
        """Empty arrays should be formatted compactly even with space"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        result = stringifier.stringify([], None, 2)

        # Empty array should still be compact: []
        assert result == '[]'

    def test_space_single_property_object(self):
        """Single-property objects can be formatted"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"x": 1}
        result = stringifier.stringify(obj, None, 2)

        # May or may not have newlines for single property
        # but should be valid JSON
        assert '"x"' in result
        assert '1' in result


class TestJSONStringifySpaceEdgeCases:
    """Test edge cases for space parameter"""

    def test_space_none_compact(self):
        """None/undefined space should produce compact JSON"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": 1}
        result = stringifier.stringify(obj, None, None)

        # Should be compact
        assert '\n' not in result

    def test_space_float_truncated_to_int(self):
        """Float space should be truncated to integer"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": {"b": 1}}
        result = stringifier.stringify(obj, None, 2.7)

        # Should use 2 spaces (truncated)
        lines = result.split('\n')
        indented_lines = [line for line in lines if line.startswith('  ') and not line.startswith('   ')]
        assert len(indented_lines) > 0

    def test_space_with_replacer(self):
        """Space should work together with replacer"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        def replacer(key, value):
            return value

        obj = {"a": 1, "b": 2}
        result = stringifier.stringify(obj, replacer, 2)

        # Should have both replacer effects and formatting
        assert '\n' in result
        assert '"a"' in result
