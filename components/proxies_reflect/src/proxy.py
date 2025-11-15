"""
Proxy implementation for JavaScript meta-programming.

Provides the Proxy class which wraps a target object and allows
interception of fundamental operations through handler traps.

Per ECMAScript 2024 specification.
"""

from typing import Any, Optional
from components.object_runtime.src import JSObject, JSFunction


def _is_object(value: Any) -> bool:
    """
    Check if value is an object (JSObject, JSFunction, Proxy, or callable).

    Args:
        value: Value to check

    Returns:
        True if value is an object, False otherwise
    """
    # Check by class name to avoid circular import
    # Allow JSObject, JSFunction, Proxy (for nested proxies), or any callable
    if isinstance(value, (JSObject, JSFunction)):
        return True
    if type(value).__name__ == 'Proxy':  # Check for Proxy instances
        return True
    if callable(value):
        return True
    return False


class Proxy:
    """
    Proxy object wrapper for meta-programming.

    A Proxy wraps a target object and allows custom behavior
    for fundamental operations via handler trap methods.

    Per ECMAScript 2024: 10.5 Proxy Object Internal Methods

    Args:
        target: Target object to wrap (must be object)
        handler: Handler object with trap methods (must be object)

    Raises:
        TypeError: If target or handler is not an object

    Example:
        >>> handler = JSObject(gc)
        >>> target = JSObject(gc)
        >>> proxy = Proxy(target, handler)
    """

    def __init__(self, target: Any, handler: Any):
        """
        Initialize Proxy with target and handler.

        Args:
            target: Object to wrap
            handler: Object with trap methods

        Raises:
            TypeError: If target or handler is not an object
        """
        # Validate target is an object
        if not _is_object(target):
            raise TypeError("Proxy target must be an object")

        # Validate handler is an object
        if not _is_object(handler):
            raise TypeError("Proxy handler must be an object")

        # Store target and handler
        self._target = target
        self._handler = handler
        self._revoked = False  # For revocable proxies

    @property
    def target(self) -> Any:
        """Get the proxy target (for internal use)."""
        if self._revoked:
            raise TypeError("Cannot perform operation on revoked proxy")
        return self._target

    @property
    def handler(self) -> Any:
        """Get the proxy handler (for internal use)."""
        if self._revoked:
            raise TypeError("Cannot perform operation on revoked proxy")
        return self._handler

    def _revoke(self) -> None:
        """Revoke this proxy (internal use by Proxy.revocable)."""
        self._revoked = True
        self._target = None
        self._handler = None

    @staticmethod
    def revocable(target: Any, handler: Any) -> dict:
        """
        Create a revocable proxy.

        Per ECMAScript 2024: Proxy.revocable(target, handler)

        Args:
            target: Target object to wrap
            handler: Handler object with trap methods

        Returns:
            Dict with 'proxy' and 'revoke' keys:
            {
                'proxy': Proxy object,
                'revoke': Function that revokes the proxy
            }

        Raises:
            TypeError: If target or handler is not an object

        Example:
            >>> result = Proxy.revocable(target, handler)
            >>> proxy = result['proxy']
            >>> revoke = result['revoke']
            >>> # Use proxy...
            >>> revoke()  # Revoke proxy
            >>> # Any further operations on proxy will throw TypeError
        """
        # Create proxy
        proxy = Proxy(target, handler)

        # Create revoke function
        def revoke():
            """Revoke the proxy. Safe to call multiple times."""
            proxy._revoke()

        return {
            'proxy': proxy,
            'revoke': revoke
        }
