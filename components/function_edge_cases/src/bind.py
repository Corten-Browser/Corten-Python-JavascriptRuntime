"""
Function.prototype.bind() implementation (FR-ES24-B-041)

Creates bound functions with:
- Bound this value
- Prepended bound arguments
- Adjusted length property
- Modified name with 'bound ' prefix
- Removed prototype property
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field


@dataclass
class BindOptions:
    """Options for bind operation"""
    this_arg: Any
    args: List[Any] = field(default_factory=list)
    preserve_name: bool = True


def bind_function(
    function: Dict[str, Any],
    options: BindOptions
) -> Dict[str, Any]:
    """
    Create a bound function.

    Args:
        function: Original function to bind
        options: Bind options (this value and arguments)

    Returns:
        Bound function object

    Examples:
        >>> func = {"type": "function", "name": "foo", "length": 2}
        >>> options = BindOptions(this_arg={"x": 1}, args=[1])
        >>> bound = bind_function(func, options)
        >>> bound["name"]
        'bound foo'
        >>> bound["length"]
        1
    """
    original_name = function.get("name", "")
    original_length = function.get("length", 0)
    original_type = function.get("type", "function")

    # Calculate new length: max(0, original.length - bound_args.length)
    bound_args_count = len(options.args) if options.args else 0
    new_length = max(0, original_length - bound_args_count)

    # For already bound functions, preserve the original bound this
    if original_type == "bound":
        # First bind's this wins
        this_value = function.get("bound_this")
        # Combine bound arguments
        existing_bound_args = function.get("bound_args", [])
        combined_args = existing_bound_args + (options.args or [])
        target_func = function.get("target_function", function)
    else:
        this_value = options.this_arg
        combined_args = options.args or []
        target_func = function

    # Create bound function object
    bound_function = {
        "type": "bound",
        "name": f"bound {original_name}",
        "length": new_length,
        "bound_this": this_value,
        "bound_args": combined_args,
        "target_function": target_func
    }

    # Bound functions don't have prototype property
    # (explicitly omit it or set to None)

    return bound_function


def _get_target_length(function: Dict[str, Any]) -> int:
    """
    Get the effective length of the target function.

    For bound functions, this traces back to the original function.

    Args:
        function: Function object

    Returns:
        Target function's original length
    """
    if function.get("type") == "bound":
        target = function.get("target_function")
        if target:
            return _get_target_length(target)
    return function.get("length", 0)
