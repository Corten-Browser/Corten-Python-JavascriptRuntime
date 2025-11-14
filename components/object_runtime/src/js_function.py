"""
JSFunction - JavaScript function representation.

This module provides the JSFunction class which extends JSObject
to implement JavaScript function semantics with callable behavior.
"""

from typing import List, Callable, Optional
import inspect
from components.memory_gc.src import GarbageCollector
from components.value_system.src import Value
from js_object import JSObject, UNDEFINED_VALUE


class JSFunction(JSObject):
    """
    JavaScript function extending JSObject.

    JSFunction represents a JavaScript function with callable behavior,
    parameter handling, and 'this' context support.

    Attributes:
        _callable (Callable): Python callable implementing the function logic
        _name (str): Function name

    Example:
        >>> gc = GarbageCollector()
        >>> def add(a, b):
        ...     return Value.from_smi(a.to_smi() + b.to_smi())
        >>> func = JSFunction(gc, add, name="add")
        >>> result = func.call([Value.from_smi(10), Value.from_smi(20)])
        >>> result.to_smi()
        30
    """

    def __init__(
        self,
        gc: GarbageCollector,
        callable_impl: Callable,
        name: Optional[str] = None,
        prototype: Optional[JSObject] = None,
    ):
        """
        Initialize JSFunction.

        Args:
            gc: Garbage collector managing this function
            callable_impl: Python callable implementing function logic
            name: Function name (optional, defaults to callable's __name__)
            prototype: Prototype object for inheritance chain (optional)

        Example:
            >>> gc = GarbageCollector()
            >>> def my_func(a, b):
            ...     return Value.from_smi(a.to_smi() + b.to_smi())
            >>> func = JSFunction(gc, my_func, name="myFunc")
        """
        # Initialize parent JSObject
        super().__init__(gc, prototype)

        # Store callable
        self._callable = callable_impl

        # Determine function name
        if name is None:
            name = getattr(callable_impl, "__name__", "anonymous")
        self._name = name

        # Set function properties
        # Get parameter count using inspect
        try:
            sig = inspect.signature(callable_impl)
            # Count parameters, excluding 'this' if present
            param_count = len(sig.parameters)
            # If first param is 'this', don't count it for length
            params = list(sig.parameters.keys())
            if params and params[0] == "this":
                param_count -= 1
        except (ValueError, TypeError):
            param_count = 0

        self.set_property("name", Value.from_smi(hash(name) % 1000))  # Placeholder
        self.set_property("length", Value.from_smi(param_count))

    def call(self, args: List[Value], this_context: Optional[JSObject] = None) -> Value:
        """
        Call the function with arguments and optional 'this' context.

        Args:
            args: List of Value objects as arguments
            this_context: Optional 'this' object for the function call

        Returns:
            Value returned by the function

        Example:
            >>> func = JSFunction(gc, lambda a, b: Value.from_smi(a.to_smi() + b.to_smi()))
            >>> result = func.call([Value.from_smi(5), Value.from_smi(10)])
            >>> result.to_smi()
            15
        """
        try:
            # Check if callable expects 'this' context as first parameter
            sig = inspect.signature(self._callable)
            params = list(sig.parameters.keys())

            if params and params[0] == "this":
                # Function expects 'this' as first argument
                if this_context is not None:
                    return self._callable(this_context, *args)
                else:
                    return self._callable(UNDEFINED_VALUE, *args)
            else:
                # Regular function
                return self._callable(*args)

        except Exception:
            # If call fails, return undefined
            return UNDEFINED_VALUE

    def get_name(self) -> str:
        """
        Get function name.

        Returns:
            Function name as string

        Example:
            >>> func = JSFunction(gc, lambda: None, name="myFunc")
            >>> func.get_name()
            'myFunc'
        """
        return self._name
