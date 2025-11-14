"""Module registry - caches loaded modules."""

from typing import Dict, Optional
from components.module_system.src.module import Module


class ModuleRegistry:
    """
    Global registry of loaded modules (singleton pattern).

    Ensures each module is loaded only once (caching).
    Modules are keyed by absolute normalized URL.
    """

    _instance = None

    def __new__(cls):
        """Singleton pattern - only one registry instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.modules = {}
        return cls._instance

    def get(self, url: str) -> Optional[Module]:
        """
        Get module by URL.

        Args:
            url: Absolute normalized module URL

        Returns:
            Module if found, None otherwise
        """
        return self.modules.get(url)

    def register(self, module: Module):
        """
        Register module in registry.

        Args:
            module: Module to register
        """
        self.modules[module.url] = module

    def has(self, url: str) -> bool:
        """Check if module is registered."""
        return url in self.modules

    def clear(self):
        """Clear all registered modules (for testing)."""
        self.modules.clear()

    def get_all(self) -> Dict[str, Module]:
        """Get all registered modules."""
        return self.modules.copy()
