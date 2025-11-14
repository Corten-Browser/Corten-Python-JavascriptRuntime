"""Module loader - loads module source from file system."""

import os
from pathlib import Path
from typing import Optional
from components.module_system.src.module import Module
from components.module_system.src.module_status import ModuleStatus


class ModuleLoadError(Exception):
    """Raised when module cannot be loaded."""
    pass


class ModuleLoader:
    """
    Loads module source code from file system.

    Responsibilities:
    - Load module source from file path
    - Normalize module URLs
    - Resolve relative paths
    - Validate module files exist
    - Error handling for missing modules
    """

    def __init__(self, base_url: Optional[str] = None):
        """
        Initialize module loader.

        Args:
            base_url: Base directory for resolving relative URLs (default: cwd)
        """
        self.base_url = base_url or os.getcwd()

    def load(self, url: str, referrer: Optional[str] = None) -> Module:
        """
        Load module from URL/path.

        Args:
            url: Module specifier (e.g., './math.js', '/app/utils.js')
            referrer: URL of module making the import (for relative resolution)

        Returns:
            Module object with source loaded

        Raises:
            ModuleLoadError: If module cannot be loaded

        Examples:
            loader.load('./math.js', referrer='/app/main.js')
            # Resolves to: /app/math.js

            loader.load('../utils.js', referrer='/app/src/main.js')
            # Resolves to: /app/utils.js
        """
        # Resolve URL to absolute path
        resolved_url = self.resolve_url(url, referrer)

        # Normalize URL (remove .., ./, etc.)
        normalized_url = self.normalize_url(resolved_url)

        # Load source code
        source = self.load_source(normalized_url)

        # Create module object
        module = Module(url=normalized_url, source=source)

        return module

    def resolve_url(self, url: str, referrer: Optional[str] = None) -> str:
        """
        Resolve module URL to absolute path.

        Args:
            url: Module specifier
            referrer: URL of importing module

        Returns:
            Absolute file path

        Resolution rules:
        - './' or '../' - Relative to referrer directory
        - '/' - Absolute path
        - No prefix - Relative to base_url

        Examples:
            resolve_url('./math.js', '/app/main.js') → '/app/math.js'
            resolve_url('../utils.js', '/app/src/main.js') → '/app/utils.js'
            resolve_url('/lib/core.js', '/app/main.js') → '/lib/core.js'
        """
        # Handle absolute paths
        if url.startswith('/'):
            return url

        # Handle relative paths
        if url.startswith('./') or url.startswith('../'):
            if referrer is None:
                # Resolve relative to base_url
                base_dir = self.base_url
            else:
                # Resolve relative to referrer's directory
                base_dir = os.path.dirname(referrer)

            # Join paths and normalize
            resolved = os.path.join(base_dir, url)
            return self.normalize_url(resolved)

        # Handle bare specifiers (future: node_modules resolution)
        # For now, treat as relative to base_url
        return self.normalize_url(os.path.join(self.base_url, url))

    def normalize_url(self, url: str) -> str:
        """
        Normalize URL path (resolve .., ./, symlinks).

        Args:
            url: File path

        Returns:
            Normalized absolute path

        Examples:
            normalize_url('/app/./math.js') → '/app/math.js'
            normalize_url('/app/src/../math.js') → '/app/math.js'
        """
        # Use Path for normalization
        path = Path(url)

        # Resolve to absolute path, resolving .. and .
        normalized = path.resolve()

        return str(normalized)

    def load_source(self, url: str) -> str:
        """
        Load module source code from file.

        Args:
            url: Absolute file path

        Returns:
            Module source code

        Raises:
            ModuleLoadError: If file doesn't exist or can't be read
        """
        try:
            with open(url, 'r', encoding='utf-8') as f:
                source = f.read()
            return source
        except FileNotFoundError:
            raise ModuleLoadError(f"Cannot find module: {url}")
        except IOError as e:
            raise ModuleLoadError(f"Cannot read module: {url}: {e}")
        except UnicodeDecodeError as e:
            raise ModuleLoadError(f"Invalid UTF-8 in module: {url}: {e}")
