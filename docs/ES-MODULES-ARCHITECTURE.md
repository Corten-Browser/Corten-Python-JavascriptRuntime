# ES Modules Architecture Design

**Date:** 2025-11-14
**Version:** 1.0
**Status:** Design Phase
**Depends On:** Phase 2.6 (Async/Await), Phase 2.5 (Promises)

---

## Overview

This document outlines the architectural design for implementing JavaScript ES Modules in the Corten JavaScript Runtime. ES Modules provide a standardized module system for JavaScript, enabling code organization, encapsulation, and dependency management through `import` and `export` statements.

ES Modules represent a fundamental shift from script-based execution to module-based execution, requiring changes to:
- Source code loading and caching
- Dependency resolution and linking
- Execution context management
- Namespace management

---

## Current State

**Execution Model:** Single-file script execution
- Parser processes one file at a time
- No concept of modules or dependencies
- All code shares global scope
- No encapsulation beyond function/block scope
- No standardized way to split code across files

**Not Implemented:**
- ❌ Import/export syntax
- ❌ Module loading system
- ❌ Module dependency resolution
- ❌ Module namespace objects
- ❌ Module caching
- ❌ Cyclic dependency handling

---

## Target State

**Execution Model:** Module-based execution with dependency graph
- Load and link multiple files as modules
- Each module has isolated scope
- Explicit import/export of bindings
- Static dependency analysis
- Module caching for performance
- Support for cyclic dependencies

**Goal:** Enable JavaScript code like this to work:

```javascript
// math.js - Named exports
export function add(a, b) {
    return a + b;
}

export function subtract(a, b) {
    return a - b;
}

export const PI = 3.14159;
export const E = 2.71828;

// main.js - Named imports
import { add, subtract, PI } from './math.js';

console.log(add(5, 3));        // 8
console.log(subtract(10, 4));   // 6
console.log(PI);                // 3.14159

// greet.js - Default export
export default function greet(name) {
    return `Hello, ${name}!`;
}

// app.js - Default import
import greet from './greet.js';
console.log(greet('World'));    // Hello, World!

// utils.js - Mixed exports
export default class Calculator {
    add(a, b) { return a + b; }
}

export const version = '1.0.0';

// client.js - Mixed imports
import Calculator, { version } from './utils.js';

const calc = new Calculator();
console.log(calc.add(1, 2));    // 3
console.log(version);           // 1.0.0

// data.js - Namespace import
import * as math from './math.js';

console.log(math.add(1, 2));    // 3
console.log(math.PI);           // 3.14159

// re-export.js - Re-exports
export { add, subtract } from './math.js';
export { default as greet } from './greet.js';

// side-effects.js - Side-effect import
import './polyfills.js';  // Just execute, don't import anything
```

---

## Design Approach: Node.js-Style Synchronous Loading

### Module System Options Compared

**1. Browser-Style Async Loading:**
- Fetches modules over HTTP
- Asynchronous by nature (fetch API)
- Requires top-level await for main module
- ❌ Cons: Complex, requires HTTP server, async everywhere

**2. Node.js-Style Sync Loading:**
- Loads modules from file system
- Synchronous file I/O
- Simpler execution model
- ✅ Pros: Fits our current synchronous runtime, simpler to implement

**3. Bundler-Style Static Linking:**
- Pre-process all modules into single bundle
- No runtime loading
- ❌ Cons: Requires separate build step, not spec-compliant

**Decision:** Node.js-style synchronous loading

**Rationale:**
- Our runtime is synchronous (no async I/O yet)
- File system access is simpler than HTTP
- Matches Node.js ESM behavior
- Can add async loading later if needed

---

## Architecture Components

### 1. Parser Changes

**Add Tokens:**
```python
class TokenType(Enum):
    # Existing tokens...

    # Module tokens
    IMPORT = auto()        # import
    EXPORT = auto()        # export
    FROM = auto()          # from
    AS = auto()            # as
    DEFAULT = auto()       # default (already exists as keyword)
    STAR = auto()          # * (already exists for multiply)
```

**Add Keywords:**
```python
KEYWORDS = {
    # Existing keywords...
    "import": TokenType.IMPORT,
    "export": TokenType.EXPORT,
    "from": TokenType.FROM,
    "as": TokenType.AS,
}
```

**Add AST Nodes:**

```python
# ============================================================================
# IMPORT DECLARATIONS
# ============================================================================

@dataclass
class ImportDeclaration:
    """
    Base import declaration.

    Examples:
        import { x, y } from './module.js';
        import x from './module.js';
        import * as ns from './module.js';
    """
    specifiers: List[Any]  # List of ImportSpecifier variants
    source: StringLiteral  # Module path

@dataclass
class ImportSpecifier:
    """
    Named import specifier: { x, y, z as alias }

    Examples:
        { x }           -> ImportSpecifier(imported='x', local='x')
        { x as y }      -> ImportSpecifier(imported='x', local='y')
    """
    imported: Identifier  # Name in source module
    local: Identifier     # Name in current module (can be same or alias)

@dataclass
class ImportDefaultSpecifier:
    """
    Default import specifier: import x from './module.js'

    Example:
        import greet from './greet.js'
        -> ImportDefaultSpecifier(local='greet')
    """
    local: Identifier  # Local name for default export

@dataclass
class ImportNamespaceSpecifier:
    """
    Namespace import specifier: import * as name from './module.js'

    Example:
        import * as math from './math.js'
        -> ImportNamespaceSpecifier(local='math')
    """
    local: Identifier  # Local name for namespace object

# ============================================================================
# EXPORT DECLARATIONS
# ============================================================================

@dataclass
class ExportNamedDeclaration:
    """
    Named export declaration.

    Examples:
        export const x = 1;
        export function foo() {}
        export { x, y };
        export { x as y };
        export { x } from './other.js';
    """
    declaration: Optional[Any]  # VariableDeclaration, FunctionDeclaration, etc.
    specifiers: List['ExportSpecifier']  # For export { x, y }
    source: Optional[StringLiteral]  # For re-exports

@dataclass
class ExportSpecifier:
    """
    Export specifier in export list.

    Examples:
        { x }       -> ExportSpecifier(local='x', exported='x')
        { x as y }  -> ExportSpecifier(local='x', exported='y')
    """
    local: Identifier   # Name in current module
    exported: Identifier  # Name when imported

@dataclass
class ExportDefaultDeclaration:
    """
    Default export declaration.

    Examples:
        export default function() {}
        export default class {}
        export default 42;
        export default expression;
    """
    declaration: Any  # Expression, FunctionDeclaration, ClassDeclaration

@dataclass
class ExportAllDeclaration:
    """
    Re-export all from another module.

    Examples:
        export * from './module.js';
        export * as ns from './module.js';
    """
    source: StringLiteral
    exported: Optional[Identifier]  # For 'export * as ns'
```

