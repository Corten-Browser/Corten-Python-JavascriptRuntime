"""Additional parser tests for coverage"""

import pytest


class TestJSONParserEdgeCases:
    """Test parser edge cases"""

    def test_parse_array_with_reviver(self):
        """Parse array with reviver"""
        from json_extensions import JSONParser

        parser = JSONParser()

        def reviver(key, value):
            if isinstance(value, int):
                return value + 100
            return value

        result = parser.parse('[1, 2, 3]', reviver)

        # Reviver should transform all integers
        assert 101 in result
        assert 102 in result
        assert 103 in result

    def test_parse_empty_object(self):
        """Parse empty object"""
        from json_extensions import JSONParser

        parser = JSONParser()
        result = parser.parse('{}')

        assert result == {}

    def test_parse_empty_array(self):
        """Parse empty array"""
        from json_extensions import JSONParser

        parser = JSONParser()
        result = parser.parse('[]')

        assert result == []

    def test_parse_with_source_empty(self):
        """Parse with source for empty object"""
        from json_extensions import JSONParser

        parser = JSONParser()

        def reviver(key, value, context=None):
            return value

        result = parser.parse_with_source('{}', reviver)

        assert result == {}
