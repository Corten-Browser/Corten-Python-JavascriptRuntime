"""
Function length property calculation (FR-ES24-B-043)

Calculates function.length correctly:
- Count parameters before first default parameter
- Exclude rest parameters
- Include destructured parameters (count as 1)
- For bound functions: max(0, original.length - boundArgs.length)
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass


@dataclass
class LengthCalculation:
    """Rules for calculating function.length"""
    count_required: bool = True
    count_optional: bool = True
    stop_at_rest: bool = True
    stop_at_default: bool = True


def calculate_length(
    function: Dict[str, Any],
    calculation: Optional[LengthCalculation] = None
) -> Dict[str, Any]:
    """
    Calculate function.length property.

    Args:
        function: Function object
        calculation: Calculation rules

    Returns:
        Dictionary with length and breakdown

    Examples:
        >>> func = {"params": [{"name": "a", "type": "required"}, {"name": "b", "type": "required"}]}
        >>> result = calculate_length(func)
        >>> result["length"]
        2
    """
    if calculation is None:
        calculation = LengthCalculation()

    func_type = function.get("type", "function")

    # Bound functions have special length calculation
    if func_type == "bound":
        return _calculate_bound_length(function)

    # Normal functions: count parameters
    params = function.get("params", [])

    if not params:
        return {
            "length": 0,
            "breakdown": {
                "required_params": 0,
                "default_params": 0,
                "rest_param": False
            }
        }

    # Count parameters until first default or rest
    count = 0
    required_count = 0
    default_count = 0
    has_rest = False

    for param in params:
        param_type = param.get("type", "required")

        # Rest parameter: stop counting
        if param_type == "rest":
            has_rest = True
            break

        # Default parameter: stop counting (per ES spec)
        if param_type == "default":
            default_count += 1
            if calculation.stop_at_default:
                break
            continue

        # Required or destructured parameter: count it
        if param_type in ("required", "destructured"):
            count += 1
            required_count += 1

    return {
        "length": count,
        "breakdown": {
            "required_params": required_count,
            "default_params": default_count,
            "rest_param": has_rest
        }
    }


def _calculate_bound_length(function: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate length for bound function.

    Bound function length = max(0, target.length - boundArgs.length)

    Args:
        function: Bound function object

    Returns:
        Dictionary with calculated length
    """
    target_function = function.get("target_function")
    bound_args = function.get("bound_args", [])

    # Get original function's length
    if target_function:
        if target_function.get("type") == "bound":
            # Recursively calculate for nested bound functions
            target_result = _calculate_bound_length(target_function)
            original_length = target_result["length"]
        else:
            original_length = target_function.get("length", 0)
    else:
        original_length = function.get("length", 0)

    # Calculate: max(0, original - bound_args)
    bound_args_count = len(bound_args)
    new_length = max(0, original_length - bound_args_count)

    return {
        "length": new_length,
        "breakdown": {
            "original_length": original_length,
            "bound_args_count": bound_args_count
        }
    }


def get_parameter_count(params: List[Dict[str, Any]]) -> int:
    """
    Get the count of parameters for length property.

    This counts parameters until the first default parameter or rest parameter.

    Args:
        params: List of parameter objects

    Returns:
        Number of parameters to count
    """
    count = 0
    for param in params:
        param_type = param.get("type", "required")

        if param_type == "rest":
            break

        if param_type == "default":
            break

        count += 1

    return count
