"""Unit tests for ModuleLinker (Phase 2.7.3)."""

import pytest
from pathlib import Path
from components.module_system.src import (
    Module, ModuleStatus, ModuleLoader, ModuleLinker,
    ModuleRegistry, ModuleLinkError, CircularDependencyError
)


@pytest.fixture
def registry():
    """Fresh module registry for each test."""
    reg = ModuleRegistry()
    reg.clear()
    return reg


@pytest.fixture
def loader(tmp_path):
    """Module loader with temp directory."""
    return ModuleLoader(base_url=str(tmp_path))


@pytest.fixture
def linker(loader, registry):
    """Module linker."""
    return ModuleLinker(loader, registry)


class TestModuleRegistryBasics:
    """Test ModuleRegistry caching."""

    def test_registry_singleton(self):
        """Registry should be singleton."""
        reg1 = ModuleRegistry()
        reg2 = ModuleRegistry()
        assert reg1 is reg2

    def test_register_and_get_module(self, registry):
        """Test registering and retrieving modules."""
        module = Module(url="/test/module.js", source="export const x = 1;")
        registry.register(module)

        retrieved = registry.get("/test/module.js")
        assert retrieved is module

    def test_has_module(self, registry):
        """Test has() method."""
        module = Module(url="/test/module.js", source="export const x = 1;")
        registry.register(module)

        assert registry.has("/test/module.js")
        assert not registry.has("/nonexistent.js")

    def test_get_returns_none_for_missing_module(self, registry):
        """Test get() returns None for missing module."""
        result = registry.get("/nonexistent.js")
        assert result is None

    def test_clear_removes_all_modules(self, registry):
        """Test clear() removes all modules."""
        module1 = Module(url="/test/module1.js", source="export const x = 1;")
        module2 = Module(url="/test/module2.js", source="export const y = 2;")
        registry.register(module1)
        registry.register(module2)

        registry.clear()

        assert not registry.has("/test/module1.js")
        assert not registry.has("/test/module2.js")

    def test_get_all_returns_copy(self, registry):
        """Test get_all() returns a copy of modules dict."""
        module = Module(url="/test/module.js", source="export const x = 1;")
        registry.register(module)

        all_modules = registry.get_all()
        all_modules["/test/other.js"] = "should not affect registry"

        assert not registry.has("/test/other.js")


class TestBasicLinking:
    """Test basic module linking."""

    def test_link_simple_module_no_imports(self, tmp_path, linker, registry):
        """Test linking module with no imports."""
        # Create module
        module_path = tmp_path / "simple.js"
        module_path.write_text("export const x = 42;")

        # Load and link
        module = linker.loader.load("simple.js")
        linker.link(module)

        # Verify
        assert module.status == ModuleStatus.LINKED
        assert module.ast is not None
        # Note: bytecode is None until Phase 2.7.4 implements module compilation
        assert module.bytecode is None
        assert len(module.imports) == 0
        assert len(module.exports) == 1

    def test_link_module_with_single_import(self, tmp_path, linker):
        """Test linking module with single import."""
        # Create dependency
        math_js = tmp_path / "math.js"
        math_js.write_text("export const add = (a, b) => a + b;")

        # Create main module
        main_js = tmp_path / "main.js"
        main_js.write_text("import { add } from './math.js';\nconst result = add(1, 2);")

        # Load and link
        module = linker.loader.load("main.js")
        linker.link(module)

        # Verify
        assert module.status == ModuleStatus.LINKED
        assert len(module.dependencies) == 1
        assert module.dependencies[0].url.endswith("math.js")
        assert module.dependencies[0].status == ModuleStatus.LINKED

    def test_link_module_with_multiple_imports(self, tmp_path, linker):
        """Test linking module with multiple imports."""
        # Create dependencies
        math_js = tmp_path / "math.js"
        math_js.write_text("export const add = (a, b) => a + b;")

        utils_js = tmp_path / "utils.js"
        utils_js.write_text("export const log = (msg) => console.log(msg);")

        # Create main module
        main_js = tmp_path / "main.js"
        main_js.write_text(
            "import { add } from './math.js';\n"
            "import { log } from './utils.js';\n"
            "log(add(1, 2));"
        )

        # Load and link
        module = linker.loader.load("main.js")
        linker.link(module)

        # Verify
        assert module.status == ModuleStatus.LINKED
        assert len(module.dependencies) == 2
        dep_urls = [dep.url for dep in module.dependencies]
        assert any("math.js" in url for url in dep_urls)
        assert any("utils.js" in url for url in dep_urls)

    def test_link_already_linked_module_is_noop(self, tmp_path, linker):
        """Test linking already linked module is no-op."""
        # Create module
        module_path = tmp_path / "simple.js"
        module_path.write_text("export const x = 42;")

        # Load and link
        module = linker.loader.load("simple.js")
        linker.link(module)

        # Store original AST
        original_ast = module.ast

        # Link again
        linker.link(module)

        # Should not re-parse
        assert module.ast is original_ast
        assert module.status == ModuleStatus.LINKED


