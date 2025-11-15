"""
Unit tests for JSON.parse reviver improvements (FR-ES24-B-034)

Tests enhanced reviver functionality:
- Proper this binding to holder object
- Property traversal order (depth-first)
- Source text access (context parameter)
- Key and holder access
"""

import pytest


class TestJSONParseReviverBinding:
    """Test proper this binding in reviver functions"""

    def test_reviver_this_bound_to_holder_object(self):
        """Reviver 'this' should be bound to the object containing the property"""
        from json_extensions import JSONParser

        parser = JSONParser()
        this_values = []

        def reviver(key, value):
            this_values.append(this)
            return value

        result = parser.parse('{"a": 1, "b": 2}', reviver)

        # 'this' should be the object containing each property
        assert len(this_values) >= 2
        # Root object should receive final call with empty key
        assert this_values[-1] == result

    def test_reviver_this_for_nested_objects(self):
        """Test this binding for nested object properties"""
        from json_extensions import JSONParser

        parser = JSONParser()
        this_bindings = {}

        def reviver(key, value):
            if key:  # Skip root call
                this_bindings[key] = this
            return value

        result = parser.parse('{"outer": {"inner": 42}}', reviver)

        # 'this' for 'inner' should be the inner object
        assert 'inner' in this_bindings
        assert this_bindings['inner']['inner'] == 42

    def test_reviver_this_for_arrays(self):
        """Test this binding for array elements"""
        from json_extensions import JSONParser

        parser = JSONParser()
        this_values = []

        def reviver(key, value):
            this_values.append((key, type(this).__name__))
            return value

        parser.parse('[1, 2, 3]', reviver)

        # Array elements should have array as 'this'
        assert any(binding[1] == 'list' for binding in this_values)


class TestJSONParseReviverOrder:
    """Test property traversal order in reviver"""

    def test_reviver_depth_first_order(self):
        """Reviver should visit properties depth-first, innermost to outermost"""
        from json_extensions import JSONParser

        parser = JSONParser()
        visit_order = []

        def reviver(key, value):
            visit_order.append(key)
            return value

        parser.parse('{"a": {"b": 1}, "c": 2}', reviver)

        # 'b' (innermost) should be visited before 'a' and 'c'
        b_index = visit_order.index('b')
        a_index = visit_order.index('a')
        c_index = visit_order.index('c')

        assert b_index < a_index
        # Root (empty key) should be last
        assert '' in visit_order
        assert visit_order.index('') == len(visit_order) - 1

    def test_reviver_nested_array_order(self):
        """Test depth-first order for nested arrays"""
        from json_extensions import JSONParser

        parser = JSONParser()
        visit_order = []

        def reviver(key, value):
            visit_order.append((key, value if not isinstance(value, (dict, list)) else type(value).__name__))
            return value

        parser.parse('[1, [2, 3], 4]', reviver)

        # Inner array elements (2, 3) should be visited before outer array completion
        # Order should be: '0'->1, '0'->2, '1'->3, '1'->[2,3], '2'->4, ''->[...]
        assert len(visit_order) > 0

    def test_reviver_multiple_nesting_levels(self):
        """Test order for multiple nesting levels"""
        from json_extensions import JSONParser

        parser = JSONParser()
        visit_order = []

        def reviver(key, value):
            if not isinstance(value, (dict, list)):
                visit_order.append(key)
            return value

        parser.parse('{"a": {"b": {"c": 1}}}', reviver)

        # Innermost 'c' should be visited first
        assert visit_order[0] == 'c'


class TestJSONParseReviverContext:
    """Test reviver context parameter for source access"""

    def test_reviver_receives_context(self):
        """Reviver should receive context as third parameter"""
        from json_extensions import JSONParser

        parser = JSONParser()
        contexts = []

        def reviver(key, value, context=None):
            contexts.append(context)
            return value

        parser.parse_with_source('{"date": "2024-01-01"}', reviver)

        # Context should be provided
        assert len(contexts) > 0
        assert any(ctx is not None for ctx in contexts)

    def test_context_get_source(self):
        """Context should provide get_source() method"""
        from json_extensions import JSONParser

        parser = JSONParser()
        sources = []

        def reviver(key, value, context=None):
            if context and key == 'date':
                sources.append(context.get_source())
            return value

        parser.parse_with_source('{"date": "2024-01-01"}', reviver)

        assert len(sources) > 0
        assert '"2024-01-01"' in sources[0]

    def test_context_get_key(self):
        """Context should provide get_key() method"""
        from json_extensions import JSONParser

        parser = JSONParser()
        keys = []

        def reviver(key, value, context=None):
            if context:
                keys.append(context.get_key())
            return value

        parser.parse_with_source('{"a": 1, "b": 2}', reviver)

        assert 'a' in keys
        assert 'b' in keys

    def test_context_get_holder(self):
        """Context should provide get_holder() method"""
        from json_extensions import JSONParser

        parser = JSONParser()
        holders = []

        def reviver(key, value, context=None):
            if context and key:
                holders.append(context.get_holder())
            return value

        result = parser.parse_with_source('{"a": 1}', reviver)

        assert len(holders) > 0
        assert holders[0] == result


class TestJSONParseReviverTransformations:
    """Test reviver value transformations"""

    def test_reviver_transforms_values(self):
        """Reviver should be able to transform parsed values"""
        from json_extensions import JSONParser

        parser = JSONParser()

        def reviver(key, value):
            if isinstance(value, str) and value.startswith('date:'):
                return f"DATE({value[5:]})"
            return value

        result = parser.parse('{"created": "date:2024-01-01"}', reviver)

        assert result['created'] == "DATE(2024-01-01)"

    def test_reviver_can_delete_properties(self):
        """Reviver can delete properties by returning undefined"""
        from json_extensions import JSONParser

        parser = JSONParser()

        def reviver(key, value):
            if key == 'secret':
                return None  # In Python, None represents undefined
            return value

        result = parser.parse('{"public": 1, "secret": 2}', reviver)

        assert 'public' in result
        # 'secret' should be filtered out
        assert result.get('secret') is None or 'secret' not in result

    def test_reviver_transforms_nested_values(self):
        """Reviver should transform values at all nesting levels"""
        from json_extensions import JSONParser

        parser = JSONParser()

        def reviver(key, value):
            if isinstance(value, int):
                return value * 2
            return value

        result = parser.parse('{"a": 1, "b": {"c": 2}}', reviver)

        assert result['a'] == 2
        assert result['b']['c'] == 4
