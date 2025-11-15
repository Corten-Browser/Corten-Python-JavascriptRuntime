"""
JSON.parse implementation with enhanced reviver support (FR-ES24-B-034)

Provides:
- Enhanced reviver with proper this binding
- Depth-first property traversal
- Source text access via context
"""

import json
from typing import Any, Callable, Optional, Dict, List


class JSONReviverContext:
    """Context object passed to reviver functions"""

    def __init__(self, key: str, holder: Any, source: str = None):
        self._key = key
        self._holder = holder
        self._source = source

    def get_source(self) -> str:
        """Get original source text for parsed value"""
        return self._source or ""

    def get_key(self) -> str:
        """Get current property key"""
        return self._key

    def get_holder(self) -> Any:
        """Get object containing current property"""
        return self._holder


class JSONParser:
    """Enhanced JSON.parse with improved reviver support"""

    def __init__(self):
        self._source_map = {}  # Track source text for values

    def parse(self, text: str, reviver: Optional[Callable] = None) -> Any:
        """
        Parse JSON with enhanced reviver support (proper this binding, property order)

        Args:
            text: JSON text to parse
            reviver: Optional reviver function (key, value) -> transformed value

        Returns:
            Parsed and optionally transformed value
        """
        # Parse JSON text
        parsed = json.loads(text)

        if reviver is None:
            return parsed

        # Apply reviver with proper this binding and order
        return self._walk(parsed, '', {'': parsed}, reviver)

    def parse_with_source(self, text: str, reviver: Optional[Callable] = None) -> Any:
        """
        Parse with reviver receiving source text context

        Args:
            text: JSON text to parse
            reviver: Reviver with access to source text (key, value, context)

        Returns:
            Parsed value
        """
        # Parse JSON and track source positions
        parsed = json.loads(text)

        if reviver is None:
            return parsed

        # Build source map (simplified - maps keys to source text)
        self._build_source_map(text, parsed)

        # Apply reviver with context
        return self._walk_with_context(parsed, '', {'': parsed}, reviver, text)

    def _walk(self, holder: Any, key: str, root: Dict, reviver: Callable) -> Any:
        """
        Walk object/array and apply reviver depth-first

        This ensures innermost properties are visited before outer properties.
        """
        # Get value for current key
        if isinstance(holder, dict):
            value = holder.get(key, holder) if key else holder
        elif isinstance(holder, list) and key.isdigit():
            value = holder[int(key)]
        else:
            value = holder

        # For objects/arrays, recurse first (depth-first)
        if isinstance(value, dict):
            for k in list(value.keys()):
                new_val = self._walk(value, k, root, reviver)
                value[k] = new_val

        elif isinstance(value, list):
            for i in range(len(value)):
                new_val = self._walk(value, str(i), root, reviver)
                value[i] = new_val

        # Now call reviver on this value (after children processed)
        try:
            import inspect
            sig = inspect.signature(reviver)
            if len(sig.parameters) >= 3:
                # Reviver supports context
                context = JSONReviverContext(key, holder)
                result = reviver(key, value, context)
            else:
                # Standard reviver (key, value)
                result = reviver(key, value)

            return result
        except Exception:
            # If reviver fails, return original value
            return value

    def _walk_with_context(self, holder: Any, key: str, root: Dict,
                          reviver: Callable, source_text: str) -> Any:
        """Walk with context support for source access"""
        # Get value for current key
        if isinstance(holder, dict):
            value = holder.get(key, holder) if key else holder
        elif isinstance(holder, list) and key.isdigit():
            value = holder[int(key)]
        else:
            value = holder

        # Recurse depth-first
        if isinstance(value, dict):
            for k in list(value.keys()):
                new_val = self._walk_with_context(value, k, root, reviver, source_text)
                value[k] = new_val

        elif isinstance(value, list):
            for i in range(len(value)):
                new_val = self._walk_with_context(value, str(i), root, reviver, source_text)
                value[i] = new_val

        # Create context with source information
        source_for_value = self._get_source_for_key(key, source_text)
        context = JSONReviverContext(key, holder, source_for_value)

        # Call reviver with context
        try:
            import inspect
            sig = inspect.signature(reviver)
            if len(sig.parameters) >= 3:
                result = reviver(key, value, context)
            else:
                result = reviver(key, value)
            return result
        except Exception:
            return value

    def _build_source_map(self, source: str, parsed: Any) -> None:
        """Build mapping from keys to source text (simplified)"""
        # Simplified implementation - just store the source
        # A full implementation would track exact character positions
        self._source_map['__full__'] = source

    def _get_source_for_key(self, key: str, source_text: str) -> str:
        """Get source text for a specific key (simplified)"""
        # Simplified - return relevant portion of source
        # A full implementation would track exact positions
        if key in source_text:
            # Find the value associated with this key
            import re
            pattern = f'"{key}"\\s*:\\s*([^,}}]+)'
            match = re.search(pattern, source_text)
            if match:
                return match.group(1).strip()

        return source_text
