"""
Private class features for ES2024 compliance.

Provides:
- Private fields (#field)
- Private methods (#method)
- Private getters/setters (#get, #set)
- Static initialization blocks
- Private static fields and methods
- Ergonomic brand checks (#field in obj)
"""

from .private_field_manager import PrivateFieldManager, PrivateField
from .private_method_manager import PrivateMethodManager, PrivateMethod, PrivateAccessor
from .static_initialization import StaticInitializationManager
from .brand_checker import PrivateBrandChecker

__all__ = [
    "PrivateFieldManager",
    "PrivateField",
    "PrivateMethodManager",
    "PrivateMethod",
    "PrivateAccessor",
    "StaticInitializationManager",
    "PrivateBrandChecker",
]