**Parsing Logic:**

```python
def _parse_statement(self):
    """Parse a statement, including import/export."""

    # Import statement
    if self._match(TokenType.IMPORT):
        return self._parse_import_declaration()

    # Export statement
    if self._match(TokenType.EXPORT):
        return self._parse_export_declaration()

    # ... existing statement parsing ...

def _parse_import_declaration(self):
    """
    Parse import declaration.

    Grammar:
        import DefaultImport from 'source';
        import { NamedImports } from 'source';
        import * as NamespaceImport from 'source';
        import DefaultImport, { NamedImports } from 'source';
        import DefaultImport, * as NamespaceImport from 'source';
        import 'source';  // Side-effect only
    """
    specifiers = []

    # Check for side-effect import: import './module.js'
    if self._check(TokenType.STRING):
        source = self._parse_string_literal()
        self._consume(TokenType.SEMICOLON)
        return ImportDeclaration(specifiers=[], source=source)

    # Default import: import x from '...'
    if not self._check(TokenType.LBRACE) and not self._check(TokenType.STAR):
        local = self._parse_identifier()
        specifiers.append(ImportDefaultSpecifier(local=local))

        # Check for comma (mixed import)
        if self._match(TokenType.COMMA):
            # Can have { named } or * as ns after default
            pass  # Fall through to named/namespace parsing
        else:
            self._consume(TokenType.FROM)
            source = self._parse_string_literal()
            self._consume(TokenType.SEMICOLON)
            return ImportDeclaration(specifiers=specifiers, source=source)

    # Namespace import: import * as ns from '...'
    if self._match(TokenType.STAR):
        self._consume(TokenType.AS)
        local = self._parse_identifier()
        specifiers.append(ImportNamespaceSpecifier(local=local))

    # Named imports: import { x, y, z as w } from '...'
    elif self._match(TokenType.LBRACE):
        while not self._check(TokenType.RBRACE):
            imported = self._parse_identifier()

            if self._match(TokenType.AS):
                local = self._parse_identifier()
            else:
                local = imported

            specifiers.append(ImportSpecifier(imported=imported, local=local))

            if not self._check(TokenType.RBRACE):
                self._consume(TokenType.COMMA)

        self._consume(TokenType.RBRACE)

    self._consume(TokenType.FROM)
    source = self._parse_string_literal()
    self._consume(TokenType.SEMICOLON)

    return ImportDeclaration(specifiers=specifiers, source=source)

def _parse_export_declaration(self):
    """
    Parse export declaration.

    Grammar:
        export default Expression;
        export default function name() {}
        export default class Name {}
        export const x = 1;
        export function foo() {}
        export { x, y };
        export { x as y };
        export { x } from './other.js';
        export * from './other.js';
        export * as ns from './other.js';
    """

    # Default export: export default ...
    if self._match(TokenType.DEFAULT):
        # export default function/class can be named or anonymous
        if self._check(TokenType.FUNCTION):
            declaration = self._parse_function_declaration(allow_anonymous=True)
        elif self._check(TokenType.CLASS):
            declaration = self._parse_class_declaration(allow_anonymous=True)
        else:
            # export default expression
            declaration = self._parse_assignment_expression()
            self._consume(TokenType.SEMICOLON)

        return ExportDefaultDeclaration(declaration=declaration)

    # Re-export all: export * from '...'
    if self._match(TokenType.STAR):
        exported = None

        # export * as ns from '...'
        if self._match(TokenType.AS):
            exported = self._parse_identifier()

        self._consume(TokenType.FROM)
        source = self._parse_string_literal()
        self._consume(TokenType.SEMICOLON)

        return ExportAllDeclaration(source=source, exported=exported)

    # Named export list: export { x, y }
    if self._match(TokenType.LBRACE):
        specifiers = []

        while not self._check(TokenType.RBRACE):
            local = self._parse_identifier()

            if self._match(TokenType.AS):
                exported = self._parse_identifier()
            else:
                exported = local

            specifiers.append(ExportSpecifier(local=local, exported=exported))

            if not self._check(TokenType.RBRACE):
                self._consume(TokenType.COMMA)

        self._consume(TokenType.RBRACE)

        # Re-export: export { x } from './other.js'
        source = None
        if self._match(TokenType.FROM):
            source = self._parse_string_literal()

        self._consume(TokenType.SEMICOLON)

        return ExportNamedDeclaration(
            declaration=None,
            specifiers=specifiers,
            source=source
        )

    # Export declaration: export const/let/function/class
    if self._check(TokenType.CONST) or self._check(TokenType.LET) or \
       self._check(TokenType.VAR) or self._check(TokenType.FUNCTION) or \
       self._check(TokenType.CLASS):

        declaration = self._parse_declaration()

        return ExportNamedDeclaration(
            declaration=declaration,
            specifiers=[],
            source=None
        )

    raise ParseError("Unexpected token in export declaration")
```

---

### 2. Module System Architecture

**Key Design Principles:**
1. **Module Record:** Each file is represented as a Module object
2. **Module Loader:** Loads source code from file system
3. **Module Linker:** Resolves dependencies and creates dependency graph
4. **Module Evaluator:** Executes module code and populates namespace
5. **Module Registry:** Caches loaded modules (singleton per URL)

**Module Lifecycle States:**

```
UNLINKED → LINKING → LINKED → EVALUATING → EVALUATED
    ↓         ↓         ↓          ↓           ↓
  (new)    (loading)  (ready)  (executing)  (complete)
```

**Core Classes:**

