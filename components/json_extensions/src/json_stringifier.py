"""
JSON.stringify implementation with enhanced replacer and formatting (FR-ES24-B-035, FR-ES24-B-037)

Provides:
- Enhanced replacer (function and array)
- Proper space parameter handling
- Well-formed Unicode output
- Circular reference detection
"""

import json
from typing import Any, Callable, Optional, Union, List, Set


class JSONReplacerContext:
    """Context for replacer functions"""

    def __init__(self, key: str, holder: Any, path: List[str]):
        self._key = key
        self._holder = holder
        self._path = path.copy()

    def get_key(self) -> str:
        """Get current property key"""
        return self._key

    def get_holder(self) -> Any:
        """Get object containing current property"""
        return self._holder

    def get_path(self) -> List[str]:
        """Get path from root to current value"""
        return self._path.copy()


class JSONStringifier:
    """Enhanced JSON.stringify with replacer, space, and Unicode improvements"""

    def __init__(self):
        self._seen = set()  # Track objects for circular detection
        self._id_map = {}  # Map objects to IDs for circular detection

    def stringify(self, value: Any, replacer: Union[Callable, List, None] = None,
                 space: Union[str, int, None] = None) -> str:
        """
        Stringify with enhanced replacer and space handling

        Args:
            value: Value to serialize
            replacer: Optional replacer function or property whitelist
            space: Indentation (string or number of spaces)

        Returns:
            JSON string
        """
        # Import edge case handler
        from .json_edge_cases import JSONEdgeCases

        edge_handler = JSONEdgeCases()

        # Reset circular detection
        self._seen.clear()
        self._id_map.clear()

        # Check for circular references first
        if self.detect_circular(value):
            raise TypeError("Converting circular structure to JSON")

        # Prepare value (handle edge cases: toJSON, BigInt, Symbol, etc.)
        value = edge_handler.prepare_for_json(value)

        # Process value with replacer
        if replacer is not None:
            value = self._apply_replacer(value, replacer, '', {'': value}, [])

            # Check for circular references again after replacer
            # (replacer could create new circular references)
            if self.detect_circular(value):
                raise TypeError("Converting circular structure to JSON")

        # Handle space parameter
        indent = self._process_space(space)

        # Serialize
        if indent:
            return json.dumps(value, indent=indent, ensure_ascii=True)
        else:
            return json.dumps(value, separators=(',', ':'), ensure_ascii=True)

    def stringify_well_formed(self, value: Any, replacer: Union[Callable, List, None] = None,
                              space: Union[str, int, None] = None) -> str:
        """
        Stringify with proper Unicode surrogate pair handling (no unpaired surrogates)

        Args:
            value: Value to serialize
            replacer: Optional replacer
            space: Indentation

        Returns:
            Well-formed JSON (proper Unicode surrogates)
        """
        # Import Unicode handler
        from .json_unicode import JSONUnicode

        unicode_handler = JSONUnicode()

        # First, fix any unpaired surrogates in the value
        value = self._fix_surrogates(value, unicode_handler)

        # Then stringify normally
        return self.stringify(value, replacer, space)

    def detect_circular(self, value: Any, seen: Optional[Set] = None) -> bool:
        """
        Detect circular references before stringification

        Args:
            value: Value to check for circular references

        Returns:
            True if circular reference exists
        """
        if seen is None:
            seen = set()

        # Only objects and lists can have circular references
        if not isinstance(value, (dict, list)):
            return False

        # Use id() to track object identity
        obj_id = id(value)

        if obj_id in seen:
            return True

        seen.add(obj_id)

        # Check nested values
        if isinstance(value, dict):
            for v in value.values():
                if self.detect_circular(v, seen):
                    return True
        elif isinstance(value, list):
            for item in value:
                if self.detect_circular(item, seen):
                    return True

        seen.remove(obj_id)
        return False

    def _apply_replacer(self, value: Any, replacer: Union[Callable, List],
                       key: str, holder: Any, path: List[str]) -> Any:
        """Apply replacer function or array filter"""
        if callable(replacer):
            # Function replacer
            return self._apply_function_replacer(value, replacer, key, holder, path)
        elif isinstance(replacer, list):
            # Array replacer (property whitelist)
            return self._apply_array_replacer(value, replacer, key, holder, path)
        else:
            return value

    def _apply_function_replacer(self, value: Any, replacer: Callable,
                                 key: str, holder: Any, path: List[str],
                                 seen: Optional[Set] = None) -> Any:
        """Apply function replacer with proper this binding"""
        # Initialize seen set for circular detection
        if seen is None:
            seen = set()

        # Create context
        context = JSONReplacerContext(key, holder, path)

        # Call replacer
        try:
            import inspect
            sig = inspect.signature(replacer)

            # Inject 'this' into replacer's scope (JavaScript-like behavior)
            if hasattr(replacer, '__globals__'):
                old_this = replacer.__globals__.get('this')
                replacer.__globals__['this'] = holder
                try:
                    if len(sig.parameters) >= 3:
                        # Replacer supports context
                        result = replacer(key, value, context)
                    else:
                        # Standard replacer
                        result = replacer(key, value)
                finally:
                    # Restore old 'this' value
                    if old_this is None:
                        replacer.__globals__.pop('this', None)
                    else:
                        replacer.__globals__['this'] = old_this
            else:
                # Fallback if can't inject 'this'
                if len(sig.parameters) >= 3:
                    result = replacer(key, value, context)
                else:
                    result = replacer(key, value)

            # Check for circular reference in result
            if isinstance(result, (dict, list)):
                obj_id = id(result)
                if obj_id in seen:
                    # Circular reference detected
                    raise TypeError("Converting circular structure to JSON")
                seen.add(obj_id)

            # Recursively apply to nested structures
            if isinstance(result, dict):
                new_obj = {}
                for k, v in result.items():
                    new_val = self._apply_function_replacer(
                        v, replacer, k, result, path + [k], seen
                    )
                    new_obj[k] = new_val

                # Remove from seen after processing
                seen.discard(id(result))
                return new_obj
            elif isinstance(result, list):
                new_list = [
                    self._apply_function_replacer(
                        item, replacer, str(i), result, path + [str(i)], seen
                    )
                    for i, item in enumerate(result)
                ]
                # Remove from seen after processing
                seen.discard(id(result))
                return new_list
            else:
                return result

        except TypeError:
            # Re-raise TypeError (circular reference)
            raise
        except Exception:
            return value

    def _apply_array_replacer(self, value: Any, replacer: List,
                              key: str, holder: Any, path: List[str]) -> Any:
        """Apply array replacer (property whitelist)"""
        # Convert replacer to set of strings
        whitelist = {str(item) for item in replacer if isinstance(item, (str, int))}

        if isinstance(value, dict):
            # Filter object properties
            filtered = {}
            for k, v in value.items():
                if k in whitelist:
                    # Recursively apply to nested values
                    filtered[k] = self._apply_array_replacer(v, replacer, k, value, path + [k])
            return filtered
        elif isinstance(value, list):
            # For arrays, filter by index
            filtered = []
            for i, item in enumerate(value):
                if str(i) in whitelist:
                    filtered.append(self._apply_array_replacer(item, replacer, str(i), value, path + [str(i)]))
                else:
                    # Keep all items but recursively process
                    filtered.append(self._apply_array_replacer(item, replacer, str(i), value, path + [str(i)]))
            return filtered
        else:
            return value

    def _process_space(self, space: Union[str, int, None]) -> Union[str, int, None]:
        """Process space parameter (clamp to max 10)"""
        if space is None:
            return None

        if isinstance(space, str):
            # String space - take first 10 characters
            if len(space) == 0:
                return None
            return space[:10]

        elif isinstance(space, (int, float)):
            # Numeric space - clamp to 0-10
            space_int = int(space)
            if space_int <= 0:
                return None
            return min(space_int, 10)

        return None

    def _fix_surrogates(self, value: Any, unicode_handler) -> Any:
        """Fix unpaired surrogates in strings"""
        if isinstance(value, str):
            # Fix unpaired surrogates
            result = []
            i = 0
            while i < len(value):
                char = value[i]
                code = ord(char)

                # Check if this is a high surrogate
                if 0xD800 <= code <= 0xDBFF:
                    # Check if next char is low surrogate
                    if i + 1 < len(value):
                        next_code = ord(value[i + 1])
                        if 0xDC00 <= next_code <= 0xDFFF:
                            # Valid pair - keep both
                            result.append(char)
                            result.append(value[i + 1])
                            i += 2
                            continue

                    # Unpaired high surrogate - escape it
                    result.append(unicode_handler.escape_unpaired_surrogate(code))
                    i += 1

                elif 0xDC00 <= code <= 0xDFFF:
                    # Unpaired low surrogate - escape it
                    result.append(unicode_handler.escape_unpaired_surrogate(code))
                    i += 1

                else:
                    # Normal character
                    result.append(char)
                    i += 1

            return ''.join(result)

        elif isinstance(value, dict):
            return {k: self._fix_surrogates(v, unicode_handler) for k, v in value.items()}

        elif isinstance(value, list):
            return [self._fix_surrogates(item, unicode_handler) for item in value]

        else:
            return value
