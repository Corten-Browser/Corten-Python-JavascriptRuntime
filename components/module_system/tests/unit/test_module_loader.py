"""Unit tests for ModuleLoader (Phase 2.7.2)."""

import pytest
import os
import tempfile
from pathlib import Path
from components.module_system.src import ModuleLoader, ModuleLoadError, Module, ModuleStatus


class TestModuleLoaderBasics:
    """Test basic module loading functionality."""

    def test_load_simple_module(self, tmp_path):
        """Test loading a simple module file."""
        # Create test module
        module_path = tmp_path / "math.js"
        module_path.write_text("export const add = (a, b) => a + b;")

        # Load module
        loader = ModuleLoader(base_url=str(tmp_path))
        module = loader.load("./math.js")

        # Verify
        assert isinstance(module, Module)
        assert module.status == ModuleStatus.UNLINKED
        assert "export const add" in module.source
        assert str(tmp_path / "math.js") in module.url

    def test_load_module_with_absolute_path(self, tmp_path):
        """Test loading module with absolute path."""
        module_path = tmp_path / "test.js"
        module_path.write_text("export default 42;")

        loader = ModuleLoader()
        module = loader.load(str(module_path))

        assert module.source == "export default 42;"

    def test_load_nonexistent_module_raises_error(self):
        """Test that loading nonexistent module raises ModuleLoadError."""
        loader = ModuleLoader()

        with pytest.raises(ModuleLoadError, match="Cannot find module"):
            loader.load("/nonexistent/module.js")

    def test_module_initial_state(self, tmp_path):
        """Test that newly loaded module has correct initial state."""
        module_path = tmp_path / "test.js"
        module_path.write_text("export const x = 1;")

        loader = ModuleLoader(base_url=str(tmp_path))
        module = loader.load("./test.js")

        assert module.status == ModuleStatus.UNLINKED
        assert module.ast is None
        assert module.bytecode is None
        assert module.namespace == {}
        assert module.imports == []
        assert module.exports == []
        assert module.dependencies == []
        assert module.environment == {}
        assert module.error is None

    def test_load_empty_module(self, tmp_path):
        """Test loading an empty module file."""
        module_path = tmp_path / "empty.js"
        module_path.write_text("")

        loader = ModuleLoader(base_url=str(tmp_path))
        module = loader.load("./empty.js")

        assert module.source == ""
        assert module.status == ModuleStatus.UNLINKED


class TestURLResolution:
    """Test URL resolution logic."""

    def test_resolve_relative_to_referrer(self, tmp_path):
        """Test resolving relative URL to referrer."""
        loader = ModuleLoader(base_url=str(tmp_path))

        referrer = str(tmp_path / "src" / "main.js")
        result = loader.resolve_url("./utils.js", referrer)

        expected = str(tmp_path / "src" / "utils.js")
        assert result == expected

    def test_resolve_parent_directory(self, tmp_path):
        """Test resolving ../ path."""
        loader = ModuleLoader(base_url=str(tmp_path))

        referrer = str(tmp_path / "src" / "components" / "app.js")
        result = loader.resolve_url("../utils.js", referrer)

        expected = str(tmp_path / "src" / "utils.js")
        assert result == expected

    def test_resolve_absolute_path(self):
        """Test resolving absolute path."""
        loader = ModuleLoader()

        result = loader.resolve_url("/lib/core.js", referrer="/app/main.js")

        assert result == "/lib/core.js"

    def test_resolve_bare_specifier_to_base_url(self, tmp_path):
        """Test resolving bare specifier (no ./ or /)."""
        loader = ModuleLoader(base_url=str(tmp_path))

        result = loader.resolve_url("utils.js")

        expected = str(tmp_path / "utils.js")
        assert result == expected

    def test_resolve_relative_without_referrer(self, tmp_path):
        """Test resolving relative path without referrer uses base_url."""
        loader = ModuleLoader(base_url=str(tmp_path))

        result = loader.resolve_url("./test.js")

        expected = str(tmp_path / "test.js")
        assert result == expected

    def test_resolve_deeply_nested_parent_directories(self, tmp_path):
        """Test resolving multiple ../ in path."""
        loader = ModuleLoader(base_url=str(tmp_path))

        referrer = str(tmp_path / "a" / "b" / "c" / "d" / "main.js")
        result = loader.resolve_url("../../utils.js", referrer)

        expected = str(tmp_path / "a" / "b" / "utils.js")
        assert result == expected