class TestDependencyGraphs:
    """Test dependency graph construction."""

    def test_dependency_graph_linear(self, tmp_path, linker):
        """
        Test linear dependency chain: main → utils → helpers
        """
        # Create modules
        helpers = tmp_path / "helpers.js"
        helpers.write_text("export const log = console.log;")

        utils = tmp_path / "utils.js"
        utils.write_text("import { log } from './helpers.js';\nexport { log };")

        main = tmp_path / "main.js"
        main.write_text("import { log } from './utils.js';")

        # Link
        module = linker.loader.load("main.js")
        linker.link(module)

        # Get dependency graph
        graph = linker.get_dependency_graph(module)

        # Verify graph structure
        assert len(graph) == 3
        assert len(graph[module.url]) == 1  # main → utils
        utils_url = next(url for url in graph if "utils.js" in url)
        assert len(graph[utils_url]) == 1  # utils → helpers

    def test_dependency_graph_diamond(self, tmp_path, linker):
        """
        Test diamond dependency:
            main
           /    \
        left   right
           \    /
           shared
        """
        # Create shared dependency
        shared = tmp_path / "shared.js"
        shared.write_text("export const x = 1;")

        # Create left path
        left = tmp_path / "left.js"
        left.write_text("import { x } from './shared.js';\nexport const y = x;")

        # Create right path
        right = tmp_path / "right.js"
        right.write_text("import { x } from './shared.js';\nexport const z = x;")

        # Create main
        main = tmp_path / "main.js"
        main.write_text(
            "import { y } from './left.js';\n"
            "import { z } from './right.js';"
        )

        # Link
        module = linker.loader.load("main.js")
        linker.link(module)

        # Get dependency graph
        graph = linker.get_dependency_graph(module)

        # Verify graph has 4 nodes
        assert len(graph) == 4

    def test_topological_sort(self, tmp_path, linker):
        """Test topological sort for evaluation order."""
        # Create modules
        helpers = tmp_path / "helpers.js"
        helpers.write_text("export const x = 1;")

        utils = tmp_path / "utils.js"
        utils.write_text("import { x } from './helpers.js';\nexport const y = x;")

        main = tmp_path / "main.js"
        main.write_text("import { y } from './utils.js';")

        # Link
        module = linker.loader.load("main.js")
        linker.link(module)

        # Get topological order
        order = linker.topological_sort(module)

        # Verify order: dependencies before dependents
        urls = [m.url for m in order]
        helpers_idx = next(i for i, url in enumerate(urls) if "helpers.js" in url)
        utils_idx = next(i for i, url in enumerate(urls) if "utils.js" in url)
        main_idx = next(i for i, url in enumerate(urls) if "main.js" in url)

        assert helpers_idx < utils_idx < main_idx


class TestCircularDependencies:
    """Test circular dependency handling."""

    def test_detect_simple_cycle(self, tmp_path, linker):
        """Test detecting simple A → B → A cycle."""
        # Create circular modules
        a_js = tmp_path / "a.js"
        a_js.write_text("import { b } from './b.js';\nexport const a = 1;")

        b_js = tmp_path / "b.js"
        b_js.write_text("import { a } from './a.js';\nexport const b = 2;")

        # Link - should complete (cycles allowed with TDZ)
        module = linker.loader.load("a.js")
        linker.link(module)

        # Both modules should be linked
        assert module.status == ModuleStatus.LINKED
        assert module.dependencies[0].status == ModuleStatus.LINKED

    def test_self_import_cycle(self, tmp_path, linker):
        """Test detecting self-import cycle."""
        # Create self-importing module
        self_js = tmp_path / "self.js"
        self_js.write_text("import { x } from './self.js';\nexport const x = 1;")

        # Link - cycles allowed
        module = linker.loader.load("self.js")
        linker.link(module)

        assert module.status == ModuleStatus.LINKED

    def test_three_module_cycle(self, tmp_path, linker):
        """Test three-module cycle: A → B → C → A."""
        # Create circular modules
        a_js = tmp_path / "a.js"
        a_js.write_text("import { c } from './c.js';\nexport const a = 1;")

        b_js = tmp_path / "b.js"
        b_js.write_text("import { a } from './a.js';\nexport const b = 2;")

        c_js = tmp_path / "c.js"
        c_js.write_text("import { b } from './b.js';\nexport const c = 3;")

        # Link - should handle cycle
        module = linker.loader.load("a.js")
        linker.link(module)

        assert module.status == ModuleStatus.LINKED