```python
# ============================================================================
# MODULE STATE
# ============================================================================

class ModuleStatus(Enum):
    """Module lifecycle states."""
    UNLINKED = auto()      # Created, not processed
    LINKING = auto()       # Loading dependencies
    LINKED = auto()        # Dependencies resolved, ready to evaluate
    EVALUATING = auto()    # Currently executing
    EVALUATED = auto()     # Execution complete
    ERRORED = auto()       # Error during linking or evaluation

# ============================================================================
# MODULE RECORD
# ============================================================================

@dataclass
class Module:
    """
    Represents a JavaScript module.

    Attributes:
        url: Absolute file path (e.g., '/path/to/module.js')
        source: Source code text
        ast: Parsed AST (Program node)
        bytecode: Compiled bytecode
        namespace: Module namespace object (exports)
        imports: List of import declarations
        exports: List of export declarations
        status: Current lifecycle status
        dependencies: List of Module objects this depends on
        environment: Module-scoped execution environment
        error: Error if status == ERRORED
    """
    url: str
    source: str
    ast: Optional[Any] = None
    bytecode: Optional[BytecodeArray] = None
    namespace: Dict[str, Value] = field(default_factory=dict)
    imports: List[ImportDeclaration] = field(default_factory=list)
    exports: List[Any] = field(default_factory=list)  # Export declarations
    status: ModuleStatus = ModuleStatus.UNLINKED
    dependencies: List['Module'] = field(default_factory=list)
    environment: Dict[str, Value] = field(default_factory=dict)
    error: Optional[Exception] = None

    # For cyclic dependency handling
    _dfs_index: int = -1
    _dfs_ancestor_index: int = -1

# ============================================================================
# MODULE LOADER
# ============================================================================

class ModuleLoader:
    """
    Loads module source from file system.

    Responsibilities:
        - Read file from disk
        - Normalize URLs
        - Handle file not found errors
    """

    def __init__(self, base_dir: str = None):
        """
        Initialize loader.

        Args:
            base_dir: Base directory for resolving relative paths
        """
        self.base_dir = base_dir or os.getcwd()

    def load(self, url: str) -> str:
        """
        Load module source from file system.

        Args:
            url: Absolute or relative file path

        Returns:
            Source code as string

        Raises:
            ModuleNotFoundError: If file doesn't exist
        """
        # Normalize path
        if not os.path.isabs(url):
            url = os.path.join(self.base_dir, url)

        url = os.path.normpath(url)

        # Read file
        try:
            with open(url, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            raise ModuleNotFoundError(f"Cannot find module: {url}")
        except Exception as e:
            raise ModuleLoadError(f"Error loading module {url}: {e}")

    def normalize_url(self, url: str) -> str:
        """
        Normalize module URL to absolute path.

        Args:
            url: Relative or absolute path

        Returns:
            Absolute normalized path
        """
        if not os.path.isabs(url):
            url = os.path.join(self.base_dir, url)

        return os.path.normpath(url)

# ============================================================================
# MODULE LINKER
# ============================================================================

class ModuleLinker:
    """
    Links modules together, resolving dependencies.

    Responsibilities:
        - Parse modules
        - Resolve import specifiers to module URLs
        - Build dependency graph
        - Detect cyclic dependencies
        - Link import/export bindings
    """

    def __init__(self, loader: ModuleLoader, parser_class, registry: 'ModuleRegistry'):
        self.loader = loader
        self.parser_class = parser_class
        self.registry = registry

    def link(self, module: Module) -> None:
        """
        Link module and all dependencies.

        This implements the ES spec "InnerModuleLinking" algorithm.

        Args:
            module: Module to link

        Raises:
            ModuleLinkError: If linking fails
        """
        if module.status in (ModuleStatus.LINKING, ModuleStatus.LINKED,
                            ModuleStatus.EVALUATING, ModuleStatus.EVALUATED):
            return  # Already linked or linking

        if module.status == ModuleStatus.ERRORED:
            raise module.error

        module.status = ModuleStatus.LINKING

        try:
            # Parse module if not already parsed
            if module.ast is None:
                parser = self.parser_class(module.source)
                module.ast = parser.parse()

            # Extract import/export declarations
            self._extract_imports_exports(module)

            # Load and link dependencies
            for import_decl in module.imports:
                # Resolve specifier to absolute URL
                dep_url = self.resolve_specifier(
                    import_decl.source.value,
                    module.url
                )

                # Get or create module
                dep_module = self.registry.get(dep_url)
                if dep_module is None:
                    # Load module
                    source = self.loader.load(dep_url)
                    dep_module = Module(url=dep_url, source=source)
                    self.registry.register(dep_module)

                # Recursively link dependency
                self.link(dep_module)

                # Add to dependencies
                module.dependencies.append(dep_module)

            module.status = ModuleStatus.LINKED

        except Exception as e:
            module.status = ModuleStatus.ERRORED
            module.error = e
            raise

    def resolve_specifier(self, specifier: str, referrer: str) -> str:
        """
        Resolve import specifier to absolute URL.

        Args:
            specifier: Import specifier (e.g., './math.js', '/abs/path.js')
            referrer: URL of module containing the import

        Returns:
            Absolute normalized URL

        Examples:
            resolve_specifier('./math.js', '/app/main.js') -> '/app/math.js'
            resolve_specifier('../util.js', '/app/lib/foo.js') -> '/app/util.js'
        """
        # Relative import: ./... or ../...
        if specifier.startswith('./') or specifier.startswith('../'):
            referrer_dir = os.path.dirname(referrer)
            resolved = os.path.join(referrer_dir, specifier)
            return os.path.normpath(resolved)

        # Absolute import: /...
        if specifier.startswith('/'):
            return os.path.normpath(specifier)

        # Bare specifier (future: node_modules resolution)
        # For now, treat as error
        raise ModuleResolutionError(
            f"Bare module specifiers not supported yet: {specifier}"
        )

    def _extract_imports_exports(self, module: Module):
        """
        Extract import and export declarations from module AST.

        Args:
            module: Module to extract from
        """
        module.imports = []
        module.exports = []

        for statement in module.ast.body:
            if isinstance(statement, ImportDeclaration):
                module.imports.append(statement)
            elif isinstance(statement, (ExportNamedDeclaration,
                                       ExportDefaultDeclaration,
                                       ExportAllDeclaration)):
                module.exports.append(statement)

# ============================================================================
# MODULE EVALUATOR
# ============================================================================

class ModuleEvaluator:
    """
    Evaluates module bytecode and populates namespace.

    Responsibilities:
        - Create module execution environment
        - Execute module bytecode
        - Populate module namespace with exports
        - Resolve import bindings from dependencies
        - Handle cyclic dependencies via TDZ
    """

    def __init__(self, interpreter):
        self.interpreter = interpreter

    def evaluate(self, module: Module) -> None:
        """
        Evaluate module and populate namespace.

        This implements the ES spec "InnerModuleEvaluation" algorithm.

        Args:
            module: Module to evaluate

        Raises:
            ModuleEvaluationError: If evaluation fails
        """
        if module.status == ModuleStatus.EVALUATED:
            return  # Already evaluated

        if module.status == ModuleStatus.EVALUATING:
            # Cyclic dependency - allowed in ES modules
            # Bindings will be in TDZ until initialized
            return

        if module.status == ModuleStatus.ERRORED:
            raise module.error

        if module.status != ModuleStatus.LINKED:
            raise ModuleEvaluationError(
                f"Module must be linked before evaluation: {module.url}"
            )

        module.status = ModuleStatus.EVALUATING

        try:
            # Evaluate dependencies first (depth-first)
            for dep_module in module.dependencies:
                self.evaluate(dep_module)

            # Create module environment
            module.environment = self._create_module_environment(module)

            # Compile module if not already compiled
            if module.bytecode is None:
                compiler = Compiler()
                module.bytecode = compiler.compile(module.ast)

            # Execute module bytecode in module environment
            result = self.interpreter.execute_in_environment(
                module.bytecode,
                module.environment
            )

            # Populate namespace with exports
            self._populate_namespace(module)

            module.status = ModuleStatus.EVALUATED

        except Exception as e:
            module.status = ModuleStatus.ERRORED
            module.error = e
            raise

    def _create_module_environment(self, module: Module) -> Dict[str, Value]:
        """
        Create execution environment for module.

        Environment contains:
            - Imported bindings from dependencies
            - Module-local variables (initially undefined/TDZ)

        Args:
            module: Module to create environment for

        Returns:
            Environment dictionary
        """
        env = {}

        # Resolve import bindings
        for import_decl in module.imports:
            dep_module = self._find_dependency_module(
                module,
                import_decl.source.value
            )

            for specifier in import_decl.specifiers:
                if isinstance(specifier, ImportDefaultSpecifier):
                    # import x from './module.js'
                    # x = dep_module.namespace['default']
                    env[specifier.local.name] = dep_module.namespace.get(
                        'default',
                        Value.from_undefined()  # TDZ for cyclic deps
                    )

                elif isinstance(specifier, ImportNamespaceSpecifier):
                    # import * as ns from './module.js'
                    # ns = module namespace object
                    namespace_obj = self._create_namespace_object(dep_module)
                    env[specifier.local.name] = namespace_obj

                elif isinstance(specifier, ImportSpecifier):
                    # import { x, y as z } from './module.js'
                    imported_name = specifier.imported.name
                    local_name = specifier.local.name

                    env[local_name] = dep_module.namespace.get(
                        imported_name,
                        Value.from_undefined()  # TDZ for cyclic deps
                    )

        return env

    def _populate_namespace(self, module: Module):
        """
        Populate module namespace with exported bindings.

        Args:
            module: Module to populate namespace for
        """
        for export_decl in module.exports:
            if isinstance(export_decl, ExportDefaultDeclaration):
                # export default expr
                # Evaluate expression and store as 'default'
                value = self._evaluate_export_value(
                    export_decl.declaration,
                    module.environment
                )
                module.namespace['default'] = value

            elif isinstance(export_decl, ExportNamedDeclaration):
                if export_decl.declaration:
                    # export const x = 1; export function foo() {}
                    self._export_declaration(export_decl.declaration, module)

                elif export_decl.specifiers:
                    # export { x, y as z }
                    for spec in export_decl.specifiers:
                        local_name = spec.local.name
                        exported_name = spec.exported.name

                        if export_decl.source:
                            # Re-export: export { x } from './other.js'
                            dep_module = self._find_dependency_module(
                                module,
                                export_decl.source.value
                            )
                            value = dep_module.namespace.get(
                                local_name,
                                Value.from_undefined()
                            )
                        else:
                            # Local export
                            value = module.environment.get(
                                local_name,
                                Value.from_undefined()
                            )

                        module.namespace[exported_name] = value

            elif isinstance(export_decl, ExportAllDeclaration):
                # export * from './other.js'
                dep_module = self._find_dependency_module(
                    module,
                    export_decl.source.value
                )

                if export_decl.exported:
                    # export * as ns from './other.js'
                    namespace_obj = self._create_namespace_object(dep_module)
                    module.namespace[export_decl.exported.name] = namespace_obj
                else:
                    # export * from './other.js'
                    # Copy all exports except 'default'
                    for name, value in dep_module.namespace.items():
                        if name != 'default':
                            module.namespace[name] = value

    def _create_namespace_object(self, module: Module) -> Value:
        """
        Create module namespace object.

        Args:
            module: Module to create namespace for

        Returns:
            Value wrapping namespace object
        """
        # Create object with module exports
        namespace = JSObject()
        for name, value in module.namespace.items():
            namespace.set_property(name, value)

        return Value.from_object(namespace)

    def _find_dependency_module(self, module: Module, specifier: str) -> Module:
        """Find dependency module by specifier."""
        # This is simplified - in practice would use the registry
        for dep in module.dependencies:
            if dep.url.endswith(specifier):
                return dep

        raise ModuleEvaluationError(
            f"Dependency not found: {specifier} in {module.url}"
        )

    def _export_declaration(self, declaration, module: Module):
        """Export bindings from a declaration."""
        # For declarations like: export const x = 1;
        # The binding is already in module.environment from execution
        # We just need to add it to namespace

        if isinstance(declaration, VariableDeclaration):
            for declarator in declaration.declarations:
                name = declarator.id.name
                value = module.environment.get(name, Value.from_undefined())
                module.namespace[name] = value

        elif isinstance(declaration, FunctionDeclaration):
            name = declaration.id.name
            value = module.environment.get(name, Value.from_undefined())
            module.namespace[name] = value

        elif isinstance(declaration, ClassDeclaration):
            name = declaration.id.name
            value = module.environment.get(name, Value.from_undefined())
            module.namespace[name] = value

# ============================================================================
# MODULE REGISTRY
# ============================================================================

class ModuleRegistry:
    """
    Global registry of loaded modules.

    Responsibilities:
        - Cache modules by URL (singleton per URL)
        - Prevent duplicate loading
        - Enable module sharing across imports
    """

    def __init__(self):
        self.modules: Dict[str, Module] = {}

    def get(self, url: str) -> Optional[Module]:
        """
        Get module from registry.

        Args:
            url: Absolute module URL

        Returns:
            Module if registered, None otherwise
        """
        return self.modules.get(url)

    def register(self, module: Module) -> None:
        """
        Register module in registry.

        Args:
            module: Module to register
        """
        self.modules[module.url] = module

    def clear(self):
        """Clear all registered modules."""
        self.modules.clear()

# ============================================================================
# EXCEPTIONS
# ============================================================================

class ModuleError(Exception):
    """Base class for module errors."""
    pass

class ModuleNotFoundError(ModuleError):
    """Module file not found."""
    pass

class ModuleLoadError(ModuleError):
    """Error loading module source."""
    pass

class ModuleResolutionError(ModuleError):
    """Error resolving module specifier."""
    pass

class ModuleLinkError(ModuleError):
    """Error linking module."""
    pass

class ModuleEvaluationError(ModuleError):
    """Error evaluating module."""
    pass
```

