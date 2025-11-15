"""
Function.prototype.call/apply implementation (FR-ES24-B-042)

Implements explicit this binding with edge cases:
- Normal functions: use provided this
- Arrow functions: ignore provided this (use lexical)
- Bound functions: ignore provided this (use bound)
- Strict mode: no boxing of primitives
- Non-strict mode: box primitives, convert undefined/null to global
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class CallApplyOptions:
    """Options for call/apply operation"""
    this_arg: Any
    args: Optional[List[Any]] = None


def call_function(
    function: Dict[str, Any],
    options: CallApplyOptions,
    args: Optional[List[Any]] = None
) -> Dict[str, Any]:
    """
    Call function with explicit this value.

    Args:
        function: Function to call
        options: Call options (this value)
        args: Arguments to pass

    Returns:
        Result object with this_value and result

    Examples:
        >>> func = {"type": "function", "name": "test"}
        >>> options = CallApplyOptions(this_arg={"x": 1})
        >>> result = call_function(func, options, args=[])
        >>> result["this_value"]
        {'x': 1}
    """
    func_type = function.get("type", "function")
    is_strict = function.get("strict", False)

    # Determine actual this value
    actual_this = _resolve_this_value(function, options.this_arg, is_strict)

    # Simulate function execution
    # (In real implementation, this would execute the function)
    return {
        "result": None,  # Placeholder for actual execution result
        "this_value": actual_this
    }


def apply_function(
    function: Dict[str, Any],
    options: CallApplyOptions
) -> Dict[str, Any]:
    """
    Apply function with arguments array.

    Args:
        function: Function to apply
        options: Apply options (this value and args array)

    Returns:
        Result object with this_value, result, and args_used

    Raises:
        TypeError: If args is not array-like

    Examples:
        >>> func = {"type": "function", "name": "sum"}
        >>> options = CallApplyOptions(this_arg=None, args=[1, 2, 3])
        >>> result = apply_function(func, options)
        >>> result["args_used"]
        [1, 2, 3]
    """
    func_type = function.get("type", "function")
    is_strict = function.get("strict", False)

    # Determine actual this value
    actual_this = _resolve_this_value(function, options.this_arg, is_strict)

    # Process arguments
    args = _process_apply_arguments(options.args)

    # Simulate function execution
    return {
        "result": None,  # Placeholder for actual execution result
        "this_value": actual_this,
        "args_used": args
    }


def _resolve_this_value(
    function: Dict[str, Any],
    this_arg: Any,
    is_strict: bool
) -> Any:
    """
    Resolve the actual this value based on function type and mode.

    Args:
        function: Function object
        this_arg: Provided this argument
        is_strict: Whether in strict mode

    Returns:
        Actual this value to use
    """
    func_type = function.get("type", "function")

    # Arrow functions always use lexical this
    if func_type == "arrow":
        return function.get("lexical_this", {"__type__": "global"})

    # Bound functions always use bound this
    if func_type == "bound":
        return function.get("bound_this")

    # Normal functions
    # Strict mode: use this_arg as-is
    if is_strict:
        return this_arg

    # Non-strict mode: box primitives, convert undefined/null to global
    return _box_this_value(this_arg)


def _box_this_value(this_arg: Any) -> Any:
    """
    Box this value for non-strict mode.

    Args:
        this_arg: Original this argument

    Returns:
        Boxed or converted this value
    """
    # undefined or null becomes global object
    if this_arg is None:
        return {"__type__": "global"}

    # Primitives are boxed
    if isinstance(this_arg, (int, float)):
        return {"__primitive__": this_arg, "__type__": "Number"}
    elif isinstance(this_arg, str):
        return {"__primitive__": this_arg, "__type__": "String"}
    elif isinstance(this_arg, bool):
        return {"__primitive__": this_arg, "__type__": "Boolean"}

    # Objects are used as-is
    return this_arg


def _process_apply_arguments(args: Any) -> List[Any]:
    """
    Process arguments for apply().

    Args:
        args: Arguments (array, array-like, null, or undefined)

    Returns:
        List of arguments

    Raises:
        TypeError: If args is not array-like
    """
    # null or undefined treated as empty array
    if args is None:
        return []

    # Array
    if isinstance(args, list):
        return args

    # Array-like object (has length property and indexed elements)
    if isinstance(args, dict) and "length" in args:
        length = args["length"]
        result = []
        for i in range(length):
            if str(i) in args:
                result.append(args[str(i)])
        return result

    # Not array-like
    raise TypeError(f"Arguments not array-like: {type(args)}")
