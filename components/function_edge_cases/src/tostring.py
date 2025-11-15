"""
Function.prototype.toString() implementation (FR-ES24-B-040)

Converts functions to their string representation:
- Returns original source code if available
- Preserves syntactic form (function*, async, arrow)
- Returns [native code] for built-in/bound functions
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class ToStringOptions:
    """Options for toString operation"""
    include_source: bool = True
    syntactic: bool = True
    native_code_placeholder: str = "[native code]"


def function_to_string(
    function: Dict[str, Any],
    options: Optional[ToStringOptions] = None
) -> str:
    """
    Convert function to string representation.

    Args:
        function: Function object
        options: ToString options

    Returns:
        String representation of function

    Examples:
        >>> func = {"type": "function", "name": "foo", "source": "function foo() { return 1; }"}
        >>> function_to_string(func)
        'function foo() { return 1; }'
    """
    if options is None:
        options = ToStringOptions()

    func_type = function.get("type", "function")
    name = function.get("name", "")
    source = function.get("source")
    is_native = function.get("is_native", False)

    # Bound functions always show [native code]
    if func_type == "bound":
        return f"function () {{ {options.native_code_placeholder} }}"

    # Native/built-in functions show [native code]
    if is_native:
        return f"function {name}() {{ {options.native_code_placeholder} }}"

    # If source is available and we should include it
    if source and options.include_source:
        return source

    # If source not available but not including source
    if not options.include_source:
        return f"function {name}() {{ {options.native_code_placeholder} }}"

    # Reconstruct source for synthetic functions
    return _reconstruct_function_source(function)


def _reconstruct_function_source(function: Dict[str, Any]) -> str:
    """
    Reconstruct function source code from metadata.

    Args:
        function: Function object with params and body

    Returns:
        Reconstructed source code
    """
    func_type = function.get("type", "function")
    name = function.get("name", "")
    params = function.get("params", [])
    body = function.get("body", "")
    is_arrow = function.get("is_arrow", False) or func_type == "arrow"
    is_async = function.get("is_async", False) or func_type == "async"
    is_generator = function.get("is_generator", False) or func_type == "generator"

    # Format parameters
    if isinstance(params, list):
        if params and isinstance(params[0], dict):
            # Params are objects with names
            param_names = [p.get("name", "") for p in params]
        else:
            # Params are strings
            param_names = params
        param_str = ", ".join(param_names)
    else:
        param_str = ""

    # Arrow function
    if is_arrow or func_type == "arrow":
        if not body:
            return f"({param_str}) => {{}}"
        return f"({param_str}) => {body}"

    # Build function keyword
    keyword = ""
    if is_async or func_type == "async":
        keyword = "async "

    if is_generator or func_type == "generator":
        keyword += "function* "
    elif func_type == "async_generator":
        keyword = "async function* "
    else:
        keyword += "function "

    # Build function source
    if not body:
        body = ""

    # Check if body is already wrapped in braces
    if body and not body.strip().startswith("{"):
        body = f"{{ {body} }}"
    elif not body:
        body = "{}"

    return f"{keyword}{name}({param_str}) {body}".strip()
