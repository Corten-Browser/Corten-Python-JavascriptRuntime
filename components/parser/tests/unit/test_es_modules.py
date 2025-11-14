"""
Unit tests for ES Modules parser support (Phase 2.7.1).

Tests verify parsing of import/export syntax including:
- Import declarations (default, named, namespace, side-effect)
- Export declarations (default, named, re-export)
- All import/export variants and combinations
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest
from components.parser.src.lexer import Lexer
from components.parser.src.parser import Parser
from components.parser.src.ast_nodes import (
    Program,
    ImportDeclaration,
    ImportSpecifier,
    ImportDefaultSpecifier,
    ImportNamespaceSpecifier,
    ExportNamedDeclaration,
    ExportSpecifier,
    ExportDefaultDeclaration,
    ExportAllDeclaration,
    Identifier,
    Literal,
    VariableDeclaration,
    FunctionDeclaration,
    FunctionExpression,
)


def parse(source: str) -> Program:
    """Helper to parse source code into AST."""
    lexer = Lexer(source, "test.js")
    parser = Parser(lexer)
    return parser.parse()


# ============================================================================
# IMPORT DECLARATIONS TESTS
# ============================================================================


class TestImportDeclarations:
    """Test parsing of import declarations."""

    def test_import_side_effect(self):
        """
        Given a side-effect import statement
        When parsing import './module.js';
        Then it should create ImportDeclaration with no specifiers
        """
        program = parse("import './module.js';")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        import_stmt = program.body[0]
        assert isinstance(import_stmt, ImportDeclaration)
        assert len(import_stmt.specifiers) == 0
        assert isinstance(import_stmt.source, Literal)
        assert import_stmt.source.value == "./module.js"

    def test_import_default(self):
        """
        Given a default import statement
        When parsing import foo from './module.js';
        Then it should create ImportDeclaration with ImportDefaultSpecifier
        """
        program = parse("import foo from './module.js';")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        import_stmt = program.body[0]
        assert isinstance(import_stmt, ImportDeclaration)
        assert len(import_stmt.specifiers) == 1

        spec = import_stmt.specifiers[0]
        assert isinstance(spec, ImportDefaultSpecifier)
        assert isinstance(spec.local, Identifier)
        assert spec.local.name == "foo"

        assert isinstance(import_stmt.source, Literal)
        assert import_stmt.source.value == "./module.js"

    def test_import_named_single(self):
        """
        Given a single named import
        When parsing import { x } from './module.js';
        Then it should create ImportDeclaration with one ImportSpecifier
        """
        program = parse("import { x } from './module.js';")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        import_stmt = program.body[0]
        assert isinstance(import_stmt, ImportDeclaration)
        assert len(import_stmt.specifiers) == 1

        spec = import_stmt.specifiers[0]
        assert isinstance(spec, ImportSpecifier)
        assert isinstance(spec.imported, Identifier)
        assert spec.imported.name == "x"
        assert isinstance(spec.local, Identifier)
        assert spec.local.name == "x"

    def test_import_named_multiple(self):
        """
        Given multiple named imports
        When parsing import { x, y, z } from './module.js';
        Then it should create ImportDeclaration with three ImportSpecifiers
        """
        program = parse("import { x, y, z } from './module.js';")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        import_stmt = program.body[0]
        assert isinstance(import_stmt, ImportDeclaration)
        assert len(import_stmt.specifiers) == 3

        # Verify each specifier
        for i, name in enumerate(['x', 'y', 'z']):
            spec = import_stmt.specifiers[i]
            assert isinstance(spec, ImportSpecifier)
            assert spec.imported.name == name
            assert spec.local.name == name

    def test_import_named_with_alias(self):
        """
        Given a named import with alias
        When parsing import { x as y } from './module.js';
        Then it should create ImportSpecifier with different imported and local
        """
        program = parse("import { x as y } from './module.js';")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        import_stmt = program.body[0]
        assert isinstance(import_stmt, ImportDeclaration)
        assert len(import_stmt.specifiers) == 1

        spec = import_stmt.specifiers[0]
        assert isinstance(spec, ImportSpecifier)
        assert spec.imported.name == "x"
        assert spec.local.name == "y"

    def test_import_named_multiple_with_aliases(self):
        """
        Given multiple named imports with some aliases
        When parsing import { x, y as z, w } from './module.js';
        Then it should create correct ImportSpecifiers with appropriate aliases
        """
        program = parse("import { x, y as z, w } from './module.js';")

        assert isinstance(program, Program)
        import_stmt = program.body[0]
        assert len(import_stmt.specifiers) == 3

        # x (no alias)
        assert import_stmt.specifiers[0].imported.name == "x"
        assert import_stmt.specifiers[0].local.name == "x"

        # y as z (alias)
        assert import_stmt.specifiers[1].imported.name == "y"
        assert import_stmt.specifiers[1].local.name == "z"

        # w (no alias)
        assert import_stmt.specifiers[2].imported.name == "w"
        assert import_stmt.specifiers[2].local.name == "w"

    def test_import_namespace(self):
        """
        Given a namespace import
        When parsing import * as math from './module.js';
        Then it should create ImportNamespaceSpecifier
        """
        program = parse("import * as math from './module.js';")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        import_stmt = program.body[0]
        assert isinstance(import_stmt, ImportDeclaration)
        assert len(import_stmt.specifiers) == 1

        spec = import_stmt.specifiers[0]
        assert isinstance(spec, ImportNamespaceSpecifier)
        assert isinstance(spec.local, Identifier)
        assert spec.local.name == "math"

    def test_import_default_and_named(self):
        """
        Given a mixed default and named import
        When parsing import foo, { x, y } from './module.js';
        Then it should create both ImportDefaultSpecifier and ImportSpecifiers
        """
        program = parse("import foo, { x, y } from './module.js';")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        import_stmt = program.body[0]
        assert isinstance(import_stmt, ImportDeclaration)
        assert len(import_stmt.specifiers) == 3

        # First should be default
        assert isinstance(import_stmt.specifiers[0], ImportDefaultSpecifier)
        assert import_stmt.specifiers[0].local.name == "foo"

        # Next should be named imports
        assert isinstance(import_stmt.specifiers[1], ImportSpecifier)
        assert import_stmt.specifiers[1].local.name == "x"

        assert isinstance(import_stmt.specifiers[2], ImportSpecifier)
        assert import_stmt.specifiers[2].local.name == "y"

    def test_import_default_and_namespace(self):
        """
        Given a default and namespace import
        When parsing import foo, * as bar from './module.js';
        Then it should create both ImportDefaultSpecifier and ImportNamespaceSpecifier
        """
        program = parse("import foo, * as bar from './module.js';")

        assert isinstance(program, Program)
        import_stmt = program.body[0]
        assert len(import_stmt.specifiers) == 2

        # First should be default
        assert isinstance(import_stmt.specifiers[0], ImportDefaultSpecifier)
        assert import_stmt.specifiers[0].local.name == "foo"

        # Second should be namespace
        assert isinstance(import_stmt.specifiers[1], ImportNamespaceSpecifier)
        assert import_stmt.specifiers[1].local.name == "bar"


# ============================================================================
# EXPORT DECLARATIONS TESTS
# ============================================================================


class TestExportDeclarations:
    """Test parsing of export declarations."""

    def test_export_named_const(self):
        """
        Given an export const declaration
        When parsing export const x = 1;
        Then it should create ExportNamedDeclaration with VariableDeclaration
        """
        program = parse("export const x = 1;")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        export_stmt = program.body[0]
        assert isinstance(export_stmt, ExportNamedDeclaration)
        assert isinstance(export_stmt.declaration, VariableDeclaration)
        assert export_stmt.declaration.kind == "const"
        assert len(export_stmt.specifiers) == 0
        assert export_stmt.source is None

    def test_export_named_function(self):
        """
        Given an export function declaration
        When parsing export function foo() { return 42; }
        Then it should create ExportNamedDeclaration with FunctionDeclaration
        """
        program = parse("export function foo() { return 42; }")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        export_stmt = program.body[0]
        assert isinstance(export_stmt, ExportNamedDeclaration)
        assert isinstance(export_stmt.declaration, FunctionDeclaration)
        assert export_stmt.declaration.name == "foo"
        assert len(export_stmt.specifiers) == 0
        assert export_stmt.source is None

    def test_export_named_list(self):
        """
        Given an export list
        When parsing export { x, y };
        Then it should create ExportNamedDeclaration with specifiers
        """
        program = parse("const x = 1, y = 2; export { x, y };")

        assert isinstance(program, Program)
        assert len(program.body) == 2

        export_stmt = program.body[1]
        assert isinstance(export_stmt, ExportNamedDeclaration)
        assert export_stmt.declaration is None
        assert len(export_stmt.specifiers) == 2
        assert export_stmt.source is None

        # Verify specifiers
        assert export_stmt.specifiers[0].local.name == "x"
        assert export_stmt.specifiers[0].exported.name == "x"

        assert export_stmt.specifiers[1].local.name == "y"
        assert export_stmt.specifiers[1].exported.name == "y"

    def test_export_named_with_alias(self):
        """
        Given an export list with alias
        When parsing export { x as y };
        Then it should create ExportSpecifier with different local and exported
        """
        program = parse("const x = 1; export { x as y };")

        assert isinstance(program, Program)
        export_stmt = program.body[1]
        assert isinstance(export_stmt, ExportNamedDeclaration)
        assert len(export_stmt.specifiers) == 1

        spec = export_stmt.specifiers[0]
        assert isinstance(spec, ExportSpecifier)
        assert spec.local.name == "x"
        assert spec.exported.name == "y"

    def test_export_default_expression(self):
        """
        Given a default export with expression
        When parsing export default 42;
        Then it should create ExportDefaultDeclaration
        """
        program = parse("export default 42;")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        export_stmt = program.body[0]
        assert isinstance(export_stmt, ExportDefaultDeclaration)
        assert isinstance(export_stmt.declaration, Literal)
        assert export_stmt.declaration.value == 42

    def test_export_default_function(self):
        """
        Given a default export with anonymous function
        When parsing export default function() { return 42; }
        Then it should create ExportDefaultDeclaration with FunctionExpression
        """
        program = parse("export default function() { return 42; }")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        export_stmt = program.body[0]
        assert isinstance(export_stmt, ExportDefaultDeclaration)
        # Anonymous function should be FunctionExpression
        assert isinstance(export_stmt.declaration, FunctionExpression)

    def test_export_default_named_function(self):
        """
        Given a default export with named function
        When parsing export default function foo() { return 42; }
        Then it should create ExportDefaultDeclaration with named function
        """
        program = parse("export default function foo() { return 42; }")

        assert isinstance(program, Program)
        export_stmt = program.body[0]
        assert isinstance(export_stmt, ExportDefaultDeclaration)
        assert isinstance(export_stmt.declaration, FunctionDeclaration)
        assert export_stmt.declaration.name == "foo"

    def test_export_from_reexport_named(self):
        """
        Given a re-export statement
        When parsing export { x } from './other.js';
        Then it should create ExportNamedDeclaration with source
        """
        program = parse("export { x } from './other.js';")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        export_stmt = program.body[0]
        assert isinstance(export_stmt, ExportNamedDeclaration)
        assert export_stmt.declaration is None
        assert len(export_stmt.specifiers) == 1
        assert export_stmt.specifiers[0].local.name == "x"
        assert isinstance(export_stmt.source, Literal)
        assert export_stmt.source.value == "./other.js"

    def test_export_from_reexport_with_alias(self):
        """
        Given a re-export with alias
        When parsing export { x as y } from './other.js';
        Then it should create correct ExportSpecifier with alias
        """
        program = parse("export { x as y } from './other.js';")

        assert isinstance(program, Program)
        export_stmt = program.body[0]
        assert isinstance(export_stmt, ExportNamedDeclaration)
        assert len(export_stmt.specifiers) == 1

        spec = export_stmt.specifiers[0]
        assert spec.local.name == "x"
        assert spec.exported.name == "y"
        assert export_stmt.source.value == "./other.js"

    def test_export_all_from(self):
        """
        Given an export all statement
        When parsing export * from './other.js';
        Then it should create ExportAllDeclaration
        """
        program = parse("export * from './other.js';")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        export_stmt = program.body[0]
        assert isinstance(export_stmt, ExportAllDeclaration)
        assert isinstance(export_stmt.source, Literal)
        assert export_stmt.source.value == "./other.js"
        assert export_stmt.exported is None

    def test_export_all_as_namespace(self):
        """
        Given an export all as namespace
        When parsing export * as math from './math.js';
        Then it should create ExportAllDeclaration with exported name
        """
        program = parse("export * as math from './math.js';")

        assert isinstance(program, Program)
        assert len(program.body) == 1

        export_stmt = program.body[0]
        assert isinstance(export_stmt, ExportAllDeclaration)
        assert isinstance(export_stmt.source, Literal)
        assert export_stmt.source.value == "./math.js"
        assert isinstance(export_stmt.exported, Identifier)
        assert export_stmt.exported.name == "math"


# ============================================================================
# COMPLEX MODULE SCENARIOS
# ============================================================================


class TestComplexModuleScenarios:
    """Test complex combinations of import/export."""

    def test_multiple_imports_and_exports(self):
        """
        Given a module with multiple import and export statements
        When parsing imports and exports together
        Then all declarations should be parsed correctly
        """
        source = """
        import { a } from './a.js';
        import { b } from './b.js';

        const c = a + b;

        export { c };
        export const d = c * 2;
        """
        program = parse(source)

        assert isinstance(program, Program)

        # Should have: 2 imports, 1 variable declaration, 2 exports
        import_count = sum(1 for stmt in program.body if isinstance(stmt, ImportDeclaration))
        export_count = sum(1 for stmt in program.body if isinstance(stmt, (ExportNamedDeclaration, ExportDefaultDeclaration, ExportAllDeclaration)))

        assert import_count == 2
        assert export_count == 2

    def test_import_export_same_module(self):
        """
        Given imports and exports in the same module
        When parsing import foo from './foo.js'; export default foo;
        Then both should be parsed correctly
        """
        source = """
        import foo from './foo.js';
        export default foo;
        """
        program = parse(source)

        assert isinstance(program, Program)
        assert len(program.body) == 2

        # First should be import
        assert isinstance(program.body[0], ImportDeclaration)
        assert isinstance(program.body[0].specifiers[0], ImportDefaultSpecifier)

        # Second should be export
        assert isinstance(program.body[1], ExportDefaultDeclaration)

    def test_mixed_import_styles(self):
        """
        Given various import styles in one module
        When parsing different import formats
        Then all should be parsed correctly
        """
        source = """
        import './polyfill.js';
        import React from 'react';
        import { useState, useEffect } from 'react';
        import * as utils from './utils.js';
        """
        program = parse(source)

        assert isinstance(program, Program)
        assert len(program.body) == 4

        # Verify each import type
        assert len(program.body[0].specifiers) == 0  # Side-effect
        assert isinstance(program.body[1].specifiers[0], ImportDefaultSpecifier)  # Default
        assert isinstance(program.body[2].specifiers[0], ImportSpecifier)  # Named
        assert isinstance(program.body[3].specifiers[0], ImportNamespaceSpecifier)  # Namespace

    def test_mixed_export_styles(self):
        """
        Given various export styles in one module
        When parsing different export formats
        Then all should be parsed correctly
        """
        source = """
        export const x = 1;
        export function foo() {}
        export { y, z };
        export default class Bar {}
        """
        program = parse(source)

        assert isinstance(program, Program)
        assert len(program.body) == 4

        # Verify each export type
        assert isinstance(program.body[0], ExportNamedDeclaration)
        assert isinstance(program.body[0].declaration, VariableDeclaration)

        assert isinstance(program.body[1], ExportNamedDeclaration)
        assert isinstance(program.body[1].declaration, FunctionDeclaration)

        assert isinstance(program.body[2], ExportNamedDeclaration)
        assert len(program.body[2].specifiers) == 2

        assert isinstance(program.body[3], ExportDefaultDeclaration)

    def test_reexport_patterns(self):
        """
        Given various re-export patterns
        When parsing re-exports
        Then all should be parsed correctly
        """
        source = """
        export { x, y } from './module1.js';
        export { a as b } from './module2.js';
        export * from './module3.js';
        export * as utils from './module4.js';
        """
        program = parse(source)

        assert isinstance(program, Program)
        assert len(program.body) == 4

        # Named re-export
        assert isinstance(program.body[0], ExportNamedDeclaration)
        assert program.body[0].source.value == "./module1.js"

        # Named with alias re-export
        assert isinstance(program.body[1], ExportNamedDeclaration)
        assert program.body[1].specifiers[0].exported.name == "b"

        # Export all
        assert isinstance(program.body[2], ExportAllDeclaration)
        assert program.body[2].exported is None

        # Export all as namespace
        assert isinstance(program.body[3], ExportAllDeclaration)
        assert program.body[3].exported.name == "utils"


# ============================================================================
# EDGE CASES AND ERROR HANDLING
# ============================================================================


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_import_no_semicolon(self):
        """
        Given an import without semicolon
        When parsing with ASI (Automatic Semicolon Insertion)
        Then it should parse successfully
        """
        program = parse("import foo from './module.js'")

        assert isinstance(program, Program)
        assert len(program.body) == 1
        assert isinstance(program.body[0], ImportDeclaration)

    def test_export_no_semicolon(self):
        """
        Given an export without semicolon
        When parsing with ASI
        Then it should parse successfully
        """
        program = parse("export const x = 1")

        assert isinstance(program, Program)
        assert len(program.body) == 1
        assert isinstance(program.body[0], ExportNamedDeclaration)

    def test_empty_import_list(self):
        """
        Given an import with empty braces (edge case)
        When parsing import {} from './module.js';
        Then it should create ImportDeclaration with no specifiers
        """
        # Note: This is technically invalid ES6, but let's verify parser behavior
        # The parser should handle this gracefully
        try:
            program = parse("import {} from './module.js';")
            import_stmt = program.body[0]
            assert isinstance(import_stmt, ImportDeclaration)
            assert len(import_stmt.specifiers) == 0
        except SyntaxError:
            # It's also valid to reject this as a syntax error
            pass

    def test_module_path_variations(self):
        """
        Given various module path formats
        When parsing different path styles
        Then all should be parsed correctly
        """
        # Relative path
        program1 = parse("import x from './module.js';")
        assert program1.body[0].source.value == "./module.js"

        # Parent directory
        program2 = parse("import x from '../module.js';")
        assert program2.body[0].source.value == "../module.js"

        # Absolute path
        program3 = parse("import x from '/abs/path/module.js';")
        assert program3.body[0].source.value == "/abs/path/module.js"

        # Package name
        program4 = parse("import x from 'lodash';")
        assert program4.body[0].source.value == "lodash"