class TestURLNormalization:
    """Test URL normalization."""

    def test_normalize_removes_dot_slash(self, tmp_path):
        """Test normalization removes ./"""
        loader = ModuleLoader(base_url=str(tmp_path))

        url = str(tmp_path / "src" / "." / "main.js")
        result = loader.normalize_url(url)

        expected = str(tmp_path / "src" / "main.js")
        assert result == expected

    def test_normalize_resolves_parent_directory(self, tmp_path):
        """Test normalization resolves ../"""
        loader = ModuleLoader(base_url=str(tmp_path))

        url = str(tmp_path / "src" / "components" / ".." / "utils.js")
        result = loader.normalize_url(url)

        expected = str(tmp_path / "src" / "utils.js")
        assert result == expected

    def test_normalize_handles_multiple_slashes(self, tmp_path):
        """Test normalization handles multiple slashes."""
        loader = ModuleLoader(base_url=str(tmp_path))

        url = str(tmp_path / "src" / "." / "." / "main.js")
        result = loader.normalize_url(url)

        expected = str(tmp_path / "src" / "main.js")
        assert result == expected


class TestCompleteLoadingFlow:
    """Test complete loading workflow."""

    def test_load_resolves_and_normalizes(self, tmp_path):
        """Test that load() combines resolution and normalization."""
        # Create modules
        src_dir = tmp_path / "src"
        src_dir.mkdir()

        main_js = src_dir / "main.js"
        main_js.write_text("import { x } from './utils.js';")

        utils_js = src_dir / "utils.js"
        utils_js.write_text("export const x = 42;")

        # Load with relative path
        loader = ModuleLoader(base_url=str(tmp_path))
        module = loader.load("./utils.js", referrer=str(main_js))

        # Should resolve to src/utils.js
        assert "utils.js" in module.url
        assert module.source == "export const x = 42;"

    def test_load_multiple_modules_same_directory(self, tmp_path):
        """Test loading multiple modules from same directory."""
        # Create modules
        math_js = tmp_path / "math.js"
        math_js.write_text("export const add = (a, b) => a + b;")

        utils_js = tmp_path / "utils.js"
        utils_js.write_text("export const log = console.log;")

        loader = ModuleLoader(base_url=str(tmp_path))

        # Load both
        math_module = loader.load("./math.js")
        utils_module = loader.load("./utils.js")

        assert "add" in math_module.source
        assert "log" in utils_module.source

    def test_load_with_complex_relative_path(self, tmp_path):
        """Test loading with complex relative path involving ../"""
        # Create directory structure
        (tmp_path / "src" / "components").mkdir(parents=True)
        (tmp_path / "src" / "utils").mkdir()

        app_js = tmp_path / "src" / "components" / "app.js"
        app_js.write_text("import { helper } from '../utils/helper.js';")

        helper_js = tmp_path / "src" / "utils" / "helper.js"
        helper_js.write_text("export const helper = () => {};")

        loader = ModuleLoader(base_url=str(tmp_path))
        module = loader.load("../utils/helper.js", referrer=str(app_js))

        assert "helper.js" in module.url
        assert "export const helper" in module.source


class TestErrorHandling:
    """Test error handling for various failure cases."""

    def test_load_missing_file_error_message(self, tmp_path):
        """Test error message for missing file."""
        loader = ModuleLoader(base_url=str(tmp_path))

        with pytest.raises(ModuleLoadError) as exc_info:
            loader.load("./missing.js")

        assert "Cannot find module" in str(exc_info.value)
        assert "missing.js" in str(exc_info.value)

    def test_load_invalid_utf8_raises_error(self, tmp_path):
        """Test that invalid UTF-8 raises ModuleLoadError."""
        # Create file with invalid UTF-8
        bad_file = tmp_path / "bad.js"
        bad_file.write_bytes(b'\x80\x81\x82')

        loader = ModuleLoader(base_url=str(tmp_path))

        with pytest.raises(ModuleLoadError, match="Invalid UTF-8"):
            loader.load("./bad.js")

    def test_load_directory_raises_error(self, tmp_path):
        """Test that trying to load a directory raises error."""
        # Create a directory
        dir_path = tmp_path / "mydir"
        dir_path.mkdir()

        loader = ModuleLoader(base_url=str(tmp_path))

        with pytest.raises(ModuleLoadError):
            loader.load("./mydir")


class TestModuleRepresentation:
    """Test Module class representation and attributes."""

    def test_module_repr(self, tmp_path):
        """Test Module __repr__ method."""
        module_path = tmp_path / "test.js"
        module_path.write_text("export const x = 1;")

        loader = ModuleLoader(base_url=str(tmp_path))
        module = loader.load("./test.js")

        repr_str = repr(module)
        assert "Module(" in repr_str
        assert "test.js" in repr_str
        assert "UNLINKED" in repr_str

    def test_module_url_is_absolute(self, tmp_path):
        """Test that module URL is always absolute after loading."""
        module_path = tmp_path / "test.js"
        module_path.write_text("export const x = 1;")

        loader = ModuleLoader(base_url=str(tmp_path))
        module = loader.load("./test.js")

        # URL should be absolute (starts with /)
        assert os.path.isabs(module.url)
        assert module.url == str(tmp_path / "test.js")
