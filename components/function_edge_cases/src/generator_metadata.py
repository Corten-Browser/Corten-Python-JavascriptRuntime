"""
Generator function metadata implementation (FR-ES24-B-046)

Generator function edge cases:
- function* name() {} has name "name"
- Generator.prototype.constructor is GeneratorFunction
- toString shows "function*"
- Length calculated same as normal functions
- Async generators have AsyncGeneratorFunction constructor
"""

from typing import Dict, Any
from dataclasses import dataclass


@dataclass
class GeneratorFunctionMetadata:
    """Metadata for generator functions"""
    is_generator: bool
    generator_kind: str  # "sync" or "async"
    prototype_constructor: str


def get_generator_metadata(function: Dict[str, Any]) -> Dict[str, Any]:
    """
    Get metadata for a generator function.

    Args:
        function: Function object

    Returns:
        Dictionary with generator metadata

    Raises:
        TypeError: If function is not a generator

    Examples:
        >>> func = {"type": "generator", "name": "gen"}
        >>> result = get_generator_metadata(func)
        >>> result["is_generator"]
        True
    """
    func_type = function.get("type", "function")

    # Verify it's a generator
    if func_type not in ("generator", "async_generator"):
        raise TypeError("Not a generator function")

    # Determine generator kind
    if func_type == "async_generator":
        kind = "async"
        constructor = "AsyncGeneratorFunction"
    else:
        kind = "sync"
        constructor = "GeneratorFunction"

    # Get name (same as normal functions)
    name = function.get("name", "")

    # Get source for toString
    source = function.get("source", "")
    if not source:
        source = _reconstruct_generator_source(function)

    # Calculate length (same as normal functions)
    length = _calculate_generator_length(function)

    return {
        "is_generator": True,
        "generator_kind": kind,
        "prototype_constructor": constructor,
        "name": name,
        "to_string": source,
        "length": length,
        "instances_have_prototype": False  # Generator instances don't have prototype
    }


def _reconstruct_generator_source(function: Dict[str, Any]) -> str:
    """
    Reconstruct generator function source code.

    Args:
        function: Generator function object

    Returns:
        Reconstructed source
    """
    func_type = function.get("type", "generator")
    name = function.get("name", "")
    params = function.get("params", [])
    body = function.get("body", "yield 1;")

    # Format parameters
    if isinstance(params, list) and params:
        if isinstance(params[0], dict):
            param_names = [p.get("name", "") for p in params]
        else:
            param_names = params
        param_str = ", ".join(param_names)
    else:
        param_str = ""

    # Build source based on type
    if func_type == "async_generator":
        keyword = "async function* "
    else:
        keyword = "function* "

    # Format body
    if not body.strip().startswith("{"):
        body = f"{{ {body} }}"

    return f"{keyword}{name}({param_str}) {body}".strip()


def _calculate_generator_length(function: Dict[str, Any]) -> int:
    """
    Calculate generator function length.

    Generator functions follow same length rules as normal functions:
    - Count parameters until first default or rest parameter

    Args:
        function: Generator function object

    Returns:
        Length value
    """
    params = function.get("params", [])

    if not params:
        return 0

    count = 0
    for param in params:
        if isinstance(param, dict):
            param_type = param.get("type", "required")

            # Stop at default or rest parameter
            if param_type in ("default", "rest"):
                break

            count += 1
        else:
            # Simple string parameter
            count += 1

    return count


def is_generator_function(function: Dict[str, Any]) -> bool:
    """
    Check if a function is a generator.

    Args:
        function: Function object

    Returns:
        True if generator function
    """
    return function.get("type") in ("generator", "async_generator")


def is_async_generator_function(function: Dict[str, Any]) -> bool:
    """
    Check if a function is an async generator.

    Args:
        function: Function object

    Returns:
        True if async generator function
    """
    return function.get("type") == "async_generator"