---

### 3. Bytecode Changes

**Add Opcodes:**

```python
class Opcode(Enum):
    # Existing opcodes...

    # Module opcodes
    IMPORT_MODULE = auto()         # Load and link module
    EXPORT_BINDING = auto()        # Export a binding
    GET_MODULE_NAMESPACE = auto()  # Get module namespace object
    IMPORT_BINDING = auto()        # Import binding from module
```

**Compilation Strategy:**

**Import statements compile to:**
1. IMPORT_MODULE - Ensure module is loaded and linked
2. IMPORT_BINDING - Get binding from module namespace
3. STORE_LOCAL - Store in module environment

**Export statements compile to:**
1. Regular code execution (for export declarations)
2. EXPORT_BINDING - Add binding to module namespace

**Example:**

```javascript
// Source
import { add } from './math.js';
export const result = add(1, 2);

// Bytecode (conceptual)
IMPORT_MODULE './math.js'        // Load math.js
IMPORT_BINDING 'add'              // Get math.namespace.add
STORE_LOCAL 'add'                 // add = ...

LOAD_LOCAL 'add'                  // Load add function
LOAD_CONSTANT 1                   // Push 1
LOAD_CONSTANT 2                   // Push 2
CALL_FUNCTION 2                   // add(1, 2)
STORE_LOCAL 'result'              // const result = ...
EXPORT_BINDING 'result'           // Export result
```

