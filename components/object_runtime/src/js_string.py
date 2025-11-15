"""
JSString - JavaScript string representation.

This module provides the JSString class which extends JSObject
to implement JavaScript string semantics.
"""

from typing import Optional
from components.memory_gc.src import GarbageCollector
from components.value_system.src import Value
from .js_object import JSObject


class JSString(JSObject):
    """
    JavaScript string extending JSObject.

    JSString represents a JavaScript string with character access
    and length property.

    Attributes:
        _value (str): The string value

    Example:
        >>> gc = GarbageCollector()
        >>> s = JSString(gc, "hello")
        >>> s.get_value()
        'hello'
        >>> s.length()
        5
        >>> s.char_at(0)
        'h'
    """

    def __init__(
        self, gc: GarbageCollector, value: str, prototype: Optional[JSObject] = None
    ):
        """
        Initialize JSString.

        Args:
            gc: Garbage collector managing this string
            value: The string value
            prototype: Prototype object for inheritance chain (optional)

        Example:
            >>> gc = GarbageCollector()
            >>> s = JSString(gc, "test")
            >>> s.get_value()
            'test'
        """
        # Initialize parent JSObject
        super().__init__(gc, prototype)

        # Store string value
        self._value = value

        # Set length property
        self.set_property("length", Value.from_smi(len(value)))

        # Update size estimate for string storage
        string_size = len(value) * 2  # Estimate 2 bytes per character
        self.size = 100 + string_size
        gc.used_bytes += string_size

    def get_value(self) -> str:
        """
        Get the string value.

        Returns:
            The string value

        Example:
            >>> s = JSString(gc, "hello world")
            >>> s.get_value()
            'hello world'
        """
        return self._value

    def length(self) -> int:
        """
        Get string length.

        Returns:
            Number of characters in the string

        Example:
            >>> s = JSString(gc, "hello")
            >>> s.length()
            5
        """
        return len(self._value)

    def char_at(self, index: int) -> str:
        """
        Get character at specified index.

        Args:
            index: Character index (0-based)

        Returns:
            Character at index, or empty string if out of bounds

        Example:
            >>> s = JSString(gc, "hello")
            >>> s.char_at(0)
            'h'
            >>> s.char_at(4)
            'o'
            >>> s.char_at(10)
            ''
        """
        if index < 0 or index >= len(self._value):
            return ""

        return self._value[index]

    def is_well_formed(self) -> bool:
        """
        Check if string contains unpaired surrogate code units (ES2024).

        Returns true if the string is well-formed (no unpaired surrogates),
        false if it contains unpaired surrogate code units.

        Surrogate pairs:
        - High surrogate: U+D800-U+DBFF (0xD800-0xDBFF)
        - Low surrogate: U+DC00-U+DFFF (0xDC00-0xDFFF)
        - Valid pair: high surrogate followed by low surrogate

        Returns:
            True if string is well-formed (no unpaired surrogates),
            False if string contains unpaired surrogates

        Example:
            >>> s = JSString(gc, "hello")
            >>> s.is_well_formed()
            True
            >>> # String with unpaired high surrogate (0xD800)
            >>> s = JSString(gc, "test\\ud800")
            >>> s.is_well_formed()
            False
        """
        i = 0
        while i < len(self._value):
            code_point = ord(self._value[i])

            # Check if it's a high surrogate (0xD800-0xDBFF)
            if 0xD800 <= code_point <= 0xDBFF:
                # High surrogate must be followed by low surrogate
                if i + 1 >= len(self._value):
                    # High surrogate at end of string (unpaired)
                    return False

                next_code_point = ord(self._value[i + 1])
                # Check if next is low surrogate (0xDC00-0xDFFF)
                if not (0xDC00 <= next_code_point <= 0xDFFF):
                    # High surrogate not followed by low surrogate (unpaired)
                    return False

                # Valid pair, skip both characters
                i += 2
            # Check if it's a low surrogate (0xDC00-0xDFFF)
            elif 0xDC00 <= code_point <= 0xDFFF:
                # Low surrogate without preceding high surrogate (unpaired)
                return False
            else:
                # Regular character
                i += 1

        return True

    def to_well_formed(self) -> "JSString":
        """
        Return new string with unpaired surrogates replaced by U+FFFD (ES2024).

        Creates a new JSString where any unpaired surrogate code units
        are replaced with the replacement character U+FFFD (�).
        Well-formed strings are returned unchanged.

        This method does NOT mutate the original string.

        Returns:
            New JSString with unpaired surrogates replaced by U+FFFD

        Example:
            >>> gc = GarbageCollector()
            >>> s = JSString(gc, "hello")
            >>> s2 = s.to_well_formed()
            >>> s2.get_value()
            'hello'
            >>> # String with unpaired high surrogate (0xD800)
            >>> s = JSString(gc, "test\\ud800end")
            >>> s2 = s.to_well_formed()
            >>> s2.get_value()
            'test\ufffdend'
        """
        result = []
        i = 0

        while i < len(self._value):
            code_point = ord(self._value[i])

            # Check if it's a high surrogate (0xD800-0xDBFF)
            if 0xD800 <= code_point <= 0xDBFF:
                # High surrogate must be followed by low surrogate
                if i + 1 >= len(self._value):
                    # High surrogate at end of string (unpaired) - replace with U+FFFD
                    result.append("\uFFFD")
                    i += 1
                else:
                    next_code_point = ord(self._value[i + 1])
                    # Check if next is low surrogate (0xDC00-0xDFFF)
                    if 0xDC00 <= next_code_point <= 0xDFFF:
                        # Valid pair, keep both characters
                        result.append(self._value[i])
                        result.append(self._value[i + 1])
                        i += 2
                    else:
                        # High surrogate not followed by low surrogate (unpaired)
                        result.append("\uFFFD")
                        i += 1
            # Check if it's a low surrogate (0xDC00-0xDFFF)
            elif 0xDC00 <= code_point <= 0xDFFF:
                # Low surrogate without preceding high surrogate (unpaired)
                result.append("\uFFFD")
                i += 1
            else:
                # Regular character
                result.append(self._value[i])
                i += 1

        # Create and return new JSString with the well-formed value
        return JSString(self._gc, "".join(result), self._prototype)
