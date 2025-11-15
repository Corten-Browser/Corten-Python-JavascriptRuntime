"""
object_methods - ES2024 Object static method implementations.

This component implements missing Object static methods for ES2024 compliance:
- Object.fromEntries() - Create object from [key, value] pairs
- Object.entries() - Get [key, value] pairs
- Object.values() - Get property values
- Object.getOwnPropertyDescriptors() - All property descriptors
- Object.setPrototypeOf() with edge cases
- Object.is() - SameValue equality
- Object.assign() with edge cases
- Object[Symbol.iterator] for iteration
"""

__version__ = "0.1.0"
