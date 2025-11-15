"""
Reflect API implementation for JavaScript meta-programming.

Provides all 13 Reflect methods that mirror Proxy traps.
Per ECMAScript 2024 specification.
"""

from typing import Any
from components.value_system.src import Value


class Reflect:
    """
    Reflect object with static methods for meta-programming operations.

    All methods mirror corresponding Proxy traps and provide default behaviors.
    Per ECMAScript 2024: 28.1 The Reflect Object
    """

    @staticmethod
    def get(target: Any, prop: str, receiver: Any = None) -> Value:
        """
        Get property value from target object.

        Per ECMAScript 2024: 28.1.6 Reflect.get

        Args:
            target: Object to get property from
            prop: Property name
            receiver: Optional receiver (defaults to target)

        Returns:
            Property value

        Raises:
            TypeError: If target is not an object
        """
        if not _is_object(target):
            raise TypeError("Reflect.get target must be an object")

        if receiver is None:
            receiver = target

        return target.get_property(prop)

    @staticmethod
    def set(target: Any, prop: str, value: Value, receiver: Any = None) -> bool:
        """
        Set property value on target object.

        Per ECMAScript 2024: 28.1.13 Reflect.set

        Args:
            target: Object to set property on
            prop: Property name
            value: Value to set
            receiver: Optional receiver (defaults to target)

        Returns:
            True if property was set successfully

        Raises:
            TypeError: If target is not an object
        """
        if not _is_object(target):
            raise TypeError("Reflect.set target must be an object")

        if receiver is None:
            receiver = target

        target.set_property(prop, value)
        return True

    @staticmethod
    def has(target: Any, prop: str) -> bool:
        """
        Check if target has property.

        Per ECMAScript 2024: 28.1.7 Reflect.has

        Args:
            target: Object to check
            prop: Property name

        Returns:
            True if property exists

        Raises:
            TypeError: If target is not an object
        """
        if not _is_object(target):
            raise TypeError("Reflect.has target must be an object")

        return hasattr(target, "_properties") and prop in target._properties

    @staticmethod
    def deleteProperty(target: Any, prop: str) -> bool:
        """
        Delete property from target object.

        Per ECMAScript 2024: 28.1.4 Reflect.deleteProperty

        Args:
            target: Object to delete property from
            prop: Property name

        Returns:
            True if property was deleted or doesn't exist

        Raises:
            TypeError: If target is not an object
        """
        if not _is_object(target):
            raise TypeError("Reflect.deleteProperty target must be an object")

        if hasattr(target, "_properties") and prop in target._properties:
            del target._properties[prop]

        return True

    @staticmethod
    def getOwnPropertyDescriptor(target: Any, prop: str) -> Any:
        """
        Get own property descriptor.

        Per ECMAScript 2024: 28.1.5 Reflect.getOwnPropertyDescriptor

        Args:
            target: Object to get descriptor from
            prop: Property name

        Returns:
            Property descriptor dict or None

        Raises:
            TypeError: If target is not an object
        """
        if not _is_object(target):
            raise TypeError("Reflect.getOwnPropertyDescriptor target must be an object")

        if hasattr(target, "_properties") and prop in target._properties:
            return target._properties[prop]

        return None

    @staticmethod
    def defineProperty(target: Any, prop: str, descriptor: dict) -> bool:
        """
        Define property on target object.

        Per ECMAScript 2024: 28.1.3 Reflect.defineProperty

        Args:
            target: Object to define property on
            prop: Property name
            descriptor: Property descriptor

        Returns:
            True if property was defined

        Raises:
            TypeError: If target is not an object
        """
        if not _is_object(target):
            raise TypeError("Reflect.defineProperty target must be an object")

        if not hasattr(target, "_properties"):
            target._properties = {}

        target._properties[prop] = descriptor
        return True

    @staticmethod
    def ownKeys(target: Any) -> list:
        """
        Get array of target's own property keys.

        Per ECMAScript 2024: 28.1.11 Reflect.ownKeys

        Args:
            target: Object to get keys from

        Returns:
            List of property keys

        Raises:
            TypeError: If target is not an object
        """
        if not _is_object(target):
            raise TypeError("Reflect.ownKeys target must be an object")

        if hasattr(target, "_properties"):
            return list(target._properties.keys())

        return []

    @staticmethod
    def getPrototypeOf(target: Any) -> Any:
        """
        Get prototype of target object.

        Per ECMAScript 2024: 28.1.8 Reflect.getPrototypeOf

        Args:
            target: Object to get prototype from

        Returns:
            Prototype object or None

        Raises:
            TypeError: If target is not an object
        """
        if not _is_object(target):
            raise TypeError("Reflect.getPrototypeOf target must be an object")

        return getattr(target, "_prototype", None)

    @staticmethod
    def setPrototypeOf(target: Any, prototype: Any) -> bool:
        """
        Set prototype of target object.

        Per ECMAScript 2024: 28.1.14 Reflect.setPrototypeOf

        Args:
            target: Object to set prototype on
            prototype: New prototype object or None

        Returns:
            True if prototype was set

        Raises:
            TypeError: If target is not an object
        """
        if not _is_object(target):
            raise TypeError("Reflect.setPrototypeOf target must be an object")

        target._prototype = prototype
        return True

    @staticmethod
    def isExtensible(target: Any) -> bool:
        """
        Check if target is extensible.

        Per ECMAScript 2024: 28.1.9 Reflect.isExtensible

        Args:
            target: Object to check

        Returns:
            True if target is extensible

        Raises:
            TypeError: If target is not an object
        """
        if not _is_object(target):
            raise TypeError("Reflect.isExtensible target must be an object")

        return getattr(target, "_extensible", True)

    @staticmethod
    def preventExtensions(target: Any) -> bool:
        """
        Prevent extensions on target object.

        Per ECMAScript 2024: 28.1.12 Reflect.preventExtensions

        Args:
            target: Object to make non-extensible

        Returns:
            True if extensions were prevented

        Raises:
            TypeError: If target is not an object
        """
        if not _is_object(target):
            raise TypeError("Reflect.preventExtensions target must be an object")

        target._extensible = False
        return True

    @staticmethod
    def apply(target: Any, this_arg: Any, args: list) -> Any:
        """
        Call function with given 'this' and arguments.

        Per ECMAScript 2024: 28.1.1 Reflect.apply

        Args:
            target: Function to call
            this_arg: 'this' binding for call
            args: Argument list

        Returns:
            Result of function call

        Raises:
            TypeError: If target is not callable
        """
        if not callable(target):
            raise TypeError("Reflect.apply target must be callable")

        return target(*args)

    @staticmethod
    def construct(target: Any, args: list, new_target: Any = None) -> Any:
        """
        Construct new object with constructor.

        Per ECMAScript 2024: 28.1.2 Reflect.construct

        Args:
            target: Constructor function
            args: Argument list for constructor
            new_target: Optional constructor that was originally called

        Returns:
            Newly constructed object

        Raises:
            TypeError: If target is not a constructor
        """
        if new_target is None:
            new_target = target

        if not callable(target):
            raise TypeError("Reflect.construct target must be constructor")

        # Simplified construction (real implementation would use proper new semantics)
        result = target(*args)

        if not _is_object(result):
            raise TypeError("Constructor must return an object")

        return result


def _is_object(value: Any) -> bool:
    """Check if value is an object."""
    from components.object_runtime.src import JSObject, JSFunction
    return isinstance(value, (JSObject, JSFunction))