---

### 4. Interpreter Changes

**Module Execution:**

```python
class Interpreter:
    def __init__(self, gc, event_loop=None, module_registry=None):
        self.gc = gc
        self.event_loop = event_loop or EventLoop()
        self.module_registry = module_registry or ModuleRegistry()
        # ... existing init ...

    def execute_module(self, module_url: str) -> Value:
        """
        Execute module as entry point.

        Args:
            module_url: Absolute path to module

        Returns:
            Module namespace
        """
        # Create module system components
        loader = ModuleLoader()
        linker = ModuleLinker(loader, Parser, self.module_registry)
        evaluator = ModuleEvaluator(self)

        # Load module
        source = loader.load(module_url)
        module = Module(url=module_url, source=source)
        self.module_registry.register(module)

        # Link module (and all dependencies)
        linker.link(module)

        # Evaluate module (and all dependencies)
        evaluator.evaluate(module)

        # Return namespace
        return evaluator._create_namespace_object(module)

    def execute_in_environment(self, bytecode, environment):
        """
        Execute bytecode in specified environment.

        Args:
            bytecode: Bytecode to execute
            environment: Environment dict

        Returns:
            Execution result
        """
        # Save current environment
        saved_env = self.environment

        # Set module environment
        self.environment = environment

        try:
            result = self.execute(bytecode)
            return result
        finally:
            # Restore environment
            self.environment = saved_env

    def execute(self, bytecode, *args):
        # ... existing execute code ...

        elif opcode == Opcode.IMPORT_MODULE:
            # Ensure module is loaded and linked
            module_url = instruction.operand1

            # Module should already be loaded by linker
            module = self.module_registry.get(module_url)
            if module is None:
                raise RuntimeError(f"Module not loaded: {module_url}")

            # Push module onto stack
            frame.push(Value.from_object(module))

        elif opcode == Opcode.IMPORT_BINDING:
            # Get binding from module namespace
            module = frame.pop()
            binding_name = instruction.operand1

            value = module.namespace.get(binding_name, Value.from_undefined())
            frame.push(value)

        elif opcode == Opcode.EXPORT_BINDING:
            # Add binding to current module's namespace
            binding_name = instruction.operand1
            value = frame.peek()  # Don't pop - export doesn't consume

            # Get current module from execution context
            current_module = self.current_module
            current_module.namespace[binding_name] = value

        elif opcode == Opcode.GET_MODULE_NAMESPACE:
            # Get module namespace object
            module = frame.pop()

            namespace_obj = JSObject()
            for name, value in module.namespace.items():
                namespace_obj.set_property(name, value)

            frame.push(Value.from_object(namespace_obj))
```

---

### 5. Cyclic Dependency Handling

**Problem:**

```javascript
// a.js
import { b } from './b.js';
export const a = b + 1;

// b.js
import { a } from './a.js';
export const b = a + 1;

// Cycle: a.js → b.js → a.js
```

**Solutions:**

1. **Detect and error**: Reject cyclic dependencies
   - ❌ Too restrictive, ES spec allows cycles

2. **Temporal Dead Zone (TDZ)**: Bindings are undefined until initialized
   - ✅ Matches ES spec
   - Imports create bindings immediately (undefined)
   - Bindings become available after module evaluates
   - Accessing before initialization throws ReferenceError

