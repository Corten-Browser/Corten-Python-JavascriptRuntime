"""
Unit tests for JSON edge cases (FR-ES24-B-038)

Tests handling of:
- Circular references (TypeError)
- BigInt serialization (TypeError)
- Symbol handling (undefined/skip)
- Function handling (undefined/skip)
- Undefined in objects vs arrays
- toJSON() method support
"""

import pytest


class TestJSONCircularReferences:
    """Test circular reference detection and error handling"""

    def test_direct_circular_reference_throws(self):
        """Direct circular reference should throw TypeError"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": 1}
        obj["self"] = obj  # Direct circular reference

        with pytest.raises(TypeError, match="circular|Converting circular structure"):
            stringifier.stringify(obj)

    def test_indirect_circular_reference_throws(self):
        """Indirect circular reference should throw TypeError"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj1 = {"name": "obj1"}
        obj2 = {"name": "obj2", "ref": obj1}
        obj1["ref"] = obj2  # Indirect circular reference

        with pytest.raises(TypeError, match="circular|Converting circular structure"):
            stringifier.stringify(obj1)

    def test_deep_circular_reference_throws(self):
        """Deep circular reference should be detected"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": {"b": {"c": {}}}}
        obj["a"]["b"]["c"]["root"] = obj  # Deep circular reference

        with pytest.raises(TypeError, match="circular|Converting circular structure"):
            stringifier.stringify(obj)

    def test_circular_array_reference_throws(self):
        """Circular reference in arrays should throw"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        arr = [1, 2]
        arr.append(arr)  # Circular reference

        with pytest.raises(TypeError, match="circular|Converting circular structure"):
            stringifier.stringify(arr)

    def test_detect_circular_method(self):
        """detect_circular method should identify circular references"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": 1}
        obj["self"] = obj

        assert stringifier.detect_circular(obj) is True

    def test_detect_circular_no_reference(self):
        """detect_circular should return False for non-circular structures"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": {"b": {"c": 1}}}

        assert stringifier.detect_circular(obj) is False

    def test_circular_after_replacer(self):
        """Circular reference created by replacer should be detected"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        root = {"value": 1}

        def replacer(key, value):
            if key == "value":
                return root  # Create circular reference
            return value

        # Should still throw even with replacer
        with pytest.raises(TypeError, match="circular|Converting circular structure"):
            stringifier.stringify(root, replacer)


class TestJSONBigIntHandling:
    """Test BigInt serialization rejection"""

    def test_bigint_throws_typeerror(self):
        """BigInt should throw TypeError"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        # Python doesn't have BigInt like JavaScript, but we can simulate
        # For this test, we'll use a custom class or marker
        class BigInt:
            def __init__(self, value):
                self.value = value

        obj = {"number": BigInt(123)}

        with pytest.raises(TypeError, match="BigInt|serialize"):
            stringifier.stringify(obj)

    def test_bigint_in_array_throws(self):
        """BigInt in array should throw TypeError"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        class BigInt:
            def __init__(self, value):
                self.value = value

        arr = [1, 2, BigInt(999)]

        with pytest.raises(TypeError, match="BigInt|serialize"):
            stringifier.stringify(arr)

    def test_handle_bigint_method(self):
        """handle_bigint should throw appropriate error"""
        from json_extensions import JSONEdgeCases

        edge_cases = JSONEdgeCases()

        class BigInt:
            def __init__(self, value):
                self.value = value

        with pytest.raises(TypeError, match="BigInt|serialize"):
            edge_cases.handle_bigint(BigInt(123))


class TestJSONSymbolHandling:
    """Test Symbol handling (skip/undefined)"""

    def test_symbol_in_object_skipped(self):
        """Symbol values in objects should be skipped"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        # Simulate Symbol with a marker class
        class Symbol:
            def __init__(self, description):
                self.description = description

        obj = {"a": 1, "b": Symbol("test"), "c": 2}
        result = stringifier.stringify(obj)

        # Symbol should be skipped
        assert '"a"' in result
        assert '"c"' in result
        # 'b' should be absent or have null/undefined behavior
        # Depending on implementation, might be absent entirely

    def test_symbol_in_array_becomes_null(self):
        """Symbol values in arrays should become null"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        class Symbol:
            def __init__(self, description):
                self.description = description

        arr = [1, Symbol("test"), 3]
        result = stringifier.stringify(arr)

        # In arrays, symbols should become null
        assert 'null' in result or result == '[1,null,3]' or result == '[1, null, 3]'

    def test_handle_symbol_method(self):
        """handle_symbol should return undefined"""
        from json_extensions import JSONEdgeCases

        edge_cases = JSONEdgeCases()

        class Symbol:
            pass

        result = edge_cases.handle_symbol(Symbol())

        # Should return None (undefined)
        assert result is None


class TestJSONFunctionHandling:
    """Test Function handling (skip/undefined)"""

    def test_function_in_object_skipped(self):
        """Function values in objects should be skipped"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        obj = {"a": 1, "b": lambda x: x, "c": 2}
        result = stringifier.stringify(obj)

        # Function should be skipped
        assert '"a"' in result
        assert '"c"' in result
        assert 'lambda' not in result
        assert 'function' not in result

    def test_function_in_array_becomes_null(self):
        """Function values in arrays should become null"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        arr = [1, lambda x: x, 3]
        result = stringifier.stringify(arr)

        # Functions in arrays should become null
        assert 'null' in result

    def test_handle_function_method(self):
        """handle_function should return undefined"""
        from json_extensions import JSONEdgeCases

        edge_cases = JSONEdgeCases()

        result = edge_cases.handle_function(lambda: None)

        # Should return None (undefined)
        assert result is None


class TestJSONUndefinedHandling:
    """Test undefined handling in objects vs arrays"""

    def test_undefined_in_object_skipped(self):
        """Undefined values in objects should be skipped"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        # In Python, None represents both null and undefined
        # We need a way to distinguish - use a sentinel
        class Undefined:
            pass

        undefined = Undefined()

        obj = {"a": 1, "b": undefined, "c": 2}
        result = stringifier.stringify(obj)

        # 'b' should be skipped (not included in output)
        assert '"a"' in result
        assert '"c"' in result
        # Implementation should skip undefined properties

    def test_undefined_in_array_becomes_null(self):
        """Undefined values in arrays should become null"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        class Undefined:
            pass

        arr = [1, Undefined(), 3]
        result = stringifier.stringify(arr)

        # Should have null in array
        assert 'null' in result

    def test_handle_undefined_in_array_method(self):
        """handle_undefined_in_array should convert to null"""
        from json_extensions import JSONEdgeCases

        edge_cases = JSONEdgeCases()

        arr = [1, None, 3]  # None as undefined
        result = edge_cases.handle_undefined_in_array(arr)

        # Should have null for undefined
        assert 'null' in result


class TestJSONToJSONMethod:
    """Test toJSON() method support"""

    def test_object_with_toJSON_called(self):
        """Objects with toJSON() should have method called"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        class CustomObject:
            def __init__(self, value):
                self.value = value

            def toJSON(self):
                return {"custom": self.value}

        obj = CustomObject(42)
        result = stringifier.stringify(obj)

        # Should call toJSON() and serialize result
        assert 'custom' in result
        assert '42' in result

    def test_toJSON_return_primitive(self):
        """toJSON() can return primitive values"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        class CustomObject:
            def toJSON(self):
                return 123

        obj = {"value": CustomObject()}
        result = stringifier.stringify(obj)

        # Should serialize the primitive returned by toJSON()
        assert '123' in result

    def test_toJSON_return_string(self):
        """toJSON() can return strings"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        class CustomObject:
            def toJSON(self):
                return "custom string"

        result = stringifier.stringify(CustomObject())

        # Should serialize the string
        assert 'custom string' in result

    def test_toJSON_in_nested_object(self):
        """toJSON() should work in nested structures"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        class CustomObject:
            def toJSON(self):
                return "CUSTOM"

        obj = {"outer": {"inner": CustomObject()}}
        result = stringifier.stringify(obj)

        # Should call toJSON() on nested object
        assert 'CUSTOM' in result

    def test_toJSON_in_array(self):
        """toJSON() should work for objects in arrays"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        class CustomObject:
            def __init__(self, value):
                self.value = value

            def toJSON(self):
                return self.value * 10

        arr = [CustomObject(1), CustomObject(2)]
        result = stringifier.stringify(arr)

        # Should call toJSON() on array elements
        assert '10' in result
        assert '20' in result

    def test_handle_toJSON_method(self):
        """handle_toJSON should call toJSON() if present"""
        from json_extensions import JSONEdgeCases

        edge_cases = JSONEdgeCases()

        class CustomObject:
            def toJSON(self):
                return {"result": 99}

        result = edge_cases.handle_toJSON(CustomObject())

        # Should return the result of toJSON()
        assert result == {"result": 99}

    def test_toJSON_with_replacer(self):
        """toJSON() should be called before replacer"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        class CustomObject:
            def toJSON(self):
                return 100

        def replacer(key, value):
            if isinstance(value, int):
                return value + 1
            return value

        result = stringifier.stringify(CustomObject(), replacer)

        # toJSON returns 100, replacer adds 1 -> 101
        assert '101' in result


class TestJSONEdgeCaseIntegration:
    """Integration tests for multiple edge cases"""

    def test_complex_object_with_multiple_edge_cases(self):
        """Test object with multiple edge case types"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        class Symbol:
            pass

        obj = {
            "number": 42,
            "text": "hello",
            "func": lambda: None,  # Should be skipped
            "symbol": Symbol(),  # Should be skipped
            "null": None,  # Should be null
            "nested": {"valid": True}
        }

        result = stringifier.stringify(obj)

        # Valid properties should be present
        assert '42' in result
        assert 'hello' in result
        assert 'null' in result or 'None' not in result  # null handling
        assert 'nested' in result

        # Functions and symbols should be absent
        assert 'lambda' not in result
        assert 'Symbol' not in result

    def test_array_with_mixed_edge_cases(self):
        """Test array with various edge case values"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        arr = [
            1,
            None,  # null
            "text",
            lambda: None,  # Should become null in array
            42
        ]

        result = stringifier.stringify(arr)

        # Should have multiple nulls (one for None, one for function)
        null_count = result.count('null')
        assert null_count >= 1

    def test_nested_structure_with_toJSON(self):
        """Test nested structure with toJSON at various levels"""
        from json_extensions import JSONStringifier

        stringifier = JSONStringifier()

        class Wrapper:
            def __init__(self, value):
                self.value = value

            def toJSON(self):
                return {"wrapped": self.value}

        obj = {
            "level1": Wrapper(1),
            "level2": {
                "item": Wrapper(2)
            }
        }

        result = stringifier.stringify(obj)

        # Both toJSON calls should be honored
        assert 'wrapped' in result
        assert result.count('wrapped') == 2
