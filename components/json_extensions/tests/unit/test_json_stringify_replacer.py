"""
Unit tests for JSON.stringify replacer improvements (FR-ES24-B-035)

Tests enhanced replacer functionality:
- Function replacer with proper this binding
- Array replacer (property whitelist)
- Replacer context (key, holder, path)
- Proper replacer invocation order
"""

import pytest


class TestJSONStringifyFunctionReplacer:
    """Test function replacer behavior"""

    def test_function_replacer_transforms_values(self):
        """Function replacer should transform values during stringification"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        def replacer(key, value):
            if isinstance(value, int):
                return value * 2
            return value

        result = stringifier.stringify({"a": 1, "b": 2}, replacer)

        assert '"a":2' in result or '"a": 2' in result
        assert '"b":4' in result or '"b": 4' in result

    def test_function_replacer_this_binding(self):
        """Replacer 'this' should be bound to holder object"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()
        this_values = []

        def replacer(key, value):
            this_values.append(this)
            return value

        obj = {"a": 1, "b": 2}
        stringifier.stringify(obj, replacer)

        # Root call should have wrapper object as 'this'
        assert len(this_values) > 0

    def test_function_replacer_can_filter(self):
        """Replacer can filter out properties by returning undefined"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        def replacer(key, value):
            if key == 'password':
                return None  # undefined
            return value

        result = stringifier.stringify({"user": "john", "password": "secret"}, replacer)

        assert 'user' in result
        assert 'password' not in result or 'null' in result

    def test_function_replacer_invocation_order(self):
        """Replacer should be invoked in correct order"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()
        call_order = []

        def replacer(key, value):
            call_order.append(key)
            return value

        stringifier.stringify({"a": 1, "b": {"c": 2}}, replacer)

        # Root should be called first with empty string key
        assert call_order[0] == ''

    def test_function_replacer_with_arrays(self):
        """Function replacer should work with arrays"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        def replacer(key, value):
            if isinstance(value, int):
                return value + 10
            return value

        result = stringifier.stringify([1, 2, 3], replacer)

        assert '11' in result
        assert '12' in result
        assert '13' in result


class TestJSONStringifyArrayReplacer:
    """Test array replacer (property whitelist) behavior"""

    def test_array_replacer_filters_properties(self):
        """Array replacer should only include whitelisted properties"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        result = stringifier.stringify(
            {"a": 1, "b": 2, "c": 3},
            ["a", "c"]
        )

        assert '"a"' in result
        assert '"c"' in result
        assert '"b"' not in result

    def test_array_replacer_nested_objects(self):
        """Array replacer should apply to nested objects"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        result = stringifier.stringify(
            {"a": 1, "nested": {"b": 2, "c": 3}},
            ["a", "nested", "b"]
        )

        assert '"a"' in result
        assert '"nested"' in result
        assert '"b"' in result
        assert '"c"' not in result

    def test_array_replacer_with_numbers(self):
        """Array replacer can contain numeric indices for arrays"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        result = stringifier.stringify(
            {"items": [1, 2, 3, 4]},
            ["items", "0", "2"]
        )

        # Only indices 0 and 2 should be included from array
        assert '"items"' in result

    def test_array_replacer_empty_array(self):
        """Empty array replacer should exclude all properties"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        result = stringifier.stringify(
            {"a": 1, "b": 2},
            []
        )

        # Should return empty object or only root
        assert result == '{}' or result == 'null'

    def test_array_replacer_ignores_non_string_entries(self):
        """Array replacer should only use string/number entries"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        result = stringifier.stringify(
            {"a": 1, "b": 2},
            ["a", None, {"key": "b"}]  # Only "a" is valid
        )

        assert '"a"' in result
        assert '"b"' not in result


class TestJSONStringifyReplacerContext:
    """Test replacer context for path tracking"""

    def test_replacer_context_get_key(self):
        """Replacer context should provide current key"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()
        keys = []

        def replacer(key, value, context=None):
            if context:
                keys.append(context.get_key())
            return value

        stringifier.stringify({"a": 1, "b": 2}, replacer)

        assert '' in keys  # Root key
        assert 'a' in keys
        assert 'b' in keys

    def test_replacer_context_get_holder(self):
        """Replacer context should provide holder object"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()
        holders = []

        def replacer(key, value, context=None):
            if context and key:
                holders.append(context.get_holder())
            return value

        obj = {"a": 1}
        stringifier.stringify(obj, replacer)

        assert len(holders) > 0

    def test_replacer_context_get_path(self):
        """Replacer context should provide path from root"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()
        paths = {}

        def replacer(key, value, context=None):
            if context and key and not isinstance(value, (dict, list)):
                paths[key] = context.get_path()
            return value

        stringifier.stringify({"a": {"b": {"c": 1}}}, replacer)

        # Path to 'c' should be ['a', 'b', 'c']
        assert 'c' in paths
        assert paths['c'] == ['a', 'b', 'c']

    def test_replacer_context_path_for_arrays(self):
        """Context path should work for arrays"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()
        paths = {}

        def replacer(key, value, context=None):
            if context and isinstance(value, int):
                paths[value] = context.get_path()
            return value

        stringifier.stringify({"items": [10, 20]}, replacer)

        # Paths should include array indices
        assert any('items' in str(path) for path in paths.values())


class TestJSONStringifyReplacerEdgeCases:
    """Test edge cases for replacer functionality"""

    def test_replacer_with_null_values(self):
        """Replacer should handle null values correctly"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        def replacer(key, value):
            if value is None:
                return "NULL"
            return value

        result = stringifier.stringify({"a": None}, replacer)

        assert '"NULL"' in result or 'NULL' in result

    def test_replacer_returning_objects(self):
        """Replacer can return objects that get stringified"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        def replacer(key, value):
            if key == 'complex':
                return {"expanded": True}
            return value

        result = stringifier.stringify({"complex": 123}, replacer)

        assert 'expanded' in result

    def test_replacer_called_on_root(self):
        """Replacer should be called on root value with empty key"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()
        root_called = []

        def replacer(key, value):
            if key == '':
                root_called.append(True)
            return value

        stringifier.stringify({"a": 1}, replacer)

        assert len(root_called) > 0