3. **Partial evaluation**: Evaluate modules incrementally
   - ❌ Complex, hard to get right

**Decision:** TDZ approach (option 2)

**Implementation:**

```python
def _create_module_environment(self, module: Module) -> Dict[str, Value]:
    """Create module environment with TDZ for imports."""
    env = {}

    for import_decl in module.imports:
        dep_module = self._find_dependency_module(module, import_decl.source.value)

        for specifier in import_decl.specifiers:
            if isinstance(specifier, ImportSpecifier):
                imported_name = specifier.imported.name
                local_name = specifier.local.name

                # Create binding in TDZ
                # If dep_module is EVALUATING (cyclic), binding is undefined
                # If dep_module is EVALUATED, binding has value
                if dep_module.status == ModuleStatus.EVALUATING:
                    # Cyclic dependency - TDZ
                    env[local_name] = Value.from_tdz(imported_name)
                else:
                    # Normal dependency - get value
                    env[local_name] = dep_module.namespace.get(
                        imported_name,
                        Value.from_undefined()
                    )

    return env

# When accessing TDZ binding:
def _load_local(self, name):
    value = self.environment.get(name)

    if value.is_tdz():
        raise ReferenceError(
            f"Cannot access '{value.tdz_name}' before initialization"
        )

    return value
```

**Example execution:**

```javascript
// a.js
import { b } from './b.js';
console.log(b);  // OK if b.js evaluated first
export const a = 1;

// b.js
import { a } from './a.js';
console.log(a);  // ReferenceError - a is in TDZ
export const b = 2;
```

Evaluation order:
1. Link a.js → discovers b.js dependency
2. Link b.js → discovers a.js dependency (cycle detected)
3. Evaluate a.js:
   - Imports b from b.js (not evaluated yet, creates TDZ binding)
   - Evaluates b.js:
     - Imports a from a.js (EVALUATING, creates TDZ binding)
     - console.log(a) → ReferenceError (TDZ)

---

### 6. Module Resolution Algorithm

**Specification:** Resolve import specifier to absolute URL

**Algorithm:**

```python
def resolve_specifier(self, specifier: str, referrer: str) -> str:
    """
    Resolve import specifier to absolute URL.

    Args:
        specifier: Import specifier string
        referrer: URL of importing module

    Returns:
        Absolute URL
    """

    # 1. Relative path: ./... or ../...
    if specifier.startswith('./') or specifier.startswith('../'):
        referrer_dir = os.path.dirname(referrer)
        resolved = os.path.join(referrer_dir, specifier)
        return os.path.normpath(resolved)

    # 2. Absolute path: /...
    if specifier.startswith('/'):
        return os.path.normpath(specifier)

    # 3. Bare specifier: 'lodash', 'react'
    # Future: node_modules resolution
    # For now: error
    raise ModuleResolutionError(
        f"Bare module specifiers not supported: {specifier}"
    )

# Examples:
resolve_specifier('./math.js', '/app/main.js')
# → /app/math.js

resolve_specifier('../util/helper.js', '/app/lib/foo.js')
# → /app/util/helper.js

resolve_specifier('/abs/path/module.js', '/anywhere.js')
# → /abs/path/module.js
```

---

## Implementation Phases

### Phase 2.7.1: Parser Support (4-6 hours)

**Goal:** Parse import/export syntax

**Tasks:**
- Add IMPORT, EXPORT, FROM, AS tokens
- Add import/export AST nodes
- Implement `_parse_import_declaration()`
- Implement `_parse_export_declaration()`
- Handle all import variants:
  - Default import
  - Named imports
  - Namespace import
  - Side-effect import
  - Mixed imports
- Handle all export variants:
  - Default export
  - Named export (declaration)
  - Named export (list)
  - Re-export

**Tests:**
```python
def test_parse_import_default():
    source = "import foo from './module.js';"
    ast = parse(source)
    assert isinstance(ast.body[0], ImportDeclaration)

def test_parse_import_named():
    source = "import { x, y as z } from './module.js';"
    ast = parse(source)
    assert len(ast.body[0].specifiers) == 2

def test_parse_export_default():
    source = "export default function() {}"
    ast = parse(source)
    assert isinstance(ast.body[0], ExportDefaultDeclaration)

# ... 20+ parser tests
```

**Deliverable:** Parser handles all import/export syntax

---

### Phase 2.7.2: Module Loader (3-4 hours)

**Goal:** Load module source from file system

**Tasks:**
- Implement `ModuleLoader` class
- Implement `load()` method
- Implement `normalize_url()` method
- Handle file not found errors
- Handle encoding errors

**Tests:**
```python
def test_load_module():
    loader = ModuleLoader()
    source = loader.load('/path/to/module.js')
    assert isinstance(source, str)

def test_load_nonexistent_module():
    loader = ModuleLoader()
    with pytest.raises(ModuleNotFoundError):
        loader.load('/nonexistent.js')

def test_normalize_url():
    loader = ModuleLoader(base_dir='/app')
    url = loader.normalize_url('./module.js')
    assert url == '/app/module.js'

# ... 10+ loader tests
```

**Deliverable:** Can load module source from disk

---

### Phase 2.7.3: Module Linker (4-6 hours)

**Goal:** Link modules and resolve dependencies

**Tasks:**
- Implement `ModuleLinker` class
- Implement `link()` method
- Implement `resolve_specifier()` method
- Implement `_extract_imports_exports()` method
- Build dependency graph
- Detect cyclic dependencies

**Tests:**
```python
def test_link_single_module():
    # Module with no imports
    linker = ModuleLinker(...)
    module = Module(url='/test.js', source='export const x = 1;')
    linker.link(module)
    assert module.status == ModuleStatus.LINKED

def test_link_with_dependencies():
    # Module importing another module
    linker = ModuleLinker(...)
    module = Module(url='/main.js', source="import {x} from './dep.js';")
    linker.link(module)
    assert len(module.dependencies) == 1

def test_resolve_relative_specifier():
    linker = ModuleLinker(...)
    url = linker.resolve_specifier('./math.js', '/app/main.js')
    assert url == '/app/math.js'

def test_cyclic_dependency_detection():
    # a.js imports b.js, b.js imports a.js
    linker = ModuleLinker(...)
    # Should not throw - cycles are allowed
    linker.link(module_a)

# ... 15+ linker tests
```

