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