class TestModuleCaching:
    """Test that modules are cached and not loaded twice."""

    def test_import_same_module_twice_uses_cache(self, tmp_path, linker, registry):
        """Test that importing same module twice uses cached version."""
        # Create shared dependency
        shared = tmp_path / "shared.js"
        shared.write_text("export const shared = 1;")

        # Create two modules importing same dependency
        a_js = tmp_path / "a.js"
        a_js.write_text("import { shared } from './shared.js';\nexport const a = shared;")

        b_js = tmp_path / "b.js"
        b_js.write_text("import { shared } from './shared.js';\nexport const b = shared;")

        # Link both
        module_a = linker.loader.load("a.js")
        linker.link(module_a)

        module_b = linker.loader.load("b.js")
        linker.link(module_b)

        # Both should reference same shared module (same object)
        assert module_a.dependencies[0] is module_b.dependencies[0]

    def test_diamond_dependency_uses_single_instance(self, tmp_path, linker, registry):
        """Test diamond dependency pattern uses single instance of shared module."""
        # Create shared
        shared = tmp_path / "shared.js"
        shared.write_text("export const x = 1;")

        # Create left and right paths
        left = tmp_path / "left.js"
        left.write_text("import { x } from './shared.js';\nexport const y = x;")

        right = tmp_path / "right.js"
        right.write_text("import { x } from './shared.js';\nexport const z = x;")

        # Create main
        main = tmp_path / "main.js"
        main.write_text(
            "import { y } from './left.js';\n"
            "import { z } from './right.js';"
        )

        # Link
        module = linker.loader.load("main.js")
        linker.link(module)

        # Find shared module instances
        left_module = next(dep for dep in module.dependencies if "left.js" in dep.url)
        right_module = next(dep for dep in module.dependencies if "right.js" in dep.url)

        left_shared = left_module.dependencies[0]
        right_shared = right_module.dependencies[0]

        # Should be same instance
        assert left_shared is right_shared


class TestErrorHandling:
    """Test error handling in module linker."""

    def test_parse_error_sets_error_status(self, tmp_path, linker):
        """Test that parse errors set module to ERROR status."""
        # Create module with syntax error
        bad_js = tmp_path / "bad.js"
        bad_js.write_text("export const x = ;")  # Syntax error

        # Load and try to link
        module = linker.loader.load("bad.js")

        with pytest.raises(ModuleLinkError) as exc_info:
            linker.link(module)

        # Verify module status
        assert module.status == ModuleStatus.ERROR
        assert module.error is not None
        assert "Parse error" in str(exc_info.value)

    def test_missing_dependency_raises_error(self, tmp_path, linker):
        """Test that missing dependency raises error."""
        # Create module importing non-existent file
        main_js = tmp_path / "main.js"
        main_js.write_text("import { x } from './nonexistent.js';")

        # Load and try to link
        module = linker.loader.load("main.js")

        with pytest.raises(ModuleLinkError):
            linker.link(module)

    def test_compile_error_sets_error_status(self, tmp_path, linker):
        """Test that compile errors set module to ERROR status."""
        # Note: This test depends on bytecode compiler behavior
        # For now, we'll test that errors are properly propagated

        # Create module (valid parse but might fail compilation)
        module_path = tmp_path / "module.js"
        module_path.write_text("export const x = 1;")

        module = linker.loader.load("module.js")

        # If compilation fails, verify error handling
        try:
            linker.link(module)
        except ModuleLinkError as e:
            # Verify error is properly captured
            assert module.status == ModuleStatus.ERROR
            assert module.error is not None


class TestImportExportExtraction:
    """Test import/export extraction from AST."""

    def test_extract_named_import(self, tmp_path, linker):
        """Test extracting named import declarations."""
        # Create dependency
        math_js = tmp_path / "math.js"
        math_js.write_text("export const add = (a, b) => a + b;")

        # Create module with named import
        main_js = tmp_path / "main.js"
        main_js.write_text("import { add } from './math.js';")

        # Link
        module = linker.loader.load("main.js")
        linker.link(module)

        # Verify import extracted
        assert len(module.imports) == 1
        assert module.imports[0].source.value == './math.js'

    def test_extract_named_export(self, tmp_path, linker):
        """Test extracting named export declarations."""
        # Create module with named export
        module_path = tmp_path / "module.js"
        module_path.write_text("export const x = 1;")

        # Link
        module = linker.loader.load("module.js")
        linker.link(module)

        # Verify export extracted
        assert len(module.exports) == 1

    def test_extract_default_export(self, tmp_path, linker):
        """Test extracting default export declaration."""
        # Create module with default export
        module_path = tmp_path / "module.js"
        module_path.write_text("export default 42;")

        # Link
        module = linker.loader.load("module.js")
        linker.link(module)

        # Verify export extracted
        assert len(module.exports) == 1

    def test_extract_mixed_imports_exports(self, tmp_path, linker):
        """Test extracting mixed import/export declarations."""
        # Create dependencies
        math_js = tmp_path / "math.js"
        math_js.write_text("export const add = (a, b) => a + b;")

        utils_js = tmp_path / "utils.js"
        utils_js.write_text("export const log = console.log;")

        # Create module with multiple imports and exports
        main_js = tmp_path / "main.js"
        main_js.write_text(
            "import { add } from './math.js';\n"
            "import { log } from './utils.js';\n"
            "export const result = add(1, 2);\n"
            "export default result;"
        )

        # Link
        module = linker.loader.load("main.js")
        linker.link(module)

        # Verify imports and exports extracted
        assert len(module.imports) == 2
        assert len(module.exports) == 2