**Deliverable:** Can link modules and resolve dependencies

---

### Phase 2.7.4: Module Evaluator (4-6 hours)

**Goal:** Execute modules and populate namespaces

**Tasks:**
- Implement `ModuleEvaluator` class
- Implement `evaluate()` method
- Implement `_create_module_environment()` method
- Implement `_populate_namespace()` method
- Handle TDZ for cyclic dependencies
- Create module namespace objects

**Tests:**
```python
def test_evaluate_simple_module():
    # export const x = 42;
    evaluator = ModuleEvaluator(...)
    module = create_and_link_module('export const x = 42;')
    evaluator.evaluate(module)
    assert module.namespace['x'].as_number() == 42

def test_evaluate_with_import():
    # a.js: export const x = 1;
    # b.js: import {x} from './a.js'; export const y = x + 1;
    evaluator = ModuleEvaluator(...)
    evaluator.evaluate(module_b)
    assert module_b.namespace['y'].as_number() == 2

def test_cyclic_dependency_tdz():
    # a.js: import {b} from './b.js'; export const a = 1;
    # b.js: import {a} from './a.js'; console.log(a); export const b = 2;
    # Accessing a in b.js should throw ReferenceError
    with pytest.raises(ReferenceError):
        evaluator.evaluate(module_a)

# ... 15+ evaluator tests
```

**Deliverable:** Can execute modules and populate namespaces

---

### Phase 2.7.5: Bytecode Integration (3-4 hours)

**Goal:** Compile import/export to bytecode

**Tasks:**
- Add IMPORT_MODULE, EXPORT_BINDING, etc. opcodes
- Implement compilation of import declarations
- Implement compilation of export declarations
- Implement interpreter opcode handlers

**Tests:**
```python
def test_compile_import():
    source = "import { x } from './module.js';"
    bytecode = compile(source)
    assert Opcode.IMPORT_MODULE in bytecode

def test_compile_export():
    source = "export const x = 42;"
    bytecode = compile(source)
    assert Opcode.EXPORT_BINDING in bytecode

def test_execute_import():
    # Integration test
    # ... setup modules ...
    result = interpreter.execute_module('/main.js')
    assert result is not None

# ... 10+ bytecode tests
```

**Deliverable:** Import/export compiled to bytecode

---

### Phase 2.7.6: End-to-End Integration (2-3 hours)

**Goal:** Complete module system integration

**Tasks:**
- Integrate all components
- Add `execute_module()` to interpreter
- Test complete module lifecycle
- Handle edge cases
- Comprehensive integration tests

**Tests:**
```javascript
// Test 1: Simple export/import
// math.js
export const add = (a, b) => a + b;

// main.js
import { add } from './math.js';
console.log(add(1, 2));  // 3

// Test 2: Default export/import
// greet.js
export default (name) => `Hello, ${name}!`;

// main.js
import greet from './greet.js';
console.log(greet('World'));  // Hello, World!

// Test 3: Namespace import
// math.js
export const PI = 3.14;
export const E = 2.71;

// main.js
import * as math from './math.js';
console.log(math.PI);  // 3.14

// Test 4: Multiple modules
// a.js
export const x = 1;

// b.js
export const y = 2;

// main.js
import { x } from './a.js';
import { y } from './b.js';
console.log(x + y);  // 3

// Test 5: Cyclic dependency (safe)
// a.js
import { b } from './b.js';
export const a = 1;
console.log(b);  // 2 (OK - b evaluated first)

// b.js
export const b = 2;

// main.js
import { a } from './a.js';
console.log(a);  // 1

// Test 6: Re-export
// math.js
export const add = (a, b) => a + b;

// index.js
export { add } from './math.js';

// main.js
import { add } from './index.js';
console.log(add(1, 2));  // 3
```

**Deliverable:** Fully functional ES Modules system

---

**Total Estimated Time:** 20-29 hours

---

## Testing Strategy

### Unit Tests

**Parser (20+ tests):**
- Import default
- Import named
- Import namespace
- Import side-effect
- Export default (function/class/expression)
- Export named (declaration/list)
- Export all
- Re-export
- Mixed imports
- Edge cases (no semicolon, etc.)

**Module Loader (10+ tests):**
- Load existing file
- Load non-existent file (error)
- Normalize relative paths
- Normalize absolute paths
- Handle encoding errors

**Module Linker (15+ tests):**
- Link module with no dependencies
- Link module with dependencies
- Resolve relative specifiers
- Resolve absolute specifiers
- Detect cyclic dependencies
- Build dependency graph
- Extract imports/exports from AST

**Module Evaluator (15+ tests):**
- Evaluate simple module
- Evaluate module with imports
- Evaluate module with exports
- Create module environment
- Populate namespace
- Handle TDZ for cyclic dependencies
- Create namespace objects

**Bytecode/Interpreter (10+ tests):**
- Compile import statements
- Compile export statements
- Execute IMPORT_MODULE opcode
- Execute EXPORT_BINDING opcode
- Execute GET_MODULE_NAMESPACE opcode

### Integration Tests

**End-to-End (20+ tests):**

```javascript
// Test: Simple named export/import
// math.js
export const add = (a, b) => a + b;
export const PI = 3.14;

// main.js
import { add, PI } from './math.js';
assert(add(1, 2) === 3);
assert(PI === 3.14);

// Test: Default export/import
// greet.js
export default (name) => `Hello, ${name}!`;

// main.js
import greet from './greet.js';
assert(greet('World') === 'Hello, World!');

// Test: Namespace import
// math.js
export const PI = 3.14;
export const E = 2.71;

// main.js
import * as math from './math.js';
assert(math.PI === 3.14);
assert(math.E === 2.71);

// Test: Mixed exports
// utils.js
export default class Calculator {
    add(a, b) { return a + b; }
}
export const version = '1.0';

// main.js
import Calculator, { version } from './utils.js';
const calc = new Calculator();
assert(calc.add(1, 2) === 3);
assert(version === '1.0');

// Test: Re-export
// math.js
export const add = (a, b) => a + b;

// index.js
export { add } from './math.js';

// main.js
import { add } from './index.js';
assert(add(1, 2) === 3);

// Test: Cyclic dependencies (valid)
// a.js
import { b } from './b.js';
export const a = 1;
// Can access b after both modules evaluated

// b.js
import { a } from './a.js';
export const b = 2;
// CANNOT access a during b.js evaluation (TDZ)

// main.js
import { a } from './a.js';
import { b } from './b.js';
assert(a === 1);
assert(b === 2);

// Test: Multiple dependencies
// a.js
export const a = 1;

// b.js
export const b = 2;

// c.js
import { a } from './a.js';
import { b } from './b.js';
export const c = a + b;

// main.js
import { c } from './c.js';
assert(c === 3);

// Test: Side-effect import
// polyfill.js
Array.prototype.last = function() {
    return this[this.length - 1];
};

// main.js
import './polyfill.js';
assert([1, 2, 3].last() === 3);
```

