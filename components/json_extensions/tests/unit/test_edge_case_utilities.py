"""Additional tests for edge case utility methods to improve coverage"""

import pytest


class TestJSONEdgeCaseUtilities:
    """Test standalone edge case utility methods"""

    def test_detect_circular_deeply_nested(self):
        """Detect circular references in deeply nested structures"""
        from json_extensions import JSONEdgeCases

        handler = JSONEdgeCases()

        obj = {"a": {"b": {"c": {"d": {}}}}}
        obj["a"]["b"]["c"]["d"]["root"] = obj

        assert handler.detect_circular(obj) is True

    def test_detect_circular_array_in_object(self):
        """Detect circular reference with arrays"""
        from json_extensions import JSONEdgeCases

        handler = JSONEdgeCases()

        obj = {"items": [1, 2, {"nested": None}]}
        obj["items"][2]["nested"] = obj

        assert handler.detect_circular(obj) is True

    def test_stringify_with_edge_cases_full(self):
        """Test stringify_with_edge_cases method"""
        from json_extensions import JSONEdgeCases, Symbol

        handler = JSONEdgeCases()

        obj = {"a": 1, "b": Symbol("test"), "c": 2}
        result = handler.stringify_with_edge_cases(obj)

        # Symbol should be removed
        assert '"a"' in result
        assert '"c"' in result
        assert 'Symbol' not in result

    def test_handle_undefined_in_array_multiple(self):
        """Test handle_undefined_in_array with multiple undefined"""
        from json_extensions import JSONEdgeCases, Undefined

        handler = JSONEdgeCases()

        arr = [1, Undefined(), 2, Undefined(), 3]
        result = handler.handle_undefined_in_array(arr)

        # Should have multiple nulls
        assert result.count('null') >= 2

    def test_prepare_for_json_nested_symbols(self):
        """Test prepare_for_json with nested symbols"""
        from json_extensions import JSONEdgeCases, Symbol

        handler = JSONEdgeCases()

        obj = {
            "outer": {
                "inner": {
                    "symbol": Symbol("test"),
                    "value": 42
                }
            }
        }

        result = handler.prepare_for_json(obj)

        # Symbol should be removed, value preserved
        assert result["outer"]["inner"]["value"] == 42
        assert "symbol" not in result["outer"]["inner"]

    def test_prepare_for_json_mixed_array(self):
        """Test prepare_for_json with mixed types in array"""
        from json_extensions import JSONEdgeCases, Symbol, Undefined

        handler = JSONEdgeCases()

        arr = [1, Symbol("test"), 2, Undefined(), lambda: None, 3]
        result = handler.prepare_for_json(arr)

        # Should have nulls for special types
        assert result[0] == 1
        assert result[1] is None  # Symbol -> null
        assert result[2] == 2
        assert result[3] is None  # Undefined -> null
        assert result[4] is None  # Function -> null
        assert result[5] == 3

    def test_prepare_for_json_with_toJSON_nested(self):
        """Test toJSON in nested structures"""
        from json_extensions import JSONEdgeCases

        handler = JSONEdgeCases()

        class Custom:
            def __init__(self, value):
                self.value = value

            def toJSON(self):
                return {"wrapped": self.value}

        obj = {
            "items": [
                Custom(1),
                Custom(2),
                {"normal": 3}
            ]
        }

        result = handler.prepare_for_json(obj)

        # toJSON should be called for Custom objects
        assert result["items"][0] == {"wrapped": 1}
        assert result["items"][1] == {"wrapped": 2}
        assert result["items"][2] == {"normal": 3}

    def test_detect_circular_no_false_positives(self):
        """Ensure detect_circular doesn't give false positives"""
        from json_extensions import JSONEdgeCases

        handler = JSONEdgeCases()

        # Complex but non-circular structure
        obj = {
            "a": [1, 2, 3],
            "b": {"x": 1, "y": 2},
            "c": [{"nested": [1, 2]}]
        }

        assert handler.detect_circular(obj) is False
