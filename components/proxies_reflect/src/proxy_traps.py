"""
Proxy trap implementations with invariant enforcement.

Implements all 13 proxy traps per ECMAScript 2024 specification,
with strict invariant checking to maintain JavaScript semantics.
"""

from typing import Any
from components.value_system.src import Value, IsUndefined
from components.object_runtime.src import JSObject


def proxy_get(proxy: "Proxy", prop: str, receiver: Any = None) -> Value:
    """
    [[Get]] trap for Proxy.

    Intercepts property reads with handler.get trap.

    Per ECMAScript 2024: 10.5.8 [[Get]] (P, Receiver)

    Args:
        proxy: Proxy object
        prop: Property name to get
        receiver: Receiver object (defaults to proxy)

    Returns:
        Property value from trap or target

    Raises:
        TypeError: On revoked proxy or invariant violation

    Invariants:
        - Non-configurable, non-writable property must return same value
        - Non-configurable accessor with undefined get must return undefined
    """
    from proxy import Proxy

    # Check if proxy is revoked
    if proxy._revoked:
        raise TypeError("Cannot perform 'get' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    # Default receiver to proxy if not provided
    if receiver is None:
        receiver = proxy

    # Check if handler has get trap
    trap = None
    if hasattr(handler, "_get_trap"):
        trap = handler._get_trap

    # If no trap, return target's value
    if trap is None:
        return target.get_property(prop)

    # Call the trap
    trap_result = trap(target, prop, receiver)

    # Invariant checks
    # Per ECMAScript 2024: 10.5.8 step 9
    # Check if target property exists and get descriptor
    if hasattr(target, "_properties") and prop in target._properties:
        prop_desc = target._properties[prop]

        # If property descriptor is a dict (simulating descriptor)
        if isinstance(prop_desc, dict):
            # Check for data property descriptor
            if "value" in prop_desc:
                # Non-writable, non-configurable property
                if (
                    not prop_desc.get("writable", True)
                    and not prop_desc.get("configurable", True)
                ):
                    # Must return same value
                    target_value = prop_desc["value"]
                    # Compare values (simplified - in real impl, use SameValue)
                    if not _same_value(trap_result, target_value):
                        raise TypeError(
                            "Cannot return different value for non-writable, "
                            "non-configurable property"
                        )

            # Check for accessor property descriptor
            elif "get" in prop_desc:
                # Non-configurable accessor with undefined getter
                if prop_desc.get("get") is None and not prop_desc.get(
                    "configurable", True
                ):
                    # Must return undefined
                    if not IsUndefined(trap_result):
                        raise TypeError(
                            "Must return undefined for non-configurable accessor "
                            "with undefined getter"
                        )

    return trap_result


def proxy_set(proxy: "Proxy", prop: str, value: Value, receiver: Any = None) -> bool:
    """
    [[Set]] trap for Proxy.

    Intercepts property writes with handler.set trap.

    Per ECMAScript 2024: 10.5.9 [[Set]] (P, V, Receiver)

    Args:
        proxy: Proxy object
        prop: Property name to set
        value: Value to set
        receiver: Receiver object (defaults to proxy)

    Returns:
        True if property was set successfully, False otherwise

    Raises:
        TypeError: On revoked proxy or invariant violation

    Invariants:
        - Cannot set non-configurable, non-writable property
        - Cannot set non-configurable accessor without setter
    """
    from proxy import Proxy

    # Check if proxy is revoked
    if proxy._revoked:
        raise TypeError("Cannot perform 'set' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    # Default receiver to proxy if not provided
    if receiver is None:
        receiver = proxy

    # Check if handler has set trap
    trap = None
    if hasattr(handler, "_set_trap"):
        trap = handler._set_trap

    # If no trap, set on target directly
    if trap is None:
        target.set_property(prop, value)
        return True

    # Call the trap
    trap_result = trap(target, prop, value, receiver)

    # Invariant checks (only if trap returned true)
    if trap_result:
        # Per ECMAScript 2024: 10.5.9 step 10
        if hasattr(target, "_properties") and prop in target._properties:
            prop_desc = target._properties[prop]

            if isinstance(prop_desc, dict):
                # Check for data property descriptor
                if "value" in prop_desc:
                    # Non-writable, non-configurable property
                    if (
                        not prop_desc.get("writable", True)
                        and not prop_desc.get("configurable", True)
                    ):
                        # Cannot set
                        raise TypeError(
                            "Cannot set non-writable, non-configurable property"
                        )

                # Check for accessor property descriptor
                elif "get" in prop_desc or "set" in prop_desc:
                    # Non-configurable accessor without setter
                    if prop_desc.get("set") is None and not prop_desc.get(
                        "configurable", True
                    ):
                        raise TypeError(
                            "Cannot set non-configurable accessor without setter"
                        )

    return bool(trap_result)


def proxy_has(proxy: "Proxy", prop: str) -> bool:
    """
    [[HasProperty]] trap for Proxy.

    Intercepts 'in' operator with handler.has trap.

    Per ECMAScript 2024: 10.5.7 [[HasProperty]] (P)

    Args:
        proxy: Proxy object
        prop: Property name to check

    Returns:
        True if property exists, False otherwise

    Raises:
        TypeError: On revoked proxy or invariant violation

    Invariants:
        - Non-configurable property cannot be reported as non-existent
        - Property of non-extensible target cannot be reported as non-existent
    """
    from proxy import Proxy

    # Check if proxy is revoked
    if proxy._revoked:
        raise TypeError("Cannot perform 'has' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    # Check if handler has 'has' trap
    trap = None
    if hasattr(handler, "_has_trap"):
        trap = handler._has_trap

    # If no trap, check target directly
    if trap is None:
        return hasattr(target, "_properties") and prop in target._properties

    # Call the trap
    trap_result = trap(target, prop)

    # Invariant checks
    # Per ECMAScript 2024: 10.5.7 step 8-9
    if hasattr(target, "_properties") and prop in target._properties:
        prop_desc = target._properties[prop]

        if isinstance(prop_desc, dict):
            # Non-configurable property cannot be reported as non-existent
            if not prop_desc.get("configurable", True):
                if not trap_result:
                    raise TypeError(
                        "Cannot report non-configurable property as non-existent"
                    )

    # Check if target is non-extensible
    if hasattr(target, "_extensible") and not target._extensible:
        # If target is non-extensible and has the property,
        # cannot report as non-existent
        if hasattr(target, "_properties") and prop in target._properties:
            if not trap_result:
                raise TypeError(
                    "Cannot report property of non-extensible target as non-existent"
                )

    return bool(trap_result)


def proxy_delete_property(proxy: "Proxy", prop: str) -> bool:
    """
    [[Delete]] trap for Proxy.

    Intercepts delete operator with handler.deleteProperty trap.

    Per ECMAScript 2024: 10.5.10 [[Delete]] (P)

    Args:
        proxy: Proxy object
        prop: Property name to delete

    Returns:
        True if property was deleted or doesn't exist, False if deletion failed

    Raises:
        TypeError: On revoked proxy or invariant violation

    Invariants:
        - Non-configurable property cannot be deleted
    """
    from proxy import Proxy

    # Check if proxy is revoked
    if proxy._revoked:
        raise TypeError("Cannot perform 'deleteProperty' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    # Check if handler has deleteProperty trap
    trap = None
    if hasattr(handler, "_delete_property_trap"):
        trap = handler._delete_property_trap

    # If no trap, delete from target
    if trap is None:
        if hasattr(target, "_properties") and prop in target._properties:
            del target._properties[prop]
            return True
        return True  # Property didn't exist, deletion "succeeds"

    # Call the trap
    trap_result = trap(target, prop)

    # Invariant checks (only if trap returned true)
    if trap_result:
        # Per ECMAScript 2024: 10.5.10 step 8
        if hasattr(target, "_properties") and prop in target._properties:
            prop_desc = target._properties[prop]

            if isinstance(prop_desc, dict):
                # Non-configurable property cannot be deleted
                if not prop_desc.get("configurable", True):
                    raise TypeError("Cannot delete non-configurable property")

    return bool(trap_result)


def proxy_own_keys(proxy: "Proxy") -> list:
    """
    [[OwnPropertyKeys]] trap for Proxy.

    Intercepts Object.keys(), Object.getOwnPropertyNames(), etc.

    Per ECMAScript 2024: 10.5.11 [[OwnPropertyKeys]] ()

    Args:
        proxy: Proxy object

    Returns:
        List of property keys (strings and symbols)

    Raises:
        TypeError: On revoked proxy or invariant violation

    Invariants:
        - Must return array
        - All elements must be string or symbol
        - Must include all non-configurable properties
        - If target non-extensible, must include exactly target's keys
    """
    from proxy import Proxy

    # Check if proxy is revoked
    if proxy._revoked:
        raise TypeError("Cannot perform 'ownKeys' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    # Check if handler has ownKeys trap
    trap = None
    if hasattr(handler, "_own_keys_trap"):
        trap = handler._own_keys_trap

    # If no trap, return target's keys
    if trap is None:
        if hasattr(target, "_properties"):
            return list(target._properties.keys())
        return []

    # Call the trap
    trap_result = trap(target)

    # Invariant: must return list
    if not isinstance(trap_result, list):
        raise TypeError("ownKeys trap must return an array")

    # Invariant: all elements must be string or symbol
    for key in trap_result:
        if not isinstance(key, (str, int)):  # symbols would be here too
            raise TypeError("ownKeys trap result must contain only strings or symbols")

    # Invariant: must include all non-configurable properties
    if hasattr(target, "_properties"):
        for prop_name, prop_desc in target._properties.items():
            if isinstance(prop_desc, dict):
                if not prop_desc.get("configurable", True):
                    # Non-configurable property must be in result
                    if prop_name not in trap_result:
                        raise TypeError(
                            "ownKeys trap result must include all non-configurable properties"
                        )

    # Invariant: if target non-extensible, must match exactly
    if hasattr(target, "_extensible") and not target._extensible:
        target_keys = set(target._properties.keys()) if hasattr(target, "_properties") else set()
        result_keys = set(trap_result)

        if target_keys != result_keys:
            raise TypeError(
                "ownKeys trap result must match target keys for non-extensible target"
            )

    return trap_result


def proxy_get_own_property_descriptor(proxy: "Proxy", prop: str) -> Any:
    """
    [[GetOwnProperty]] trap for Proxy.

    Intercepts Object.getOwnPropertyDescriptor with handler.getOwnPropertyDescriptor trap.

    Args:
        proxy: Proxy object
        prop: Property name

    Returns:
        Property descriptor dict or None

    Raises:
        TypeError: On revoked proxy or invariant violation
    """
    from proxy import Proxy

    if proxy._revoked:
        raise TypeError("Cannot perform 'getOwnPropertyDescriptor' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    trap = None
    if hasattr(handler, "_get_own_property_descriptor_trap"):
        trap = handler._get_own_property_descriptor_trap

    if trap is None:
        if hasattr(target, "_properties") and prop in target._properties:
            return target._properties[prop]
        return None

    trap_result = trap(target, prop)

    # Invariants
    if trap_result is not None and not isinstance(trap_result, dict):
        raise TypeError("getOwnPropertyDescriptor trap must return object or undefined")

    return trap_result


def proxy_define_property(proxy: "Proxy", prop: str, descriptor: dict) -> bool:
    """
    [[DefineOwnProperty]] trap for Proxy.

    Intercepts Object.defineProperty with handler.defineProperty trap.

    Args:
        proxy: Proxy object
        prop: Property name
        descriptor: Property descriptor

    Returns:
        True if property was defined successfully

    Raises:
        TypeError: On revoked proxy or invariant violation
    """
    from proxy import Proxy

    if proxy._revoked:
        raise TypeError("Cannot perform 'defineProperty' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    trap = None
    if hasattr(handler, "_define_property_trap"):
        trap = handler._define_property_trap

    if trap is None:
        if hasattr(target, "_properties"):
            target._properties[prop] = descriptor
            return True
        return False

    trap_result = trap(target, prop, descriptor)

    # Invariant: cannot add property to non-extensible target
    if trap_result:
        if hasattr(target, "_extensible") and not target._extensible:
            if not (hasattr(target, "_properties") and prop in target._properties):
                raise TypeError("Cannot add property to non-extensible target")

    return bool(trap_result)


def proxy_get_prototype_of(proxy: "Proxy") -> Any:
    """
    [[GetPrototypeOf]] trap for Proxy.

    Intercepts Object.getPrototypeOf with handler.getPrototypeOf trap.

    Args:
        proxy: Proxy object

    Returns:
        Prototype object or None

    Raises:
        TypeError: On revoked proxy or invariant violation
    """
    from proxy import Proxy

    if proxy._revoked:
        raise TypeError("Cannot perform 'getPrototypeOf' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    trap = None
    if hasattr(handler, "_get_prototype_of_trap"):
        trap = handler._get_prototype_of_trap

    if trap is None:
        return getattr(target, "_prototype", None)

    trap_result = trap(target)

    # Invariant: if target non-extensible, must return target's prototype
    if hasattr(target, "_extensible") and not target._extensible:
        target_proto = getattr(target, "_prototype", None)
        if trap_result is not target_proto:
            raise TypeError(
                "getPrototypeOf trap must return target's prototype for non-extensible target"
            )

    return trap_result


def proxy_set_prototype_of(proxy: "Proxy", prototype: Any) -> bool:
    """
    [[SetPrototypeOf]] trap for Proxy.

    Intercepts Object.setPrototypeOf with handler.setPrototypeOf trap.

    Args:
        proxy: Proxy object
        prototype: New prototype object or None

    Returns:
        True if prototype was set successfully

    Raises:
        TypeError: On revoked proxy or invariant violation
    """
    from proxy import Proxy

    if proxy._revoked:
        raise TypeError("Cannot perform 'setPrototypeOf' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    trap = None
    if hasattr(handler, "_set_prototype_of_trap"):
        trap = handler._set_prototype_of_trap

    if trap is None:
        target._prototype = prototype
        return True

    trap_result = trap(target, prototype)

    # Invariant: if target non-extensible, cannot change prototype
    if trap_result:
        if hasattr(target, "_extensible") and not target._extensible:
            target_proto = getattr(target, "_prototype", None)
            if prototype is not target_proto:
                raise TypeError("Cannot change prototype of non-extensible target")

    return bool(trap_result)


def proxy_is_extensible(proxy: "Proxy") -> bool:
    """
    [[IsExtensible]] trap for Proxy.

    Intercepts Object.isExtensible with handler.isExtensible trap.

    Args:
        proxy: Proxy object

    Returns:
        True if target is extensible

    Raises:
        TypeError: On revoked proxy or invariant violation
    """
    from proxy import Proxy

    if proxy._revoked:
        raise TypeError("Cannot perform 'isExtensible' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    trap = None
    if hasattr(handler, "_is_extensible_trap"):
        trap = handler._is_extensible_trap

    target_extensible = getattr(target, "_extensible", True)

    if trap is None:
        return target_extensible

    trap_result = trap(target)

    # Invariant: must return same as target's extensibility
    if bool(trap_result) != bool(target_extensible):
        raise TypeError("isExtensible trap result must match target's extensibility")

    return bool(trap_result)


def proxy_prevent_extensions(proxy: "Proxy") -> bool:
    """
    [[PreventExtensions]] trap for Proxy.

    Intercepts Object.preventExtensions with handler.preventExtensions trap.

    Args:
        proxy: Proxy object

    Returns:
        True if extensions were prevented

    Raises:
        TypeError: On revoked proxy or invariant violation
    """
    from proxy import Proxy

    if proxy._revoked:
        raise TypeError("Cannot perform 'preventExtensions' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    trap = None
    if hasattr(handler, "_prevent_extensions_trap"):
        trap = handler._prevent_extensions_trap

    if trap is None:
        target._extensible = False
        return True

    trap_result = trap(target)

    # Invariant: can only return true if target is now non-extensible
    if trap_result:
        target_extensible = getattr(target, "_extensible", True)
        if target_extensible:
            raise TypeError(
                "preventExtensions trap can only return true if target is non-extensible"
            )

    return bool(trap_result)


def proxy_apply(proxy: "Proxy", this_arg: Any, args: list) -> Any:
    """
    [[Call]] trap for Proxy.

    Intercepts function calls with handler.apply trap.

    Args:
        proxy: Proxy object (must wrap callable)
        this_arg: 'this' binding for call
        args: Argument list

    Returns:
        Result of function call

    Raises:
        TypeError: On revoked proxy or if target not callable
    """
    from proxy import Proxy

    if proxy._revoked:
        raise TypeError("Cannot perform 'apply' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    # Check if target is callable
    if not callable(target):
        raise TypeError("Proxy target must be callable for apply trap")

    trap = None
    if hasattr(handler, "_apply_trap"):
        trap = handler._apply_trap

    if trap is None:
        # Call target directly
        return target(*args)

    return trap(target, this_arg, args)


def proxy_construct(proxy: "Proxy", args: list, new_target: Any = None) -> Any:
    """
    [[Construct]] trap for Proxy.

    Intercepts 'new' operator with handler.construct trap.

    Args:
        proxy: Proxy object (must wrap constructor)
        args: Argument list for constructor
        new_target: The constructor that was originally called

    Returns:
        Newly constructed object

    Raises:
        TypeError: On revoked proxy, if target not constructor, or if result not object
    """
    from proxy import Proxy

    if proxy._revoked:
        raise TypeError("Cannot perform 'construct' on a revoked proxy")

    target = proxy._target
    handler = proxy._handler

    if new_target is None:
        new_target = proxy

    trap = None
    if hasattr(handler, "_construct_trap"):
        trap = handler._construct_trap

    if trap is None:
        # Construct with target
        if not hasattr(target, "__call__"):
            raise TypeError("Proxy target must be constructor for construct trap")
        # Simplified construction (real implementation would use proper new semantics)
        return target(*args)

    result = trap(target, args, new_target)

    # Invariant: must return object
    if not _is_object(result):
        raise TypeError("construct trap must return an object")

    return result


def _is_object(value: Any) -> bool:
    """Check if value is an object."""
    from components.object_runtime.src import JSObject, JSFunction
    return isinstance(value, (JSObject, JSFunction))


def _same_value(a: Value, b: Value) -> bool:
    """
    SameValue comparison for invariant checking.

    Simplified version - in real implementation would use proper SameValue.

    Args:
        a: First value
        b: Second value

    Returns:
        True if values are the same
    """
    # For now, simple comparison
    # In full implementation, this would handle all value types properly
    try:
        # Try SMI comparison
        return a.to_smi() == b.to_smi()
    except:
        # For non-SMI values, compare objects
        return a is b