---

## Success Criteria

- [ ] Named exports work
- [ ] Default exports work
- [ ] Named imports work
- [ ] Default imports work
- [ ] Namespace imports (`import * as`) work
- [ ] Re-exports work
- [ ] Side-effect imports work
- [ ] Module loader loads from file system
- [ ] Module linker resolves dependencies correctly
- [ ] Module evaluator executes modules correctly
- [ ] Module registry caches modules
- [ ] Cyclic dependencies handled via TDZ
- [ ] Module namespace objects work
- [ ] 50+ tests passing
- [ ] No breaking changes to existing features
- [ ] Performance: Module caching prevents re-execution

---

## Future Work (Phase 3+)

### Dynamic Imports
```javascript
// Dynamic import returns Promise
const module = await import('./module.js');
console.log(module.default);
```

### Top-Level Await
```javascript
// In ES modules
const data = await fetch('/api/data');
export const result = await data.json();
```

### Import Assertions (JSON modules)
```javascript
import data from './data.json' assert { type: 'json' };
console.log(data.name);
```

### Package.json Support
```javascript
// Support package.json "exports" field
import { add } from 'my-library';
```

### node_modules Resolution
```javascript
// Bare specifiers resolve to node_modules
import React from 'react';
import lodash from 'lodash';
```

### Web Compatibility
```javascript
// Fetch modules over HTTP
import { add } from 'https://example.com/math.js';
```

### Import Maps
```javascript
// Configure bare specifier resolution
<script type="importmap">
{
  "imports": {
    "lodash": "/node_modules/lodash/index.js"
  }
}
</script>
```

---

## Architecture Diagrams

### Module Lifecycle

```
┌─────────────────────────────────────────────────────────────────┐
│                        MODULE LIFECYCLE                          │
└─────────────────────────────────────────────────────────────────┘

User calls interpreter.execute_module('/main.js')
    ↓
┌───────────────┐
│ UNLINKED      │  Module created
│ (Created)     │  source loaded
└───────┬───────┘
        ↓
┌───────────────┐
│ LINKING       │  Parse AST
│ (Loading)     │  Extract imports/exports
│               │  Load dependencies (recursive)
│               │  Build dependency graph
└───────┬───────┘
        ↓
┌───────────────┐
│ LINKED        │  All dependencies resolved
│ (Ready)       │  Dependency graph complete
└───────┬───────┘
        ↓
┌───────────────┐
│ EVALUATING    │  Create module environment
│ (Executing)   │  Compile to bytecode
│               │  Execute bytecode
│               │  Populate namespace
└───────┬───────┘
        ↓
┌───────────────┐
│ EVALUATED     │  Execution complete
│ (Complete)    │  Namespace populated
│               │  Ready for import
└───────────────┘
```

### Module Loading Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    MODULE LOADING FLOW                           │
└─────────────────────────────────────────────────────────────────┘

import { add } from './math.js';
    ↓
┌──────────────────────┐
│ ModuleLinker         │
│ resolve_specifier()  │  './math.js' + '/app/main.js'
│                      │  → '/app/math.js'
└──────────┬───────────┘
           ↓
┌──────────────────────┐
│ ModuleRegistry       │
│ get('/app/math.js')  │  Check cache
└──────────┬───────────┘
           ↓
      Cache hit?
      ┌───┴───┐
     YES     NO
      │       │
      │       ↓
      │  ┌──────────────────┐
      │  │ ModuleLoader     │
      │  │ load()           │  Read file from disk
      │  └────────┬─────────┘
      │           ↓
      │  ┌──────────────────┐
      │  │ Module           │
      │  │ (new instance)   │  Create Module object
      │  └────────┬─────────┘
      │           ↓
      │  ┌──────────────────┐
      │  │ ModuleRegistry   │
      │  │ register()       │  Cache for future imports
      │  └────────┬─────────┘
      │           │
      └───────────┘
           ↓
      Return Module
```

### Cyclic Dependency Handling

```
┌─────────────────────────────────────────────────────────────────┐
│              CYCLIC DEPENDENCY HANDLING (TDZ)                    │
└─────────────────────────────────────────────────────────────────┘

// a.js                      // b.js
import { b } from './b.js';  import { a } from './a.js';
export const a = 1;          console.log(a);  // ReferenceError!
                             export const b = 2;

Evaluation:
    ┌──────────────┐
    │ Evaluate a.js│
    └──────┬───────┘
           │ status = EVALUATING
           ↓
    ┌──────────────┐
    │ Import b     │
    │ from b.js    │
    └──────┬───────┘
           ↓
    ┌──────────────┐
    │ Evaluate b.js│
    └──────┬───────┘
           │ status = EVALUATING
           ↓
    ┌──────────────┐
    │ Import a     │
    │ from a.js    │  ← Cycle detected!
    └──────┬───────┘
           ↓
    ┌──────────────────────┐
    │ Create TDZ binding   │  a = Value.from_tdz('a')
    │ for 'a'              │  (binding exists but uninitialized)
    └──────┬───────────────┘
           ↓
    ┌──────────────────────┐
    │ console.log(a)       │  Access TDZ binding
    └──────┬───────────────┘
           ↓
    ┌──────────────────────┐
    │ ReferenceError!      │  Cannot access 'a' before initialization
    └──────────────────────┘

Solution: Don't access imported bindings during module initialization
```

---

**Document Status:** Ready for implementation
**Next Step:** Begin Phase 2.7.1 (Parser Support)
