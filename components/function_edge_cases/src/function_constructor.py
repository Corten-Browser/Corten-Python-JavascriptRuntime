"""
Function constructor implementation (FR-ES24-B-045)

Dynamic function creation with edge cases:
- Function(arg1, arg2, ..., argN, body)
- Function(body) for no parameters
- Created in global scope (not lexical)
- Strict mode detection from body
- Syntax validation
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import re


@dataclass
class FunctionConstructorOptions:
    """Options for Function constructor"""
    parameters: List[str]
    body: str
    strict: bool = False


# Reserved words in strict mode
STRICT_RESERVED_WORDS = {
    "implements", "interface", "let", "package", "private",
    "protected", "public", "static", "yield", "eval", "arguments"
}


def create_dynamic_function(options: FunctionConstructorOptions) -> Dict[str, Any]:
    """
    Create a function using the Function constructor.

    Args:
        options: Constructor options (parameters and body)

    Returns:
        Dictionary with function object and parsed parameters

    Raises:
        SyntaxError: If function code is invalid

    Examples:
        >>> options = FunctionConstructorOptions(parameters=["a", "b"], body="return a + b")
        >>> result = create_dynamic_function(options)
        >>> result["function"]["type"]
        'function'
    """
    # Detect strict mode from body
    is_strict = options.strict or _has_use_strict(options.body)

    # Validate and parse parameters
    params = _parse_parameters(options.parameters, is_strict)

    # Validate body syntax
    _validate_body_syntax(options.body)

    # Create function object
    function = {
        "type": "function",
        "name": "anonymous",
        "params": [{"name": p, "type": "required"} for p in params],
        "body": options.body,
        "strict": is_strict,
        "scope": "global",  # Functions created with constructor have global scope
        "length": len(params)
    }

    return {
        "function": function,
        "parsed_params": params
    }


def _has_use_strict(body: str) -> bool:
    """
    Check if function body has "use strict" directive.

    Args:
        body: Function body code

    Returns:
        True if strict mode directive found
    """
    # Check for "use strict" at the beginning of body
    stripped = body.strip()
    return (
        stripped.startswith('"use strict"') or
        stripped.startswith("'use strict'")
    )


def _parse_parameters(
    parameters: List[str],
    is_strict: bool
) -> List[str]:
    """
    Parse and validate parameter list.

    Args:
        parameters: List of parameter strings
        is_strict: Whether in strict mode

    Returns:
        List of validated parameter names

    Raises:
        SyntaxError: If parameters are invalid
    """
    parsed = []
    seen = set()

    for param in parameters:
        param = param.strip()

        # Handle default parameters (a = 10)
        if "=" in param:
            param_name = param.split("=")[0].strip()
        # Handle rest parameters (...rest)
        elif param.startswith("..."):
            param_name = param[3:].strip()
        else:
            param_name = param

        # Validate parameter name
        if not _is_valid_identifier(param_name):
            raise SyntaxError(f"Invalid parameter name: {param_name}")

        # Check for duplicates in strict mode
        if is_strict and param_name in seen:
            raise SyntaxError(f"Duplicate parameter name: {param_name}")

        # Check for reserved words in strict mode
        if is_strict and param_name in STRICT_RESERVED_WORDS:
            raise SyntaxError(f"Reserved word used as parameter: {param_name}")

        seen.add(param_name)
        parsed.append(param)

    return parsed


def _is_valid_identifier(name: str) -> bool:
    """
    Check if a name is a valid JavaScript identifier.

    Args:
        name: Identifier name

    Returns:
        True if valid identifier
    """
    if not name:
        return False

    # Must start with letter, underscore, or dollar sign
    if not re.match(r'^[a-zA-Z_$]', name):
        return False

    # Rest can be letters, digits, underscore, or dollar sign
    if not re.match(r'^[a-zA-Z_$][a-zA-Z0-9_$]*$', name):
        return False

    return True


def _validate_body_syntax(body: str) -> None:
    """
    Validate function body syntax.

    Args:
        body: Function body code

    Raises:
        SyntaxError: If body has syntax errors
    """
    # Basic syntax validation
    # Check for unmatched braces
    brace_count = 0
    for char in body:
        if char == '{':
            brace_count += 1
        elif char == '}':
            brace_count -= 1
        if brace_count < 0:
            raise SyntaxError("Unexpected closing brace")

    if brace_count > 0:
        raise SyntaxError("Unexpected end of input - unclosed brace")

    # Check for incomplete return statement
    if body.rstrip().endswith("return {") and brace_count > 0:
        raise SyntaxError("Unexpected end of input")
